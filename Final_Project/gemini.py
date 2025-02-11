import glob
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import os
import httpx
import base64

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")
genai.configure(api_key=API_KEY)

# view available models
# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)

model = genai.GenerativeModel(model_name = MODEL)

image_path = glob.glob('./images/0x0.jpg')

# image = httpx.get(image_path)

image = Image.open(image_path[0])

prompt = "Caption this image."
# response = model.generate_content([{'mime_type':'image/jpeg', 'data': base64.b64encode(image.content).decode('utf-8')}, prompt])

response = model.generate_content([image, prompt])

print(response.text)