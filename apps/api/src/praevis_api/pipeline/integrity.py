"""Content integrity helpers (hashes for original and sanitized artifacts)."""

from __future__ import annotations

import hashlib


def sha256_digest(data: bytes | str) -> str:
    """Return a stable ``sha256:<hex>`` digest for bytes or UTF-8 text."""

    if isinstance(data, str):
        payload = data.encode("utf-8")
    else:
        payload = data
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"
