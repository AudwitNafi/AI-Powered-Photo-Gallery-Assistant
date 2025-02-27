from typing import Optional, List

from config.llm_instantiation import load_gemini_model

from config.constants import SYSTEM_INSTRUCTION, MODEL

class ChatService:
    """
    A service class to manage chat interactions using the google.generativeai library,
    Includes capability to add image descriptions to chat history.
    """
    def __init__(self, model_name=MODEL):
        """
        Initializes the ChatService with an API key and model name.

        Args:
            model_name (str, optional): The name of the Gemini model to use.
                                         Defaults to "gemini-2.0-flash".
        """
        self.system_instruction = SYSTEM_INSTRUCTION
        self.model = load_gemini_model(model_name, self.system_instruction) # Configure API key globally for genai
        self.chat = self.model.start_chat()
        self.history = self.chat.history

    def send_message(self, message_text: str, image_descriptions: Optional[List[str]] = None) -> str:
        """
        Sends a message to the chat model and optionally appends image descriptions
        to the chat history as context before sending the message. Returns the text response.

        Args:
            message_text (str): The text message to send to the chat.
            image_descriptions (Optional[List[str]], optional): A list of image description strings
                to be added to the chat history as context before sending the message.
                Defaults to None.

        Returns:
            str: The text response from the chat model.
        """
        if image_descriptions:
            combined_descriptions = ""
            # Prepend image descriptions to the message history by sending them as separate user messages first
            for description in image_descriptions:
                combined_descriptions += "\n\n" + description
            # Send each image description as a user message *before* the main message
            self.chat.send_message(f"""
                Image Description: {combined_descriptions}
                This is a description for the retrieved image.  
                You can use this to provide more context or information in later turns.
            """)
        response = self.chat.send_message(message_text)
        return response.text

    def get_history(self) -> list:
        """
        Returns the chat history.  Note: Direct access to history might be different
        in the updated API.  This method might need adjustment based on the API's
        publicly exposed history access methods if available.
        For now, we return the internal representation if possible, or None if not easily accessible.

        Returns:
            list: A list representing the chat history, or None if history access is restricted.
        """

        if hasattr(self.chat, 'history'): # Check if 'history' is a public attribute
            return self.chat.history
        else:
            print("Warning: Direct access to chat history might not be publicly available in this API version.")
            return []

    def show_history(self) -> None:
        """
        Prints the chat history in a formatted way to the console.
        Note: This might need to be adjusted depending on how history is accessed in the new API.
        If direct history access is limited, this might not be fully functional.
        """
        history = self.get_history()
        if history:
            print("\n--- Chat History ---")
            for message in history:
                print(f'role - {message.role}: {message.parts[0].text}') # Assuming message structure is similar
            print("--- End of History ---\n")
        else:
            print("Chat history is not accessible or could not be retrieved for display.")
