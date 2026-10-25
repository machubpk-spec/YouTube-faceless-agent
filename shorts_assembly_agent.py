from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    CompositeVideoClip, TextClip, concatenate_videoclips
)

CANVAS_W, CANVAS_H = 1080, 1920
FONT = "DejaVu-Sans-Bold"

def ken_burns_vertical(image_path, duration, zoom_direction="in"):
    clip = ImageClip(image_path).set_duration(duration)
    if zoom_direction == "in":
        clip = clip.resize(lambda t: 1 + 0.03 * t)
    else:
        clip = clip.resize(lambda t: 1.08 - 0.03 * t)
    return clip.set_position("center")

def make_caption_clips(word_groups):
    clips = []
    for g in word_groups:
        txt = TextClip(
            g["text"],
            fontsize=75,
            font=FONT,
            color="white",
            stroke_color="black",
            stroke_width=3,
            method="caption",
            size=(CANVAS_W - 120, None)
        ).set_start(g["start"]).set_end(g["end"]).set_position(("center", int(CANVAS_H * 0.65)))
        clips.append(txt)
    return clips

def make_hook_text(hook_line, duration=2.5):
    txt = TextClip(
        hook_line.upper()[:70],
        fontsize=80,
        font=FONT,
        color="yellow",
        stroke_color="black",
        stroke_width=4,
        method="caption",
        size=(CANVAS_W - 100, None)
    )
    return txt.set_start(0).set_duration(duration).set_position(("center", int(CANVAS_H * 0.25)))

def assemble_short(image_paths, audio_path, music_path, word_groups, hook_line, output_path="final_short.mp4"):
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    per_img_duration = 2.5
    n_needed = int(total_duration / per_img_duration) + 2
    cycled = (image_paths * ((n_needed // len(image_paths)) + 1))[:n_needed]

    clips = [
        ken_burns_vertical(img, per_img_duration, "in" if i % 2 == 0 else "out")
        for i, img in enumerate(cycled)
    ]
    video = concatenate_videoclips(clips, method="compose").subclip(0, total_duration)

    caption_clips = make_caption_clips(word_groups)
    hook_clip = make_hook_text(hook_line)

    final_video = CompositeVideoClip([video] + caption_clips + [hook_clip], size=(CANVAS_W, CANVAS_H))

    music = AudioFileClip(music_path).volumex(0.08)
    if music.duration < total_duration:
        music = music.loop(duration=total_duration)
    else:
        music = music.subclip(0, total_duration)

    final_video = final_video.set_audio(CompositeAudioClip([audio, music]))
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
