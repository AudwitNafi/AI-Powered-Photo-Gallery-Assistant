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


# print(extract_keywords('Show images of Dhaka'))
# file_path = UPLOAD_DIR / file.filename

# print(image_collection.get(where={"$and":[{"person_or_entity": "Ayush"},{"location":"Lalmatia"}]}))
# import chromadb
# client = chromadb.PersistentClient(path='./chroma_db')
# # client.delete_collection('image')
# client.delete_collection('image_descriptions')
# from gemini import get_gemini_response
#
# print(get_gemini_response('Hello Gemini!'))

filtered_ids = ['989130a3-329d-4fac-aa77-51846c106e98', 'f5ae8d2f-f7bb-448e-8e1c-621b1e1802cb', 'ec8c2429-f612-4f59-a4b2-91c05468e2cf']

results = desc_collection.query(
    query_texts=['show images of Ayush'],
    n_results=3,
    where={"id": {"$in": filtered_ids}},       ##doesn't work
    include=['metadatas', 'documents']
)
print(f"Filtered ids: {results['ids'][0]}")

