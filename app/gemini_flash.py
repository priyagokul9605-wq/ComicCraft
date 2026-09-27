import os
import json
import re
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        genai.configure(api_key=GEMINI_API_KEY, transport="rest")
    except Exception:
        genai.configure(api_key=GEMINI_API_KEY)


def _get_fallback_outline(user_prompt: str) -> list:
    """Provides a realistic fallback 5-panel comic outline if the API is unavailable."""
    print("ℹ️ Using intelligent fallback outline for development/testing.")
    return [
        {
            "panel": 1,
            "title": "The Awakening",
            "scene_description": f"The story begins with the main character setting off on their journey: {user_prompt}",
            "image_prompt": f"Comic book style illustration, establishing shot, cinematic lighting, {user_prompt}, panel 1, vibrant comic art"
        },
        {
            "panel": 2,
            "title": "Into the Unknown",
            "scene_description": "Venturing deeper into the environment, mysterious signs and atmospheric tension appear.",
            "image_prompt": f"Comic book panel, character cautiously exploring, dynamic perspective, detailed environment, comic ink style"
        },
        {
            "panel": 3,
            "title": "The Unexpected Encounter",
            "scene_description": "A sudden discovery or surprising obstacle challenges the protagonist.",
            "image_prompt": f"Dramatic comic strip panel, sudden encounter, high contrast shadows, expressive character, detailed graphic novel art"
        },
        {
            "panel": 4,
            "title": "The Decisive Moment",
            "scene_description": "Action reaches its peak as the hero faces the dilemma head-on with courage.",
            "image_prompt": f"Action shot, intense emotional expression, comic style motion lines, vibrant colors, dramatic angle"
        },
        {
            "panel": 5,
            "title": "A New Dawn",
            "scene_description": "Resolution is reached, leaving a lasting impression and a sense of wonder.",
            "image_prompt": f"Wide panoramic comic panel, heroic pose at sunset, resolution, golden hour lighting, cinematic comic book art"
        }
    ]


_gemini_api_failed = False


def generate_outline(user_prompt: str) -> list:
    """
    Generates a 5-panel comic layout based on the user's story idea using Gemini.
    
    Args:
        user_prompt (str): The user's comic idea prompt.
        
    Returns:
        list: A list of dictionaries, one for each panel.
    """
    global _gemini_api_failed
    if _gemini_api_failed:
        return _get_fallback_outline(user_prompt)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        print("⚠️ Warning: GEMINI_API_KEY is not configured in .env. Using fallback comic outline.")
        return _get_fallback_outline(user_prompt)

    try:
        # Try gemini-1.5-flash as specified in project documentation
        model = genai.GenerativeModel("models/gemini-1.5-flash")
    except Exception:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
        except Exception:
            model = genai.GenerativeModel("gemini-pro")

    prompt = f"""
you are a professional AI comic planner.

Your task is to generate a *strictly formatted* JSON array containing 5 panel descriptions for a comic based on the story idea below:

STORY: "{user_prompt}"

Each JSON object must include:
- "panel" (integer)
- "title" (string)
- "scene_description" (string)
- "image_prompt" (string)

Respond ONLY in this valid JSON format, without any explanations or markdown:
[
  {{
    "panel": 1,
    "title": "title here",
    "scene_description": "scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }}
]
"""

    output_text = ""
    try:
        response = model.generate_content(prompt, request_options={"timeout": 8})
        output_text = response.text.strip()
        print("\n🎨 RAW GEMINI RESPONSE \n", output_text)

        # Remove any markdown formatting if present
        if output_text.startswith("```json"):
            output_text = output_text.replace("```json", "", 1)
        elif output_text.startswith("```"):
            output_text = output_text.replace("```", "", 1)
            
        if output_text.endswith("```"):
            output_text = output_text[:-3]

        output_text = output_text.strip()

        # Handle cases where markdown wasn't at the very start
        json_match = re.search(r'\[\s*\{.*\}\s*\]', output_text, re.DOTALL)
        if json_match:
            output_text = json_match.group(0)

        panel_data = json.loads(output_text)

        # Additional structure validation
        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a list.")

        for panel in panel_data:
            if not isinstance(panel, dict) or not all(key in panel for key in ("panel", "title", "scene_description", "image_prompt")):
                raise ValueError(f"Invalid panel format or missing keys: {panel}")

        return panel_data

    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print(f"❌ Full Text Received:\n{output_text}")
        return _get_fallback_outline(user_prompt)

    except Exception as e:
        print(f"❌ Gemini API unavailable ({e}). Using intelligent fallback outline.")
        _gemini_api_failed = True
        return _get_fallback_outline(user_prompt)
