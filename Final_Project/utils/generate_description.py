import google.generativeai as genai
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")
genai.configure(api_key=API_KEY)

def generate_image_description(image):
  model = genai.GenerativeModel(model_name = MODEL)
  prompt = """
  Generate a detailed concise description in a single paragraph and comma-separated tags under it for this image. 
  Maintain the following format:
  Description (bold): (...)
  Tags (bold): tag1, tag2, ...
  No other content except these two sections (Description and Tags)
  """
  try:
    response = model.generate_content([
      prompt,
      image
    ])
    description = response.text
    return description
  except:
    raise ValueError("Could not generate description")