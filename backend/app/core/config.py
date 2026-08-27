import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "CineMatch AI"
    ENV: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # API Keys
    TMDB_API_KEY: str = ""

    # Keep the default deployment lightweight enough for free hosting. Set this
    # to True only on an instance with enough RAM for PyTorch/SentenceTransformers.
    ENABLE_SEMANTIC_MODEL: bool = False
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    PROCESSED_DATA_DIR: str = os.path.join(DATA_DIR, "processed")
    MODEL_DIR: str = os.path.join(BASE_DIR, "backend", "app", "model_artifacts")
    
    # Recommender Weights (Warm User)
    WARM_USER_WEIGHTS: Dict[str, float] = {
        "content": 0.30,
        "collaborative": 0.25,
        "semantic": 0.20,
        "genre": 0.10,
        "quality": 0.10,
        "popularity": 0.05
    }
    
    # Recommender Weights (Cold Start / New User)
    COLD_START_WEIGHTS: Dict[str, float] = {
        "content": 0.35,
        "collaborative": 0.00,  # No collaborative signal for cold start
        "semantic": 0.30,
        "genre": 0.20,
        "quality": 0.10,
        "popularity": 0.05
    }
    
    # Recommender Weights (Sparse History User)
    SPARSE_HISTORY_WEIGHTS: Dict[str, float] = {
        "content": 0.40,
        "collaborative": 0.10,  # Weak collaborative signal
        "semantic": 0.25,
        "genre": 0.15,
        "quality": 0.07,
        "popularity": 0.03
    }
    
    # Diversity (MMR) Lambda settings
    DIVERSITY_LAMBDA: Dict[str, float] = {
        "focused": 0.0,
        "balanced": 0.5,
        "exploratory": 0.85
    }

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure model directory exists
os.makedirs(settings.MODEL_DIR, exist_ok=True)
