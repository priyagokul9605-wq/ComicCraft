# ComicCraft - AI Comic Story Creator

ComicCraft is an AI-powered web application that turns story ideas into personalized, multi-panel comic books complete with panel outlines, dialogues, vivid illustrations, and exportable multi-page PDFs.

Built with **FastAPI**, **Google Gemini AI models** (`models/gemini-1.5-flash` and `models/gemini-1.5-pro`), and **Stable Diffusion** (`diffusers`), ComicCraft bridges generative storytelling with visual comic artistry.

---

## 🏗️ Architecture & Model Roles

| Component | Technology | Primary Function |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, Jinja2 | Clean, responsive UI for story customization, panel preview, and PDF export |
| **Backend** | FastAPI, Uvicorn | High-performance asynchronous API, routing, template rendering, and validation |
| **Outline Generator** | Gemini 1.5 Flash | Fast, strictly structured 5-panel JSON comic breakdown and scene descriptions |
| **Story & Dialogue** | Gemini 1.5 Pro | Rich narrative writing, atmospheric captions, and character dialogue |
| **Art Generator** | Stable Diffusion / Diffusers | Comic-style illustration generation per panel with intelligent fallback |
| **Layout Builder** | Python (`layout_builder.py`) | Synthesizes prompts, text, dialogue, and artwork into structured panels |
| **PDF Exporter** | FPDF (`exporters.py`) | Compiles comic pages with headers, artwork, and narratives into PDF |

---

## 📁 Project Directory Structure

```
comiccraft/
│
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI application setup and static mounting
│   ├── routes.py             # Route handlers for web UI, JSON API, and utilities
│   ├── gemini_flash.py       # Outline generation using Gemini 1.5 Flash
│   ├── gemini_pro.py         # Narration and dialogue using Gemini 1.5 Pro
│   ├── image_generator.py    # Panel illustration using Stable Diffusion
│   ├── layout_builder.py     # Panel data binding and layout assembly
│   └── exporters.py          # Multi-page PDF generation via FPDF
│
├── templates/
│   ├── index.html            # Comic creator input form (scenic background)
│   ├── comic_preview.html    # Panel-by-panel preview and export trigger
│   └── export_success.html   # Download confirmation and call-to-action page
│
├── static/
│   ├── css/
│   │   └── style.css         # Modern typography and responsive styling
│   ├── images/
│   │   └── bg.jpg            # Scenic background image
│   ├── panels/               # Generated comic panel images
│   ├── exports/              # Compiled comic PDF files
│   └── fonts/                # TrueType fonts (DejaVu / Arial) for PDF engine
│
├── .env                      # API keys and environment configuration
├── .env.example              # Template for environment configuration
├── requirements.txt          # Python dependencies
├── test_app.py               # Comprehensive automated test suite
└── README.md                 # Project guide and documentation
```

---

## ⚙️ Prerequisites

1. **Python**: Version 3.10 to 3.13+ installed.
2. **VS Code**: Visual Studio Code with the Python extension installed.
3. **API Keys**:
   - **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/)).
   - **Hugging Face API Token** *(optional)* for cloud-based Stable Diffusion inference.

---

## 🚀 VS Code Setup & Installation Guide

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File** > **Open Folder...** (or press `Ctrl + K, Ctrl + O`).
3. Select the folder:
   ```
   C:\Users\Admin\.gemini\antigravity\scratch\comiccraft
   ```

### Step 2: Open Integrated Terminal
- Press ``Ctrl + ` `` (Backtick) or go to **Terminal** > **New Terminal** in the top menu bar.

### Step 3: Create & Activate a Virtual Environment
In the VS Code terminal (PowerShell or Bash):

**On Windows (PowerShell):**
```powershell
python -m venv comiccraft-env
.\comiccraft-env\Scripts\Activate.ps1
```
*(If script execution is restricted on Windows, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

**On macOS / Linux:**
```bash
python3 -m venv comiccraft-env
source comiccraft-env/bin/activate
```

### Step 4: Install Dependencies
Run:
```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables
Open the `.env` file in the project root and add your Gemini API key:
```env
GEMINI_API_KEY=AIzaSy...your_actual_gemini_api_key_here
HF_API_KEY=your_optional_huggingface_token_here
```
*(Note: If you run without an active Gemini API key, ComicCraft seamlessly uses intelligent procedural fallbacks so you can test all features and routes out of the box).*

---

## 🏃 Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access:
- 🌐 **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📚 **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📖 **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Testing the Application

### 1. Automated Test Suite (Pytest)
Run the complete suite of 7 unit and integration tests:
```bash
pytest -v test_app.py
```
This tests:
- Homepage rendering (`/`)
- Developer image test endpoint (`/test-image`)
- Modular AI functions (`generate_outline`, `generate_story`, `generate_image`, `build_comic_layout`, `save_pdf`)
- Form submission flow (`/generate`)
- JSON API endpoint (`/generate-comic/json`)
- PDF download endpoint (`/download-pdf`)
- Export success confirmation page (`/export-success`)

### 2. Testing via Web Browser (End-to-End User Flow)
1. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
2. Enter story parameters:
   - **Story Prompt**: `A brave fox explores an enchanted forest.`
   - **Main Character Name**: `Free`
   - **Setting**: `Forest`
   - **Story Tone**: `Dramatic`
   - **Art Style**: `Realistic`
3. Click **Generate Comic**.
4. Review the 5 generated panels on the **Comic Preview** page with titles, artwork, scene descriptions, and dialogue.
5. Click **Download Your Comic as PDF**. The multi-page PDF will download to your device and you will be routed to the **Export Success** page.

### 3. Testing via JSON REST API
You can test the programmatic comic generation endpoint using PowerShell or `curl`:

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/generate-comic/json" -Method Post -ContentType "application/json" -Body (@{
    prompt = "A brave fox exploring an enchanted forest"
    character_name = "Free"
    setting = "forest"
    tone = "dramatic"
    style = "comic book"
} | ConvertTo-Json)
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/generate-comic/json" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A brave fox exploring an enchanted forest",
    "character_name": "Free",
    "setting": "forest",
    "tone": "dramatic",
    "style": "comic book"
  }'
```

### 4. Testing Image Generator Separately
Test image generation without creating an entire comic:
```bash
curl "http://127.0.0.1:8000/test-image?prompt=A+futuristic+city+at+sunset"
```
Or open [http://127.0.0.1:8000/test-image](http://127.0.0.1:8000/test-image) in your web browser.

---

## 🛡️ Robust Architecture Features
- **Triple-Engine Image Pipeline**: Supports local GPU Diffusers (`runwayml/stable-diffusion-v1-5`), Hugging Face Serverless API, and stylized Pillow procedural comic rendering so users on any machine (CPU, GPU, or offline) get high-quality visual comic panels immediately.
- **Fail-Safe Story Generation**: Even during Gemini API rate limits or network dropouts, intelligent fallback story engines ensure the application never throws 500 errors.
- **Unicode PDF Protection**: Robust character sanitization and TrueType font mapping protect FPDF from unicode character encoding exceptions.
- **Modern FastAPI & Pydantic V2**: Uses current `ConfigDict` and `TemplateResponse(request=...)` conventions for seamless compatibility.
