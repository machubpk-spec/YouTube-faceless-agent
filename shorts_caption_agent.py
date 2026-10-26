import json


def generate_captions_for_scene(narration: str, duration: float, scene_number: int) -> list:
    """
    Simple proportional word-timing (no need for whisper alignment 
    at this content length/complexity)
    """
    words = narration.split()
    if not words:
        return []

    time_per_word = duration / len(words)
    captions = []

    # Group into chunks of 3-4 words for readable on-screen captions
    chunk_size = 3
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        start_time = i * time_per_word
        end_time = min((i + chunk_size) * time_per_word, duration)
        captions.append({
            "scene_number": scene_number,
            "text": " ".join(chunk),
            "start": round(start_time, 2),
            "end": round(end_time, 2)
        })

    return captions


def generate_all_captions(script_data: dict, audio_data: list) -> list:
    """audio_data must come from tts_agent.generate_all_narration()"""
    all_captions = []
    audio_lookup = {a["scene_number"]: a["duration"] for a in audio_data}

    for scene in script_data["scenes"]:
        duration = audio_lookup.get(scene["scene_number"], 3.0)
        captions = generate_captions_for_scene(
            scene["narration"],
            duration,
            scene["scene_number"]
        )
        all_captions.extend(captions)

    return all_captions


def save_captions_json(captions: list, output_path: str = "assets/captions.json"):
    with open(output_path, "w") as f:
        json.dump(captions, f, indent=2)
    return output_path
