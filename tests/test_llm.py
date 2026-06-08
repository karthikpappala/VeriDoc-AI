"""
Day 5 test — LLM via Groq API.
Run from project root: python tests/test_llm.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.ingestion import parse_pdf
from core.embedder import Embedder
from core.vector_store import VectorStore
from core.llm import LLMClient

PDF_PATH = "data/sample_docs/sample_test.pdf"


def main():
    print("=" * 55)
    print("  VeriDoc AI — Day 5 LLM Test")
    print("=" * 55)

    # 1. Load LLM
    print("\n── Step 1: Connect to Groq ──────────────────────────────")
    llm = LLMClient()

    # 2. Simple generation test
    print("\n── Step 2: Basic generation test ────────────────────────")
    answer = llm.generate("What is RAG in AI in one sentence?")
    print(f"  Response: {answer}")

    # 3. Full RAG test with our PDF
    print("\n── Step 3: RAG answer from PDF ──────────────────────────")
    doc = parse_pdf(PDF_PATH, verbose=False)
    embedder = Embedder(verbose=False)
    embeddings = embedder.embed_chunks(doc.chunks, verbose=False)

    store = VectorStore(doc_id=doc.doc_id, dimension=embedder.dimension)
    store.add(doc.chunks, embeddings)

    question = "What academic programs are available?"
    print(f"\n  Question: {question}")

    q_emb = embedder.embed_query(question)
    results = store.search(q_emb, k=3)

    print(f"  Retrieved {len(results)} chunks (scores: "
          f"{', '.join(str(round(r['score'], 2)) for r in results)})")
    answer = llm.generate_rag_answer(question, results)
    print(f"\n  Answer:\n  {answer}")

    print("\n" + "=" * 55)
    print("  Day 5 passed ✓  LLM + RAG working end-to-end")
    print("  Next: Day 6 — full RAG pipeline with citations")
    print("=" * 55)


if __name__ == "__main__":
    main()
