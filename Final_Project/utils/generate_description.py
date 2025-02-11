import google.generativeai as genai
import os
from PIL import Image
from dotenv import load_dotenv

MODEL = os.getenv("GEMINI_MODEL")

def generate_image_description(image_path):
  model = genai.GenerativeModel(model_name = MODEL)
  prompt = "Describe this image concisely and in a detailed manner including objects, activities and settings. The description should be a single paragraph."
  image = Image.open(image_path)
  response = model.generate_content([image, prompt])
  return response.text