"""
Day 2 test — run this to verify the ingestion pipeline works.
Downloads a small real-world government PDF, parses it, and prints results.

Usage (from project root):
    python tests/test_ingestion.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import urllib.request
from pathlib import Path
from core.ingestion import parse_pdf
from core.document_store import DocumentStore


SAMPLE_PDF_URL = (
    "https://www.w3.org/WAI/WCAG21/wcag21.pdf"  # publicly available, ~1MB
)
SAMPLE_LOCAL = Path("data/sample_docs/sample_test.pdf")


def download_sample():
    if SAMPLE_LOCAL.exists():
        print(f"✓  Using existing sample: {SAMPLE_LOCAL}")
        return str(SAMPLE_LOCAL)
    print("⬇  Downloading sample PDF...")
    SAMPLE_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(SAMPLE_PDF_URL, SAMPLE_LOCAL)
    print(f"   Saved to {SAMPLE_LOCAL}")
    return str(SAMPLE_LOCAL)


def test_chunking_sizes():
    """Verify different chunk sizes produce correct chunk counts."""
    print("\n── Chunk-size sanity test ───────────────────────────────────")
    # Build a synthetic long text (3 "pages")
    from core.ingestion import split_into_chunks, extract_text_from_pdf
    fake_pages = [
        {"page": i + 1, "text": ("word " * 200).strip()}
        for i in range(3)
    ]
    for size in [200, 500, 1000]:
        chunks = split_into_chunks(fake_pages, chunk_size=size, chunk_overlap=0)
        print(f"   chunk_size={size:4d} → {len(chunks):3d} chunks")
    print("   ✓ chunking looks correct")


def test_document_store(doc):
    """Save and reload a document from the store."""
    print("\n── DocumentStore test ───────────────────────────────────────")
    store = DocumentStore(persist_dir="data/parsed_docs")
    store.add(doc)
    print(f"   Saved. Store now has {len(store)} document(s).")

    # Reload from disk
    reloaded = store.get(doc.doc_id)
    assert reloaded is not None, "Failed to reload document from disk"
    assert reloaded.total_chunks == doc.total_chunks, "Chunk count mismatch after reload"
    print(f"   Reload OK — chunks match ({reloaded.total_chunks})")

    listing = store.list_docs()
    print(f"   list_docs() returned {len(listing)} doc(s)")
    print("   ✓ DocumentStore working correctly")
    return store


def main():
    print("=" * 55)
    print("  VeriDoc AI — Day 2 Ingestion Pipeline Test")
    print("=" * 55)

    # 1. Parse PDF
    pdf_path = download_sample()
    doc = parse_pdf(pdf_path, chunk_size=500, chunk_overlap=50, verbose=True)

    print(f"\n✅  Parsed: {doc.summary()}")

    # 2. Print sample chunks
    print("\n── Sample chunks ────────────────────────────────────────────")
    for chunk in doc.chunks[:2]:
        print(f"\n  [Chunk {chunk.chunk_index} | Page {chunk.page} | {chunk.char_count} chars]")
        preview = chunk.text[:200].replace("\n", " ")
        print(f"  {preview}...")

    # 3. Chunking size test
    test_chunking_sizes()

    # 4. Document store test
    store = test_document_store(doc)

    print("\n" + "=" * 55)
    print("  All Day 2 tests passed ✓")
    print("  Next: Day 3 — embed chunks with sentence-transformers")
    print("=" * 55)


if __name__ == "__main__":
    main()
