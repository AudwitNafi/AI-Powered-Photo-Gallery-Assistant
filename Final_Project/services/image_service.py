from PIL import Image
from io import BytesIO
import base64

def encode_image(uri):
    """Helper function to encode images for Gemini API"""
    try:
        img = Image.open(uri)
        if img.mode != "RGB":
            img = img.convert("RGB")
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        return {
            'mime_type': 'image/jpeg',
            'data': base64.b64encode(buffer.getvalue()).decode('utf-8')
        }
    except Exception as e:
        print(f"Error encoding image {uri}: {str(e)}")
        return None
