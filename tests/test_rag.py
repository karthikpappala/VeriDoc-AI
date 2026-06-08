"""
Day 6 test — full RAG pipeline.
Run from project root: python tests/test_rag.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.rag_pipeline import RAGPipeline

PDF_PATH = "data/sample_docs/sample_test.pdf"

QUESTIONS = [
    "What colleges or academic units are mentioned?",
    "What resources are available for students?",
    "Tell me about the university history.",
]


def main():
    print("=" * 55)
    print("  VeriDoc AI — Day 6 Full RAG Pipeline Test")
    print("=" * 55)

    # Boot the pipeline (loads embedder + LLM once)
    pipeline = RAGPipeline(verbose=True)
    print()

    # Load PDF (parses + indexes on first run, loads from disk after)
    doc_id = pipeline.load_pdf(PDF_PATH)
    print(f"\n✓  doc_id: {doc_id}")

    # Run queries
    for question in QUESTIONS:
        response = pipeline.query(question, doc_id=doc_id, k=3)
        response.pretty_print()

    # Show structured output (what the API will return)
    print("\n\n── JSON output sample (what /query API returns) ─────────")
    import json
    response = pipeline.query(QUESTIONS[0], doc_id=doc_id, k=2)
    print(json.dumps(response.to_dict(), indent=2))

    print("\n" + "=" * 55)
    print("  Day 6 passed ✓  Full RAG pipeline working")
    print("  Next: Day 7+8 — FastAPI endpoints")
    print("=" * 55)


if __name__ == "__main__":
    main()
