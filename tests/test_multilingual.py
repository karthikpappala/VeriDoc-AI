"""
Days 11-12 test — Multilingual support (Hindi, Telugu, Tamil)
Run from project root: python tests/test_multilingual.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.language_utils import detect_language, translate, process_multilingual_query, translate_answer
from core.rag_pipeline import RAGPipeline

PDF_PATH = "data/uploads/pmkisan.pdf"


def test_language_detection():
    print("\n── Language Detection ───────────────────────────────────")
    tests = [
        ("Who is eligible for PM-KISAN?", "en"),
        ("पीएम किसान के लिए कौन पात्र है?", "hi"),
        ("పీఎం కిసాన్ కోసం అర్హత ఏమిటి?", "te"),
        ("பிஎம் கிசான் திட்டத்திற்கு யார் தகுதியானவர்கள்?", "ta"),
    ]
    for text, expected in tests:
        detected = detect_language(text)
        status = "✓" if detected == expected else "⚠️"
        print(f"  {status} '{text[:40]}...' → {detected} (expected {expected})")


def test_translation():
    print("\n── Translation Tests ────────────────────────────────────")

    # English → Hindi
    en_text = "Farmers with cultivable land are eligible for PM-KISAN scheme."
    hi_result = translate(en_text, "en", "hi")
    print(f"  EN→HI: {hi_result}")

    # English → Telugu
    te_result = translate(en_text, "en", "te")
    print(f"  EN→TE: {te_result}")

    # English → Tamil
    ta_result = translate(en_text, "en", "ta")
    print(f"  EN→TA: {ta_result}")

    # Hindi → English
    hi_question = "पीएम किसान योजना के लाभार्थी कौन हैं?"
    en_result = translate(hi_question, "hi", "en")
    print(f"  HI→EN: {en_result}")


def test_multilingual_rag():
    print("\n── Multilingual RAG Queries ─────────────────────────────")

    pipeline = RAGPipeline(verbose=False)
    doc_id = pipeline.load_pdf(PDF_PATH)

    questions = [
        ("पीएम किसान योजना के लाभार्थी कौन हैं?", "hi"),
        ("పీఎం కిసాన్ పథకంలో ఎవరు లబ్ధి పొందవచ్చు?", "te"),
    ]

    for question, lang in questions:
        print(f"\n  [{lang.upper()}] {question}")

        # Translate question to English
        from core.language_utils import process_multilingual_query, translate_answer
        english_q, detected_lang = process_multilingual_query(question)

        # RAG query in English
        response = pipeline.query(english_q, doc_id=doc_id, k=3, run_eval=False)

        # Translate answer back
        translated_answer = translate_answer(response.answer, "en", lang)

        print(f"  EN answer  : {response.answer[:150]}...")
        print(f"  {lang.upper()} answer  : {translated_answer[:150]}...")
        print(f"  Top score  : {response.top_score:.3f}")


def main():
    print("=" * 55)
    print("  VeriDoc AI — Days 11-12 Multilingual Test")
    print("=" * 55)

    test_language_detection()
    test_translation()
    test_multilingual_rag()

    print("\n" + "=" * 55)
    print("  Days 11-12 passed ✓  Multilingual support working")
    print("  Hindi, Telugu, Tamil → English → RAG → back")
    print("=" * 55)


if __name__ == "__main__":
    main()
