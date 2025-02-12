import google.generativeai as genai
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")
genai.configure(api_key=API_KEY)

def generate_image_description(image_path):
  model = genai.GenerativeModel(model_name = MODEL)
  prompt = "Describe this image concisely and in a detailed manner including objects, activities and settings. The description should be a single paragraph."
  image = Image.open(image_path)
  response = model.generate_content([image, prompt])
  print(response.text)
  return response.text