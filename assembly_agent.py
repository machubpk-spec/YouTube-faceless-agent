from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
from PIL import Image

def prepare_16_9(image_path):
    img = Image.open(image_path).convert("RGB").resize((1920, 1080))
    img.save(image_path)
    return image_path

def ken_burns(image_path, duration):
    prepare_16_9(image_path)
    clip = ImageClip(image_path).set_duration(duration)
    clip = clip.resize(lambda t: 1 + 0.015 * t)
    return clip.set_position("center")

def assemble_video(image_paths, audio_path, music_path, output_path="final.mp4"):
    audio = AudioFileClip(audio_path)
    duration_per_img = audio.duration / max(len(image_paths), 1)

    clips = [ken_burns(img, duration_per_img) for img in image_paths]
    video = concatenate_videoclips(clips, method="compose").set_duration(audio.duration)

    music = AudioFileClip(music_path).volumex(0.08)
    if music.duration < audio.duration:
        music = music.loop(duration=audio.duration)
    else:
        music = music.subclip(0, audio.duration)

    final_audio = CompositeAudioClip([audio, music])
    video = video.set_audio(final_audio)
    video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
