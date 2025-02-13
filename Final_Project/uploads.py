import streamlit as st
import requests
import io

st.title("📤 Upload Images")

uploaded_file = st.file_uploader("Choose an image to upload...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    # print(files)
    # image_file = io.BytesIO(uploaded_file.getvalue())
    response = requests.post("http://127.0.0.1:8000/upload/", files=files)

    if response.status_code == 200:
        st.success("Image uploaded successfully!")
        st.image(uploaded_file, caption="Uploaded Image")
    else:
        st.error("Failed to upload image.")
