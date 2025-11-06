import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Realtime Chat Server"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./chatserver.db"
    )
    
    # redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # jwt
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "your-secret-key-change-this-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # cors
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"


settings = Settings()