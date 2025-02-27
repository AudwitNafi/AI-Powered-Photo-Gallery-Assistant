from fastapi import APIRouter
from api.endpoints import query, query_hybrid, gallery, upload, get_image, chat_upload # Import your endpoint modules
main_router = APIRouter()

main_router.include_router(gallery.router)
main_router.include_router(query.router)
main_router.include_router(query_hybrid.router)
main_router.include_router(upload.router)
main_router.include_router(get_image.router)
main_router.include_router(chat_upload.router)