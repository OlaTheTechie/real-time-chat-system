from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.chat.ws_routes import router as ws_router
from app.database.database import engine
from app.models import Base

# create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A realtime chat server built with FastAPI",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# set up cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include api router
app.include_router(api_router, prefix=settings.API_V1_STR)

# include websocket router
app.include_router(ws_router)

@app.get("/")
async def root():
    return {"message": "Realtime Chat Server API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}