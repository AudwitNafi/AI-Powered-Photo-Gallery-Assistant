# import chromadb_config
from typing import List

from chromadb_config import add_image, add_description, configure_db
from utils.generate_description import generate_image_description
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from rag import rag_pipeline, image_rag_pipeline
import shutil

image_collection, desc_collection = configure_db()
app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

QUERY_IMAGE_DIR = Path("query_images")
QUERY_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/query")
async def query(query_text: str):
    try:
        return {"llm-response": rag_pipeline(query_text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#
# @app.post("/query")
# async def query(query_text: str):
#     return {"llm_response": rag_pipeline(query_text)}

@app.post("/query_image")
async def query_image(query_uri: str):
    return {"llm_response": image_rag_pipeline([query_uri])}
@app.get("/view")
async def view():
    return {"descriptions": desc_collection.get()}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    image_id = add_image(str(file_path), image_collection)
    description = generate_image_description(file_path)
    add_description(description, desc_collection, image_id)
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