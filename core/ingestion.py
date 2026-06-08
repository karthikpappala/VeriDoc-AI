"""
VeriDoc AI — PDF Ingestion Pipeline (Day 2)
Parses PDFs and splits text into semantic chunks with metadata.
"""

import os
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import fitz  # PyMuPDF


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class Chunk:
    """A single piece of text extracted from a PDF, with metadata."""
    text: str
    page: int
    chunk_index: int
    doc_id: str
    source_file: str
    char_count: int = field(init=False)

    def __post_init__(self):
        self.char_count = len(self.text)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "page": self.page,
            "chunk_index": self.chunk_index,
            "doc_id": self.doc_id,
            "source_file": self.source_file,
            "char_count": self.char_count,
        }


@dataclass
class ParsedDocument:
    """The full result of parsing a single PDF file."""
    doc_id: str
    filename: str
    total_pages: int
    total_chunks: int
    chunks: list[Chunk]
    language_hint: str = "en"  # will be updated by language detector later

    def summary(self) -> str:
        return (
            f"[{self.filename}] "
            f"{self.total_pages} pages · "
            f"{self.total_chunks} chunks · "
            f"doc_id={self.doc_id}"
        )


# ── Core functions ─────────────────────────────────────────────────────────────

def generate_doc_id(file_path: str) -> str:
    """Stable ID based on filename + file size (no full read needed)."""
    size = os.path.getsize(file_path)
    raw = f"{Path(file_path).name}:{size}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract raw text page-by-page using PyMuPDF (fitz).
    Returns: list of {"page": int, "text": str}
    """
    pages = []
    doc = fitz.open(file_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")  # plain text, no HTML

        # Clean up: remove excessive whitespace but keep paragraph breaks
        cleaned = "\n".join(
            line.strip() for line in text.splitlines() if line.strip()
        )

        if cleaned:  # skip blank pages
            pages.append({
                "page": page_num + 1,  # 1-indexed for humans
                "text": cleaned,
            })

    doc.close()
    return pages


def split_into_chunks(
    pages: list[dict],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[dict]:
    """
    Split page text into overlapping chunks.
    Uses word-boundary splitting so chunks never cut mid-word.

    Args:
        pages: output of extract_text_from_pdf()
        chunk_size: target characters per chunk
        chunk_overlap: characters of overlap between adjacent chunks
    Returns:
        list of {"page": int, "text": str}
    """
    raw_chunks = []

    for page_info in pages:
        text = page_info["text"]
        page_num = page_info["page"]
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Snap to word boundary if not at end of text
            if end < len(text):
                # Walk back to last space
                snap = text.rfind(" ", start, end)
                if snap > start:
                    end = snap

            chunk_text = text[start:end].strip()
            if chunk_text:
                raw_chunks.append({"page": page_num, "text": chunk_text})

            # Move forward with overlap
            start = end - chunk_overlap if end - chunk_overlap > start else end

    return raw_chunks


def parse_pdf(
    file_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    verbose: bool = True,
) -> ParsedDocument:
    """
    Full pipeline: PDF file → ParsedDocument with chunks.

    Args:
        file_path: absolute or relative path to a .pdf file
        chunk_size: characters per chunk (default 500)
        chunk_overlap: overlap between chunks (default 50)
        verbose: print progress
    Returns:
        ParsedDocument
    """
    file_path = str(Path(file_path).resolve())
    filename = Path(file_path).name

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found: {file_path}")

    if verbose:
        print(f"📄  Parsing: {filename}")

    doc_id = generate_doc_id(file_path)
    pages = extract_text_from_pdf(file_path)

    if not pages:
        raise ValueError(f"No text extracted from {filename}. "
                         "It may be a scanned PDF — OCR support coming in Day 15.")

    if verbose:
        total_chars = sum(len(p["text"]) for p in pages)
        print(f"    Pages with text : {len(pages)}")
        print(f"    Total characters: {total_chars:,}")

    raw_chunks = split_into_chunks(pages, chunk_size, chunk_overlap)

    # Wrap in Chunk dataclass with full metadata
    chunks = [
        Chunk(
            text=rc["text"],
            page=rc["page"],
            chunk_index=i,
            doc_id=doc_id,
            source_file=filename,
        )
        for i, rc in enumerate(raw_chunks)
    ]

    if verbose:
        print(f"    Chunks created  : {len(chunks)}")
        avg = sum(c.char_count for c in chunks) / len(chunks) if chunks else 0
        print(f"    Avg chunk size  : {avg:.0f} chars")
        print(f"    doc_id          : {doc_id}")

    return ParsedDocument(
        doc_id=doc_id,
        filename=filename,
        total_pages=len(pages),
        total_chunks=len(chunks),
        chunks=chunks,
    )


# ── CLI test entry point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python ingestion.py <path/to/file.pdf>")
        sys.exit(1)

    result = parse_pdf(sys.argv[1], verbose=True)
    print(f"\n✅  {result.summary()}")
    print("\n── First 3 chunks ──────────────────────────────────────")
    for chunk in result.chunks[:3]:
        print(f"\n[Chunk {chunk.chunk_index} | Page {chunk.page} | {chunk.char_count} chars]")
        print(chunk.text[:300] + ("..." if chunk.char_count > 300 else ""))
    print("\n── Last chunk ──────────────────────────────────────────")
    last = result.chunks[-1]
    print(f"\n[Chunk {last.chunk_index} | Page {last.page} | {last.char_count} chars]")
    print(last.text[:300])
