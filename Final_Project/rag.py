import base64
import os
import google.generativeai as genai
from io import BytesIO
from PIL import Image

from utils.chromadb_config import configure_db, get_images
from utils.query_parser import extract_keywords, extract_keywords_from_image
from dotenv import load_dotenv
image_collection, desc_collection = configure_db()
image_uris = sorted(get_images('uploads'))
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

system_instruction = "You are a photo gallery assistant. Your responses should assist in retrieving relevant images, describing images, or asking if users want relevant images based on their previous prompts."
model = genai.GenerativeModel(MODEL, system_instruction=system_instruction)

def determine_retrieval_intent(query: str) -> bool:
    """
    Use LLM to determine if image retrieval is needed
    Returns True if images should be retrieved, False otherwise
    """
    prompt = f"""Analyze this query and decide if it requires image retrieval. 
    Return 'true' if the user is asking to see, show, find, or get images/photos/pictures.
    Return 'false' for general questions or non-visual requests.

    Query: {query}

    Respond ONLY with 'true' or 'false' in lowercase."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower() == 'true'
    except Exception as e:
        print(f"Error determining intent: {str(e)}")
        return False  # Fallback to no retrieval

def encode_image(uri):
    """Helper function to encode images for Gemini API"""
    try:
        img = Image.open(uri)
        if img.mode != "RGB":
            img = img.convert("RGB")
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        return {
            'mime_type': 'image/jpeg',
            'data': base64.b64encode(buffer.getvalue()).decode('utf-8')
        }
    except Exception as e:
        print(f"Error encoding image {uri}: {str(e)}")
        return None


def unified_rag_pipeline(text_query=None, query_uris=None, top_k=3):
    """
    Unified RAG pipeline handling text, image, and hybrid queries
    Returns tuple: (retrieved_uris, description)
    """
    prompt_text = ""
    query_filter = []
    metadata_count = 0
    image_data = []

    # Query logic for different input combinations
    # text only query
    if text_query:
        keywords = extract_keywords(text_query)
        print(f"keywords: {keywords}")
        query_filter = []
        metadata_count = 0

        for key in ['date', 'month', 'year', 'location', 'person_or_entity']:
            if key in keywords:
                query_filter.append({key: keywords[key]})
                metadata_count += 1
        print(f"metadata_count: {metadata_count}")

        filtered_ids = []
        if metadata_count > 0:
            if metadata_count == 1:
                query_filter = query_filter[0]
            else:
                query_filter = {"$and": query_filter} if query_filter else {}

            print(f"query_filter: {query_filter}")

            # Filter images by metadata
            filtered_images = image_collection.get(where=query_filter) #querying image collection
            filtered_ids = filtered_images['ids']
            print(f'filtered_ids: {filtered_ids}')

        if filtered_ids:
            # matching description with text for the filtered images
            results = desc_collection.query(
                query_texts=[text_query],
                n_results=top_k,
                where={"id": {"$in": filtered_ids}},       ##doesn't work
                include=['distances', 'documents']
            )
            print(f"Filtered ids: {results['ids'][0]}")
            prompt_text += f"Mention that images matching the provided filters/keywords have been found."
        else:
            results = desc_collection.query(
                query_texts=[text_query],
                n_results=top_k,
                include=['distances', 'documents']
            )
            prompt_text += f"Mention that no images matching provided keywords/filters have been found. So you are giving similar images."
            # print(f"Filtered ids 2: {results['ids'][0]}")

        # get the result ids
        image_ids = results['ids'][0]
        print(f"filtered image_ids based on desc match: {image_ids}")
        # filtered_ids = image_ids['ids'] if image_ids else filtered_ids
        image_results = image_collection.get(ids=image_ids, include=['uris'])  #querying image collection again to get the uris
        distances = results['distances'][0]
        descriptions = results['documents'][0]
        retrieved_uris = image_results['uris']

        prompt_text += f"Based on the query '{text_query}', describe these images in a single paragraph, giving an overall description:"
        # metadata_count = 0
    elif text_query and query_uris:
        keywords = extract_keywords(text_query)
        for key in ['date', 'month', 'year', 'location', 'person_or_entity']:
            if key in keywords:
                query_filter.append({key: keywords[key]})
                metadata_count += 1
        filtered_ids = []
        if metadata_count > 0:
            if metadata_count == 1:
                query_filter = query_filter[0]
            else:
                query_filter = {"$and": query_filter} if query_filter else {}

            # fetching the images similar to given image that meet the text query filters
            results = image_collection.query(
                query_uris=query_uris,
                n_results=top_k,
                where=query_filter,
                include=['uris', 'distances']
            )
            filtered_ids = results['ids'][0]

        if filtered_ids:
            results = image_collection.query(
                query_uris = [query_uris],
                n_results = top_k,
                where = {"id": {"$in": filtered_ids}},
                include = ['distances', 'uris']
            )
            prompt_text += f"Mention that images matching the provided filters/keywords have been found."
        else:
            results = image_collection.query(
                query_uris=[query_uris],
                n_results=top_k,
                include=['distances', 'uris']
            )
            prompt_text += f"Mention that no image matching the provided filters/keywords have been found."
            # print(f"Filtered ids 2: {results['ids'][0]}")

        retrieved_uris = results['uris'][0]
        prompt_text += f"Describe the similarity in a paragraph between retrieved images and the uploaded image(first one). Focus on:"
        for uri in query_uris:
            if encoded := encode_image(uri):
                image_data.append(encoded)
    elif query_uris:
        # Image-only query
        results = image_collection.query(
            query_uris=query_uris,
            n_results=top_k,
            include=['uris', 'distances']
        )
        retrieved_uris = results['uris'][0]
        prompt_text = "Describe the similarity between the query images and these results in a paragraph.:"

        # Include query images in the context
        for uri in query_uris:
            if encoded := encode_image(uri):
                image_data.append(encoded)
    else:
        return [], "Please provide either text or image input"

    # Encode retrieved images
    for uri in retrieved_uris:
        if encoded := encode_image(uri):
            image_data.append(encoded)

    if not image_data:
        return [], "No relevant images found"

    # Generate dynamic prompt based on input type
    if text_query and query_uris:
        prompt_text += (
            f"\n- Text query: {text_query}"
            f"\n- Visual similarity to provided examples"
            "\nHighlight both aspects in your description."
        )
    elif query_uris:
        prompt_text += (
            "\nFocus on visual elements like:"
            "\n- Color schemes\n- Composition\n- Subjects\n- Style"
        )

    # Get LLM response
    # model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))
    response = model.generate_content([prompt_text] + image_data)
    retrieved_uris = [f"http://localhost:8000/{filename}" for filename in retrieved_uris]
    print(f'retrieved_uris: {retrieved_uris}')
    return retrieved_uris, response.text