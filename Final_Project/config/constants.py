SYSTEM_INSTRUCTION = (
    """
    You are a photo gallery assistant. Your responses should be like the following
    -   if user asks for images, assist in retrieving relevant images, describing images. 
        Skip any preamble in your responses. Just provide the overall descriptions
        in a paragraph for the retrieved images.
    -   if user is making a general or image non-retrieval query, respond in your usual way.
    """
)

DETERMINE_INTENT_PROMPT = (
    """
    Analyze this query and decide if it requires image retrieval. 
    Return 'true' if the user is asking to see, show, find, or get images/photos/pictures.
    Return 'false' for general questions or non-visual requests.

    Query: {query}

    Respond ONLY with 'true' or 'false' in lowercase."""
)

FILTERED_IMAGES_PROMPT = (
    "Images matching the provided filters/keywords have been found."
)

SIMILAR_IMAGES_PROMPT = (
    "No images matching provided keywords/filters have been found. So you are giving similar images."
)

DESCRIBE_IMAGES_PROMPT = (
    "Based on the query '{text_query}', describe these images in a single paragraph, giving an overall description:"
)

NO_IMAGES_FOUND_PROMPT = (
    "No images found based on given query."
)

SIMILARITY_DESCRIPTION_PROMPT = (
    "Describe the similarity in a paragraph between retrieved images and the uploaded image (first one)."
)

QUERY_IMAGE_DESCRIPTION_PROMPT = (
    "Report that no similar images were found based on the provided query image and describe the given image."
)

NO_RELEVANT_IMAGES_PROMPT = (
    "No relevant images found. Please try searching for something else."
)

HYBRID_QUERY_PROMPT = (
    """
    Highlight both aspects in your description:
    - Text query: {text_query}
    - Visual similarity to provided examples
    """
)

NO_IMAGES_IN_GALLERY_PROMPT = (
    "\nNo relevant images found in the gallery."
)

IMAGE_OR_TEXT_PROMPT = (
    "Please provide either text or image input"
)

SIMILARITY_THRESHOLD = 0.8

MIN_RESULTS = 1

MODEL = "gemini-2.0-flash"