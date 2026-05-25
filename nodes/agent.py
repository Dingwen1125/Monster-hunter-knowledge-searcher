from __future__ import annotations

from typing import Literal

from langchain_openai import ChatOpenAI

from config import CHAT_MODEL
from state import RagState


def agent(state: RagState) -> RagState:
    

    route_text = f"{state['question']} {state.get('search_query', '')}".lower()
    monster_hunter_terms = {
        "monster hunter",
        "rathalos",
        "diablos",
        "zinogre",
        "hunter",
        "hunt",
        "weapon",
        "potion",
        "carting",
        "fainting",
        "怪物猎人",
        "怪猎",
        "火龙",
        "角龙",
        "雷狼龙",
        "猎人",
    }
    if any(term in route_text for term in monster_hunter_terms):
        return {"should_retrieve": True}

    llm = ChatOpenAI(model=CHAT_MODEL, temperature=0.0)
    prompt = f"""
You are a routing agent for a Monster Hunter RAG workflow.
Decide whether answering this question requires retrieving from the PDF knowledge base.
Return only RETRIEVE or END.

Original question: {state["question"]}
English search query: {state.get("search_query", "")}
"""
    decision = str(llm.invoke(prompt).content).strip().upper()
    if "END" in decision and "RETRIEVE" not in decision:
        return {
            "should_retrieve": False,
            "answer": "This workflow is configured to answer Monster Hunter knowledge-base questions. Ask a Monster Hunter question to trigger retrieval.",
        }
    return {"should_retrieve": True}


def should_retrieve(state: RagState) -> Literal["continue", "end"]:
    return "continue" if state.get("should_retrieve", True) else "end"
