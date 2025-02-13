from chromadb_config import get_images, configure_db

image_collection, desc_collection = configure_db()

print(get_images('./uploads'))

# results = desc_collection.query(
#         query_texts=["show image"],
#         n_results=3,
#         include=['distances', 'documents', 'metadatas']
#     )
# # print(results['ids'][0])
#
# img_results = image_collection.get(
#     ids = results['ids'][0],
#     include=['uris']
# )

# results = image_collection.query(
#     query_uris = ['uploads\A-clear-close-up-photo-of-a-woman.jpg'],
#     include=['uris']
# )
# print(results['uris'])

# file_path = UPLOAD_DIR / file.filename