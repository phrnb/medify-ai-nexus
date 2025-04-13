
from pydantic_settings import BaseSettings
from typing import List, Optional, Union
import secrets
from pathlib import Path
import os

class Settings(BaseSettings):
    # API configuration
    API_V1_STR: str = "/api/v1"
    APP_NAME: str = "Medify AI Nexus"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    
    # CORS
    FRONTEND_URL: str = "http://localhost:8080"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Email
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_PORT: Optional[int] = None
    MAIL_SERVER: Optional[str] = None
    MAIL_TLS: bool = False
    MAIL_SSL: bool = True
    
    # File storage
    UPLOAD_DIR: Path = Path("static/uploads")
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/dicom"]
    
    # Neural Network
    NN_SERVICE_URL: str = "http://localhost:5000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create upload directories if they don't exist
def create_upload_dirs(settings: Settings):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR / "images", exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR / "reports", exist_ok=True)
    os.makedirs("static/temp", exist_ok=True)

settings = Settings()
create_upload_dirs(settings)
