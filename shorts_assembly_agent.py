import os
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, TextClip,
    concatenate_videoclips
)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30


def apply_ken_burns(image_clip: ImageClip, duration: float, zoom_factor: float = 1.15):
    """Classic slow zoom-in effect to simulate motion on static images"""
    return image_clip.resize(lambda t: 1 + (zoom_factor - 1) * (t / duration)) \
                      .set_position('center') \
                      .set_duration(duration)


def create_scene_clip(image_path: str, audio_path: str, captions: list, duration: float):
    # Base image with Ken Burns zoom
    img_clip = ImageClip(image_path).resize(height=VIDEO_HEIGHT)
    img_clip = apply_ken_burns(img_clip, duration)
    img_clip = img_clip.set_position('center')

    # Audio
    audio_clip = AudioFileClip(audio_path)

    # Caption overlays
    caption_clips = []
    for cap in captions:
        txt_clip = (
            TextClip(
                cap["text"],
                fontsize=70,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=3,
                method='caption',
                size=(VIDEO_WIDTH - 100, None)
            )
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
