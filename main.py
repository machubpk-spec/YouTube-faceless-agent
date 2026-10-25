import argparse
import os
import re
from topics import get_next_topic
from script_agent import generate_script
from fact_check_agent import verify_script
from tts_agent import run_tts
from visual_agent import fetch_pixabay_images, fetch_wikimedia
from assembly_agent import assemble_video
from thumbnail_agent import make_thumbnail
from upload_agent import upload_video

def clean_narration(script_text):
    cleaned = re.sub(r"\[.*?\]", "", script_text)
    cleaned = re.sub(r"KEYWORDS:.*", "", cleaned)
    return cleaned.strip()

def run_pipeline(long_form=True, save_script_path=None):
    topic = get_next_topic()
    raw_script = generate_script(topic, long_form)
    script = verify_script(raw_script, topic)

    if save_script_path:
        os.makedirs(os.path.dirname(save_script_path), exist_ok=True)
        with open(save_script_path, "w", encoding="utf-8") as f:
            f.write(script)

    narration_text = clean_narration(script)
    run_tts(narration_text, "voice.mp3")

    keywords = re.findall(r"KEYWORDS:\s*(.+)", script)
    images = []
    for kw_line in keywords:
        kw = kw_line.split(",")[0].strip()
        imgs = fetch_wikimedia(kw) or fetch_pexels_images(kw, count=1)
        images.extend(imgs)

    if not images:
        images = fetch_pexels_images("dark mystery history", count=5)

    assemble_video(images, "voice.mp3", "bg_music.mp3", "final.mp4")
    make_thumbnail(images[0], topic["title"], "thumb.jpg")

    video_id = upload_video(
        "final.mp4",
        title=f"{topic['title']} ({topic['year']}) - The Untold Story",
        description=f"A documentary deep dive into {topic['title']} ({topic['year']}).\n\n#truecrime #history #documentary",
        tags=["true crime", "history", "documentary", topic["title"]],
        thumbnail_path="thumb.jpg"
    )
    print(f"Uploaded Long-Form Video ID: {video_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--long", action="store_true", default=True)
    parser.add_argument("--save-script", type=str, default=None)
    args = parser.parse_args()
    run_pipeline(long_form=args.long, save_script_path=args.save_script)
