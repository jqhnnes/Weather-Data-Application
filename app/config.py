from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    database_url: str = "postgresql://postgres:postgres@127.0.0.1:55432/weather"
    
    # Legacy settings (no longer used, kept for backwards compatibility)
    poll_interval_minutes: int = 30  # Not used - each location has its own interval
    default_location: str = "Berlin,DE"  # Not used - locations are user-specific
    
    # JWT Settings
    secret_key: str = "your-secret-key-change-in-production"  # Should be in .env
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

