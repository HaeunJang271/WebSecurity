"""
Application configuration settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = Field(default="SecureScan", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=True, alias="DEBUG")  # True for development
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    
    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    
    # Database (SQLite for easy testing, PostgreSQL for production)
    database_url: str = Field(
        default="sqlite+aiosqlite:///./securescan.db",
        alias="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # JWT
    jwt_secret_key: str = Field(default="jwt-secret-change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # OWASP ZAP
    zap_api_key: str = Field(default="", alias="ZAP_API_KEY")
    zap_proxy_host: str = Field(default="localhost", alias="ZAP_PROXY_HOST")
    zap_proxy_port: int = Field(default=8080, alias="ZAP_PROXY_PORT")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()

