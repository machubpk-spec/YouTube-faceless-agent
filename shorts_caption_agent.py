from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

def get_word_timestamps(audio_path):
    segments, _ = model.transcribe(audio_path, word_timestamps=True)
    words = []
    for seg in segments:
        if seg.words:
            for w in seg.words:
                words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    return words

def group_words(words, group_size=3):
    groups = []
    for i in range(0, len(words), group_size):
        chunk = words[i:i+group_size]
        groups.append({
            "text": " ".join(w["word"] for w in chunk).upper(),
            "start": chunk[0]["start"],
            "end": chunk[-1]["end"]
        })
    return groups
