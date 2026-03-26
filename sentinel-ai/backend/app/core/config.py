from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "SentinelAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sentinel"

    # Security Settings
    SECRET_KEY: str = "b881fbd70b8379e213277e698acc14cb9fb09e49710a2a5e283a830248fe0cb2"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    LLAMA_KEY: str = "llx-VhCRAL5lWI2ROwdnCtCgGpmciLVcIhPKMAAKwugKJmqLohbo"
    # CORS Settings
    # CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # MLFlow Settings
    MLFLOW_TRACKING_URI: Optional[str] = None

    # Google AI Settings
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_KEY: Optional[str] = None

    # RAG Settings (Qdrant + Ollama)
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_COLLECTION: str = "sentinelai-security-manual"
    QDRANT_API_KEY: Optional[str] = None
    RAG_SOURCE_PATH: str = "data/processing/Guide-des-Protocoles.md"
    RAG_RETRIEVER_K: int = 20
    RAG_RERANKER_MODEL: str = "BAAI/bge-reranker-base"
    RAG_RERANKER_TOP_N: int = 5
    RAG_CHUNK_SIZE: int = 800
    RAG_CHUNK_OVERLAP: int = 150
    RAG_FORCE_REINDEX: bool = False
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "mistral-nemo"
    OLLAMA_NUM_CTX: int = 2048
    OLLAMA_NUM_PREDICT: int = 256
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    RAG_CONTEXT_DOCS: int = 3
    RAG_MAX_CONTEXT_CHARS: int = 8000
    RAG_ASK_TIMEOUT_SECONDS: int = 120

    # Camera Streaming Settings
    RTSP_HOST_ALIAS: str = "mediamtx"
    OPENCV_FFMPEG_CAPTURE_OPTIONS: str = (
        "rtsp_transport;tcp|max_delay;500000|stimeout;5000000"
    )
    MJPEG_FPS: int = 10
    MJPEG_JPEG_QUALITY: int = 80
    MJPEG_MAX_READ_FAILURES: int = 40
    MJPEG_RECONNECT_DELAY_SECONDS: float = 0.25

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
