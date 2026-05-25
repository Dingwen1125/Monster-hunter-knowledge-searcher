"""Custom LangGraph RAG agent over a Monster Hunter PDF knowledge base.

Usage:
    cp .env.example .env
    # edit .env and set OPENAI_API_KEY
    python monster_hunter_rag_agent.py "How should I fight Rathalos?"
"""

from __future__ import annotations

import argparse
import os

from openai import APIConnectionError, RateLimitError

from env import load_dotenv
from graph import build_graph
from knowledge_base import fetch_documents, preprocess_documents
from retriever import index_documents
from state import RagState


def ask(question: str) -> RagState:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY before running the RAG agent.")
    documents = fetch_documents()
    chunks = preprocess_documents(documents)
    retriever = index_documents(chunks)
    graph = build_graph(retriever)
    return graph.invoke({"question": question, "attempts": 0})


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the Monster Hunter LangGraph RAG agent.")
    parser.add_argument("question", nargs="?", default="How should a new hunter prepare for Rathalos?")
    args = parser.parse_args()

    try:
        result = ask(args.question)
    except FileNotFoundError as error:
        if str(error) == "no pdf":
            raise SystemExit("no pdf") from error
        raise
    except APIConnectionError as error:
        raise SystemExit(
            "Could not connect to the OpenAI API. Check your network/VPN/proxy, "
            "then run the command again."
        ) from error
    except RateLimitError as error:
        message = str(error)
        if "insufficient_quota" in message:
            raise SystemExit(
                "OpenAI API quota is insufficient. Check your API key billing/quota, "
                "then run the command again."
            ) from error
        raise
    print(result["answer"])


if __name__ == "__main__":
    main()
