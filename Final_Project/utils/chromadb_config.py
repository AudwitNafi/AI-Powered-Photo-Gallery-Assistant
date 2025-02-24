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
    # client = chromadb.Client()
    # Creating Image Collection
    image_collection = client.get_or_create_collection(
        # image_collection = client.create_collection(
        name='image',
        embedding_function=embedding_function,
        data_loader=image_loader,
        metadata={"hnsw:space": "cosine"})

    # Defining Description Collection
    desc_collection = client.get_or_create_collection(
    # desc_collection = client.create_collection(
        name='image_descriptions',
        metadata={"hnsw:space": "cosine"}
    )
    return image_collection, desc_collection

# Get the uris to the images
# def get_images(folder_path):
#     return [f for f in glob.glob(f"{folder_path}/*.jpg") if os.path.isfile(f)]

def get_images(folder_path):
    return glob.glob(f"{folder_path}/*")

# Get the uris to the images, excluding directories
# image_uris = sorted(get_images('./uploaded_images'))
# ids = [str(i) for i in range(len(image_uris))]

# image_collection.add(ids=ids, uris=image_uris)

def add_image(image_path, image_collection, metadata):
    unique_id = str(uuid.uuid4())
    metadata['id'] = unique_id
    image_collection.add(
        uris = [image_path],
        metadatas=[metadata],
        ids= [unique_id],
    )
    return unique_id

def add_description(description, desc_collection, image_id, metadata):
    desc_collection.add(
        documents = [description],
        metadatas = [metadata],
        ids= [image_id],
    )


#
# Get items from the collection
# items = image_collection.get()
# print(f"From chroma_db file: {items}")

# Or we can use the peek method
# image_collection.peek(limit=5)
# Counting items in a collection
# item_count = image_collection.count()
# print(f"Count of items in collection: {item_count}")
