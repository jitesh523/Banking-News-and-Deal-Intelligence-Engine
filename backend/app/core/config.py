from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017/banking_news_engine"
    mongodb_db_name: str = "banking_news_engine"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # NewsAPI
    news_api_key: str = ""
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = "your-secret-key-change-this"
    api_rate_limit: int = 100
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    # Environment
    environment: str = "development"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
