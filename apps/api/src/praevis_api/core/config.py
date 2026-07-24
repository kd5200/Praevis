"""Application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-based configuration for the API."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Praevis"
    service_name: str = "praevis-api"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    log_json: bool = True

    database_url: str = "postgresql+psycopg://praevis:praevis@localhost:5432/praevis"
    redis_url: str = "redis://localhost:6379/0"

    # Readiness probes may skip dependency checks in unit tests.
    ready_check_dependencies: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
