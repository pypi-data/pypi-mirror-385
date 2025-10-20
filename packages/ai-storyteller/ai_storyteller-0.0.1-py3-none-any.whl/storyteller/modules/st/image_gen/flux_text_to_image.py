import fal_client

from storyteller.modules.st.option_choices import artistic_styles

__all__ = ("generate_flux_text_to_image",)


def generate_flux_text_to_image(
    prompt: str,
    artistic_style: str | None = None,
    guidance_scale: float = 9.5,
    num_inference_steps: int = 40,
) -> tuple[str, str, bool]:
    """Generate a flux text image."""
    artistic_style_prompt = artistic_styles.get(artistic_style, None)

    if artistic_style_prompt:
        final_prompt = f"""{prompt}
        Create an image in the style of {artistic_style}: {artistic_style_prompt}
        """
    else:
        final_prompt = prompt

    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])

    response = fal_client.subscribe(
        "fal-ai/nano-banana",
        # "fal-ai/flux-pro/v1.1-ultra",
        arguments={
            "prompt": final_prompt,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "seed": 1_000_000,
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    if response:
        return response["images"][0]["url"], final_prompt, True
    else:
        return "Error generating image", final_prompt, False
