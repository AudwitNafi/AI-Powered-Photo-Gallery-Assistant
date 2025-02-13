# Import the Streamlit library
import streamlit as st
import glob
import os
from dotenv import load_dotenv

from chromadb_config import get_images
from rag import rag_pipeline
from gemini import get_gemini_response
# from google import genai
import google.generativeai as genai
import gallery

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

genai.configure(api_key=API_KEY)
instruction = "You are a photo gallery assistant. You're responses should be to assist the user in retrieving relevant images, describe image or ask the user if they want relevant images based on user's previous prompt(s)."
model = genai.GenerativeModel(
    MODEL,
    system_instruction=instruction,
)
chat = model.start_chat()
# Create a chat session
# chat = client.chats.create(model=MODEL)


def chat_interface():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Write a simple message to the app's webpage
    st.title('Conversational Memory Bot')
    st.write('AI-Powered Photo Gallery Assistant')
    st.image('./images/0x0.jpg')

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "images" in message:
                # Display images
                cols = st.columns(4)  # Create a 4-column grid
                for idx, img_url in enumerate(message["images"]):
                    with cols[idx % 4]:  # Distribute images in columns
                        st.image(img_url)
                st.markdown(message["content"])
            else:
                st.markdown(message["content"])

    # User input
    user_input = st.chat_input("What kind of images are you looking for?")


    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Check if user is requesting images
        # if "show me images of" in user_input.lower():
        search_query = user_input.replace("show me images of", "").strip()
        images, description = rag_pipeline(search_query)  # Fetch images and description from RAG pipeline

        # Add images to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": f"{description}", "images": images})

        # Display images in a grid
        with st.chat_message("assistant"):
            st.markdown(f"Here are some images of {search_query}:")
            cols = st.columns(3)  # 3 images per row
            for idx, img_url in enumerate(images):
                with cols[idx % 3]:  # Distribute in columns
                    st.image(img_url)
            st.write(description)

pg = st.navigation([st.Page(chat_interface, title="Chat"),
                    st.Page("gallery.py", title="Gallery"),
                    st.Page("uploads.py", title="Upload")])

pg.run()