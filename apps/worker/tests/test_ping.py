"""Worker unit tests."""

from praevis_worker import __version__
from praevis_worker.celery_app import ping


def test_package_version() -> None:
    assert __version__ == "0.1.0"


def test_ping_task_body() -> None:
    # Call the underlying function directly (no broker required).
    result = ping()
    assert result["status"] == "ok"
    assert result["service"] == "praevis-worker"
