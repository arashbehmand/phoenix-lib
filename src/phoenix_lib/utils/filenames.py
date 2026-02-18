"""Filename sanitization helpers."""

from __future__ import annotations

import os
import re
import unicodedata

_UNICODE_DASHES_RE = re.compile(r"[‐‑‒–—―−]+")
_SEPARATORS_RE = re.compile(r"[\s_]+")
_INVALID_BASE_CHAR_RE = re.compile(r"[^A-Za-z0-9.-]+")
_INVALID_EXT_CHAR_RE = re.compile(r"[^A-Za-z0-9]+")
_MULTI_DASH_RE = re.compile(r"-+")


def _ascii_normalize(value: str) -> str:
    value = _UNICODE_DASHES_RE.sub("-", value)
    normalized = unicodedata.normalize("NFKD", value)
    return normalized.encode("ascii", "ignore").decode("ascii")


def sanitize_filename_component(value: str, fallback: str = "file") -> str:
    """Sanitize a single filename component using dash-separated words."""
    normalized = _ascii_normalize(value or "")
    normalized = _SEPARATORS_RE.sub("-", normalized)
    normalized = _INVALID_BASE_CHAR_RE.sub("-", normalized)
    normalized = _MULTI_DASH_RE.sub("-", normalized)
    normalized = normalized.strip("-.")
    return normalized or fallback


def sanitize_filename(filename: str, fallback: str = "download") -> str:
    """Sanitize a filename for cross-platform use and HTTP headers.

    Rules:
    - Converts unicode punctuation to ASCII where possible.
    - Converts spaces and underscores to dashes.
    - Collapses consecutive dashes.
    - Removes unsupported characters.
    """
    raw = (filename or "").strip()
    base, ext = os.path.splitext(raw)

    safe_base = sanitize_filename_component(base or raw, fallback=fallback)
    safe_ext = _ascii_normalize(ext)
    safe_ext = _INVALID_EXT_CHAR_RE.sub("", safe_ext.lstrip("."))

    if safe_ext:
        return f"{safe_base}.{safe_ext.lower()}"
    return safe_base
