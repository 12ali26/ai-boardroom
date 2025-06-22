from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    openrouter_api_key: str
    database_url: str = "sqlite:///./ai_boardroom.db"  # Default to SQLite
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()

# Test
if __name__ == "__main__":
    print("✅ Config loaded successfully")
    print(f"Database: {settings.database_url}")
    print(f"API Key: {'Set' if settings.openrouter_api_key else 'Missing'}")