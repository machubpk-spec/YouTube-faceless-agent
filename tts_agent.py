import os
import asyncio
import time
import edge_tts
from mutagen.mp3 import MP3

VOICE_OPTIONS = {
    "US": "en-US-AnaNeural",
    "GB": "en-GB-SoniaNeural",
    "CA": "en-CA-ClaraNeural",
    "default": "en-US-AnaNeural"
}


async def _generate_audio(text: str, output_path: str, voice: str):
    communicate = edge_tts.Communicate(text, voice, rate="-10%")
    await communicate.save(output_path)


def _generate_with_retry(text: str, output_path: str, voice: str, max_retries: int = 3):
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            asyncio.run(_generate_audio(text, output_path, voice))
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return
            raise RuntimeError("Audio file was empty after save")
        except Exception as e:
            last_error = e
            print(f"⚠️ TTS attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(2 * attempt)
    raise RuntimeError(f"TTS failed after {max_retries} attempts: {last_error}")


def generate_narration(text: str, scene_number: int, output_dir: str = "assets/audio", region: str = "US") -> dict:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"scene_{scene_number:02d}.mp3")
    voice = VOICE_OPTIONS.get(region, VOICE_OPTIONS["default"])

    _generate_with_retry(text, output_path, voice)

    audio = MP3(output_path)
    duration = audio.info.length
    return {"path": output_path, "duration": duration, "scene_number": scene_number}


def generate_all_narration(script_data: dict, output_dir: str = "assets/audio") -> list:
    audio_data = []
    for scene in script_data["scenes"]:
        result = generate_narration(scene["narration"], scene["scene_number"], output_dir)
        audio_data.append(result)
    return audio_data


if __name__ == "__main__":
    result = generate_narration("Hi there! I'm Benny the Bunny!", 1)
    print(result)
