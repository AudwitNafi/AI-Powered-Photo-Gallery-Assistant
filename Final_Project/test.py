from utils.query_parser import extract_keywords
from utils.chromadb_config import configure_db
image_collection, desc_collection = configure_db()
import os

import google.generativeai as genai
from dotenv import load_dotenv
#

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

genai.configure(api_key=API_KEY)
# model = genai.GenerativeModel("gemini-2.0-flash")
# print(get_images('./uploads'))

# results = desc_collection.query(
#         query_texts=["beach"],
#         n_results=3,
#         include=['distances', 'documents', 'metadatas']
#     )
# # print(results['ids'][0])
# ids = results['ids'][0]
#
# img_results = image_collection.get(
#     ids=ids,
# )

# img_results = image_collection.query(
#     query_texts=["beach"],
#     n_results=2,
#     # include=['distances', 'documents', 'metadatas']
#     include=['uris']
# )
# retrieved_uris = img_results['uris'][0]
# # results = image_collection.query(
# #     query_uris = ['uploads\A-clear-close-up-photo-of-a-woman.jpg'],
# #     include=['uris']
# # )
# print(retrieved_uris)
# print(desc_collection.get(include=['metadatas', 'documents'], where={'person_or_entity': 'Cindy'})['ids'][0])
# print(image_collection.get(include=['uris'])['uris'])
# print(desc_collection.get(include=['documents']))
# import os
# print(os.listdir('./uploads'))


print(extract_keywords('Show images of Dhaka'))
# file_path = UPLOAD_DIR / file.filename

# import chromadb
# client = chromadb.PersistentClient(path='./chroma_db')
# # client.delete_collection('image')
# client.delete_collection('image_descriptions')
# from gemini import get_gemini_response
#
# print(get_gemini_response('Hello Gemini!'))

