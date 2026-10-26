"""Plain-text helpers for Telegram messages.

MoodBloom uses Python strings and Telegram inline keyboards. These helpers no
longer emit HTML tags, so message text remains readable without HTML parsing.
"""
from __future__ import annotations

from typing import Any, Iterable


def escape_html(value: Any) -> str:
    """Backward-compatible name; returns safe plain text without HTML entities."""
    return str(value)


def bold(value: Any) -> str:
    """Backward-compatible name; plain text has no HTML formatting tags."""
    return str(value)


def italic(value: Any) -> str:
    return str(value)


def code(value: Any) -> str:
    return str(value)


def title(value: Any) -> str:
    return str(value)


def join_lines(lines: Iterable[str]) -> str:
    return "\n".join(str(line) for line in lines)
