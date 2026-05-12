from fastapi import APIRouter

from backend.api.routes import chat, diagnosis, documents, knowledge, products, system, tickets


api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(products.router)
api_router.include_router(knowledge.router)
api_router.include_router(tickets.router)
api_router.include_router(diagnosis.router)
