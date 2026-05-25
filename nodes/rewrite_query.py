from __future__ import annotations

from langchain_openai import ChatOpenAI

from config import CHAT_MODEL
from state import RagState


def rewrite_query(state: RagState) -> RagState:
    llm = ChatOpenAI(model=CHAT_MODEL, temperature=0.0)
    prompt = (
        "Convert the user question from any language into a concise English "
        "Monster Hunter knowledge-base search query for an English PDF. Preserve "
        "monster names, weapon names, item names, and game terms. Return only the "
        "English search query.\n\n"
        f"Original question: {state['question']}\n"
        f"Current search query: {state.get('search_query', state['question'])}"
    )
    rewritten = llm.invoke(prompt).content
    attempts = state.get("attempts", 0)
    if state.get("chunks"):
        attempts += 1
    return {
        "rewritten_question": str(rewritten).strip(),
        "search_query": str(rewritten).strip(),
        "attempts": attempts,
    }
