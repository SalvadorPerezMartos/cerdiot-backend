# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # datos básicos
    app_name: str = "CerdIoT API"
    version: str = "1.0.0"
    environment: str = "production"

    # ==== BASE DE DATOS ====
    # en tu .env tienes DATABASE_URL=postgresql+psycopg2://...
    database_url: str
    # Alembic y tu app a veces esperan este nombre:
    SQLALCHEMY_DATABASE_URI: str | None = None

    # ==== JWT ====
    jwt_secret_key: str  # en .env: JWT_SECRET_KEY=...
    jwt_algorithm: str = "HS256"  # en .env: JWT_ALGORITHM=HS256
    access_token_expire_minutes: int = 60  # en .env: ACCESS_TOKEN_EXPIRE_MINUTES=1440

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # mapeamos nombres en mayúsculas del .env a los de aquí
        env_prefix="",
        case_sensitive=False,
    )

    def get_db_uri(self) -> str:
        # si no nos han puesto SQLALCHEMY_DATABASE_URI, usamos database_url
        return self.SQLALCHEMY_DATABASE_URI or self.database_url


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    # aseguramos que SQLALCHEMY_DATABASE_URI tenga valor
    if not s.SQLALCHEMY_DATABASE_URI:
        s.SQLALCHEMY_DATABASE_URI = s.database_url
    return s


# este es el que importas en el resto de módulos
settings = get_settings()
