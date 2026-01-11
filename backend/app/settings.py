import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    app_name: str = "SiliconPulse API"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    data_stream_path: str = os.getenv("DATA_STREAM_PATH", "data/stream.jsonl")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
