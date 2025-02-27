from config.chromadb_config import db_manager, image_collection
from utils.generate_description import generate_image_description
from utils.extract_date import split_date
from utils.query_parser import extract_keywords_from_image
from config.settings import settings # Import settings instance
from fastapi import File, Form, UploadFile, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from config.constants import MAX_FILE_SIZE, MAX_FILES_PER_UPLOAD

router = APIRouter()

QUERY_IMAGE_DIR = settings.query_image_dir
QUERY_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/chat-upload")
async def chat_upload(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    file_location = QUERY_IMAGE_DIR  / file.filename # QUERY_IMAGE_DIR needs to be defined or imported
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return JSONResponse(content={
        "filepath": str(file_location)
    })