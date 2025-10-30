"""
Configuration management using Pydantic Settings.
Loads environment variables and provides typed configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Adiq
    adiq_base_url: str
    adiq_client_id: str
    adiq_client_secret: str
    
    # Environment
    env: str = "development"
    log_level: str = "INFO"
    
    # Security
    jwt_secret: str
    api_key_header: str = "X-API-Key"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000


# Global settings instance
settings = Settings()
