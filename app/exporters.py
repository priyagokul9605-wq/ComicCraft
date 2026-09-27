import os
from datetime import datetime
from fpdf import FPDF

EXPORT_FOLDER = os.path.join("static", "exports")
FONT_PATH = os.path.join("static", "fonts", "DejaVuSans.ttf")


def _sanitize_for_pdf(text: str) -> str:
    """Replaces unrenderable unicode characters to prevent PDF generation errors."""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "•": "-",
        "⚡": "*",
        "🎨": "*",
        "📖": "*",
        "✏️": "*"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def save_pdf(layout: list) -> str:
    """
    Compiles the full comic into a multi-page PDF file using FPDF.
    Each panel's image and narration are placed neatly on separate pages.
    The final PDF file is saved into the static/exports folder, and the path is returned.

    Args:
        layout (list): List of panel layout dictionaries.

    Returns:
        str: Relative path to the saved PDF file.
    """
    os.makedirs(EXPORT_FOLDER, exist_ok=True)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Add Unicode font if available
    font_name = "Helvetica"
    if os.path.exists(FONT_PATH):
        try:
            pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
            font_name = "DejaVu"
        except Exception:
            try:
                pdf.add_font("DejaVu", "", FONT_PATH)
                font_name = "DejaVu"
            except Exception:
                font_name = "Helvetica"

    for panel in layout:
        image_path = panel.get("image_path", "")
        story_text = panel.get("text", "")
        panel_num = panel.get("panel", 1)
        panel_title = panel.get("title", f"Panel {panel_num}")

        pdf.add_page()

        # Panel title header
        pdf.set_font(font_name, "", 16)
        title_text = _sanitize_for_pdf(f"Panel {panel_num}: {panel_title}")
        pdf.cell(0, 10, title_text, ln=True, align="C")

        # Scene description sub-header if available
        scene_desc = panel.get("scene_description", "")
        if scene_desc:
            pdf.set_font(font_name, "", 10)
            desc_text = _sanitize_for_pdf(f"({scene_desc})")
            pdf.cell(0, 8, desc_text, ln=True, align="C")

        pdf.set_font(font_name, "", 12)

        # Image placement
        y_image = 34
        image_height = 105
        spacing_after_image = 12

        # Verify image existence (check both relative and raw path)
        resolved_img = image_path
        if not os.path.exists(resolved_img):
            resolved_img = os.path.join(os.getcwd(), image_path)

        if os.path.exists(resolved_img):
            try:
                pdf.image(resolved_img, x=15, y=y_image, w=pdf.w - 30, h=image_height)
            except Exception as img_err:
                pdf.set_y(y_image + 10)
                pdf.cell(0, 10, f"[Image display error: {img_err}]", ln=True, align="C")
        else:
            pdf.set_y(y_image + 10)
            pdf.cell(0, 10, _sanitize_for_pdf(f"[Image missing: {image_path}]"), ln=True, align="C")

        # Text placement below image
        pdf.set_y(y_image + image_height + spacing_after_image)
        story_lines = story_text.strip().splitlines()

        # Remove duplicate title line if present at start of text
        if story_lines and story_lines[0].strip().lower().startswith("**panel"):
            story_lines = story_lines[1:]

        cleaned_text = "\n".join(story_lines).strip()
        cleaned_text = _sanitize_for_pdf(cleaned_text)

        # Output the formatted story lines
        pdf.multi_cell(0, 7, cleaned_text)

    # Save with timestamp as requested in documentation
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf_path = os.path.join(EXPORT_FOLDER, filename)
    pdf.output(pdf_path)

    return pdf_path.replace("\\", "/")
