import base64
import logging

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field, ValidationError

from storyteller.modules.common.progress_bar import ProgressBar
from storyteller.modules.st.option_choices import artistic_styles

__all__ = (
    "describe_image",
    "generate_story",
    "load_characters",
)

# Load environment variables from a .env file
load_dotenv()

# Storyteller LLM
STORY_LLM = ChatOpenAI(
    # model="o4-mini",
    model="gpt-4o-mini",
    # reasoning_effort="high",
    # max_tokens=20_000,
)

# Image descriptor LLM
IMAGE_LLM = ChatOpenAI(
    # model="gpt-4.1",
    model="gpt-4o-mini",
    max_tokens=100,
)

LOGGER = logging.getLogger(__name__)

# --- Pydantic Models ---


class Character(BaseModel):
    name: str
    interests: list[str]
    favourite_animal: str
    age: int
    eye_color: str | None = None
    hair_color: str | None = None
    skin_color: str | None = None
    height: int | None = None  # Height in cm
    identity: str | None = None
    features: str | None = None


class StoryOutput(BaseModel):
    title: str = Field(
        description="Engaging short story title. Use from 15 to 40 characters."
    )
    story: str = Field(description="The full, engaging LONG story text.")
    key_moments: list[str] = Field(
        description=(
            "A list of 8 to 10 most important paragraphs or key events from "
            "the story. These should highlight significant events, character "
            "developments, or turning points."
        )
    )
    key_sd_prompts: list[str] = Field(
        description=(
            "A list of descriptive Stable Diffusion (Flux1.1) prompts, "
            "corresponding to each key moment. "
            "Each prompt should be vivid and detailed. When a character is a "
            "primary subject, "
            "include their key physical attributes in a parenthetical format "
            "(e.g., 'CharacterName (age year old, identity, eye color eyes, "
            "hair color hair, skin color skin, height cm tall) interacting "
            "with the scene'). "
            "Ensure the number of prompts matches key moments, ideally 8 "
            "to 10 prompts."
        )
    )
    cover_image_sd_prompt: str = Field(
        description=(
            "A single, highly descriptive Stable Diffusion (Flux1.1) prompt "
            "suitable for generating a captivating cover image for the entire "
            "story. "
            "This prompt should encapsulate the main theme, atmosphere, and "
            "key characters of the story. "
            "If characters are central, include their key physical attributes "
            "in a parenthetical format "
            "(e.g., 'CharacterName (age year old, identity, eye color eyes, "
            "hair color hair, skin color skin, height cm tall) in a thematic "
            "setting')."
        )
    )
    back_cover_image_sd_prompt: str = Field(
        description=(
            "A single, richly descriptive Stable Diffusion (Flux1.1) prompt "
            "designed for generating a visually compelling back cover image "
            "for the storybook. "
            "This prompt should reflect the story's resolution, lingering "
            "emotions, or symbolic closure, offering a sense of reflection or "
            "finality. "
            "If relevant, include visual motifs, key locations, or character "
            "silhouettes to subtly echo the journey without revealing "
            "critical plot points. "
            "Aim for mood, symbolism, and visual harmony with the cover, "
            "rather than literal scenes or direct character depictions."
        )
    )


def load_characters(data: list[dict], progress_bar: ProgressBar) -> list[Character]:
    """
    Convert a list of raw dicts into validated Character objects.
    Expects input dictionary keys to match Character model field
    names (e.g., 'name', 'favourite_animal').
    Parses 'interests' if it's a comma-separated string or ensures it's a
    list of strings.
    """
    characters: list[Character] = []
    for item_dict in data:
        try:
            char_name = item_dict.get("name")
            if not char_name:
                LOGGER.warning(
                    f"Skipping character data due to missing 'name' field or "
                    f"empty name: {item_dict}"
                )
                continue

            interests_input = item_dict.get("interests", "")
            parsed_interests: list[str] = []
            if isinstance(interests_input, str):
                parsed_interests = [
                    i.strip() for i in interests_input.split(",") if i.strip()
                ]
            elif isinstance(interests_input, list):
                parsed_interests = [
                    str(i).strip() for i in interests_input if str(i).strip()
                ]

            age_input = item_dict.get("age")
            if age_input is None:
                LOGGER.warning(
                    f"Skipping character '{char_name}' due to missing 'age' field."
                )
                continue
            parsed_age = int(age_input)

            height_input = item_dict.get("height")
            parsed_height: int | None = None
            if height_input is not None and str(height_input).strip() != "":
                try:
                    parsed_height = int(height_input)
                except ValueError:
                    LOGGER.warning(
                        f"Invalid 'height' value "
                        f"for '{char_name}': {height_input}. Setting to None."
                    )

            _character_image_data = item_dict.get("image")
            _character_image = _character_image_data[0] if _character_image_data else None
            LOGGER.info(type(_character_image))
            # dump_pickle(_character_image, "_character_image.pkl")
            _image_bytes = _character_image.contents if _character_image else None
            if _image_bytes:
                if progress_bar:
                    progress_bar.update(subtitle="Describing the user-uploaded image...")
                character_features = describe_image(_image_bytes)
            else:
                character_features = None

            model_data = {
                "name": char_name,
                "interests": parsed_interests,
                "favourite_animal": item_dict.get("favourite_animal", "Unknown"),
                "age": parsed_age,
                "eye_color": item_dict.get("eye_color"),
                "hair_color": item_dict.get("hair_color"),
                "skin_color": item_dict.get("skin_color"),
                "height": parsed_height,
                "identity": item_dict.get("identity"),
                "features": character_features,
            }

            LOGGER.info("model_data")
            LOGGER.info(model_data)

            characters.append(Character(**model_data))

        except ValidationError as e:
            LOGGER.error(
                f"Pydantic validation error for character "
                f"'{item_dict.get('name', 'Unknown')}': {e}"
            )
        except ValueError as e:
            LOGGER.error(
                f"Data type error for character '{item_dict.get('name', 'Unknown')}': {e}"
            )
        except Exception as e:
            LOGGER.error(
                f"Unexpected error processing character data "
                f"'{item_dict.get('name', 'Unknown')}': {e}"
            )

    return characters


def generate_story(
    base_prompt: str,
    characters: list[Character],
    progress_bar: ProgressBar,
    artistic_style: str | None = None,
    # Options: "early" (5-6), "middle" (7-8), "advanced" (9-10), "balanced"
    reading_level: str = "balanced",
) -> StoryOutput:
    """
    Generate a short story with key moments and Stable Diffusion prompts
    using a base prompt and a list of Character objects with detailed
    descriptions.
    Returns a structured StoryOutput object.
    """
    if not characters:
        raise ValueError(
            "Character list cannot be empty for story generation.",
        )

    _artistic_style = artistic_styles.get(artistic_style, None)
    style_instruction = ""
    if _artistic_style:
        style_instruction = (
            f"\n\nPlease apply the following artistic style to all image "
            f"prompts: Create an image in the style of "
            f"{artistic_style} {_artistic_style}."
        )

    reading_level_guide = {
        "early": (
            "Use very simple sentences, familiar words, and frequent picture "
            "opportunities. Average sentence: 7-10 words. Limit to 800-1000 "
            "words total."
        ),
        "middle": (
            "Use straightforward sentences with occasional compound "
            "sentences. Average sentence: 10-12 words. Aim for 1000-1200 "
            "words total."
        ),
        "advanced": (
            "Use more varied sentence structures and introduce moderate "
            "vocabulary challenges. Average sentence: 12-15 words. Aim for "
            "1200-1500 words total."
        ),
        "balanced": (
            "Blend approaches to be accessible to the full age range with "
            "simpler sections and more advanced sections. Average sentence "
            "length should vary between 8-15 words. Aim for 1000-1300 words "
            "total."
        ),
    }

    if progress_bar:
        progress_bar.update(subtitle="Assembling the characters...")

    chars_desc_list = []
    for c in characters:
        desc = f"- {c.name}: A {c.age}-year-old"
        if c.identity:
            desc += f" {c.identity}"
        if c.height:
            desc += f", {c.height}cm tall"
        if c.features:
            desc += f", {c.features}"

        physical_traits = []
        if c.eye_color:
            physical_traits.append(f"{c.eye_color} eyes")
        if c.hair_color:
            physical_traits.append(f"{c.hair_color} hair")
        if c.skin_color:
            physical_traits.append(f"{c.skin_color} skin")

        if physical_traits:
            desc += f", with {', '.join(physical_traits)}"

        desc += (
            f". Interested in {', '.join(c.interests)}. "
            f"Favourite animal: {c.favourite_animal}."
        )
        chars_desc_list.append(desc)
    chars_desc = "\n".join(chars_desc_list)

    system_message_content = (
        "You are a highly creative st specialized in creating "
        "engaging children's stories for ages 5-10. "
        "You craft vivid, age-appropriate narratives and generate detailed "
        "image prompts. "
        "Your task is to write a story based on the provided "
        "characters (including their physical descriptions) and themes, "
        "then extract key moments and generate corresponding image prompts "
        "for Stable Diffusion (Flux1.1)."
        "Ensure your output strictly adheres to the requested JSON structure."
    )

    human_message_content = (
        f"{base_prompt}\n\n"
        "Here are the characters to feature in the story:\n"
        f"{chars_desc}\n\n"
        f"This story should use a {reading_level} reading level. "
        f"{reading_level_guide[reading_level]}\n\n"
        "Please generate the following based on these characters and the base "
        "prompt:\n\n"
        "1.  **Full Story**: An engaging story that incorporates the "
        "characters naturally. "
        "The story should be engaging and easy to follow for children "
        "between 5-10 years old. "
        "Use the following guidelines for child-friendly writing:\n"
        "- Structure the story into 8-12 shorter paragraphs with 3-5 "
        "sentences per paragraph and clear section breaks\n"
        "- Use vocabulary appropriate for the specified reading level\n"
        "- Introduce no more than 3-5 new or challenging words (with "
        "context clues to help understand them)\n"
        "- Use active voice and concrete descriptions\n"
        "- Include natural-sounding dialogue that's fun to read aloud\n"
        "- Avoid idioms, metaphors, and complex sentence structures with "
        "multiple clauses\n"
        "- Include 2-3 questions or moments where the reader is invited to "
        "participate (e.g., 'Can you guess what happened next?')\n"
        "- Create at least one repeating phrase or sound that appears 3-4 "
        "times in the story\n\n"
        "Use the following story references as inspiration: "
        "'Frog and Toad' (Arnold Lobel), "
        "'Amelia Bedelia' (Peggy Parish), "
        "'Magic Tree House' (early books), and "
        "'Pete the Cat' series.\n\n"
        "2.  **Key Moments**: From your story, identify 5-8 key moments that "
        "would make excellent illustrations. "
        "These should be evenly distributed throughout the story and "
        "represent the most important or visually interesting scenes.\n\n"
        "3.  **Stable Diffusion Prompts for Key Moments**: For each key "
        "moment, provide one detailed and evocative prompt "
        "suitable for the Flux1.1 model. These prompts should aim to generate "
        "visually rich images representing those moments. "
        "The number of these prompts MUST exactly match the number of key "
        "moments.\n"
        "*When a character is a primary subject of a key moment, their "
        "description in the prompt MUST include their key physical "
        "attributes in a concise parenthetical format. For example: "
        "'CharacterName (age year old, identity, eye_color eyes, "
        "hair_color hair, skin_color skin, height cm tall) doing X'. If a "
        "detail is not available, omit it from the parenthetical "
        "description but include what is available.*\n\n"
        "4.  **Cover Image Stable Diffusion Prompt**: A single, highly "
        "descriptive prompt suitable for generating a captivating cover "
        "image for the entire story using Flux1.1. This prompt should "
        "encapsulate the main theme, atmosphere, and key characters. "
        "If characters are central to the cover concept, include their key "
        "physical attributes in the parenthetical format described above.\n\n"
        "5.  **Back Cover Image Stable Diffusion Prompt**: A single, richly "
        "descriptive prompt suitable for generating a visually compelling "
        "back cover image for the story using Flux1.1. This prompt should "
        "convey the story’s emotional resolution, overarching message, or "
        "symbolic closure. "
        "If appropriate, include visual motifs, key locations, or subtle "
        "character elements (e.g., silhouettes or distant figures) that echo "
        "the journey without revealing major plot points. The image should "
        "complement the front cover in tone and atmosphere.\n\n"
        "6.  **Title**: Create a simple, memorable title for the story that "
        "will appeal to children in the target age range.\n\n"
        f"{style_instruction}\n\n"
        "Remember to structure your entire response as a single JSON object "
        "with the fields 'story', 'key_moments', 'key_sd_prompts', "
        "'title', 'cover_image_sd_prompt', and 'back_cover_image_sd_prompt'."
    )

    if progress_bar:
        progress_bar.update(subtitle="Generating the story...")

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(system_message_content),
            HumanMessagePromptTemplate.from_template("{user_prompt}"),
        ]
    )

    structured_llm = STORY_LLM.with_structured_output(StoryOutput)

    chain = chat_prompt | structured_llm

    try:
        response_data = chain.invoke({"user_prompt": human_message_content})
        return response_data
    except Exception as e:
        LOGGER.error(f"Error during LLM invocation or output parsing: {e}")
        raise


def describe_image(image_bytes: bytes) -> str:
    """Describe image."""
    describe_image_prompt = """Describe this person in detail for to be used later in the text-to-image prompt.
    Start with description right away. No intro, no outro. Just the description. Stay concise within the limit
    of 100 characters.
    """  # noqa
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(describe_image_prompt),
            HumanMessage(
                content=[
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    }
                ]
            ),
        ]
    )

    # Create a chain by piping the prompt template to the LLM.
    chain = chat_prompt | IMAGE_LLM

    ai_response = chain.invoke({})

    # The response from the LLM (AIMessage) contains the generated content.
    description = ai_response.content

    return description
