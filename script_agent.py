import os
import json
import re
from groq import Groq
from character_config import CHARACTER_NAME, CHARACTER_BIBLE, TARGET_REGIONS

client = Groq(api_key=os.environ["GROQ_API_KEY"])

# IMPORTANT: Run list_groq_models.py to confirm this model ID is still live
GROQ_MODEL = "llama-3.3-70b-versatile"


def _extract_json(text):
    """Groq sometimes wraps JSON in markdown fences - strip them"""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No valid JSON found in model response")


def generate_script(theme: str, character_name: str = CHARACTER_NAME) -> dict:
    prompt = f"""
You are a children's YouTube Shorts scriptwriter for ages 2-6, targeting
US, UK, Canada, and European English-speaking audiences.

Create a 45-60 second animated short script about: "{theme}"
Main character: {character_name}

STRICT STRUCTURE (for retention):
1. HOOK (0-3s): A visual/question that stops scrolling instantly
2. SETUP (3-10s): Introduce the simple problem/goal
3. REPETITION CORE (10-40s): Repeating phrase or song pattern, 2-3 interactive
   questions like "Can you find the red balloon?"
4. RESOLUTION (40-50s): Simple happy ending
5. LOOP HOOK (50-55s): End with a question or tease that makes kids rewatch

RULES:
- Max 3-syllable words wherever possible
- Warm, slow-paced tone
- No scary content, no violence, no complex plots
- 5-7 scenes total
- Each scene: 1-2 short sentences of narration MAX

Return ONLY valid JSON in this exact format:
{{
  "title_concepts": ["title1", "title2", "title3"],
  "repeating_phrase": "...",
  "educational_takeaway": "...",
  "scenes": [
    {{
      "scene_number": 1,
      "narration": "...",
      "image_prompt": "describe ONLY the visual action/setting, no character description",
      "is_interactive_question": false
    }}
  ],
  "seo_description": "2-3 sentence YouTube description",
  "seo_tags": ["tag1", "tag2", "..."]
}}
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=2000,
    )

    content = response.choices[0].message.content
    script_data = _extract_json(content)
    script_data["character_name"] = character_name
    script_data["theme"] = theme
    return script_data


def generate_titles(theme: str, character_name: str = CHARACTER_NAME) -> list:
    """Separate, focused SEO title generation"""
    prompt = f"""
Generate 5 YouTube Shorts titles for a kids video about "{theme}" featuring
"{character_name}". 

RULES:
- Front-load the main keyword (e.g. "Learn Colors with..." not "Join us to learn...")
- Max 60 characters
- Include high-search terms: kids songs, nursery rhymes, learning video,
  toddler, preschool
- No misleading clickbait (YouTube penalizes kids content for mismatches)

Return ONLY a JSON array of 5 strings, nothing else.
"""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300,
    )
    content = response.choices[0].message.content
    match = re.search(r'\[.*\]', content, re.DOTALL)
    return json.loads(match.group(0)) if match else []


if __name__ == "__main__":
    # Quick test
    result = generate_script("learning colors with balloons")
    print(json.dumps(result, indent=2))
