import google.generativeai as genai
import re
import json, base64
from io import BytesIO
from PIL import Image

def extract_keywords(text):
    """
    Extracts keywords from a given text query.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    Extract keywords from the following text, categorizing them into objects, activities, scene, date, month and year:
    Text: {text}
    don't include the date or month or year attributes if no value found in the query
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

def extract_keywords_from_image(image_path):
    """
    Extracts keywords from an image using the Gemini API.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    Extract keywords from the following image, categorizing them into objects, activities, and scene:
    Output format: (all in plain text without any extra formatting)
    Objects: keyword1, keyword2, ... ; Activities: keyword1, keyword2, ...; Scene: keyword1, keyword2, ...
    """
    try:
        image = Image.open(image_path)
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        response = model.generate_content([{'mime_type':'image/jpeg', 'data': base64.b64encode(image_bytes).decode('utf-8')}, prompt])
        return response.text
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None