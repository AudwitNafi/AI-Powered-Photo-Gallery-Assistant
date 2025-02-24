# import base64
# import os
# import google.generativeai as genai
# from io import BytesIO
# from PIL import Image
# from chromadb_config import configure_db, get_images
# from dotenv import load_dotenv
#
# image_collection, desc_collection = configure_db()
#
# image_uris = sorted(get_images('uploads'))
# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")
# MODEL = os.getenv("GEMINI_MODEL")
#
# system_instruction = "You are a photo gallery assistant. You're responses should be to assist the user in retrieving relevant images, describe image or ask the user if they want relevant images based on user's previous prompt(s)."
# model = genai.GenerativeModel(MODEL, system_instruction=system_instruction)
#
# def encode_image(uri):
#     img = Image.open(uri)
#     # retrieved_images.append((img, distance, description))
#     if img.mode != "RGB":
#         img = img.convert("RGB")
#     buffer = BytesIO()
#     img.save(buffer, format="JPEG")
#     image_bytes = buffer.getvalue()
#     return {'mime_type': 'image/jpeg', 'data': base64.b64encode(image_bytes).decode('utf-8')}
#
# def rag_pipeline(query_text, top_k=3):
#     """
#     RAG pipeline to query images based on natural language descriptions and send images to LLM.
#     """
#     # Search for relevant image descriptions by passing NLQ to descriptions collection
#     results = desc_collection.query(
#         query_texts=[query_text],
#         n_results=top_k,
#         include=['distances', 'documents', 'metadatas']
#     )
#
#     # Getting the ids of the matched descriptions
#     image_ids = results['ids'][0]
#     distances = results['distances'][0]
#     descriptions = results['documents'][0]
#
#     # Getting URIs of the retrieved images from their ids
#
#     image_results = image_collection.get(
#         ids=image_ids,
#         include=['uris']
#     )
#     result_uris = image_results['uris']
#     retrieved_images = []
#     image_data = []
#     # Retrieving corresponding images from the uris
#     for uri in result_uris:
#         print(uri)
#         try:
#             image_data.append(encode_image(uri))
#         except FileNotFoundError:
#             print(f"Image not found at: {uri}")
#     # prompt_text = "Describe these images in a detailed but concise manner. Key aspects like objects and activities should be mentioned."
#     query_text+="\nDescribe these images concisely in a paragraph."
#     prompt_parts = [
#         query_text,  # Include the query as text part
#         # prompt_text,
#         *image_data  # Include image data as image parts
#     ]
#
#     # Send images and prompt to LLM
#     llm_response = model.generate_content(  # Use generate_content directly on model instance
#         contents=prompt_parts
#     )
#
#     return result_uris, llm_response.text
#
# def image_rag_pipeline(query_uris):
#     results = image_collection.query(
#         query_uris= query_uris,
#         include=['uris'],
#         n_results=3
#     )
#     result_uris = results['uris'][0]
#     image_data = [encode_image(query_uris)]
#     for uri in result_uris:
#         # print(uri)
#         try:
#             image_data.append(encode_image(uri))
#         except FileNotFoundError:
#             print(f"Image not found at: {uri}")
#
#     prompt_text = "Describe the similarity of the first image to the rest of the images in a detailed manner."
#     prompt_parts = [
#         prompt_text,  # Include the query as text part
#         *image_data  # Include image data as image parts
#     ]
#
#     # Send images and prompt to LLM
#     llm_response = model.generate_content(  # Use generate_content directly on model instance
#         contents=prompt_parts
#     )
#
#     return result_uris, llm_response.text


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
    retrieved_uris = []
    image_data = []
    prompt_text = ""
    query_filter = []
    metadata_count = 0

    # text only query
    retrieved_images = []
    image_data = []
    if text_query:
        keywords = extract_keywords(text_query)
        print(f"keywords: {keywords}")
        query_filter = []
        metadata_count = 0

        for key in ['date', 'month', 'year', 'location', 'person_or_entity']:
            if key in keywords:
                query_filter.append({key: keywords[key]})
                metadata_count += 1

        if metadata_count == 0:
            results = desc_collection.query(
                query_texts=[text_query],
                n_results=top_k,
                include=['distances', 'documents', 'metadatas']
            )

            # Getting the ids of the matched descriptions
            image_ids = results['ids'][0]
            # distances = results['distances'][0]
            descriptions = results['documents'][0]

            image_results = image_collection.get(ids=image_ids, include=['uris'])
            retrieved_uris = image_results['uris']

        else:
            if metadata_count == 1:
                query_filter = query_filter[0]
            else:
                query_filter = {"$and": query_filter} if query_filter else {}

            # Step 1: Filter images by metadata
            filtered_images = image_collection.get(where=query_filter) #querying image collection
            filtered_ids = filtered_images['ids']
            print(f'filtered_ids: {filtered_ids}')
            if not filtered_ids:
                return [], "No images found matching your query."

            # matching description with text for the filtered images
            results = desc_collection.query(
                query_texts=[text_query],
                n_results=top_k,
                where={"ids": {"$in": filtered_ids}},
                include=['distances', 'documents', 'uris']
            )

            # get the result ids
            image_ids = results['ids'][0]
            print(f"filtered image_ids based on desc match: {image_ids}")
            filtered_ids = image_ids['ids'] if image_ids else filtered_ids
            image_results = image_collection.get(ids=filtered_ids, include=['uris'])  #querying image collection again to get the uris
            distances = results['distances'][0]
            descriptions = results['documents'][0]
            retrieved_uris = image_results['uris']

        prompt_text = f"Based on the query '{text_query}', describe these images:"

    # Query logic for different input combinations
    elif text_query and query_uris:
        keywords = extract_keywords(text_query)
        query_filter = []
        metadata_count = 0

        for key in ['date', 'month', 'year', 'location', 'person_or_entity']:
            if key in keywords:
                query_filter.append({key: keywords[key]})
                metadata_count += 1

        if metadata_count == 0:
            #if no keyword in query, assume similar images are requested. So image collection queried.
            image_results = image_collection.query(
                query_uris=query_uris,
                n_results=top_k,
                include=['uris']
            )
            image_ids = image_results['ids'][0]
            distances = image_results['distances'][0]
            descriptions = image_results['documents'][0]
            retrieved_uris = image_results['uris'][0]
        else:
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
            if not filtered_ids:
                return [], "No images found matching your query."

            retrieved_uris = results['uris'][0]
        prompt_text = f"Describe the similarity in a paragraph between retrieved images and the uploaded image. Focus on:"
        # prompt_text = "Combined results considering: "
        # prompt_text += f"\n- Text filters: {keywords}" if keywords else ""

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