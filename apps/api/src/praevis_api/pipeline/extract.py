"""HTML extraction and sanitization (no JavaScript execution)."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Comment, Tag
from bs4.element import NavigableString

from praevis_api.pipeline.types import ExtractedContent

_EVENT_ATTR = re.compile(r"^on", re.I)
_UNSAFE_SCHEMES = {"javascript", "vbscript", "data"}


def _attr_str(tag: Tag, name: str) -> str:
    attrs = getattr(tag, "attrs", None)
    if not attrs:
        return ""
    value = attrs.get(name)
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value)


def _is_hidden(tag: Tag) -> bool:
    if getattr(tag, "attrs", None) is None:
        return False
    style = _attr_str(tag, "style").lower().replace(" ", "")
    if "display:none" in style or "visibility:hidden" in style or "opacity:0" in style:
        return True
    if tag.get("hidden") is not None:
        return True
    aria = _attr_str(tag, "aria-hidden").lower()
    if aria == "true":
        return True
    cls = _attr_str(tag, "class").lower()
    if "hidden" in cls or "sr-only" in cls or visually_hidden_hack(cls):
        return True
    return False


def visually_hidden_hack(cls: str) -> bool:
    return "visually-hidden" in cls or "invisible" in cls


def _sanitize_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value.strip())
    if parsed.scheme and parsed.scheme.lower() in _UNSAFE_SCHEMES:
        return None
    return value


def sanitize_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "lxml")
    for tag in soup(["script", "iframe", "object", "embed", "form", "link", "meta", "base"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in list(soup.find_all(True)):
        if not isinstance(tag, Tag):
            continue
        # Decomposed / malformed nodes can have attrs=None on some parsers.
        if getattr(tag, "attrs", None) is None:
            continue
        if _is_hidden(tag):
            tag.decompose()
            continue
        attrs = dict(tag.attrs)
        for attr, value in attrs.items():
            if _EVENT_ATTR.match(attr) or attr.lower() in {"srcdoc"}:
                del tag.attrs[attr]
                continue
            if attr.lower() in {"href", "src", "xlink:href"}:
                if isinstance(value, list):
                    value = value[0] if value else ""
                cleaned = _sanitize_url(str(value))
                if cleaned is None:
                    del tag.attrs[attr]
                else:
                    tag.attrs[attr] = cleaned
    body = soup.body
    return str(body) if body else str(soup)


def extract_content(raw: bytes, content_type: str) -> ExtractedContent:
    text_body = raw.decode("utf-8", errors="replace")
    if content_type.startswith("text/plain"):
        return ExtractedContent(
            title=None, text=text_body.strip(), html="", language=None, metadata={}
        )

    soup = BeautifulSoup(text_body, "lxml")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    # Collect visible text from a sanitized clone
    sanitized = sanitize_html(text_body)
    clean_soup = BeautifulSoup(sanitized, "lxml")
    for tag in clean_soup(["script", "style", "noscript"]):
        tag.decompose()

    blocks: list[str] = []
    for el in clean_soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "article"]
    ):
        t = el.get_text(" ", strip=True)
        if t:
            blocks.append(t)
    if not blocks:
        blocks.append(clean_soup.get_text(" ", strip=True))

    text = "\n".join(blocks)
    # Collapse excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    metadata: dict[str, Any] = {}
    if soup.html and soup.html.get("lang"):
        metadata["html_lang"] = soup.html.get("lang")

    language = metadata.get("html_lang")
    return ExtractedContent(
        title=title,
        text=text,
        html=sanitized,
        language=str(language) if language else None,
        metadata=metadata,
    )


def find_hidden_text_snippets(raw_html: str) -> list[str]:
    """Return text found in hidden nodes (for detectors)."""

    soup = BeautifulSoup(raw_html, "lxml")
    snippets: list[str] = []
    for tag in soup.find_all(True):
        if isinstance(tag, Tag) and _is_hidden(tag):
            t = tag.get_text(" ", strip=True)
            if t:
                snippets.append(t)
    # Zero-width / invisible unicode in any text node
    for node in soup.find_all(string=True):
        if isinstance(node, NavigableString) and re.search(
            r"[\u200b\u200c\u200d\ufeff]", str(node)
        ):
            snippets.append(str(node))
    return snippets
