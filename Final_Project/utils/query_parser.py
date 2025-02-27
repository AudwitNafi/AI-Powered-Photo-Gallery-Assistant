import google.generativeai as genai
import re
import json, base64
from io import BytesIO
from config.constants import MODEL
from config.llm_instantiation import load_gemini_model

from config.constants import DETERMINE_INTENT_PROMPT


def extract_keywords(text):
    """
    Extracts keywords from a given text query.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    Extract keywords from the following text, categorizing them into location, date, month, year, person_or_entity, color, event and scene:
    Text: {text}
    include only the attributes that are found in the query. don't include if not found.
    provide all values as string or integer, no lists.
    person_or_entity is only singular noun.
    Format your response as a JSON object. Just provide the JSON object
    """

    response = model.generate_content(prompt)
    # Remove possible code block formatting (e.g., ```json ... ```)
    clean_text = re.sub(r"```json|```", "", response.text).strip()
    # print(clean_text)
    try:
        keywords = json.loads(clean_text)
        return keywords
    except json.JSONDecodeError:
        print("Error: Could not parse JSON response from Gemini.")
        return None

def extract_keywords_from_image(image):
    """
    Extracts keywords from an image using the Gemini API.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    Extract keywords from the following image into object, color, activity, scene in to separate attributes.
    Format your response as a JSON object. Just provide the JSON object. Each attribute should have a single value and 
    be either a string. Don't include attribute whose value is not found.
    """
    try:
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        response = model.generate_content([{'mime_type':'image/jpeg', 'data': base64.b64encode(image_bytes).decode('utf-8')}, prompt])
        clean_text = re.sub(r"```json|```", "", response.text).strip()
        # print(clean_text)
        try:
            keywords = json.loads(clean_text)
            return keywords
        except json.JSONDecodeError:
            print("Error: Could not parse JSON response from Gemini.")
            return None
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def determine_requested_attribute(text):
    """
    Determines the requested attribute from a given text.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    Find which attribute(s) among [color, activity, scene, object] is requested in the given text query:
    Text: {text}
    Format your response as a python list in json format. Just provide the JSON Object. Don't include attribute that are not found.
    """
    try:
        response = model.generate_content(prompt)
        clean_text = re.sub(r"```json|```", "", response.text).strip()
        attributes = json.loads(clean_text)
        return attributes
    except json.JSONDecodeError:
        print("Error: Could not parse response from Gemini.")
        return None

def determine_retrieval_intent(model, query: str) -> bool:
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
        # model = load_gemini_model(MODEL)
        response = model.generate_content(prompt)
        return response.text.strip().lower() == 'true'
    except Exception as e:
        print(f"Error determining intent: {str(e)}")
        return False  # Fallback to no retrieval