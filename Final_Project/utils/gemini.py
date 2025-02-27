import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def get_gemini_response(user_input):
    """
    Sends user input to Gemini API chat session and returns the response.
    Maintains chat history for a contextual conversation.
    """
    try:
        response = model.generate_content(user_input)
        return response.text  # Extract response text
    except Exception as e:
        return f"Error: {e}"
