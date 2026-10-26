import os
import asyncio
import edge_tts
from mutagen.mp3 import MP3

# Warm, friendly voices that work well for kids content in each target market
VOICE_OPTIONS = {
    "US": "en-US-AnaNeural",      # bright, young, friendly
    "GB": "en-GB-SoniaNeural",    # warm British narrator
    "CA": "en-CA-ClaraNeural",
    "default": "en-US-AnaNeural"
}


async def _generate_audio(text: str, output_path: str, voice: str):
    communicate = edge_tts.Communicate(text, voice, rate="-10%")  # slightly slower for kids
    await communicate.save(output_path)


def generate_narration(text: str, scene_number: int, output_dir: str = "assets/audio", region: str = "US") -> dict:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"scene_{scene_number:02d}.mp3")
    voice = VOICE_OPTIONS.get(region, VOICE_OPTIONS["default"])

    asyncio.run(_generate_audio(text, output_path, voice))

    audio = MP3(output_path)
    duration = audio.info.length

    return {
        "path": output_path,
        "duration": duration,
        "scene_number": scene_number
    }


def generate_all_narration(script_data: dict, output_dir: str = "assets/audio") -> list:
    audio_data = []
    for scene in script_data["scenes"]:
        result = generate_narration(
            scene["narration"],
            scene["scene_number"],
            output_dir
        )
        audio_data.append(result)
    return audio_data


if __name__ == "__main__":
    result = generate_narration("Hi there! I'm Benny the Bunny!", 1)
    print(result)
