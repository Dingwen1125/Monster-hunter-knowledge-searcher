from __future__ import annotations

from pathlib import Path
import re

from pypdf import PdfReader

from config import PDF_PATH
from state import Chunk


def fetch_documents() -> list[Path]:
    """Fetch the source documents used by the RAG system.

    For this demo, documents are expected to already exist locally.
    The same function is where remote downloads or database reads would go.
    """
    if not PDF_PATH.exists():
        raise FileNotFoundError("no pdf")
    return [PDF_PATH]


def ensure_knowledge_base() -> None:
    fetch_documents()


def preprocess_documents(paths: list[Path]) -> list[Chunk]:
    """Load, clean, and split source documents into retrievable chunks."""
    chunks: list[Chunk] = []
    for path in paths:
        if path.suffix.lower() == ".pdf":
            chunks.extend(load_pdf_chunks(path))
    return chunks


def load_pdf_chunks(path: Path) -> list[Chunk]:
    reader = PdfReader(str(path))
    chunks: list[Chunk] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for chunk_text in split_text(text):
            chunks.append(Chunk(text=chunk_text, source=path.name, page=page_number))
    return chunks


def split_text(text: str, chunk_size: int = 850, overlap: int = 120) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            sentence_end = normalized.rfind(". ", start, end)
            if sentence_end > start + chunk_size // 2:
                end = sentence_end + 1
        chunks.append(normalized[start:end].strip())
        if end == len(normalized):
            break
        start = max(0, end - overlap)
    return chunks
