import os
import re
import hashlib
import requests
from urllib.parse import quote
from character_config import CHARACTER_BIBLE, STYLE_SUFFIX

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")


def _character_seed(character_name: str) -> int:
    """Generate a stable numeric seed from the character name so the
    same character tends to look similar across scenes in one video."""
    return int(hashlib.md5(character_name.encode()).hexdigest(), 16) % 1_000_000


def _try_pollinations(full_prompt: str, output_path: str, seed: int, width=1024, height=1820, timeout=60) -> bool:
    try:
        url = f"{POLLINATIONS_BASE}/{quote(full_prompt)}"
        params = {
            "width": width,
            "height": height,
            "seed": seed,
            "nologo": "true",
            "model": "flux"
        }
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        if response.headers.get("content-type", "").startswith("image"):
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        return False
    except Exception as e:
        print(f"⚠️ Pollinations failed: {e}")
        return False


def _try_pixabay_fallback(query: str, output_path: str) -> bool:
    if not PIXABAY_API_KEY:
        return False
    try:
        clean_query = re.sub(r"[^a-zA-Z0-9 ]", "", query)[:100]
        resp = requests.get(
            "https://pixabay.com/api/",
            params={
                "key": PIXABAY_API_KEY,
                "q": clean_query or "cute cartoon bunny",
                "image_type": "illustration",
                "safesearch": "true",
                "per_page": 3,
                "orientation": "vertical"
            },
            timeout=30
        )
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        if not hits:
            return False
        img_url = hits[0]["largeImageURL"]
        img_data = requests.get(img_url, timeout=30).content
        with open(output_path, "wb") as f:
            f.write(img_data)
        return True
    except Exception as e:
        print(f"⚠️ Pixabay fallback failed: {e}")
        return False


def generate_scene_image(image_prompt: str, scene_number: int, output_dir: str = "assets/images", character_name: str = "Benny the Bunny") -> str:
    """
    Generates a single scene image.
    Primary: Pollinations.ai (free, no API key, real AI generation)
    Fallback: Pixabay stock illustration search (if Pollinations fails)
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"scene_{scene_number:02d}.png")

    full_prompt = f"{CHARACTER_BIBLE}. Scene: {image_prompt}. {STYLE_SUFFIX}"
    seed = _character_seed(character_name)

    if _try_pollinations(full_prompt, output_path, seed):
        print(f"✅ Image (Pollinations): {output_path}")
        return output_path

    print("↪️ Falling back to Pixabay stock image...")
    if _try_pixabay_fallback(image_prompt, output_path):
        print(f"✅ Image (Pixabay fallback): {output_path}")
        return output_path

    raise RuntimeError(f"No image generated for scene {scene_number} (both Pollinations and Pixabay failed)")


def generate_all_scene_images(script_data: dict, output_dir: str = "assets/images") -> list:
    image_paths = []
    character_name = script_data.get("character_name", "Benny the Bunny")
    for scene in script_data["scenes"]:
        path = generate_scene_image(
            scene["image_prompt"],
            scene["scene_number"],
            output_dir,
            character_name
        )
        image_paths.append(path)
    return image_paths


if __name__ == "__main__":
    test_prompt = "a bunny standing in a sunny meadow holding a red balloon"
    generate_scene_image(test_prompt, 1)
