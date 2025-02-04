import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader

IMAGE_FOLDER = './images'

# Initialize ChromaDB client
client = chromadb.PersistentClient(path='./chroma_db')

embedding_function = OpenCLIPEmbeddingFunction()
image_loader = ImageLoader()

collection = client.get_or_create_collection(
    name='multimodal_collection',
    embedding_function=embedding_function,
    data_loader=image_loader)

# Counting items in a collection
item_count = collection.count()
print(f"Count of items in collection: {item_count}")

# Get the uris to the images
image_uris = sorted([os.path.join(IMAGE_FOLDER, image_name) for image_name in os.listdir(IMAGE_FOLDER)])
ids = [str(i) for i in range(len(image_uris))]

collection.add(ids=ids, uris=image_uris)

# Get items from the collection
# items = collection.get()
# print(items)

# Or we can use the peek method
collection.peek(limit=5)