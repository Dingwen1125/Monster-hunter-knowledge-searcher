from __future__ import annotations

from retriever import InMemoryRetriever, create_retriever_tool
from state import RagState


def make_retrieve_tool_node(retriever: InMemoryRetriever):
    retriever_tool = create_retriever_tool(retriever)

    def retrieve_tool(state: RagState) -> RagState:
        query = state.get("rewritten_question") or state.get("search_query") or state["question"]
        return {"chunks": retriever_tool(query), "attempts": state.get("attempts", 0)}

    return retrieve_tool
