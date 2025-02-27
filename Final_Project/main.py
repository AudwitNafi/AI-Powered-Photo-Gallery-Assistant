from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.router import main_router
from config.settings import settings # Import settings instance
from pydantic import BaseModel
app = FastAPI()
app.include_router(main_router)
# app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")
app.mount("/static/uploads", StaticFiles(directory="static/uploads"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

UPLOAD_DIR = settings.upload_dir
QUERY_IMAGE_DIR = settings.query_image_dir
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
QUERY_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

class ChatRequest(BaseModel):
    message: str
