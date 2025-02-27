from fastapi import APIRouter
from config.chromadb_config import db_manager, image_collection
from utils.generate_description import generate_image_description
from utils.extract_date import split_date
from utils.query_parser import extract_keywords_from_image
from config.constants import MAX_FILE_SIZE, MAX_FILES_PER_UPLOAD
from config.settings import settings # Import settings instance
router = APIRouter()

UPLOAD_DIR = settings.upload_dir
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/gallery/")
async def get_all_images():
    images = []

    # Use db_manager.image_collection to access the collection
    results = image_collection.get(include=['metadatas', 'uris']) # Use db_manager
    image_paths = results["uris"]
    print(f"image_paths: {image_paths}")
    # Example structure - modify according to your metadata storage
    for filename, image_id, metadata in zip(image_paths, results['ids'], results['metadatas']): # Handle empty cases
        date = ""
        print(f"filename: {filename}")
        if metadata and 'month' in metadata and 'day' in metadata and 'year' in metadata: # Check metadata exists
            date = f"{metadata['month']}-{metadata['day']}-{metadata['year']}"
        images.append({
            "id": image_id,
            "filename": filename,
            "title": filename.split('.')[0].split('\\')[1],  # Replace with actual metadata access
            "date": date if date else None,  # Replace with actual date
        })
    # print(images)
    return images