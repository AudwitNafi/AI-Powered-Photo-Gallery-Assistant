import chromadb
import os
import glob
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader

IMAGE_FOLDER = './images'

# Initialize ChromaDB client
client = chromadb.PersistentClient(path='./chroma_db')

embedding_function = OpenCLIPEmbeddingFunction()
image_loader = ImageLoader()

# Creating Image Collection
image_collection = client.get_or_create_collection(
    name='image',
    embedding_function=embedding_function,
    data_loader=image_loader)


# Get the uris to the images
def get_images(folder_path):
    return [f for f in glob.glob(f"{folder_path}/*.jpg") if os.path.isfile(f)]

# Get the uris to the images, excluding directories
image_uris = sorted(get_images('./images'))
ids = [str(i) for i in range(len(image_uris))]

image_collection.add(ids=ids, uris=image_uris)

# Counting items in a collection
item_count = image_collection.count()
print(f"Count of items in collection: {item_count}")



#
# # Get items from the collection
# # items = collection.get()
# # print(items)

# Or we can use the peek method
# image_collection.peek(limit=5)