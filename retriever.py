from __future__ import annotations

import numpy as np
from langchain_openai import OpenAIEmbeddings

from config import EMBEDDING_MODEL
from state import Chunk


class InMemoryRetriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        if not chunks:
            raise ValueError("No text chunks were loaded from the PDF.")
        self.chunks = chunks
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.matrix: np.ndarray | None = None

    def search(self, query: str, k: int = 4) -> list[Chunk]:
        self._ensure_index()
        query_vector = self._normalize(
            np.array([self.embeddings.embed_query(query)], dtype=np.float32)
        )[0]
        if self.matrix is None:
            raise RuntimeError("The document index was not created.")
        scores = self.matrix @ query_vector
        indexes = np.argsort(scores)[::-1][:k]
        return [
            Chunk(
                text=self.chunks[index].text,
                source=self.chunks[index].source,
                page=self.chunks[index].page,
                score=float(scores[index]),
            )
            for index in indexes
        ]

    def _ensure_index(self) -> None:
        if self.matrix is not None:
            return
        vectors = self.embeddings.embed_documents([chunk.text for chunk in self.chunks])
        self.matrix = self._normalize(np.array(vectors, dtype=np.float32))

    @staticmethod
    def _normalize(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return matrix / norms


def index_documents(chunks: list[Chunk]) -> InMemoryRetriever:
    """Prepare a lazy semantic-search index over preprocessed chunks.

    Embeddings are created on the first retrieval call, so questions that do not
    need the retriever tool do not pay the indexing cost.
    """
    return InMemoryRetriever(chunks)


def create_retriever_tool(retriever: InMemoryRetriever):
    """Create the retrieval tool that the LangGraph agent workflow can call."""

    def retrieve_monster_hunter_docs(query: str, k: int = 4) -> list[Chunk]:
        """Search the Monster Hunter knowledge base for relevant PDF chunks."""
        return retriever.search(query, k=k)

    retrieve_monster_hunter_docs.__name__ = "retrieve_monster_hunter_docs"
    return retrieve_monster_hunter_docs


def format_context(chunks: list[Chunk]) -> str:
    return "\n\n".join(
        f"[{idx}] {chunk.source}, page {chunk.page}, score {chunk.score:.3f}\n{chunk.text}"
        for idx, chunk in enumerate(chunks, start=1)
    )
