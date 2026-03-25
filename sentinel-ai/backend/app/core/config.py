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

    # CORS Settings
    # CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # MLFlow Settings
    MLFLOW_TRACKING_URI: Optional[str] = None

    # Google AI Settings
    GOOGLE_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
