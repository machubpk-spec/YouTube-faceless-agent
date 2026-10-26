import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

STANDALONE_PROMPT = """
Write a 45-second YouTube Shorts script about: {title} ({year}).
Rules:
- First sentence after [HOOK] must be a shocking scroll-stopper (under 12 words).
- Total word count: 110-130 words.
- Format strictly with [HOOK], [BODY], [PAYOFF] labels.
- Include 3 KEYWORDS: lines throughout for image search.
"""

EXTRACT_PROMPT = """
From this documentary script, extract ONE self-contained 45-second YouTube Short (110-130 words):
---
{full_script}
---
Format strictly with [HOOK], [BODY], [PAYOFF] labels and 3 KEYWORDS: lines.
"""

def generate_standalone_short(topic):
    return model.generate_content(STANDALONE_PROMPT.format(title=topic["title"], year=topic["year"])).text

def extract_short_from_longform(full_script):
    return model.generate_content(EXTRACT_PROMPT.format(full_script=full_script)).text
