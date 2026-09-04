"""Application Configuration Settings"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Project Info
    PROJECT_NAME: str = "MediKiosk Backend"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/medikiosk_db"
    DATABASE_ECHO: bool = False
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # AI/ML Services
    BHASHINI_API_KEY: str = "your-bhashini-api-key"
    BHASHINI_API_URL: str = "https://api.bhashini.gov.in"
    DEFAULT_LANGUAGE: str = "hi"
    
    # LLM Configuration
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4"
    TEMPERATURE: float = 0.7
    
    # OCR Configuration
    TESSERACT_PATH: str = "/usr/bin/tesseract"
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GCP_PROJECT_ID: Optional[str] = None
    
    # ABDM Configuration
    ABDM_CLIENT_ID: str = ""
    ABDM_CLIENT_SECRET: str = ""
    ABDM_BASE_URL: str = "https://sandbox.abdm.gov.in"
    ABDM_GATEWAY_URL: str = "https://sandbox.ndhm.gov.in"
    
    # HIS Integration
    HIS_API_URL: str = "http://localhost:8000"
    HIS_API_KEY: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Session Management
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_UPLOAD_FILE_SIZE_MB: int = 50
    
    # Feature Flags
    ENABLE_RED_FLAG_DETECTION: bool = True
    ENABLE_AYUSH_MODE: bool = True
    ENABLE_DOCUMENT_PROCESSING: bool = True
    ENABLE_ABDM_INTEGRATION: bool = True
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@medikiosk.app"
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    SENTRY_DSN: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get settings singleton"""
    return Settings()
