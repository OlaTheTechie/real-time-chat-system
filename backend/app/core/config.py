from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Realtime Chat Server"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # database
    DATABASE_URL: str = "sqlite:///./chatserver.db"
    
    # redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # jwt
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # cors
    ALLOWED_HOSTS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8501"
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle comma-separated string
            return v.split(",") if "," in v else [v]
        elif isinstance(v, list):
            # Already a list
            return v
        return [str(v)]
    
    def get_allowed_hosts(self) -> List[str]:
        """Get ALLOWED_HOSTS as a list"""
        if isinstance(self.ALLOWED_HOSTS, str):
            return [i.strip() for i in self.ALLOWED_HOSTS.split(",")]
        return [i.strip() for i in self.ALLOWED_HOSTS]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()