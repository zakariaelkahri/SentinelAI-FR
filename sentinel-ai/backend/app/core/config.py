from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "SentinelAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sentinelai"

    # Security Settings
    SECRET_KEY: str = "b881fbd70b8379e213277e698acc14cb9fb09e49710a2a5e283a830248fe0cb2"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    LLAMA_KEY: str = "llx-VhCRAL5lWI2ROwdnCtCgGpmciLVcIhPKMAAKwugKJmqLohbo"
    # CORS Settings
    # CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # MLFlow Settings
    MLFLOW_TRACKING_URI: Optional[str] = None

    # Google AI Settings
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_KEY: Optional[str] = None

    # RAG Settings (Qdrant + Ollama)
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_COLLECTION: str = "sentinelai-rag"
    QDRANT_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
