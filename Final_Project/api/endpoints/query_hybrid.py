from typing import Optional

from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from services.rag_service import unified_rag_pipeline  # Assuming rag_service.py is in services dir
from config.chromadb_config import db_manager, image_collection # Import db_manager and image_collection
from config.settings import settings # Import settings
import os


QUERY_IMAGE_DIR = settings.query_image_dir
QUERY_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()

@router.post("/query-image")
async def query_hybrid(
        file: Optional[UploadFile] = File(None),
        message: Optional[str] = Form(None)
):
    file_location = None  # Track the file path for cleanup
    try:
        # Validate at least one input is provided
        if not message and not file:
            raise HTTPException(
                status_code=400,
                detail="At least one of text or image must be provided"
            )

        query_uris = []
        text_query = None

        # Process image if provided
        if file:
            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail="Only image files are allowed"
                )

            # Save uploaded image to temporary location
            file_location = QUERY_IMAGE_DIR / file.filename # Use settings
            with open(file_location, "wb") as f:
                content = await file.read()
                f.write(content)
            query_uris.append(str(file_location))

        # Process text if provided
        if message:
            text_query = message.strip()

        # Call unified RAG pipeline with both inputs
        retrieved_images, response = unified_rag_pipeline(
            text_query=text_query,
            query_uris=query_uris if query_uris else None
        )

        return {"text": response, "images": retrieved_images}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )
    finally:
        # Clean up the query image file if it exists
        if file_location and file_location.exists():
            try:
                os.remove(file_location)
                print(f"Deleted query image: {file_location}")
            except Exception as e:
                print(f"Error deleting query image: {str(e)}")