from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

def load_gemini_model(model_name, system_instruction=None):
    """Function to load LLM model"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment variables")
    if not model_name:
        raise ValueError("GEMINI_MODEL_NAME is missing from environment variables")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
    return model

