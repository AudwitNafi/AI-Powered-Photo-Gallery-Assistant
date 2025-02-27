from fastapi import APIRouter, Form, HTTPException
from services.rag_service import unified_rag_pipeline  # Assuming rag_service.py is in services dir
from config.chromadb_config import db_manager, image_collection # Import db_manager and image_collection
from pathlib import Path # Import Path
from config.settings import settings # Import settings

router = APIRouter()


@router.post("/query")
async def query(message: str = Form(None)):
    try:
        print(message)
        retrieved_images, response = unified_rag_pipeline(text_query=message)
        print(retrieved_images)
        print(response)
        return {"text": response, "images": retrieved_images}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))