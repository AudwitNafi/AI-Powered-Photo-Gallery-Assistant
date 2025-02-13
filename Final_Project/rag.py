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

def encode_image(uri):
    img = Image.open(uri)
    # retrieved_images.append((img, distance, description))
    if img.mode != "RGB":
        img = img.convert("RGB")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()
    return {'mime_type': 'image/jpeg', 'data': base64.b64encode(image_bytes).decode('utf-8')}

def rag_pipeline(query_text, top_k=3):
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
            image_data.append(encode_image(uri))
        except FileNotFoundError:
            print(f"Image not found at: {uri}")
    # prompt_text = "Describe these images in a detailed but concise manner. Key aspects like objects and activities should be mentioned."
    query_text+="\nDescribe these images concisely in a paragraph."
    prompt_parts = [
        query_text,  # Include the query as text part
        # prompt_text,
        *image_data  # Include image data as image parts
    ]

    # Send images and prompt to LLM
    llm_response = model.generate_content(  # Use generate_content directly on model instance
        contents=prompt_parts
    )

    return result_uris, llm_response.text

def image_rag_pipeline(query_uris):
    results = image_collection.query(
        query_uris= query_uris,
        include=['uris']
    )
    result_uris = results['uris'][0]
    image_data = [encode_image(query_uris)]
    for uri in result_uris:
        # print(uri)
        try:
            image_data.append(encode_image(uri))
        except FileNotFoundError:
            print(f"Image not found at: {uri}")

    prompt_text = "Describe these images in a detailed but concise manner. Key aspects like objects and activities should be mentioned."
    prompt_parts = [
        prompt_text,  # Include the query as text part
        *image_data  # Include image data as image parts
    ]

    # Send images and prompt to LLM
    llm_response = model.generate_content(  # Use generate_content directly on model instance
        contents=prompt_parts
    )

    return llm_response.text
