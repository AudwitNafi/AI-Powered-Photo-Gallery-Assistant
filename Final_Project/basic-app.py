# Import the Streamlit library
import streamlit as st
import glob
from gemini import get_gemini_response

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Write a simple message to the app's webpage
st.title('Conversational Memory Bot')
st.write('AI-Powered Photo Gallery Assistant')
st.image('./images/0x0.jpg')

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your message...")


if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get Gemini response using the chat conversation
    bot_reply = get_gemini_response(user_input)

    # Add bot response to history
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)


#### Display 40 images from images directory in a grid ####
# def get_images(folder_path):
#     return glob.glob(f"{folder_path}/*.jpg")
# image_paths = get_images('./images')
# image_paths.sort()
# num_rows = len(image_paths[:40])//4
# num_cols = 4
# for i in range(num_rows + 1):  # Handle remaining images
#     cols = st.columns(num_cols)
#     for j in range(num_cols):
#         index = i * num_cols + j
#         if index < len(image_paths):
#             with cols[j]:
#                 # image = Image.open(image_paths[index])
#                 st.image(image_paths[index])