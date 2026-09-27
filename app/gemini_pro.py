import os
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


def _get_fallback_story(outline: list) -> str:
    """Provides an engaging fallback comic story if the API is unavailable."""
    sections = []
    for item in outline:
        p_num = item.get("panel", 1)
        p_title = item.get("title", f"Panel {p_num}")
        p_desc = item.get("scene_description", "")
        
        section = (
            f"**Panel {p_num}: {p_title}**\n"
            f"{p_desc}\n"
            f"**CAPTION:** The quiet whisper of destiny echoes through the air.\n"
            f"**NARRATION:** With steadfast resolve, the journey unfolded into a world full of wonder and hidden dangers.\n"
            f"**DIALOGUE:** \"There's no turning back now. Adventure awaits!\""
        )
        sections.append(section)
    return "\n\n".join(sections)


_gemini_api_failed = False


def generate_story(outline: list) -> str:
    """
    Generates a detailed comic story with narration and character dialogue
    from a list of comic panel outlines using Gemini 1.5 Pro.

    Args:
        outline (list): A list of dictionaries representing each comic panel's idea.

    Returns:
        str: The generated comic story text or an error message.
    """
    global _gemini_api_failed
    if _gemini_api_failed:
        return _get_fallback_story(outline)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        print("⚠️ Warning: GEMINI_API_KEY is not configured in .env. Using fallback comic story narration.")
        return _get_fallback_story(outline)

    # Format the panel outline as a numbered list for clarity
    formatted_outline = "\n".join([f"{i+1}. {item}" for i, item in enumerate(outline)])

    # Construct the prompt with explicit panel marker instructions so layout_builder parses it cleanly
    prompt = f"""
You're a comic book writer.

Given the following panel breakdown, write a comic-style story with engaging narration and character dialogues for each panel.

Panel Outline:
{formatted_outline}

Guidelines:
- Use a fun and engaging tone, like an actual comic book.
- Begin each panel strictly with "**Panel X: Panel Title**" (where X is 1 to 5).
- Under each panel heading, write a brief scene atmosphere sentence.
- Then include:
  **CAPTION:** (ambient sound/atmospheric description)
  **NARRATION:** (storyteller voice explaining what happens)
  **DIALOGUE:** (character quotes with speaker names)
- Keep each panel self-contained but part of a cohesive story.
"""

    try:
        try:
            model = genai.GenerativeModel("models/gemini-1.5-pro")
        except Exception:
            try:
                model = genai.GenerativeModel("gemini-1.5-pro")
            except Exception:
                model = genai.GenerativeModel("gemini-pro")

        response = model.generate_content(prompt, request_options={"timeout": 8})
        text = response.text.strip()
        if not text or "**Panel" not in text:
            # If the response missed **Panel markers, format it or use fallback
            if text:
                # Attempt to normalize if it used "Panel 1:" instead of "**Panel 1:"
                import re
                text = re.sub(r'^(Panel\s+\d+:)', r'**\1**', text, flags=re.MULTILINE)
            if "**Panel" not in text:
                return _get_fallback_story(outline)
        return text
    except Exception as e:
        print(f"❌ Gemini Pro API unavailable ({e}). Using fallback story.")
        _gemini_api_failed = True
        return _get_fallback_story(outline)
