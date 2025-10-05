"""
Configuration settings for the BharatAce application.
Uses Pydantic's BaseSettings to manage environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Create a .env file in the backend directory with the required values.
    """
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None  # For admin operations (seeding, migrations)
    SUPABASE_JWT_SECRET: str  # Required for JWT token verification
    
    # Google AI Configuration
    GOOGLE_API_KEY: str
    
    # Optional Application Configuration
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    # Security Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for development
    
    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
