from fastapi import APIRouter
from app.auth.routes import router as auth_router
from app.api.v1.admin import router as admin_router
from app.chat.routes import router as chat_router

api_router = APIRouter()

# include authentication routes
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# include chat routes (protected with JWT)
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])

# include admin routes
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])

@api_router.get("/")
async def api_root():
    return {"message": "Chat Server API v1"}