from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router

from utils.text_utils import settings


app = FastAPI(
    title="LegalEase API",
    version="1.0.0",
    description=(
        "AI-powered legal document "
        "drafting API."
    ),
)


origins = [
    item.strip()
    for item in settings.allowed_origins.split(",")
    if item.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
def root():

    return {
        "name": "LegalEase",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "LegalEase API",
        "ai_configured": (
            bool(settings.gemini_api_key)
            or settings.mock_ai
        ),
        "mock_ai": settings.mock_ai,
        "model": settings.gemini_model,
    }