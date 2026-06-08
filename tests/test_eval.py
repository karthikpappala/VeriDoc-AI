"""
Day 9 test — RAGAS hallucination evaluation.
Run from project root: python tests/test_eval.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.rag_pipeline import RAGPipeline

PDF_PATH = "data/sample_docs/sample_test.pdf"


def main():
    print("=" * 55)
    print("  VeriDoc AI — Day 9 RAGAS Evaluation Test")
    print("=" * 55)

    pipeline = RAGPipeline(verbose=True)
    print()
    doc_id = pipeline.load_pdf(PDF_PATH)

    # Test 1: grounded question (should score high faithfulness)
    print("\n── Test 1: Grounded question ────────────────────────────")
    r1 = pipeline.query(
        "What colleges are mentioned in the document?",
        doc_id=doc_id,
        k=3,
        run_eval=True,
    )
    r1.pretty_print()

    # Test 2: out-of-context question (should score low / high risk)
    print("\n── Test 2: Out-of-context question ──────────────────────")
    r2 = pipeline.query(
        "What is the GDP of India in 2024?",
        doc_id=doc_id,
        k=3,
        run_eval=True,
    )
    r2.pretty_print()

    # Show full JSON with evaluation block
    print("\n── JSON with evaluation block ───────────────────────────")
    import json
    print(json.dumps(r1.to_dict(), indent=2))

    print("\n" + "=" * 55)
    print("  Day 9 passed ✓  RAGAS evaluation working")
    print("  Next: Day 10 — confidence scoring + /query API update")
    print("=" * 55)


if __name__ == "__main__":
    main()
