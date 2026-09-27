import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routes import router

# Load environment variables from .env
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="AI-driven comic book creator using Gemini Flash, Gemini Pro, and Stable Diffusion.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for API integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure required runtime directories exist
for folder in [
    os.path.join("static", "panels"),
    os.path.join("static", "exports"),
    os.path.join("static", "fonts"),
    os.path.join("static", "images"),
    os.path.join("static", "css")
]:
    os.makedirs(folder, exist_ok=True)

# Mount static folder to serve images, CSS, and exported PDFs
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
