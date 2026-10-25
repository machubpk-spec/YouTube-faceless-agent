import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

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
    return model.generate_content(prompt).text
