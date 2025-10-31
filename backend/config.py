"""Configuration management for the test prep agent."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
from pydantic import field_validator
import os
from pathlib import Path

# Get the backend directory path (where .env file should be)
backend_dir = Path(__file__).parent
env_path = backend_dir / ".env"

# Load environment variables from .env file
# Explicitly specify the path to ensure we load from the correct location
loaded = load_dotenv(dotenv_path=env_path, override=True)

# Debug: Check if .env file was found and what API key is loaded
if loaded:
    api_key_from_env = os.getenv("OPENAI_API_KEY")
    if api_key_from_env:
        # Show first 10 and last 4 characters for security
        masked_key = f"{api_key_from_env[:10]}...{api_key_from_env[-4:]}" if len(api_key_from_env) > 14 else "***"
        print(f"✅ .env file loaded. API key found (length: {len(api_key_from_env)}, preview: {masked_key})")
    else:
        print("⚠️  .env file loaded but OPENAI_API_KEY not found in environment variables")
else:
    print(f"⚠️  .env file not found at {env_path}")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    OPENAI_API_KEY: str
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = str(env_path)  # Use explicit path
        case_sensitive = True
    
    @field_validator('OPENAI_API_KEY')
    @classmethod
    def validate_and_strip_api_key(cls, v: str) -> str:
        """Strip whitespace and validate API key format."""
        if not v:
            raise ValueError("OPENAI_API_KEY cannot be empty")
        
        # Strip whitespace
        api_key = v.strip()
        
        # Validate format
        if not api_key.startswith('sk-'):
            print(f"⚠️  Warning: API key doesn't start with 'sk-' (first 3 chars: {api_key[:3]})")
        
        if len(api_key) < 20:
            raise ValueError(f"OPENAI_API_KEY seems too short (length: {len(api_key)}). Please check your .env file.")
        
        return api_key


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    # Additional validation after initialization
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is missing. Please check your .env file.")
    return settings

