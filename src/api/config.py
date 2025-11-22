# -*- coding: utf-8 -*-
"""
API Configuration

Production-grade configuration management for Smart-Trade API.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """API configuration settings."""
    
    # API Metadata
    API_VERSION: str = "3.0.0"
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Smart-Trade API"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_MAX_CONNECTIONS: int = 100
    
    # Cache Configuration
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # seconds (5 minutes)
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/api.log"
    
    # Security
    API_KEY_ENABLED: bool = False
    API_KEY_HEADER: str = "X-API-Key"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
