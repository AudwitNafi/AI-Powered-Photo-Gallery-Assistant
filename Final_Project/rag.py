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

SIMILARITY_THRESHOLD = 0.7
MIN_RESULTS = 1

system_instruction = ("""
You are a photo gallery assistant. Your responses should assist in retrieving relevant images, 
describing images. Skip any preamble in your responses. Just provide the overall descriptions 
in a paragraph for the retrieved images.
""")
model = genai.GenerativeModel(MODEL, system_instruction=system_instruction)
chat = model.start_chat()

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
        # response = model.generate_content(prompt)
        response = chat.send_message(prompt)
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

def unified_rag_pipeline(text_query=None, query_uris=None, top_k=4):
    """
    Unified RAG pipeline handling text, image, and hybrid queries
    Returns tuple: (retrieved_uris, description)
    """
    prompt_text = ""
    query_filter = []
    metadata_count = 0
    image_data = []
    retrieved_uris = []
    should_retrieve = False

    # Query logic for different input combinations
    # At first, determine the user's intent
    if text_query and not query_uris:
        should_retrieve = determine_retrieval_intent(text_query)
        if not should_retrieve:
            # Handle non-image related queries
            response = model.generate_content(text_query)
            return [], response.text

    # If retrieval requested or query image provided
    if should_retrieve or query_uris:
        # text only query
        if text_query and not query_uris:
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
                similar_ids = results['ids'][0]
                prompt_text += f"Images matching the provided filters/keywords have been found."
            else:
                results = desc_collection.query(
                    query_texts=[text_query],
                    n_results=top_k*2,
                    include=['distances', 'documents']
                )
                distances = results['distances'][0]
                ids = results['ids'][0]
                similar_ids = [id for id, distance in zip(ids, distances) if distance <= SIMILARITY_THRESHOLD]
                prompt_text += f"No images matching provided keywords/filters have been found. So you are giving similar images."
                # print(f"Filtered ids 2: {results['ids'][0]}")

            # get the result ids
            image_ids = similar_ids
            print(f"filtered image_ids based on desc match: {image_ids}")
            if image_ids:
                ###DOESN'T WORK WITH EMPTY IDS
                image_results = image_collection.get(
                    ids=image_ids, include=['uris']
                )  # querying image collection again to get the uris
                distances = results['distances'][0]
                descriptions = results['documents'][0]
                retrieved_uris = image_results['uris']
                prompt_text += f"Based on the query '{text_query}', describe these images in a single paragraph, giving an overall description:"
            # filtered_ids = image_ids['ids'] if image_ids else filtered_ids
            else:
                retrieved_uris = []
                prompt_text += "No images found based on given query. "
            # metadata_count = 0
        elif text_query and query_uris:
            keywords = extract_keywords(text_query)
            image_keywords = extract_keywords_from_image(query_uris)
            for key in ['date', 'month', 'year', 'location', 'person_or_entity', 'color', 'event']:
                if key in keywords:
                    query_filter.append({key: keywords[key]})
                    metadata_count += 1
            filtered_ids = []
            if metadata_count > 0:
                if metadata_count == 1:
                    query_filter = query_filter[0]
                else:
                    query_filter = {"$and": query_filter} if query_filter else {}

                ### METADATA FILTERING
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
                    query_uris = query_uris,
                    n_results = top_k,
                    where = {"id": {"$in": filtered_ids}},
                    include = ['distances', 'uris']
                )
                similar_uris = results['uris'][0]
                prompt_text += "Images matching the provided filters/keywords have been found."
            else:
                print(f"query_uris: {query_uris}")
                results = image_collection.query(
                    query_uris=query_uris,
                    n_results=top_k*2,
                    include=['distances', 'uris']
                )

                ### Threshold Filtering
                distances = results['distances'][0]
                uris = results['uris'][0]
                similar_uris = [uri for uri, distance in zip(uris, distances) if distance <= SIMILARITY_THRESHOLD]
            if similar_uris:
                retrieved_uris = similar_uris
                prompt_text += f"No image matching the provided filters/keywords have been found. So you are retrieving generally similar images."
                prompt_text += f"Describe the similarity in a paragraph between retrieved images and the uploaded image(first one). "
            else:
                retrieved_uris = []
                prompt_text += "No image matching provided query has been found. Just report it and describe the query image."

            # Include query images in the context
            for uri in query_uris:
                if encoded := encode_image(uri):
                    image_data.append(encoded)
        elif query_uris:
            # Image-only query
            results = image_collection.query(
                query_uris=query_uris,
                n_results=top_k*2,
                include=['uris', 'distances']
            )

            ### Threshold Filtering
            ids = results['ids'][0]
            distances = results['distances'][0]
            uris = results['uris'][0]
            similar_uris = [uri for uri, distance in zip(uris, distances) if distance <= SIMILARITY_THRESHOLD]
            if similar_uris:
                retrieved_uris = similar_uris
                prompt_text = "Describe the similarity between the query images and these results in a paragraph.:"
            # retrieved_uris = results['uris'][0]
            else:
                retrieved_uris = []
                prompt_text += "Report that no similar images found based on provided query image and describe the given image."
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
            return [], "No relevant images found. Please try searching something else."

        # Generate dynamic prompt based on input type
        if text_query and query_uris:
            prompt_text += (
                f"\n- Text query: {text_query}"
                f"\n- Visual similarity to provided examples"
                "\nHighlight both aspects in your description."
            )
        # elif query_uris:
        #     prompt_text += (
        #         "\nFocus on visual elements like:"
        #         "\n- Color schemes\n- Composition\n- Subjects\n- Style"
        #     )

    # If no images retrieved but retrieval was attempted
    if (should_retrieve or query_uris) and not retrieved_uris:
        prompt_text += "\nNo relevant images found in the gallery. "

    # Final response generation
    if retrieved_uris:
        response = model.generate_content([prompt_text] + image_data)
        retrieved_uris = [f"http://localhost:8000/{filename}" for filename in retrieved_uris]
        print(f'retrieved_uris: {retrieved_uris}')
    else:
        response = model.generate_content(prompt_text or text_query)

    return retrieved_uris, response.text