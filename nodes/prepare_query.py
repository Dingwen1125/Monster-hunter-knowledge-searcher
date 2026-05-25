from __future__ import annotations

from language import detect_answer_language
from state import RagState


def prepare_query(state: RagState) -> RagState:
    answer_language = detect_answer_language(state["question"])
    return {"answer_language": answer_language}
