"""Configuration management for CarFinder application."""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

def load_config() -> Dict[str, Any]:
    """Load application configuration from environment variables."""
    
    config = {
        # Ollama Configuration
        "ollama_host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.1"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        
        # Database Configuration
        "database_path": os.getenv("DATABASE_PATH", "data/carfinder.db"),
        
        # Search Configuration
        "max_results": int(os.getenv("MAX_RESULTS", "20")),
        "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", "0.7")),
        "rerank_top_k": int(os.getenv("RERANK_TOP_K", "10")),
        
        # UI Configuration
        "streamlit_theme": os.getenv("STREAMLIT_THEME", "light"),
        "debug_mode": os.getenv("DEBUG_MODE", "false").lower() == "true",
        
        # Optional APIs
        "nhtsa_api_key": os.getenv("NHTSA_API_KEY"),
        "recalls_api_endpoint": os.getenv("RECALLS_API_ENDPOINT", "https://api.nhtsa.gov/recalls/recallsByVehicle"),
        
        # Cloud LLM Fallback
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        
        # Vehicle Data APIs
        "auto_dev_api_key": os.getenv("AUTO_DEV_API_KEY"),
        "autotrader_api_key": os.getenv("AUTOTRADER_API_KEY"),
        "cargurus_api_key": os.getenv("CARGURUS_API_KEY"),
        "cars_com_rate_limit": int(os.getenv("CARS_COM_RATE_LIMIT", "1")),
        "enable_live_data": os.getenv("ENABLE_LIVE_DATA", "true").lower() == "true",
        "cache_duration_hours": int(os.getenv("CACHE_DURATION_HOURS", "2")),
        "max_results_per_source": int(os.getenv("MAX_RESULTS_PER_SOURCE", "20")),
        "default_search_radius": int(os.getenv("DEFAULT_SEARCH_RADIUS", "50")),
        
        # Logging
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "log_file": os.getenv("LOG_FILE", "logs/carfinder.log"),
        
        # Project paths
        "project_root": Path(__file__).parent.parent,
        "data_dir": Path(__file__).parent.parent / "data",
        "models_dir": Path(__file__).parent.parent / "models",
    }
    
    # Ensure directories exist
    config["data_dir"].mkdir(exist_ok=True)
    
    if config["log_file"]:
        log_dir = Path(config["log_file"]).parent
        log_dir.mkdir(exist_ok=True)
    
    return config

def get_database_url(config: Dict[str, Any]) -> str:
    """Get the SQLite database URL."""
    db_path = Path(config["database_path"])
    if not db_path.is_absolute():
        db_path = config["project_root"] / db_path
    
    return f"sqlite:///{db_path}"