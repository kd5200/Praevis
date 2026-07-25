"""Local fixture:// URLs for demos without opening SSRF holes."""

from __future__ import annotations

from pathlib import Path

_ALLOWED_DIRS = ("tests/malicious-pages", "tests/fixtures")
_ALLOWED_SUFFIXES = {".html", ".htm", ".txt"}


class FixtureError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _repo_roots() -> list[Path]:
    roots = [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]
    # Prefer known monorepo root if present
    for base in list(roots):
        if (base / "tests" / "malicious-pages").is_dir():
            roots.insert(0, base)
            break
    # Dedupe while preserving order
    seen: set[Path] = set()
    ordered: list[Path] = []
    for root in roots:
        resolved = root.resolve()
        if resolved not in seen:
            seen.add(resolved)
            ordered.append(resolved)
    return ordered


def parse_fixture_name(url: str) -> str:
    """Extract a safe fixture filename from fixture://... URLs."""

    raw = url.strip()
    if raw.lower().startswith("fixture://"):
        raw = raw[len("fixture://") :]
    name = raw.split("?", 1)[0].split("#", 1)[0].strip("/")
    if not name or "/" in name or "\\" in name or ".." in name:
        raise FixtureError("fixture_invalid", "Fixture name must be a single filename")
    suffix = Path(name).suffix.lower()
    if suffix not in _ALLOWED_SUFFIXES:
        raise FixtureError("fixture_invalid", "Fixture must be .html, .htm, or .txt")
    return name


def load_fixture_bytes(url: str) -> tuple[bytes, str, Path]:
    """Load fixture bytes and content-type from the repo test directories."""

    name = parse_fixture_name(url)
    for root in _repo_roots():
        for folder in _ALLOWED_DIRS:
            candidate = (root / folder / name).resolve()
            expected_parent = (root / folder).resolve()
            if expected_parent not in candidate.parents and candidate.parent != expected_parent:
                continue
            if candidate.is_file():
                content_type = "text/plain" if candidate.suffix.lower() == ".txt" else "text/html"
                return candidate.read_bytes(), content_type, candidate
    raise FixtureError("fixture_not_found", f"Unknown fixture: {name}")
