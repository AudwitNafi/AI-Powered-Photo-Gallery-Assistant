from config.chromadb_config import add_image, add_description
from generate_description import generate_image_description
from datetime import datetime

def upload_image(image_path: str, date: str, location: str):
    """Process and store image in both collections"""
    try:
        # img = Image.open(image_path)

        # Generate description with Gemini
        # vision_model = genai.GenerativeModel('gemini-pro-vision')
        description = generate_image_description(image_path)

        # Common metadata
        metadata = {
            "date": datetime.strptime(date, "%Y-%m-%d").isoformat(),
            "location": location.lower().strip(),
            "description": description,
            "tags": ", ".join(description.lower().split()[:5])
        }

        # Add to image collection
        # collection_images.add(
        #     uris=[image_path],
        #     metadatas=[metadata],
        #     ids=[image_path]
        # )
        add_image(image_path, description, metadata)
        # Add to descriptions collection
        # collection_descriptions.add(
        #     documents=[description],
        #     metadatas=[metadata],
        #     ids=[image_path]
        # )
        add_description(image_path, description, metadata)
        return True
    except Exception as e:
        print(f"Upload error: {e}")
        return False