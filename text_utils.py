from __future__ import annotations

import html
from typing import Any, Iterable


def escape_html(value: Any) -> str:
    """Escape text for Telegram HTML-safe output."""
    return html.escape(str(value), quote=False)


def bold(value: Any) -> str:
    return f"<b>{escape_html(value)}</b>"


def italic(value: Any) -> str:
    return f"<i>{escape_html(value)}</i>"


def code(value: Any) -> str:
    return f"<code>{escape_html(value)}</code>"


def title(value: Any) -> str:
    return bold(value)


def join_lines(lines: Iterable[str]) -> str:
    return "\n".join(str(line) for line in lines)
