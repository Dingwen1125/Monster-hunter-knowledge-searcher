from __future__ import annotations

import os
from pathlib import Path


PDF_PATH = Path("knowledge_base/monster_hunter_field_guide.pdf")
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
