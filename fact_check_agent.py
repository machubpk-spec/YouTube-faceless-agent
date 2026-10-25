import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

FACT_CHECK_PROMPT = """
Review this script about {title} ({year}) for historical/legal accuracy.
- Ensure dates, names, and locations are factual.
- Add "allegedly" or "reportedly" to any unproven claims.
- Keep all [SEGMENT], [HOOK], [BODY], [PAYOFF] tags and KEYWORDS: lines intact.
- Output ONLY the revised script text.

Script:
{script}
"""

def verify_script(script_text, topic):
    prompt = FACT_CHECK_PROMPT.format(title=topic["title"], year=topic["year"], script=script_text)
    return model.generate_content(prompt).text
