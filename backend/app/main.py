from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.chat.ws_routes import router as ws_router
from app.database.database import engine
from app.models import Base
from app.admin import setup_admin

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
    allow_origins=settings.get_allowed_hosts(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# setup admin panel (accessible at /admin)
admin = setup_admin(app, engine)

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