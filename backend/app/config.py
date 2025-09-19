# backend/app/config.py (Fixed for Pydantic V2)
import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API Keys
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API key")
    openweather_api_key: Optional[str] = Field(default=None, description="OpenWeather API key")
    
    # Weaviate Configuration
    weaviate_url: str = Field(default="http://localhost:8080", description="Weaviate URL")
    weaviate_api_key: Optional[str] = Field(default=None, description="Weaviate API key")
    
    # Location Settings
    default_state: str = Field(default="Tamil Nadu", description="Default state")
    default_country: str = Field(default="India", description="Default country")
    
    # External APIs
    overpass_api_url: str = Field(default="https://overpass-api.de/api/interpreter", description="Overpass API URL")
    nominatim_base_url: str = Field(default="https://nominatim.openstreetmap.org", description="Nominatim base URL")
    
    # Rate Limiting
    api_rate_limit_per_minute: int = Field(default=60, description="API rate limit per minute")
    external_api_timeout: int = Field(default=30, description="External API timeout in seconds")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    
    # Cache Settings
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }

# Global settings instance
settings = Settings()

# Validate required settings
def validate_settings():
    """Validate critical settings"""
    if not settings.gemini_api_key:
        print("⚠️ Warning: GEMINI_API_KEY not set. AI reasoning will be limited.")
    
    if settings.debug:
        print("🔧 Debug mode enabled")
    
    print(f"📍 Default location: {settings.default_state}, {settings.default_country}")
    print(f"🔗 Weaviate URL: {settings.weaviate_url}")

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'root': {
        'level': settings.log_level,
        'handlers': ['default'],
    },
}