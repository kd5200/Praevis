"""Worker settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Praevis"
    service_name: str = "praevis-worker"
    log_level: str = "INFO"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    database_url: str = "postgresql+psycopg://praevis:praevis@localhost:15432/praevis"


@lru_cache
def get_settings() -> Settings:
    return Settings()
