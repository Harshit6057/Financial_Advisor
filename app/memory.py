from __future__ import annotations

from datetime import datetime
from typing import List

import chromadb


class ConversationMemory:
    """Simple ChromaDB-backed memory for long-term user context."""

    def __init__(self, path: str = ".chroma") -> None:
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection("wealth_advisor_memory")

    def add(self, user_id: str, role: str, text: str) -> None:
        doc_id = f"{user_id}-{role}-{datetime.utcnow().timestamp()}"
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[{"user_id": user_id, "role": role, "ts": datetime.utcnow().isoformat()}],
        )

    def query(self, user_id: str, query_text: str, n_results: int = 3) -> List[str]:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"user_id": user_id},
        )
        return results.get("documents", [[]])[0]
