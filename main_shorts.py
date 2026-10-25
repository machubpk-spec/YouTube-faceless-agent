import argparse
import re
import os
from topics import get_next_topic
from shorts_script_agent import generate_standalone_short, extract_short_from_longform
from fact_check_agent import verify_script
from tts_agent import run_tts
from visual_agent import fetch_pexels_images, fetch_wikimedia
from shorts_visual_agent import reframe_to_vertical
from shorts_caption_agent import get_word_timestamps, group_words
from shorts_assembly_agent import assemble_short
from shorts_upload_agent import upload_short

def parse_script_sections(script_text):
    hook = re.search(r"\[HOOK\](.*?)\[BODY\]", script_text, re.S)
    full_text = re.sub(r"\[.*?\]|KEYWORDS:.*", "", script_text).strip()
    keywords = re.findall(r"KEYWORDS:\s*(.+)", script_text)
    hook_line = hook.group(1).strip() if hook else full_text.split(".")[0]
    return hook_line, full_text, keywords

def run_shorts_pipeline(mode="standalone", long_script_path=None):
    topic = get_next_topic()

    if mode == "extract" and long_script_path and os.path.exists(long_script_path):
        with open(long_script_path, encoding="utf-8") as f:
            long_script = f.read()
        script = extract_short_from_longform(long_script)
    else:
        raw_script = generate_standalone_short(topic)
        script = verify_script(raw_script, topic)

    hook_line, narration_text, keyword_lines = parse_script_sections(script)
    run_tts(narration_text, "short_voice.mp3")

    raw_images = []
    for kw_line in keyword_lines:
        for kw in kw_line.split(","):
            imgs = fetch_wikimedia(kw.strip()) or fetch_pexels_images(kw.strip(), count=2)
            raw_images.extend(imgs)

    if not raw_images:
        raw_images = fetch_pexels_images("vintage mystery", count=6)

    os.makedirs("assets", exist_ok=True)
    vertical_images = []
    for i, img in enumerate(raw_images):
        out_path = f"assets/vertical_{i}.jpg"
        reframe_to_vertical(img, out_path)
        vertical_images.append(out_path)

    words = get_word_timestamps("short_voice.mp3")
    word_groups = group_words(words, group_size=3)

    assemble_short(
        vertical_images,
        "short_voice.mp3",
        "bg_music_energetic.mp3",
        word_groups,
        hook_line,
        output_path="final_short.mp4"
    )

    video_id = upload_short("final_short.mp4", hook_line, topic["title"])
    print(f"Uploaded Short Video ID: {video_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="standalone")
    parser.add_argument("--source", type=str, default=None)
    args = parser.parse_args()
    run_shorts_pipeline(mode=args.mode, long_script_path=args.source)
