import json
import os
import shutil

from script_agent import generate_script, generate_titles
from fact_check_agent import full_safety_pipeline
from image_agent import generate_all_scene_images
from tts_agent import generate_all_narration
from shorts_caption_agent import generate_all_captions
from shorts_assembly_agent import assemble_video
from youtube_uploader import upload_short

QUEUE_PATH = "queue.json"


def load_queue():
    with open(QUEUE_PATH, "r") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)


def get_next_pending(queue):
    for item in queue:
        if item["status"] == "pending":
            return item
    return None


def cleanup_assets():
    """Clear temp assets between runs to avoid disk bloat on CI runner"""
    for folder in ["assets/images", "assets/audio", "output"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)


def run_pipeline():
    queue = load_queue()
    item = get_next_pending(queue)

    if not item:
        print("📭 No pending items in queue.")
        return

    print(f"🎬 Processing: {item['theme']}")
    item["status"] = "processing"
    save_queue(queue)

    try:
        # 1. Generate script
        script_data = generate_script(item["theme"], item["character"])
        print("✅ Script generated")

        # 2. Safety check
        safety_result = full_safety_pipeline(script_data)
        if not safety_result["approved"]:
            print(f"❌ Safety check failed: {safety_result['issues']}")
            item["status"] = "rejected"
            item["rejection_reason"] = safety_result["issues"]
            save_queue(queue)
            return
        print("✅ Safety check passed")

        # 3. Generate titles
        titles = generate_titles(item["theme"], item["character"])
        final_title = titles[0] if titles else script_data["title_concepts"][0]

        # 4. Generate images
        image_paths = generate_all_scene_images(script_data)
        print(f"✅ {len(image_paths)} images generated")

        # 5. Generate narration audio
        audio_data = generate_all_narration(script_data)
        print(f"✅ {len(audio_data)} audio clips generated")

        # 6. Generate captions
        captions = generate_all_captions(script_data, audio_data)
        print("✅ Captions generated")

        # 7. Assemble final video
        output_path = f"output/{item['id']}.mp4"
        assemble_video(image_paths, audio_data, captions, output_path)
        print(f"✅ Video assembled: {output_path}")

        # 8. Upload to YouTube
        video_id = upload_short(
            video_path=output_path,
            title=final_title,
            description=script_data["seo_description"],
            tags=script_data["seo_tags"]
        )

        # 9. Update queue
        item["status"] = "completed"
        item["video_id"] = video_id
        item["final_title"] = final_title
        save_queue(queue)
        print(f"🎉 Done! Video ID: {video_id}")

    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        item["status"] = "failed"
        item["error"] = str(e)
        save_queue(queue)
        raise

    finally:
        cleanup_assets()


if __name__ == "__main__":
    run_pipeline()
