from PIL import Image
from utils.chromadb_config import configure_db
from utils.query_parser import extract_keywords, extract_keywords_from_image, determine_requested_attribute
image_collection = configure_db()
import os
import google.generativeai as genai
from dotenv import load_dotenv
# from utils.generate_description import generate_image_caption

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")
#
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
SIMILARITY_THRESHOLD = 0.5
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
#     query_texts=["images of cats"],
#     include=['distances', 'documents', 'metadatas']
#     # include=['uris']
# )
# print(img_results['distances'])
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

# filtered_ids = ['989130a3-329d-4fac-aa77-51846c106e98', 'f5ae8d2f-f7bb-448e-8e1c-621b1e1802cb', 'ec8c2429-f612-4f59-a4b2-91c05468e2cf']
#
# results = desc_collection.query(
#     query_texts=['show images of Ayush'],
#     n_results=3,
#     where={"id": {"$in": filtered_ids}},       ##doesn't work
#     include=['metadatas', 'documents']
# )
# print(f"Filtered ids: {results['ids'][0]}")

# print(image_collection.count())

# print(image_collection.get(include=['uris', 'metadatas']))
# results = image_collection.query(
#     query_uris=['D:\Audwit_Anam_YSD_Repo\YSD_B4_AI_Audwit\Final_Project\query_images\e5.jpg'],
#     include=['distances', 'metadatas', 'uris']
# )

# ids = results['ids'][0]
# distances = results['distances'][0]
# uris = results['uris'][0]
# filtered_results = [uri for uri, distance in zip(uris, distances) if distance <= SIMILARITY_THRESHOLD]
#
# print(filtered_results)
#
desc_results = image_collection.query(
    query_texts = "find images of snake",
    include=['metadatas', 'distances']
)
print(desc_results['distances'])
print(desc_results['metadatas'])
# # #
# print(desc_results['metadatas'])
# image = Image.open('./uploads/07395ee3-b6be-4511-9966-82f22b2cc424.jpg')
# print(generate_image_caption(image))
# print(extract_keywords_from_image(image))
# print(determine_requested_attribute('Show me images from Thailand trip 2021 having similar color and ambience'))
# chat = model.start_chat()
# response = chat.send_message("Good day fine chatbot")
# print(response.text)
# query_filter = []
# metadata_count = 0
# image = Image.open('./uploads/0fb15fac-cc1a-4467-95b8-43d5e290e017.jpg')
# image_keywords = extract_keywords_from_image(image)
# # print(image_keywords)
#
# keywords = extract_keywords('Show me images of anything other than cat')
# print(keywords)

# requested_attributes = determine_requested_attribute('Show me images from Thailand trip 2021 having similar color and ambience')
# metadata_list = ['date', 'month', 'year', 'location', 'person_or_entity', 'event']
# for key in metadata_list:
#     if key in keywords:
#         query_filter.append({key: keywords[key]})
#         metadata_count += 1
# print(f"requested_attributes: {requested_attributes}")
# for attribute in requested_attributes:
#     if attribute in image_keywords:
#         query_filter.append({attribute: image_keywords[attribute]})
# # #
# print(query_filter)