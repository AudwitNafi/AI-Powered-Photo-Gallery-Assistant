import glob
from PIL import Image
# import google.generativeai as genai
from dotenv import load_dotenv
import os
import httpx
import base64
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

# view available models
# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)

# model = genai.GenerativeModel(model_name = MODEL)

client = genai.Client(api_key=API_KEY)

# Create a chat session
chat = client.chats.create(model="gemini-2.0-flash")

def get_gemini_response(user_input):
    """
    Sends user input to Gemini API chat session and returns the response.
    Maintains chat history for a contextual conversation.
    """
    try:
        response = chat.send_message(user_input)
        return response.text  # Extract response text
    except Exception as e:
        return f"Error: {e}"






# image_path = glob.glob('./images/0x0.jpg')
#
# # image = httpx.get(image_path)
#
# image = Image.open(image_path[0])
#
# prompt = "Caption this image."
# # response = model.generate_content([{'mime_type':'image/jpeg', 'data': base64.b64encode(image.content).decode('utf-8')}, prompt])
#
# response = model.generate_content([image, prompt])
#
# print(response.text)