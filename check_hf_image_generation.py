"""Opt-in smoke test for Hugging Face text-to-image generation.

Run from the project root with:
    comiccraft-env/Scripts/python.exe check_hf_image_generation.py
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError


MODEL_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "runwayml/stable-diffusion-v1-5"
)
OUTPUT_PATH = Path("static/panels/hf_generation_test.png")


def main() -> int:
    load_dotenv()
    token = os.getenv("HF_API_KEY", "").strip()
    if not token or token == "your-huggingface-api-key-here":
        print("HF_API_KEY is missing. Add a Hugging Face token to .env first.")
        return 1

    try:
        response = requests.post(
            MODEL_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"inputs": "A red fox astronaut on the moon, detailed comic illustration"},
            timeout=(15, 120),
        )
    except requests.RequestException as error:
        print(f"Request failed before a response was received: {error}")
        return 1

    if response.status_code != 200:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text[:1000]
        print(f"Hugging Face returned HTTP {response.status_code}: {detail}")
        return 1

    content_type = response.headers.get("content-type", "")
    if not content_type.startswith("image/"):
        print(f"Expected image bytes; received Content-Type: {content_type or '(missing)'}")
        print(response.text[:1000])
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(response.content)
    try:
        with Image.open(OUTPUT_PATH) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as error:
        OUTPUT_PATH.unlink(missing_ok=True)
        print(f"The response was not a valid image: {error}")
        return 1

    print(f"Image generation succeeded: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
