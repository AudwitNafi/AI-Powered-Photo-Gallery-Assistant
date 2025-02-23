# import chromadb_config
from gemini import get_gemini_response
from utils.chromadb_config import add_image, add_description, configure_db
from utils.generate_description import generate_image_description
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

class ChatRequest(BaseModel):
    message: str
@app.post('/')
async def root():
    print("API hit!")
    return {"message": "Hello World"}
@app.post("/query")
async def query(request: ChatRequest):
    try:
        print(request)
        retrieved_images, response = unified_rag_pipeline(text_query=request.message)
        print(retrieved_images)
        # print(response)
        return {"text": response, "images": retrieved_images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query-image")
async def query_image(file: UploadFile = File(...)):
    try:
        # if not query_image.content_type.startswith("image/"):
        #     raise HTTPException(status_code=400, detail="Only image files are allowed")
        file_location = QUERY_IMAGE_DIR / file.filename
        with open(file_location, "wb") as f:
            f.write(await file.read())
        retrieved_images, response = unified_rag_pipeline(query_uris=[file_location])
        return {"text": response, "images": retrieved_images}
        # return JSONResponse(content={"filename": file.filename, "url": f"/uploads/{file.filename}"})
    except:
        #Print the error
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Something went wrong")
@app.get("/view")
async def view():
    return {"descriptions": desc_collection.get()}

@app.post("/upload")
async def upload(file: UploadFile = File(...),
    location: str = Form(...),
    date: str = Form(...),
    person_or_entity: str = Form(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image too large!"
        )
    print(f"user input data: {location}, {date}, {person_or_entity}")
    metadata = {
        "location": location,
        "date": date,
        "person_or_entity": person_or_entity
    }
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    image_id = add_image(str(file_path), image_collection, metadata)
    description = generate_image_description(file_path)
    add_description(description, desc_collection, image_id, metadata)
    # return {"filename": file.filename, "file_path": str(file_path)}
    return JSONResponse(content={"filename": file.filename, "url": f"/uploads/{file.filename}"})

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

    # Example structure - modify according to your metadata storage
    for filename in os.listdir(upload_dir):
        images.append({
            "id": filename.split('.')[0],  # Generate unique ID
            "filename": filename,
            "title": "Sample Title",  # Replace with actual metadata
            "date": "2023-01-01",  # Replace with actual date
            "location": "Sample Location",  # Replace with actual location
            "entities": ["Person 1", "Object 1"]  # Replace with actual entities
        })

    return images

@app.get("/gallery/{image_id}")
async def get_image_details(image_id: str):
    # Implement actual database lookup here
    print(f"The id of image requested: {image_id}")
    return {
        "id": image_id,
        "filename": f"{image_id}.jpg",
        "title": "Sample Title",
        "date": "2023-01-01",
        "location": "Sample Location",
        "entities": ["Person 1", "Object 1"]
    }

# @app.post("/api/v1/chat")
# async def handle_chat(data: ChatRequest):
#     try:
#         # Process text query
#         print('text query api hit!')
#         print("\n🔹 Received request data:", data.message)  # Print the request data
#         # retrieved_images, response = unified_rag_pipeline(message)
#         response = get_gemini_response(data.message)
#         return {
#             "text": response
#         }
#     except Exception as e:
#         print("\n❌ General Error:", str(e))  # Print general errors
#         raise HTTPException(status_code=400, detail="Invalid request format")
# @app.post("/api/v1/chat-upload")
# async def handle_upload(image: UploadFile):
#     # Process image query
#     return {
#         "text": "Image analysis results",
#         "results": [...]  # Your search results
#     }