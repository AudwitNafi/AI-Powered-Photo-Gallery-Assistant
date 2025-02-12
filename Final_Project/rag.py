import base64
import os
import google.generativeai as genai
from io import BytesIO
from PIL import Image
from chromadb_config import configure_db, get_images
from dotenv import load_dotenv

image_collection, desc_collection = configure_db()

image_uris = sorted(get_images('uploads'))
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

system_instruction = "You are a photo gallery assistant. You're responses should be to assist the user in retrieving relevant images, describe image or ask the user if they want relevant images based on user's previous prompt(s)."
model = genai.GenerativeModel(MODEL, system_instruction=system_instruction)

def rag_pipeline(query_text, top_k=1):
    """
    RAG pipeline to query images based on natural language descriptions and send images to LLM.
    """
    # Search for relevant image descriptions by passing NLQ to descriptions collection
    results = desc_collection.query(
        query_texts=[query_text],
        n_results=top_k,
        include=['distances', 'documents', 'metadatas']
    )

    # Getting the ids of the matched descriptions
    image_ids = results['ids'][0]
    distances = results['distances'][0]
    descriptions = results['documents'][0]

    # Getting URIs of the retrieved images from their ids

    image_results = image_collection.get(
        ids=image_ids,
        include=['uris']
    )
    result_uris = image_results['uris']
    retrieved_images = []
    image_data = []

    # Retrieving corresponding images from the uris
    for uri in result_uris:
        print(uri)
        try:
            # img = Image.open(image_uri)
            img = Image.open(uri)
            # retrieved_images.append((img, distance, description))
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            image_bytes = buffer.getvalue()
            image_data.append({'mime_type': 'image/jpeg', 'data': base64.b64encode(image_bytes).decode('utf-8')})
        except FileNotFoundError:
            print(f"Image not found at: {uri}")
        # else:
        #     print(f"Invalid image ID: {image_id}")

    prompt_parts = [
        query_text,  # Include the query as text part
        *image_data  # Include image data as image parts
    ]

    # Send images and prompt to LLM
    llm_response = model.generate_content(  # Use generate_content directly on model instance
        contents=prompt_parts
    )

    return retrieved_images, llm_response.text

def image_rag_pipeline(query_uris):
    results = image_collection.query(
        query_uris= query_uris,
        include=['uris']
    )
    result_uris = results['uris'][0]
    # retrieved_images = []
    image_data = []
    for uri in result_uris:
        print(uri)
        try:
            # img = Image.open(image_uri)
            img = Image.open(uri)
            # retrieved_images.append((img, distance, description))
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            image_bytes = buffer.getvalue()
            image_data.append({'mime_type': 'image/jpeg', 'data': base64.b64encode(image_bytes).decode('utf-8')})
        except FileNotFoundError:
            print(f"Image not found at: {uri}")
        # else:
        #     print(f"Invalid image ID: {image_id}")

    prompt_parts = [
        query_text,  # Include the query as text part
        *image_data  # Include image data as image parts
    ]

    # Send images and prompt to LLM
    llm_response = model.generate_content(  # Use generate_content directly on model instance
        contents=prompt_parts
    )

    return llm_response.text
