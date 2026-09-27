import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

client = TestClient(app)


def test_index_page():
    """Verify that the homepage loads correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Create Your Comic" in response.text
    assert "prompt" in response.text
    assert "character_name" in response.text


def test_test_image_route():
    """Verify that the /test-image developer utility route functions."""
    response = client.get("/test-image?prompt=A+brave+fox+in+a+magical+forest")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Image generated successfully"
    assert "path" in data
    # Verify the image exists on disk
    disk_path = data["path"].lstrip("/")
    assert os.path.exists(disk_path)


def test_ai_pipeline_functions():
    """Verify the modular AI components work independently."""
    prompt = "A brave fox named Free explores an enchanted forest."
    
    # 1. Outline
    outline = generate_outline(prompt)
    assert isinstance(outline, list)
    assert len(outline) >= 1
    assert "image_prompt" in outline[0]
    assert "title" in outline[0]

    # 2. Story
    story = generate_story(outline)
    assert isinstance(story, str)
    assert len(story) > 0

    # 3. Image
    img_path = generate_image(outline[0]["image_prompt"])
    assert os.path.exists(img_path)

    # 4. Layout
    images = [img_path] * len(outline)
    layout = build_comic_layout(images, story, outline)
    assert len(layout) == len(outline)
    assert "web_image_path" in layout[0]

    # 5. Exporter PDF
    pdf_path = save_pdf(layout)
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")


def test_generate_route_form():
    """Verify form submission generates comic preview and PDF."""
    form_data = {
        "prompt": "A courageous cyborg samurai defends a neon city from rogue drones.",
        "character_name": "Jin",
        "setting": "cyberpunk metropolis",
        "tone": "dramatic",
        "style": "cyberpunk"
    }
    response = client.post("/generate", data=form_data)
    assert response.status_code == 200
    assert "Your Comic Preview" in response.text
    assert "Download Your Comic as PDF" in response.text


def test_generate_comic_json():
    """Verify JSON API endpoint returns structured layout and PDF path."""
    payload = {
        "prompt": "An astronaut discovers an ancient alien library on Mars.",
        "character_name": "Aria",
        "setting": "space",
        "tone": "mystery",
        "style": "anime"
    }
    response = client.post("/generate-comic/json", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "layout" in data
    assert "pdf_path" in data
    assert len(data["layout"]) >= 1


def test_export_success_page():
    """Verify the export success confirmation page."""
    response = client.get("/export-success?pdf_path=/static/exports/comic_test.pdf")
    assert response.status_code == 200
    assert "Comic Exported Successfully!" in response.text
    assert "Go Create Another Comic" in response.text


def test_download_pdf_route():
    """Verify downloading a generated PDF file."""
    # First generate a comic to ensure a PDF exists
    resp = client.post("/generate-comic/json", json={
        "prompt": "A young wizard discovers a dragon egg in an ancient tower.",
        "character_name": "Leo",
        "setting": "haunted castle",
        "tone": "dramatic",
        "style": "comic book"
    })
    pdf_path = resp.json()["pdf_path"]
    
    # Download the PDF
    download_resp = client.get(f"/download-pdf?file_path={pdf_path}")
    assert download_resp.status_code == 200
    assert download_resp.headers["content-type"] == "application/pdf"
    assert len(download_resp.content) > 1000

