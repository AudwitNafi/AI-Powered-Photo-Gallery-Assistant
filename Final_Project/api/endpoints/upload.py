import uuid
import shutil
from typing import Optional, List

from PIL import Image

from config.chromadb_config import db_manager, image_collection
from utils.generate_description import generate_image_description
from utils.extract_date import split_date
from utils.query_parser import extract_keywords_from_image
# from utils.upload_image import upload_image
from fastapi import File, Form, UploadFile, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from config.constants import MAX_FILE_SIZE, MAX_FILES_PER_UPLOAD
from config.settings import settings

router = APIRouter()

UPLOAD_DIR = settings.upload_dir

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def batch_upload(
    files: List[UploadFile] = File(...),
    location: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    person_or_entity: Optional[str] = Form(None),
    event: Optional[str] = Form(None)
):
    # Validate file inputs
    if len(files) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_FILES_PER_UPLOAD} files allowed per upload"
        )

    year, month, day = None, None, None
    if date:
        year, month, day = split_date(date)

    uploaded_files = []
    for file in files:
        try:
            # Validate file type
            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename}: Only image files are allowed"
                )

            # Validate file size
            if file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename}: Exceeds size limit ({MAX_FILE_SIZE//1024//1024}MB)"
                )

            # Generate unique filename
            file_ext = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            file_path = UPLOAD_DIR / unique_filename

            # Save file
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image = Image.open(file_path)
            image_keywords = extract_keywords_from_image(image)
            print(f"image_keywords: {image_keywords}")
            for keyword in ['color', 'object', 'activity', 'scene']:
                if keyword not in image_keywords:
                    image_keywords[keyword] = None

            # Prepare metadata
            data = {
                "location": location,
                "year": year,
                "month": month,
                "day": day,
                "person_or_entity": person_or_entity,
                "event": event,
                "color": image_keywords['color'],
                "object": image_keywords['object'],
                "activity": image_keywords['activity'],
                "scene": image_keywords['scene'],
            }
            metadata = {k: v for k, v in data.items() if v is not None}
            # Add to database
            metadata["description"] = generate_image_description(image)
            # Use db_manager.add_image instead of the old add_image function
            db_manager.add_image(str(file_path), metadata) # Use db_manager
            uploaded_files.append({
                "original_name": file.filename,
                "saved_name": unique_filename,
                "url": f"/uploads/{unique_filename}",
                "metadata": metadata
            })

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process {file.filename}: {str(e)}"
            )

    return JSONResponse(content={
        "uploaded": uploaded_files,
        "message": f"Successfully uploaded {len(uploaded_files)} files"
    })