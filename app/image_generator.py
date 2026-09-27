import os
import re
import hashlib
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PANELS_DIR = BASE_DIR / "static" / "panels"
PANELS_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# HUGGING FACE CONFIGURATION
# =========================================================

HF_TOKEN = (
    os.getenv("HF_TOKEN", "").strip()
    or os.getenv("HF_API_KEY", "").strip()
)

HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL",
    "black-forest-labs/FLUX.1-schnell"
)

# =========================================================
# HELPERS
# =========================================================

def sanitize_filename(text: str) -> str:
    text = str(text or "comic")

    clean = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        text[:35]
    ).strip("_")

    if not clean:
        clean = "comic"

    hash_suffix = hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()[:8]

    return f"{clean}_{hash_suffix}"


# =========================================================
# BUILD ONE COMIC-SHEET PROMPT
# =========================================================

def build_comic_sheet_prompt(outline: list) -> str:
    """
    Creates one visual prompt containing all five scenes.

    The AI generates ONE image containing five comic panels.
    """

    scenes = []

    for index, panel in enumerate(outline[:5], start=1):

        title = panel.get(
            "title",
            f"Panel {index}"
        )

        scene = panel.get(
            "scene_description",
            ""
        )

        image_prompt = panel.get(
            "image_prompt",
            ""
        )

        scenes.append(
            f"""
PANEL {index}
TITLE: {title}
SCENE: {scene}
VISUAL DESCRIPTION: {image_prompt}
"""
        )

    all_scenes = "\n".join(scenes)

    prompt = f"""
Create ONE complete five-panel comic page.

The comic must contain exactly five distinct visual panels.

Arrange them in this layout:

TOP ROW:
PANEL 1 | PANEL 2

MIDDLE ROW:
PANEL 3 | PANEL 4

BOTTOM ROW:
PANEL 5 | EMPTY SPACE

Each panel must show a different moment of the story.

The characters must remain visually consistent between panels.

The environment, character appearance, actions and events
must match the individual panel descriptions.

STORY PANELS:

{all_scenes}

VISUAL STYLE:
professional cinematic comic-book illustration,
detailed characters,
expressive faces,
dynamic composition,
rich environment,
dramatic lighting,
high-quality graphic novel artwork,
consistent character design,
clear separation between panels.

IMPORTANT:
- Generate actual illustrated scenes.
- Do not generate abstract geometric backgrounds.
- Do not turn the descriptions into visible text.
- Do not write the scene descriptions inside the artwork.
- Do not display prompts inside the artwork.
- Do not create UI elements.
- Do not create a website screenshot.
- Do not create a placeholder image.
- Do not create captions.
- Do not create speech bubbles.
- Do not create logos.
- Do not create a title.
- Do not write words inside the image.
- The five panels must contain actual story scenes.
"""

    return " ".join(prompt.split())


# =========================================================
# GENERATE ONE AI COMIC SHEET
# =========================================================

def generate_comic_sheet(
    outline: list,
    filename: str = None
) -> str:

    if not HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN is missing from the .env file."
        )

    if not outline:
        raise ValueError(
            "Comic outline is empty."
        )

    if filename is None:
        filename = "comic_sheet.png"

    sheet_path = PANELS_DIR / filename

    try:

        from huggingface_hub import InferenceClient

        print()
        print("=" * 60)
        print("COMICCRAFT - ONE IMAGE REQUEST")
        print("=" * 60)
        print(f"Model: {HF_IMAGE_MODEL}")
        print("Generating ONE five-panel comic sheet...")
        print("=" * 60)

        client = InferenceClient(
            provider="auto",
            api_key=HF_TOKEN
        )

        prompt = build_comic_sheet_prompt(
            outline
        )

        image = client.text_to_image(
            prompt=prompt,
            model=HF_IMAGE_MODEL,
            width=1024,
            height=1024,
            num_inference_steps=4
        )

        image.save(sheet_path)

        print(
            f"Comic sheet saved: {sheet_path}"
        )

        return str(sheet_path)

    except Exception as e:

        print()
        print("=" * 60)
        print("IMAGE GENERATION FAILED")
        print("=" * 60)
        print(str(e))
        print("=" * 60)

        raise RuntimeError(
            f"Comic image generation failed: {e}"
        )


# =========================================================
# SPLIT ONE SHEET INTO FIVE LOCAL IMAGES
# =========================================================

def split_comic_sheet(
    sheet_path: str,
    comic_id: str
) -> list:

    sheet = Image.open(sheet_path).convert("RGB")

    width, height = sheet.size

    # Expected layout:
    #
    # PANEL 1 | PANEL 2
    # PANEL 3 | PANEL 4
    # PANEL 5 | EMPTY
    #
    # Therefore:
    #
    # columns = 2
    # rows    = 3

    cell_width = width // 2
    cell_height = height // 3

    panel_paths = []

    coordinates = [
        # Panel 1
        (0, 0, cell_width, cell_height),

        # Panel 2
        (cell_width, 0, width, cell_height),

        # Panel 3
        (0, cell_height, cell_width, cell_height * 2),

        # Panel 4
        (
            cell_width,
            cell_height,
            width,
            cell_height * 2
        ),

        # Panel 5
        (
            0,
            cell_height * 2,
            cell_width,
            height
        )
    ]

    for index, box in enumerate(
        coordinates,
        start=1
    ):

        panel = sheet.crop(box)

        panel_filename = (
            f"{comic_id}_panel_{index}.png"
        )

        panel_path = PANELS_DIR / panel_filename

        panel.save(
            panel_path,
            "PNG"
        )

        panel_paths.append(
            str(panel_path)
        )

        print(
            f"Panel {index} saved: {panel_path}"
        )

    return panel_paths


# =========================================================
# OLD SINGLE IMAGE FUNCTION
# =========================================================

def generate_image(
    prompt: str,
    filename: str = None
) -> str:

    """
    Kept for compatibility with the existing project.

    It generates ONE normal AI image.
    The normal comic workflow should use
    generate_comic_sheet() instead.
    """

    if not prompt:
        raise ValueError(
            "Image prompt cannot be empty."
        )

    if not HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN is missing from the .env file."
        )

    if filename is None:
        filename = sanitize_filename(prompt) + ".png"

    output_path = PANELS_DIR / filename

    try:

        from huggingface_hub import InferenceClient

        client = InferenceClient(
            provider="auto",
            api_key=HF_TOKEN
        )

        image = client.text_to_image(
            prompt=prompt,
            model=HF_IMAGE_MODEL,
            width=768,
            height=768,
            num_inference_steps=4
        )

        image.save(output_path)

        return str(
            output_path.relative_to(BASE_DIR)
        ).replace("\\", "/")

    except Exception as e:

        raise RuntimeError(
            f"AI image generation failed: {e}"
        )