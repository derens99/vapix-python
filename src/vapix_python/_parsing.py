"""Internal helpers for parsing VAPIX response bodies."""

from __future__ import annotations


def parse_key_value(text: str) -> dict[str, str]:
    """Parse a VAPIX ``key=value`` line response into a dict."""
    values: dict[str, str] = {}
    for line in text.splitlines():
        key, sep, value = line.partition("=")
        if sep:
            values[key.strip()] = value.strip()
    return values
