import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
import uuid

IMAGE_FOLDER = './images'
embedding_function = OpenCLIPEmbeddingFunction()
image_loader = ImageLoader()

class ChromaDBManager:
    """
    A class to manage ChromaDB operations for image collection.
    """
    def __init__(self, db_path='../chroma_db', image_collection_name='image'):
        """
        Initializes the ChromaDBManager with a client, embedding function, image loader,
        and sets up image collection.

        Args:
            db_path (str): Path to the ChromaDB persistent storage. Defaults to '../chroma_db'.
            image_collection_name (str): Name of the image collection. Defaults to 'image'.
        """
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_function = OpenCLIPEmbeddingFunction()
        self.image_loader = ImageLoader()
        self.image_collection_name = image_collection_name
        self.image_collection = self._create_image_collection()

    def _create_image_collection(self):
        """
        Creates or gets the image collection in ChromaDB.

        Returns:
            chromadb.Collection: The image collection object.
        """
        return self.client.get_or_create_collection(
            name=self.image_collection_name,
            embedding_function=self.embedding_function,
            data_loader=self.image_loader,
            metadata={"hnsw:space": "cosine"}
        )

    def add_image(self, image_path, metadata):
        """
        Adds an image to the image collection.

        Args:
            image_path (str): Path to the image file.
            metadata (dict): Metadata to associate with the image.

        Returns:
            str: The unique ID of the added image.

        Raises:
            Exception: If adding the image fails.
        """
        try:
            unique_id = str(uuid.uuid4())
            metadata['id'] = unique_id # Ensure 'id' is in metadata
            self.image_collection.add(
                uris = [image_path],
                metadatas=[metadata],
                ids= [unique_id],
            )
            return unique_id
        except Exception as e:
            raise Exception(f"Failed to add image: {str(e)}")