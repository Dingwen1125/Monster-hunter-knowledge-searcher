from __future__ import annotations


def detect_answer_language(text: str) -> str:
    return "Chinese" if contains_chinese(text) else "English"


def contains_chinese(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)
