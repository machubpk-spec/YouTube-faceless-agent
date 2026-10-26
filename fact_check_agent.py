import os
import re
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
GROQ_MODEL = "llama-3.3-70b-versatile"

BANNED_KEYWORDS = [
    "scary", "kill", "death", "blood", "gun", "weapon", "fight",
    "hate", "stupid", "dumb", "ugly", "fat", "monster attack"
]


def keyword_safety_check(script_data: dict) -> tuple[bool, list]:
    """Fast local check before spending API calls"""
    issues = []
    full_text = " ".join(
        scene["narration"].lower() for scene in script_data.get("scenes", [])
    )
    for word in BANNED_KEYWORDS:
        if word in full_text:
            issues.append(f"Banned keyword found: '{word}'")
    return (len(issues) == 0, issues)


def ai_safety_check(script_data: dict) -> dict:
    """Deeper AI review for age-appropriateness and COPPA alignment"""
    narration_combined = "\n".join(
        f"Scene {s['scene_number']}: {s['narration']}"
        for s in script_data.get("scenes", [])
    )

    prompt = f"""
Review this children's video script (target age 2-6) for safety issues.

SCRIPT:
{narration_combined}

Check for:
1. Any scary, violent, or inappropriate content
2. Educational value present
3. Age-appropriate vocabulary
4. No requests for personal information (COPPA compliance)
5. No promotion of unsafe behavior

Return ONLY JSON:
{{
  "is_safe": true/false,
  "issues": ["list any issues found"],
  "age_appropriate": true/false,
  "recommendation": "approve" or "reject" or "revise"
}}
"""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )
    content = response.choices[0].message.content
    match = re.search(r'\{.*\}', content, re.DOTALL)
    import json
    return json.loads(match.group(0)) if match else {"is_safe": False, "issues": ["Parse error"]}


def full_safety_pipeline(script_data: dict) -> dict:
    """Run both checks, return final verdict"""
    keyword_ok, keyword_issues = keyword_safety_check(script_data)

    if not keyword_ok:
        return {
            "approved": False,
            "issues": keyword_issues,
            "stage": "keyword_filter"
        }

    ai_result = ai_safety_check(script_data)
    return {
        "approved": ai_result.get("is_safe", False) and ai_result.get("recommendation") == "approve",
        "issues": ai_result.get("issues", []),
        "stage": "ai_review",
        "details": ai_result
    }


if __name__ == "__main__":
    test_script = {
        "scenes": [
            {"scene_number": 1, "narration": "Benny finds a red balloon!"},
            {"scene_number": 2, "narration": "What color is this balloon?"}
        ]
    }
    print(full_safety_pipeline(test_script))
