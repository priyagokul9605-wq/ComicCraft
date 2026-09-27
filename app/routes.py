import os
import traceback
import uuid

from fastapi import (
    APIRouter,
    Request,
    Form,
    HTTPException,
    Query
)

from fastapi.responses import (
    HTMLResponse,
    FileResponse
)

from fastapi.templating import Jinja2Templates

from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story

from app.image_generator import (
    generate_comic_sheet,
    split_comic_sheet,
    generate_image
)

from app.layout_builder import build_comic_layout
from app.exporters import save_pdf


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


# =========================================================
# JSON REQUEST MODEL
# =========================================================

class PromptRequest(BaseModel):

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": (
                    "A brave fox exploring an enchanted "
                    "forest finds a glowing crystal"
                ),
                "character_name": "Free",
                "setting": "forest",
                "tone": "dramatic",
                "style": "comic book"
            }
        }
    )

    prompt: str = Field(
        ...,
        description="The main story idea or prompt for the comic"
    )

    character_name: str = Field(
        ...,
        description="Name of the main hero/character"
    )

    setting: str = Field(
        ...,
        description="The setting/location"
    )

    tone: str = Field(
        ...,
        description="Tone of the story"
    )

    style: str = Field(
        ...,
        description="Art style for illustration"
    )


# =========================================================
# HOME
# =========================================================

@router.get(
    "/",
    response_class=HTMLResponse
)
async def index(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# =========================================================
# MAIN COMIC GENERATION
# =========================================================

@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate_comic(
    request: Request,

    prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    style: str = Form(...)
):

    try:

        # -------------------------------------------------
        # Unique ID for THIS comic
        # -------------------------------------------------

        comic_id = uuid.uuid4().hex[:10]

        print()
        print("=" * 70)
        print("COMICCRAFT NEW COMIC")
        print(f"Comic ID: {comic_id}")
        print("=" * 70)

        # -------------------------------------------------
        # Build full user prompt
        # -------------------------------------------------

        full_prompt = (
            f"{prompt}\n"
            f"The main character is {character_name}.\n"
            f"The setting is a {setting}.\n"
            f"The tone is {tone}.\n"
            f"The art style is {style}."
        )

        # -------------------------------------------------
        # STEP 1
        # Gemini Flash
        # -------------------------------------------------

        print()
        print("STEP 1: Generating comic outline...")

        outline = generate_outline(
            full_prompt
        )

        if (
            not isinstance(outline, list)
            or not outline
        ):
            raise ValueError(
                "Gemini returned an invalid comic outline."
            )

        # Limit to five panels
        outline = outline[:5]

        print(
            f"Outline contains {len(outline)} panels."
        )

        # -------------------------------------------------
        # STEP 2
        # Gemini Pro
        # -------------------------------------------------

        print()
        print("STEP 2: Generating story...")

        full_story = generate_story(
            outline
        )

        # -------------------------------------------------
        # STEP 3
        # ONE IMAGE-GENERATION REQUEST
        # -------------------------------------------------

        print()
        print(
            "STEP 3: Generating ONE comic sheet..."
        )

        sheet_filename = (
            f"{comic_id}_comic_sheet.png"
        )

        sheet_path = generate_comic_sheet(
            outline,
            filename=sheet_filename
        )

        # -------------------------------------------------
        # STEP 4
        # LOCAL SPLIT
        #
        # NO AI REQUEST HERE
        # -------------------------------------------------

        print()
        print(
            "STEP 4: Splitting comic sheet locally..."
        )

        images = split_comic_sheet(
            sheet_path,
            comic_id
        )

        # -------------------------------------------------
        # STEP 5
        # BUILD LAYOUT
        # -------------------------------------------------

        print()
        print(
            "STEP 5: Building comic layout..."
        )

        layout = build_comic_layout(
            images,
            full_story,
            outline
        )

        # -------------------------------------------------
        # STEP 6
        # PDF
        # -------------------------------------------------

        print()
        print(
            "STEP 6: Creating PDF..."
        )

        pdf_path = save_pdf(
            layout
        )

        web_pdf_path = (
            "/"
            + pdf_path
            .replace("\\", "/")
            .lstrip("/")
        )

        print()
        print("=" * 70)
        print("COMIC GENERATION COMPLETE")
        print(f"Comic ID: {comic_id}")
        print("IMAGE API REQUESTS: 1")
        print("=" * 70)

        # -------------------------------------------------
        # PREVIEW
        # -------------------------------------------------

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_path": web_pdf_path,
                "character_name": character_name,
                "setting": setting,
                "tone": tone,
                "style": style
            }
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# JSON API
# =========================================================

@router.post(
    "/generate-comic/json"
)
async def generate_comic_json(
    payload: PromptRequest
):

    try:

        comic_id = uuid.uuid4().hex[:10]

        full_prompt = (
            f"{payload.prompt}\n"
            f"The main character is {payload.character_name}.\n"
            f"The setting is a {payload.setting}.\n"
            f"The tone is {payload.tone}.\n"
            f"The art style is {payload.style}."
        )

        # Gemini outline
        outline = generate_outline(
            full_prompt
        )

        outline = outline[:5]

        # Gemini story
        full_story = generate_story(
            outline
        )

        # ONE image-generation request
        sheet_path = generate_comic_sheet(
            outline,
            filename=f"{comic_id}_comic_sheet.png"
        )

        # Local processing only
        images = split_comic_sheet(
            sheet_path,
            comic_id
        )

        # Build layout
        layout = build_comic_layout(
            images,
            full_story,
            outline
        )

        # PDF
        pdf_path = save_pdf(
            layout
        )

        web_pdf_path = (
            "/"
            + pdf_path.replace(
                "\\",
                "/"
            ).lstrip("/")
        )

        return {
            "status": "success",
            "comic_id": comic_id,
            "image_generation_requests": 1,
            "full_prompt": full_prompt,
            "layout": layout,
            "pdf_path": web_pdf_path
        }

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# EXPORT SUCCESS
# =========================================================

@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(
    request: Request,
    pdf_path: str = Query("")
):

    clean_web_path = (
        "/"
        + pdf_path.lstrip("/")
        if pdf_path
        else ""
    )

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_path": clean_web_path
        }
    )


# =========================================================
# DOWNLOAD PDF
# =========================================================

@router.get(
    "/download-pdf"
)
async def download_pdf(
    file_path: str = Query(...)
):

    clean_path = (
        file_path
        .lstrip("/")
        .replace("\\", "/")
    )

    if not clean_path.startswith(
        "static/exports/"
    ):

        clean_path = os.path.join(
            "static",
            "exports",
            os.path.basename(clean_path)
        )

    if not os.path.exists(
        clean_path
    ):

        raise HTTPException(
            status_code=404,
            detail=(
                "Requested comic PDF "
                "was not found."
            )
        )

    filename = os.path.basename(
        clean_path
    )

    return FileResponse(
        clean_path,
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition":
            f'attachment; filename="{filename}"'
        }
    )


# =========================================================
# DEVELOPER IMAGE TEST
# =========================================================

@router.get(
    "/test-image"
)
async def test_image(
    prompt: str = (
        "A futuristic city at sunset, "
        "sci-fi, cinematic comic art"
    )
):

    try:

        image_path = generate_image(
            prompt
        )

        web_path = (
            "/"
            + image_path
            .replace("\\", "/")
            .lstrip("/")
        )

        return {
            "message": (
                "Image generated successfully"
            ),
            "path": web_path
        }

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )