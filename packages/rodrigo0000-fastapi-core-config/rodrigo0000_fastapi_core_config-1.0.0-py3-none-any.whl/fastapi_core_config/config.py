"""
Configuration management with environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "FastAPI Core")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

# Global settings instance
settings = Settings()
