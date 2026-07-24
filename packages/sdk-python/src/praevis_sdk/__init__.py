"""Praevis Python SDK stub."""

from __future__ import annotations

__version__ = "0.1.0"


class PraevisClient:
    """Minimal client placeholder. Scan methods arrive in later phases."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict[str, str]:
        import httpx

        response = httpx.get(f"{self.base_url}/health", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        return {"status": str(data["status"]), "service": str(data["service"])}
