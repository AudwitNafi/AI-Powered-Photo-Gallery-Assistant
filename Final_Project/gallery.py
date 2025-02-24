# Gallery Page
import streamlit as st
from utils.chromadb_config import get_images

st.title("📸 Image Gallery")
st.write("Browse all available images.")

all_images = get_images('./uploads')  # Fetch all images
cols = st.columns(4)  # 4 images per row
for idx, img_url in enumerate(all_images):
    with cols[idx % 4]:
        st.image(img_url)