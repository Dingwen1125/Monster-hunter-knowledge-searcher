from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str
    page: int
    score: float = 0.0


class RagState(TypedDict, total=False):
    question: str
    rewritten_question: str
    search_query: str
    answer_language: str
    should_retrieve: bool
    chunks: list[Chunk]
    relevant_chunks: list[Chunk]
    relevance_reason: str
    answer: str
    attempts: int
