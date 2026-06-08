"""
Day 3 test — embeddings + FAISS vector search.
Run from project root: python tests/test_embedder.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.ingestion import parse_pdf
from core.embedder import Embedder
from core.vector_store import VectorStore

PDF_PATH = "data/sample_docs/sample_test.pdf"


def main():
    print("=" * 55)
    print("  VeriDoc AI — Day 3 Embedder + Vector Store Test")
    print("=" * 55)

    # 1. Parse
    print("\n── Step 1: Parse PDF ────────────────────────────────────")
    doc = parse_pdf(PDF_PATH, verbose=True)

    # 2. Embed
    print("\n── Step 2: Embed chunks ─────────────────────────────────")
    embedder = Embedder()
    embeddings = embedder.embed_chunks(doc.chunks, verbose=True)

    # 3. Build FAISS index
    print("\n── Step 3: Build FAISS index ────────────────────────────")
    store = VectorStore(doc_id=doc.doc_id, dimension=embedder.dimension)
    store.add(doc.chunks, embeddings)
    print(f"    Vectors in index : {store.index.ntotal}")

    # 4. Semantic search
    print("\n── Step 4: Semantic search ──────────────────────────────")
    queries = [
        "What is this document about?",
        "fees and tuition",
        "academic programs",
    ]

    for query in queries:
        print(f"\n  Query: \"{query}\"")
        q_emb = embedder.embed_query(query)
        results = store.search(q_emb, k=2)
        for r in results:
            preview = r["chunk"].text[:120].replace("\n", " ")
            print(f"  [{r['rank']}] score={r['score']:.3f} | page={r['chunk'].page} | {preview}...")

    # 5. Save and reload
    print("\n── Step 5: Save and reload index ────────────────────────")
    store.save()
    store2 = VectorStore.load(doc.doc_id)
    q_emb = embedder.embed_query("university programs")
    results2 = store2.search(q_emb, k=1)
    print(f"    Reload OK — top result score: {results2[0]['score']:.3f}")

    print("\n" + "=" * 55)
    print("  All Day 3 tests passed ✓")
    print("  Next: Day 4 already done (FAISS is built in!)")
    print("  Move to Day 5 — connect the LLM via Groq API")
    print("=" * 55)


if __name__ == "__main__":
    main()
