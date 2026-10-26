import os
import base64
from google import genai
from google.genai import types
from character_config import CHARACTER_BIBLE, STYLE_SUFFIX

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Run list_models.py to confirm this model ID is current/available to your key
# image_agent.py — confirmed correct model
IMAGE_MODEL = "gemini-2.5-flash-image"

def generate_scene_image(image_prompt: str, scene_number: int, output_dir: str = "assets/images") -> str:
    """
    Generates a single scene image with the character bible locked in
    for visual consistency across the whole video.
    """
    os.makedirs(output_dir, exist_ok=True)

    full_prompt = (
        f"{CHARACTER_BIBLE}. "
        f"Scene: {image_prompt}. "
        f"{STYLE_SUFFIX}"
    )

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"]
        )
    )

    output_path = os.path.join(output_dir, f"scene_{scene_number:02d}.png")

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            with open(output_path, "wb") as f:
                f.write(part.inline_data.data)
            print(f"✅ Image saved: {output_path}")
            return output_path

    raise RuntimeError(f"No image generated for scene {scene_number}")


def generate_all_scene_images(script_data: dict, output_dir: str = "assets/images") -> list:
    """Generate images for every scene in the script"""
    image_paths = []
    for scene in script_data["scenes"]:
        path = generate_scene_image(
            scene["image_prompt"],
            scene["scene_number"],
            output_dir
        )
        image_paths.append(path)
    return image_paths


if __name__ == "__main__":
    test_prompt = "a bunny standing in a sunny meadow holding a red balloon"
    generate_scene_image(test_prompt, 1)
