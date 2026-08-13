"""HTML extraction and sanitization (no JavaScript execution)."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Comment, Tag
from bs4.element import NavigableString

from praevis_api.pipeline.types import ExtractedContent, SanitizationTransformation

_EVENT_ATTR = re.compile(r"^on", re.I)
_UNSAFE_SCHEMES = {"javascript", "vbscript", "data"}

_ACTIVE_CONTENT_TAGS = frozenset(
    {"script", "iframe", "object", "embed", "form", "link", "meta", "base"}
)


class _TransformationRecorder:
    """Aggregate sanitization operations into stable receipt records."""

    def __init__(self) -> None:
        self._counts: dict[tuple[str, str, str], int] = {}

    def record(self, *, type: str, target: str, reason: str, count: int = 1) -> None:
        if count <= 0:
            return
        key = (type, target, reason)
        self._counts[key] = self._counts.get(key, 0) + count

    def to_list(self) -> list[SanitizationTransformation]:
        items = [
            SanitizationTransformation(type=t, target=target, reason=reason, count=count)
            for (t, target, reason), count in sorted(self._counts.items())
        ]
        return items


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


def sanitize_html_with_transformations(
    raw_html: str,
) -> tuple[str, list[SanitizationTransformation]]:
    """Sanitize HTML and return cleaned markup plus transformation records."""

    recorder = _TransformationRecorder()
    soup = BeautifulSoup(raw_html, "lxml")

    for tag in soup(list(_ACTIVE_CONTENT_TAGS)):
        tag_name = tag.name or "unknown"
        tag.decompose()
        recorder.record(
            type="removed_element",
            target=tag_name,
            reason="active_content_not_allowed",
        )

    for _comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        _comment.extract()
        recorder.record(
            type="removed_comment",
            target="html_comment",
            reason="html_comment_removed",
        )

    for tag in list(soup.find_all(True)):
        if not isinstance(tag, Tag):
            continue
        if getattr(tag, "attrs", None) is None:
            continue
        if _is_hidden(tag):
            tag_name = tag.name or "unknown"
            tag.decompose()
            recorder.record(
                type="removed_element",
                target=tag_name,
                reason="hidden_instruction_removal",
            )
            continue
        attrs = dict(tag.attrs)
        for attr, value in attrs.items():
            if _EVENT_ATTR.match(attr) or attr.lower() in {"srcdoc"}:
                del tag.attrs[attr]
                recorder.record(
                    type="removed_attribute",
                    target=attr.lower(),
                    reason="unsafe_attribute_removed",
                )
                continue
            if attr.lower() in {"href", "src", "xlink:href"}:
                if isinstance(value, list):
                    value = value[0] if value else ""
                cleaned = _sanitize_url(str(value))
                if cleaned is None:
                    del tag.attrs[attr]
                    recorder.record(
                        type="removed_unsafe_url",
                        target=attr.lower(),
                        reason="unsafe_link_scheme",
                    )
                else:
                    tag.attrs[attr] = cleaned

    body = soup.body
    sanitized = str(body) if body else str(soup)
    return sanitized, recorder.to_list()


def sanitize_html(raw_html: str) -> str:
    sanitized, _transformations = sanitize_html_with_transformations(raw_html)
    return sanitized


def extract_content(raw: bytes, content_type: str) -> ExtractedContent:
    text_body = raw.decode("utf-8", errors="replace")
    if content_type.startswith("text/plain"):
        return ExtractedContent(
            title=None,
            text=text_body.strip(),
            html="",
            language=None,
            metadata={},
            transformations=[],
        )

    soup = BeautifulSoup(text_body, "lxml")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    sanitized, transformations = sanitize_html_with_transformations(text_body)
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
        transformations=transformations,
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
    for node in soup.find_all(string=True):
        if isinstance(node, NavigableString) and re.search(
            r"[\u200b\u200c\u200d\ufeff]", str(node)
        ):
            snippets.append(str(node))
    return snippets
