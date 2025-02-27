from fastapi import APIRouter
from config.chromadb_config import db_manager, image_collection
from utils.generate_description import generate_image_description
from utils.extract_date import split_date
from utils.query_parser import extract_keywords_from_image
from config.constants import MAX_FILE_SIZE, MAX_FILES_PER_UPLOAD


router = APIRouter()

@router.get("/gallery/{image_id}")
async def get_image_details(image_id: str):
    # Implement actual database lookup here
    results = image_collection.get(ids=[image_id], include=['metadatas'])

    image_details = results['metadatas'][0]
    location, entities = None, None
    if 'location' in image_details:
        location = image_details['location']
    if 'person_or_entity' in image_details:
        entities = image_details['person_or_entity']
    description = image_details['description']
    # print(f"The id of image requested: {image_id}")
    return {
        "description": description,
        "location": location,
        "entities": entities
    }