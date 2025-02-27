from PIL import Image
from config.chromadb_config import db_manager, image_collection
from utils.query_parser import extract_keywords, extract_keywords_from_image, determine_requested_attribute, determine_retrieval_intent
from config.constants import *
from config.llm_instantiation import load_gemini_model
from services.image_service import encode_image
from services.chat_service import ChatService
from config.constants import SYSTEM_INSTRUCTION, SIMILARITY_THRESHOLD
model = load_gemini_model(MODEL)

system_instruction = SYSTEM_INSTRUCTION
chat_service = ChatService(model_name = MODEL)

def unified_rag_pipeline(text_query=None, query_uris=None, top_k=3):
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
        should_retrieve = determine_retrieval_intent(model, text_query)
        print(f'should_retrieve: {should_retrieve}')
        if not should_retrieve:
            # Handle non-image related queries

            response = chat_service.send_message(text_query)

            return [], response

    # If retrieval requested or query image provided
    if should_retrieve or query_uris:
        # text only query
        if text_query and not query_uris:
            keywords = extract_keywords(text_query)
            print(f"keywords: {keywords}")
            query_filter = []
            metadata_count = 0

            for key in ['date', 'month', 'year', 'location', 'person_or_entity', 'event']:
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
                results = image_collection.query(
                    query_texts=[text_query],
                    n_results=top_k,
                    where={"id": {"$in": filtered_ids}},
                    include=['metadatas', 'uris']
                )

                descriptions = [metadata['description'] for metadata in results['metadatas'][0]]
                image_uris = results['uris'][0]
                prompt_text += FILTERED_IMAGES_PROMPT
            else:
                results = image_collection.query(
                    query_texts=[text_query],
                    n_results=top_k*2,
                    include=['distances', 'uris', 'metadatas']
                )
                print(f"results ids: {results['ids'][0]}")
                descriptions = [metadata['description'] for metadata in results['metadatas'][0]]
                distances = results['distances'][0]
                print(distances)
                uris = results['uris'][0]
                ### THRESHOLD FILTERING
                image_uris = [uri for uri, distance in zip(uris, distances) if distance <= SIMILARITY_THRESHOLD]
                prompt_text += SIMILAR_IMAGES_PROMPT

            # get the result ids

            print(f"filtered images based on desc match: {results['uris']}")
            print(f"image_uris: {image_uris}")
            if image_uris:
                retrieved_uris = image_uris
                prompt_text += f"\n{DESCRIBE_IMAGES_PROMPT.format(query=text_query)}"
            # filtered_ids = image_ids['ids'] if image_ids else filtered_ids
            else:
                retrieved_uris = []
                prompt_text += NO_IMAGES_FOUND_PROMPT

        elif text_query and query_uris:
            #Parsing both image and text query to extract keywords
            keywords = extract_keywords(text_query)
            requested_attributes = determine_requested_attribute(text_query)
            image = Image.open(query_uris[0])
            image_keywords = extract_keywords_from_image(image)
            print(f'image_keywords: {image_keywords}')
            metadata_list = ['date', 'month', 'year', 'location', 'person_or_entity', 'event']
            for key in metadata_list:
                if key in keywords:
                    query_filter.append({key: keywords[key]})
                    metadata_count += 1
            for attribute in requested_attributes:
                if attribute in image_keywords:
                    query_filter.append({attribute: image_keywords[attribute]})
                    metadata_count += 1
            filtered_ids = []
            retrieved_uris = []
            if metadata_count > 0:
                if metadata_count == 1:
                    query_filter = query_filter[0]
                else:
                    query_filter = {"$and": query_filter} if query_filter else {}

                ### METADATA FILTERING

                results = image_collection.query(
                    query_uris = query_uris,
                    n_results = top_k,
                    where = query_filter,
                    include = ['metadatas', 'uris']
                )
                descriptions = [metadata['description'] for metadata in results['metadatas'][0]]
                filtered_ids = results['ids'][0]
                retrieved_uris = results['uris'][0]
            if filtered_ids:
                prompt_text += FILTERED_IMAGES_PROMPT
            else:
                print(f"query_uris: {query_uris}")
                results = image_collection.query(
                    query_uris=query_uris,
                    n_results=top_k*2,
                    include=['distances', 'uris', 'metadatas']
                )

                ### Threshold Filtering
                descriptions = [metadata['description'] for metadata in results['metadatas'][0]]
                distances = results['distances'][0]
                uris = results['uris'][0]
                retrieved_uris = [uri for uri, distance in zip(uris, distances) if distance <= SIMILARITY_THRESHOLD]
            if retrieved_uris:
                prompt_text += SIMILAR_IMAGES_PROMPT
                prompt_text += SIMILARITY_DESCRIPTION_PROMPT
            else:
                retrieved_uris = []
                prompt_text += REPORT_NO_IMAGES_FOUND
            # Include query images in the context
            for uri in query_uris:
                if encoded := encode_image(uri):
                    image_data.append(encoded)

        elif query_uris:
            # Image-only query
            results = image_collection.query(
                query_uris=query_uris,
                n_results=top_k*2,
                include=['uris', 'distances', 'metadatas']
            )

            ### Threshold Filtering
            descriptions = [metadata['description'] for metadata in results['metadatas'][0]]
            distances = results['distances'][0]
            uris = results['uris'][0]
            similar_uris = [uri for uri, distance in zip(uris, distances) if distance <= SIMILARITY_THRESHOLD]
            if similar_uris:
                retrieved_uris = similar_uris
                prompt_text = "Describe the similarity between the query images and these results in a paragraph.:"
            else:
                retrieved_uris = []
                prompt_text += "Report that no similar images found based on provided query image and describe the given image."
            # Include query images in the context
            for uri in query_uris:
                if encoded := encode_image(uri):
                    image_data.append(encoded)

        else:
            return [], IMAGE_OR_TEXT_PROMPT

        # Encode retrieved images
        for uri in retrieved_uris:
            if encoded := encode_image(uri):
                image_data.append(encoded)

        if not image_data:
            chat_service.show_history()
            return [], "No relevant images found. Please try searching something else."

        # Generate dynamic prompt based on input type
        if text_query and query_uris:
            prompt_text += f"\n{HYBRID_QUERY_PROMPT.format(query=text_query)}"

    # If no images retrieved but retrieval was attempted
    if (should_retrieve or query_uris) and not retrieved_uris:
        prompt_text += NO_IMAGES_IN_GALLERY_PROMPT

    # Final response generation
    if retrieved_uris:
        print(retrieved_uris)

        response = chat_service.send_message(([prompt_text] + image_data), descriptions)

        retrieved_uris = [f"http://localhost:8000/{filename}" for filename in retrieved_uris]
        print(f'retrieved_uris: {retrieved_uris}')
    else:

        response = chat_service.send_message(prompt_text)

    return retrieved_uris, response