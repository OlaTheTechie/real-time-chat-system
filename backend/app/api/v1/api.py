from fastapi import APIRouter

api_router = APIRouter()

# placeholder for future route includes
# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

@api_router.get("/")
async def api_root():
    return {"message": "Chat Server API v1"}