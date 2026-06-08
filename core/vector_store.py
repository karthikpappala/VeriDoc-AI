"""
VeriDoc AI — Vector Store (Day 3)
FAISS index for storing and searching embedded chunks.
"""

import os
import json
import numpy as np
import faiss
from pathlib import Path
from core.ingestion import Chunk

DATA_DIR = Path(__file__).parent.parent / "data"
INDEX_DIR = DATA_DIR / "indexes"


class VectorStore:
    """
    Per-document FAISS index.
    Stores embeddings + chunk metadata together so search results
    always come back with the original text and page numbers.
    """

    def __init__(self, doc_id: str, dimension: int = 384):
        self.doc_id = doc_id
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product = cosine (normalized vecs)
        self.chunks: list[Chunk] = []
        INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # ── Build ────────────────────────────────────────────────────────────────

    def add(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        """Add chunks and their embeddings to the index."""
        assert len(chunks) == embeddings.shape[0], "chunks and embeddings count must match"
        self.chunks = chunks
        self.index.add(embeddings)

    # ── Search ───────────────────────────────────────────────────────────────

    def search(self, query_embedding: np.ndarray, k: int = 5) -> list[dict]:
        """
        Find top-k most similar chunks to the query.

        Returns list of dicts:
            {chunk, score, rank}
        where score is cosine similarity (0–1, higher = more relevant).
        """
        k = min(k, self.index.ntotal)  # can't retrieve more than we have
        if k == 0:
            return []

        scores, indices = self.index.search(query_embedding, k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:
                continue
            results.append({
                "chunk": self.chunks[idx],
                "score": float(score),
                "rank": rank + 1,
            })
        return results

    # ── Persist ──────────────────────────────────────────────────────────────

    def save(self) -> None:
        """Save FAISS index + chunk metadata to disk."""
        index_path = INDEX_DIR / f"{self.doc_id}.faiss"
        meta_path  = INDEX_DIR / f"{self.doc_id}.meta.json"

        faiss.write_index(self.index, str(index_path))

        meta = {
            "doc_id": self.doc_id,
            "dimension": self.dimension,
            "total_chunks": len(self.chunks),
            "chunks": [c.to_dict() for c in self.chunks],
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        print(f"💾  Saved index → {index_path.name}  ({self.index.ntotal} vectors)")

    @classmethod
    def load(cls, doc_id: str) -> "VectorStore":
        """Load a saved index from disk."""
        index_path = INDEX_DIR / f"{doc_id}.faiss"
        meta_path  = INDEX_DIR / f"{doc_id}.meta.json"

        if not index_path.exists():
            raise FileNotFoundError(f"No saved index for doc_id={doc_id}")

        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

        store = cls(doc_id=doc_id, dimension=meta["dimension"])
        store.index = faiss.read_index(str(index_path))
        store.chunks = [
            Chunk(
                text=c["text"], page=c["page"],
                chunk_index=c["chunk_index"], doc_id=c["doc_id"],
                source_file=c["source_file"],
            )
            for c in meta["chunks"]
        ]
        print(f"📂  Loaded index ← {index_path.name}  ({store.index.ntotal} vectors)")
        return store

    @staticmethod
    def exists(doc_id: str) -> bool:
        return (INDEX_DIR / f"{doc_id}.faiss").exists()
