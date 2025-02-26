import google.generativeai as genai
from typing import List
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")
genai.configure(api_key=API_KEY)
# Initialize chat context manager
class RagChatContext:
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL)
        self.chat = self.model.start_chat()
        self.retrieved_images = []
        self._init_system_prompt()

    def _init_system_prompt(self):
        system_prompt = """You are a visual assistant that can discuss images. 
        Always consider these images in context: {IMAGES}
        Current conversation history: {HISTORY}"""
        self.system_prompt = system_prompt

    def add_images(self, image_uris: List[str]):
        """Store image URIs and prepare context"""
        self.retrieved_images.extend(image_uris)
        image_context = "\n".join(
            [f"Image {i + 1}: {uri}" for i, uri in enumerate(image_uris)]
        )
        self.chat.send_message(f"New images added to context:\n{image_context}")

    def update_context(self, new_images: List[str], user_query: str, response: str):
        # Store image URIs and descriptions
        self.retrieved_images.extend(new_images)

        # Format image context for LLM
        image_context = "\n".join([f"Image {i + 1}: {uri}" for i, uri in enumerate(new_images)])

        # Update chat history
        self.chat.send_message(user_query)
        self.chat.send_message({
            "text": response,
            "metadata": {
                "images": new_images,
                "context": image_context
            }
        })

    # def get_context_prompt(self):
    #     history = "\n".join([msg.parts[0].text for msg in self.chat.history])
    #     return self.system_prompt.replace("{IMAGES}", "\n".join(self.retrieved_images)) \
    #         .replace("{HISTORY}", history)

    def get_contextual_prompt(self, query: str) -> str:
        """Generate context-aware prompt"""
        history = "\n".join(
            [f"{msg.role}: {msg.parts[0].text}"
             for msg in self.chat.history if msg.role != 'model']
        )
        return f"""Context:
        - Current Images: {len(self.retrieved_images)} images
        - History: {history}

        Query: {query}"""