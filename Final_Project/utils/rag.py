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

    retrieved_images = []
    image_data = []

    # Retrieving corresponding images from the ids
    for image_id, distance, description in zip(image_ids, distances, descriptions):
        image_index = int(image_id)
        if 0 <= image_index < len(image_uris):
            image_uri = image_uris[image_index]
            try:
                img = Image.open(image_uri)
                retrieved_images.append((img, distance, description))
                buffer = BytesIO()
                img.save(buffer, format="JPEG")
                image_bytes = buffer.getvalue()
                image_data.append({'mime_type': 'image/jpeg', 'data': base64.b64encode(image_bytes).decode('utf-8')})
            except FileNotFoundError:
                print(f"Image not found at: {image_uri}")
        else:
            print(f"Invalid image ID: {image_id}")

    prompt_parts = [
        query_text,  # Include the query as text part
        *image_data  # Include image data as image parts
    ]

    # Send images and prompt to LLM
    llm_response = model.generate_content(  # Use generate_content directly on your model instance
        contents=prompt_parts
    )

    return retrieved_images, llm_response.text
