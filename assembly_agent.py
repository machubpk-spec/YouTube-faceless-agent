import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips
)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def apply_ken_burns(image_clip: ImageClip, duration: float, zoom_factor: float = 1.15):
    return image_clip.resize(lambda t: 1 + (zoom_factor - 1) * (t / duration)) \
                      .set_position('center') \
                      .set_duration(duration)


def create_caption_image(text: str, width: int = VIDEO_WIDTH - 100, font_size: int = 70):
    """Render caption text to a transparent PNG using Pillow (no ImageMagick needed)"""
    font = ImageFont.truetype(FONT_PATH, font_size)

    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    padding = 20
    img = Image.new("RGBA", (width, text_h + padding * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    x = (width - text_w) // 2
    y = padding

    # Black stroke outline for readability
    stroke_width = 3
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    return np.array(img)


def create_scene_clip(image_path: str, audio_path: str, captions: list, duration: float):
    img_clip = ImageClip(image_path).resize(height=VIDEO_HEIGHT)
    img_clip = apply_ken_burns(img_clip, duration)
    img_clip = img_clip.set_position('center')

    audio_clip = AudioFileClip(audio_path)

    caption_clips = []
    for cap in captions:
        caption_array = create_caption_image(cap["text"])
        txt_clip = (
            ImageClip(caption_array)
            .set_start(cap["start"])
            .set_duration(cap["end"] - cap["start"])
            .set_position(('center', VIDEO_HEIGHT - 400))
        )
        caption_clips.append(txt_clip)

    scene = CompositeVideoClip(
        [img_clip] + caption_clips,
        size=(VIDEO_WIDTH, VIDEO_HEIGHT)
    ).set_duration(duration).set_audio(audio_clip)

    return scene


def assemble_video(
    image_paths: list,
    audio_data: list,
    captions: list,
    output_path: str = "output/final_video.mp4"
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    scene_clips = []
    for i, img_path in enumerate(image_paths):
        scene_number = i + 1
        audio_info = next(a for a in audio_data if a["scene_number"] == scene_number)
        scene_captions = [c for c in captions if c["scene_number"] == scene_number]

        clip = create_scene_clip(
            img_path,
            audio_info["path"],
            scene_captions,
            audio_info["duration"]
        )
        scene_clips.append(clip)

    final_video = concatenate_videoclips(scene_clips, method="compose")
    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        threads=4
    )

    return output_path
