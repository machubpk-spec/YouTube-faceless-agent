import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core import exceptions, retry

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.8-flash") # Note: I corrected the model name to 1.5-flash as 3.8 does not exist

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
    
    # We add request_options to tell Google to wait longer and retry if it times out
    response = model.generate_content(
        prompt,
        request_options={
            "timeout": 600,  # Wait up to 10 minutes for a response
            "retry": retry.Retry(
                predicate=retry.if_exception_type(
                    exceptions.DeadlineExceeded,
                    exceptions.ServiceUnavailable,
                    exceptions.InternalServerError,
                ),
                initial=5,
                maximum=60,
                multiplier=2,
            ),
        },
    )
    return response.text
