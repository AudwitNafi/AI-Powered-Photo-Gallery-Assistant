# import chromadb_config
import uuid
from typing import Optional, List

from utils.query_parser import extract_keywords_from_image
from gemini import get_gemini_response
from utils.chromadb_config import add_image, add_description, configure_db
from utils.generate_description import generate_image_description
from utils.extract_date import split_date
from utils.query_parser import extract_keywords, extract_keywords_from_image
# from utils.upload_image import upload_image
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
# from rag import rag_pipeline, image_rag_pipeline
from rag import unified_rag_pipeline
from pydantic import BaseModel
import shutil
import asyncio
import json
import os
import traceback


image_collection, desc_collection = configure_db()
app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

QUERY_IMAGE_DIR = Path("query_images")
QUERY_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_FILES_PER_UPLOAD = 10

class ChatRequest(BaseModel):
    message: str
@app.post('/')
async def root():
    print("API hit!")
    return {"message": "Hello World"}
@app.post("/query")
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

@app.post("/query-image")
async def query_hybrid(
        file: Optional[UploadFile] = File(None),
        message: Optional[str] = Form(None)
):
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
            file_location = QUERY_IMAGE_DIR / file.filename
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
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )
@app.get("/view")
async def view():
    return {"descriptions": desc_collection.get()}

# @app.post("/upload")
# async def upload(file: UploadFile = File(...),
#     location: str = Form(...),
#     date: str = Form(...),
#     person_or_entity: str = Form(...)):
#     if not file.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="Only image files are allowed")
#     year, month, day  = split_date(date)
#     if file.size > MAX_FILE_SIZE:
#         raise HTTPException(
#             status_code=400,
#             detail="Image too large!"
#         )
#     print(f"user input data: {location}, {date}, {person_or_entity}")
#     metadata = {
#         "location": location,
#         "year": year,
#         "month": month,
#         "date": day,
#         "person_or_entity": person_or_entity
#     }
#     file_path = UPLOAD_DIR / file.filename
#     with file_path.open("wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     image_id = add_image(str(file_path), image_collection, metadata)
#     description = generate_image_description(file_path)
#     metadata['id'] = image_id
#     # metadata['uri'] = str(file_path)
#     add_description(description, desc_collection, image_id, metadata)
#     # return {"filename": file.filename, "file_path": str(file_path)}
#     return JSONResponse(content={"filename": file.filename, "url": f"/uploads/{file.filename}"})

@app.post("/upload")
async def batch_upload(
    files: List[UploadFile] = File(...),
    location: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    person_or_entity: Optional[str] = Form(None),
):
    # Validate file inputs
    if len(files) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_FILES_PER_UPLOAD} files allowed per upload"
        )

    year, month, day = None, None, None
    # Process date metadata
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

            # Prepare metadata
            data = {
                "location": location,
                "year": year,
                "month": month,
                "day": day,
                "person_or_entity": person_or_entity,
            }
            metadata = {k: v for k, v in data.items() if v is not None}

            # Add to database
            image_id = add_image(str(file_path), image_collection, metadata)
            description = generate_image_description(file_path)
            metadata['id'] = image_id
            add_description(description, desc_collection, image_id, metadata)

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

@app.post("/chat-upload")
async def chat_upload(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    file_location = QUERY_IMAGE_DIR  / file.filename
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"filepath": str(file_location)}

@app.get("/gallery")
async def get_all_images():
    images = []
    upload_dir = "uploads"

    results = image_collection.get(include=['metadatas', 'uris'])
    image_paths = results["uris"]
    image_details = results['metadatas'][0]
    # Example structure - modify according to your metadata storage
    for filename, image_id, metadata in zip(image_paths, results['ids'], results['metadatas']):
        date = ""
        if 'month' and 'day' and 'year' in metadata:
            date = f"{metadata['month']}-{metadata['day']}-{metadata['year']}"
        images.append({
            "id": image_id,
            "filename": filename,
            "title": filename.split('.')[0].split('\\')[1],  # Replace with actual metadata
            "date": date if date else None,  # Replace with actual date
        })
    # print(images)
    return images

@app.get("/gallery/{image_id}")
async def get_image_details(image_id: str):
    # Implement actual database lookup here
    results = desc_collection.get(ids=[image_id], include=['documents', 'metadatas'])
    image_details = results['metadatas'][0]
    location, entities = None, None
    if 'location' in image_details:
        location = image_details['location']
    if entities in image_details:
        entities = image_details['person_or_entity']
    description = results['documents'][0]
    # print(f"The id of image requested: {image_id}")
    return {
        "description": description,
        # "date": f"{image_details['month']}-{image_details['date']}-{image_details['year']}",
        "location": location,
        "entities": entities
    }