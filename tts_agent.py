import edge_tts
import asyncio

VOICE = "en-US-ChristopherNeural"

async def generate_voiceover(text, output_path="voice.mp3"):
    communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
    await communicate.save(output_path)

def run_tts(text, output_path="voice.mp3"):
    asyncio.run(generate_voiceover(text, output_path))
