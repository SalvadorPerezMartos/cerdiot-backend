# /opt/iot-backend/app/config.py
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent  # /opt/iot-backend


class Settings(BaseSettings):
    # Estos 3 vienen tal cual en tu .env
    APP_NAME: str = "CerdIoT API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"

    # Tu .env usa DATABASE_URL (no SQLALCHEMY_DATABASE_URI)
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
