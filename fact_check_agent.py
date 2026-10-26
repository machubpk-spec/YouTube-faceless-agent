import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
            print(f"[verify_script] Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))

    raise RuntimeError(f"verify_script failed after 3 attempts: {last_error}")
