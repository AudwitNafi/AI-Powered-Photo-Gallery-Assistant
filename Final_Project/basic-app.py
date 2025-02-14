import streamlit as st
import os
import requests
from dotenv import load_dotenv

from rag import unified_rag_pipeline
import google.generativeai as genai

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

genai.configure(api_key=API_KEY)
instruction = "You are a photo gallery assistant. Your responses should assist in retrieving relevant images, describing images, or asking if users want relevant images based on their previous prompts."
model = genai.GenerativeModel(MODEL, system_instruction=instruction)
chat = model.start_chat()


def display_response(description, images):
    """Helper function to display responses consistently"""
    st.session_state.messages.append({
        "role": "assistant",
        "content": description,
        "images": images
    })

    with st.chat_message("assistant"):
        st.markdown(description)
        if images:
            cols = st.columns(3)
            for idx, img_url in enumerate(images):
                with cols[idx % 3]:
                    st.image(img_url)


def process_query(uploaded_file=None, text_query=None):
    """Handle both text and image queries using the unified RAG"""
    if uploaded_file:
        # Process image upload
        file = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post("http://127.0.0.1:8000/chat-upload/", files=file)

        if response.status_code == 200:
            file_path = response.json()['filepath']
            return unified_rag_pipeline([file_path])
        return [], "Could not process the uploaded image."

    if text_query:
        return unified_rag_pipeline(text_query)

    return [], "Please provide either text or image input"


def chat_interface():
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_file" not in st.session_state:
        st.session_state.current_file = None
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    st.title('Multimodal Photo Assistant')
    st.write('Search with text, images, or both!')
    st.image('./images/0x0.jpg')

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("images"):
                cols = st.columns(3)
                for idx, img_url in enumerate(message["images"]):
                    with cols[idx % 3]:
                        st.image(img_url)
            st.markdown(message["content"])

    # File uploader with rotating key to force reset
    uploaded_file = st.file_uploader(
        "Upload image",
        type=["png", "jpg", "jpeg"],
        key=f"file_uploader_{st.session_state.uploader_key}"
    )

    # Chat input
    user_input = st.chat_input("Ask about images or upload one...")

    # Handle new queries
    if user_input or uploaded_file:
        # Store inputs temporarily
        if uploaded_file:
            st.session_state.current_file = uploaded_file
            # Rotate uploader key to clear the widget
            st.session_state.uploader_key += 1

        # Add user message to history
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

        # Process the query
        images, description = process_query(
            uploaded_file=st.session_state.current_file,
            text_query=user_input
        )

        # Display response
        display_response(description, images)

        # Clear temporary file state
        st.session_state.current_file = None


pg = st.navigation([st.Page(chat_interface, title="Chat"),
                    st.Page("gallery.py", title="Gallery"),
                    st.Page("uploads.py", title="Upload")])
pg.run()

# import streamlit as st
# import os
# import requests
# from dotenv import load_dotenv
# from streamlit import session_state
#
# from rag import rag_pipeline, image_rag_pipeline
# import google.generativeai as genai
#
# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")
# MODEL = os.getenv("GEMINI_MODEL")
#
# genai.configure(api_key=API_KEY)
# instruction = "You are a photo gallery assistant. You're responses should be to assist the user in retrieving relevant images, describe image or ask the user if they want relevant images based on user's previous prompt(s)."
# model = genai.GenerativeModel(MODEL, system_instruction=instruction)
# chat = model.start_chat()
#
#
# def display_response(description, images):
#     """Helper function to display responses consistently"""
#     st.session_state.messages.append({
#         "role": "assistant",
#         "content": description,
#         "images": images
#     })
#
#     with st.chat_message("assistant"):
#         st.markdown(description)
#         if images:
#             cols = st.columns(3)
#             for idx, img_url in enumerate(images):
#                 with cols[idx % 3]:
#                     st.image(img_url)
#
#
# def process_image_query(uploaded_file):
#     """Handle image-based queries"""
#     file = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
#     response = requests.post("http://127.0.0.1:8000/chat-upload/", files=file)
#
#     if response.status_code == 200:
#         st.success(f"Uploaded {uploaded_file.name}")
#         file_path = response.json()['filepath']
#         images, description = image_rag_pipeline(file_path)
#         return images, description
#     else:
#         st.error("Failed to process image")
#         return [], "Could not process the uploaded image."
#
#
# def process_text_query(query):
#     """Handle text-based queries"""
#     images, description = rag_pipeline(query)
#     return images, description
#
#
# # def process_combined_query(uploaded_file, query):
# #     """Handle queries with both image and text"""
# #     # First process the image
# #     file = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
# #     response = requests.post("http://127.0.0.1:8000/chat-upload/", files=file)
# #
# #     if response.status_code == 200:
# #         st.success(f"Uploaded {uploaded_file.name} with query: {query}")
# #         file_path = response.json()
# #
# #         # Combine image search with text query
# #         base_images, _ = image_rag_pipeline(file_path)
# #         text_images, description = rag_pipeline(query)
# #
# #         # Combine and deduplicate results
# #         combined_images = list({img: None for img in base_images + text_images}.keys())[:6]
# #         return combined_images, f"Results combining your image and text: {description}"
# #     return [], "Could not process combined query"
#
#
# def chat_interface():
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
#
#     st.title('Multimodal Photo Assistant')
#     st.write('Search with text, images, or both!')
#     st.image('./images/0x0.jpg')
#
#     # Display chat history
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             if message.get("images"):
#                 cols = st.columns(3)
#                 for idx, img_url in enumerate(message["images"]):
#                     with cols[idx % 3]:
#                         st.image(img_url)
#             st.markdown(message["content"])
#
#     # User inputs
#     user_input = st.chat_input("Ask about images or upload one...")
#     uploaded_file = st.file_uploader("Upload image",
#                                      type=["png", "jpg", "jpeg"],
#                                      key="file_uploader")
#
#     # Process queries
#     if user_input or uploaded_file:
#         current_file = uploaded_file if uploaded_file else None
#         # Clear inputs from session state
#         if 'file_uploader' in st.session_state:
#             st.session_state.file_uploader = None
#         # if 'chat_input' in st.session_state:
#         #     st.session_state.chat_input = ""
#         # Add user message to history
#         if user_input:
#             st.session_state.messages.append({"role": "user", "content": user_input})
#             with st.chat_message("user"):
#                 st.markdown(user_input)
#
#         # Determine query type
#         # if uploaded_file and user_input:
#         #     images, description = process_combined_query(uploaded_file, user_input)
#         if st.session_state.uploaded_file:
#             images, description = process_image_query(uploaded_file=current_file)
#         else:
#             images, description = process_text_query(user_input)
#
#         # Display response
#         display_response(description, images)
#         # uploaded_file = None
#         del session_state['uploaded_file']
#
# pg = st.navigation([st.Page(chat_interface, title="Chat"),
#                     st.Page("gallery.py", title="Gallery"),
#                     st.Page("uploads.py", title="Upload")])
# pg.run()