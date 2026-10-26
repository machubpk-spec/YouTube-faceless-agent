import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SCRIPT_PROMPT = """
Write a documentary narration script about: {title} ({year}).
Style: {style}
Requirements:
- Hook in first 2 sentences (no generic clichés)
- Only state documented facts. Use "allegedly" or "according to reports" for disputed claims
- Length: {length}
- Break script into labeled segments like [SEGMENT 1], [SEGMENT 2]
- Include 1 keyword line per segment in exact format: KEYWORDS: term1, term2
- Do not include stage directions or narrator labels, only spoken words and the tags above.
"""

def generate_script(topic, long_form=True):
    length = "1500-1800 words" if long_form else "130-150 words"
    style = "investigative true crime documentary" if topic["type"] == "true_crime" else "gripping historical documentary"
    prompt = SCRIPT_PROMPT.format(title=topic["title"], year=topic["year"], style=style, length=length)

    last_error = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                timeout=120
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            print(f"[generate_script] Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))

    raise RuntimeError(f"generate_script failed after 3 attempts: {last_error}")
