import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    app_name: str = "SiliconPulse API"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    gemini_fallback_models: list[str] = ["gemini-1.5-pro", "gemini-1.0-pro"]
    data_stream_path: str = os.getenv("DATA_STREAM_PATH", "data/stream.jsonl")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Deduplication & Freshness Settings
    freshness_hours: int = int(os.getenv("FRESHNESS_HOURS", "12"))
    max_events_to_scan: int = int(os.getenv("MAX_EVENTS_TO_SCAN", "500"))
    dedup_enabled: bool = os.getenv("DEDUP_ENABLED", "true").lower() == "true"
    checkpoint_enabled: bool = os.getenv("CHECKPOINT_ENABLED", "true").lower() == "true"
    db_path: str = os.getenv("DB_PATH", "data/siliconpulse.db")
    
    # Pathway Settings
    use_pathway: bool = os.getenv("USE_PATHWAY", "True").lower() == "true"
    pathway_output_path: str = os.getenv("PATHWAY_OUTPUT_PATH", "data/pathway_out.jsonl")
    
    # Perplexity Settings
    perplexity_api_key: str = os.getenv("PERPLEXITY_API_KEY", "")
    perplexity_enabled: bool = os.getenv("PERPLEXITY_ENABLED", "False").lower() == "true"
    perplexity_queries: list[str] = [
        "NVIDIA TSMC contract", 
        "Apple semiconductor supply", 
        "Intel foundry", 
        "ASML EUV", 
        "AI datacenter chips"
    ]

    # X (Twitter) Settings
    x_bearer_token: str = os.getenv("X_BEARER_TOKEN", "")
    x_enabled: bool = os.getenv("X_ENABLED", "False").lower() == "true"
    x_keywords: list[str] = [
        "TSMC", "NVIDIA", "CoWoS", "N2", "EUV", "HBM", "foundry", "chip deal", "acquisition"
    ]
    x_accounts: list[str] = ["nvidia", "tsmc", "intel", "apple", "GoogleAI", "MetaAI"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def resolved_data_path(self) -> Path:
        """Resolve data stream path to absolute path"""
        path = Path(self.data_stream_path)
        if path.is_absolute():
            return path
        # Resolve relative to backend root
        base_dir = Path(__file__).resolve().parent.parent
        return base_dir / path

    @property
    def resolved_pathway_path(self) -> Path:
        """Resolve pathway output path to absolute path"""
        path = Path(self.pathway_output_path)
        if path.is_absolute():
            return path
        base_dir = Path(__file__).resolve().parent.parent
        return base_dir / path

settings = Settings()
