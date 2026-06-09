"""Lazy loading for prompt seed word lists."""

from __future__ import annotations

from pathlib import Path

_WORDS: dict[str, list[str]] = {}


def word_list(name: str) -> list[str]:
    words = _WORDS.get(name)
    if words is None:
        path = Path(__file__).parent.parent / "data" / f"{name}.txt"
        words = path.read_text().splitlines()
        _WORDS[name] = words
    return words
