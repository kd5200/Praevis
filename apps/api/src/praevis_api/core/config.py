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

    database_url: str = "postgresql+psycopg://praevis:praevis@localhost:15432/praevis"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    celery_task_always_eager: bool = False

    # Readiness probes may skip dependency checks in unit tests.
    ready_check_dependencies: bool = True

    # CORS — comma-separated origins for local dashboard / SDKs
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Fetch / security
    http_timeout_connect_seconds: float = 5.0
    http_timeout_read_seconds: float = 10.0
    http_max_response_bytes: int = 2_097_152
    http_max_redirects: int = 5
    http_user_agent: str = "PraevisSecurityGateway/0.1 (+https://example.local/praevis)"
    http_allowed_content_types: str = "text/html,application/xhtml+xml,text/plain"

    # Artifact storage (local MVP; later object storage)
    artifact_storage_backend: str = "local"
    artifact_storage_path: str = "var/artifacts"

    # Scoring thresholds
    risk_block_threshold: int = 70
    risk_warn_threshold: int = 40

    # Security rules
    security_rules_path: str = "packages/security-rules/rules/catalog.json"

    # Request limits (Phase 5)
    rate_limit_per_minute: int = 60  # 0 disables
    max_request_body_bytes: int = 65_536
    max_url_length: int = 2048


@lru_cache
def get_settings() -> Settings:
    return Settings()
