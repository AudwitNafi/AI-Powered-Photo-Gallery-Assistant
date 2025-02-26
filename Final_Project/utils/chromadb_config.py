import chromadb
import os
import glob
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
from PIL import Image
import uuid

IMAGE_FOLDER = './images'
embedding_function = OpenCLIPEmbeddingFunction()
image_loader = ImageLoader()

def configure_db():
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path='../chroma_db')
    # Creating Image Collection
    image_collection = client.get_or_create_collection(
        name='image',
        embedding_function=embedding_function,
        data_loader=image_loader,
        metadata={"hnsw:space": "cosine"})
    desc_collection = client.get_or_create_collection(
        name='image_descriptions',
        metadata={"hnsw:space": "cosine"}
    )
    return image_collection

def get_images(folder_path):
    return glob.glob(f"{folder_path}/*")

def add_image(image_path, image_collection, metadata):
    try:
        unique_id = str(uuid.uuid4())
        metadata['id'] = unique_id
        image_collection.add(
            uris = [image_path],
            metadatas=[metadata],
            ids= [unique_id],
        )
        return unique_id
    except Exception as e:
        raise Exception(f"Failed to add image: {str(e)}")