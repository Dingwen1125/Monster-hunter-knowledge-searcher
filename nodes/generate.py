from __future__ import annotations

from langchain_openai import ChatOpenAI

from config import CHAT_MODEL
from retriever import format_context
from state import RagState


def generate(state: RagState) -> RagState:
    if not state.get("relevant_chunks"):
        return {
            "answer": (
                "I could not find relevant information in the PDF knowledge base, "
                "so I will not answer this question."
            )
        }

    llm = ChatOpenAI(model=CHAT_MODEL, temperature=0.2)
    chunks = state["relevant_chunks"]
    context = format_context(chunks)
    prompt = f"""
You are a practical Monster Hunter guide. Answer only from the provided PDF
context. If the context does not contain enough information, say what is missing.
Give concrete hunting advice.
Answer in {state.get("answer_language", "English")}.

Question: {state["question"]}

PDF context:
{context}
"""
    answer = llm.invoke(prompt).content
    return {"answer": str(answer).strip()}
