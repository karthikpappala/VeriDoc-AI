"""
VeriDoc AI — Document Store (Day 2)
In-memory + disk persistence for parsed documents and their chunks.
"""

import json
import os
from pathlib import Path
from typing import Optional
from core.ingestion import ParsedDocument, Chunk


DATA_DIR = Path(__file__).parent.parent / "data"
DOCS_DIR = DATA_DIR / "parsed_docs"


class DocumentStore:
    """
    Lightweight store for ParsedDocuments.
    - Keeps all docs in memory during a session.
    - Persists chunks to JSON on disk (one file per doc).
    - Acts as a registry so the rest of the app can look up chunks by doc_id.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = Path(persist_dir) if persist_dir else DOCS_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._docs: dict[str, ParsedDocument] = {}

    # ── Write ────────────────────────────────────────────────────────────────

    def add(self, doc: ParsedDocument, save: bool = True) -> None:
        """Register a parsed document. Optionally persist to disk."""
        self._docs[doc.doc_id] = doc
        if save:
            self._save(doc)

    def _save(self, doc: ParsedDocument) -> None:
        out_path = self.persist_dir / f"{doc.doc_id}.json"
        payload = {
            "doc_id": doc.doc_id,
            "filename": doc.filename,
            "total_pages": doc.total_pages,
            "total_chunks": doc.total_chunks,
            "language_hint": doc.language_hint,
            "chunks": [c.to_dict() for c in doc.chunks],
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    # ── Read ─────────────────────────────────────────────────────────────────

    def get(self, doc_id: str) -> Optional[ParsedDocument]:
        """Return in-memory doc, or load from disk if not loaded yet."""
        if doc_id in self._docs:
            return self._docs[doc_id]
        return self._load(doc_id)

    def _load(self, doc_id: str) -> Optional[ParsedDocument]:
        path = self.persist_dir / f"{doc_id}.json"
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        chunks = [
            Chunk(
                text=c["text"],
                page=c["page"],
                chunk_index=c["chunk_index"],
                doc_id=c["doc_id"],
                source_file=c["source_file"],
            )
            for c in data["chunks"]
        ]
        doc = ParsedDocument(
            doc_id=data["doc_id"],
            filename=data["filename"],
            total_pages=data["total_pages"],
            total_chunks=data["total_chunks"],
            chunks=chunks,
            language_hint=data.get("language_hint", "en"),
        )
        self._docs[doc_id] = doc
        return doc

    def get_chunks(self, doc_id: str) -> list[Chunk]:
        doc = self.get(doc_id)
        return doc.chunks if doc else []

    def list_docs(self) -> list[dict]:
        """Return metadata for all docs (on disk, not just in memory)."""
        result = []
        for path in self.persist_dir.glob("*.json"):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            result.append({
                "doc_id": data["doc_id"],
                "filename": data["filename"],
                "total_pages": data["total_pages"],
                "total_chunks": data["total_chunks"],
            })
        return result

    def delete(self, doc_id: str) -> bool:
        self._docs.pop(doc_id, None)
        path = self.persist_dir / f"{doc_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    # ── Convenience ──────────────────────────────────────────────────────────

    def __len__(self):
        return len(list(self.persist_dir.glob("*.json")))

    def __repr__(self):
        return f"DocumentStore(docs={len(self)}, dir={self.persist_dir})"
