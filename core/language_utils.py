"""
VeriDoc AI — Language Utils (Days 11-12)
Detects language and translates using Facebook's NLLB-200 model.
Supports: English, Hindi, Telugu, Tamil
"""

from langdetect import detect
from transformers import pipeline as hf_pipeline
import torch

# NLLB-200 language codes
LANG_CODES = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "te": "tel_Telu",
    "ta": "tam_Taml",
}

LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
}

NLLB_MODEL = "facebook/nllb-200-distilled-600M"  # 600M — good balance of speed vs quality

_translator = None  # lazy load — only download when first needed


def _get_translator():
    """Load NLLB-200 translator once and reuse."""
    global _translator
    if _translator is None:
        print(f"🌐  Loading translation model: {NLLB_MODEL}")
        print(f"    (First load ~1.2GB download — subsequent loads are instant)")
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        _translator = {
            "tokenizer": AutoTokenizer.from_pretrained(NLLB_MODEL),
            "model": AutoModelForSeq2SeqLM.from_pretrained(NLLB_MODEL),
        }
        print(f"    ✓ Translation model ready")
    return _translator


def detect_language(text: str) -> str:
    """
    Detect the language of a text string.
    Returns one of: 'en', 'hi', 'te', 'ta', or 'en' as fallback.
    """
    try:
        detected = detect(text)
        # langdetect codes → our codes
        mapping = {"hi": "hi", "te": "te", "ta": "ta", "en": "en"}
        return mapping.get(detected, "en")
    except Exception:
        return "en"


def translate(text: str, src_lang: str, tgt_lang: str) -> str:
    """
    Translate text from src_lang to tgt_lang.
    Language codes: 'en', 'hi', 'te', 'ta'
    Returns original text if src and tgt are the same.
    """
    if src_lang == tgt_lang:
        return text

    src_code = LANG_CODES.get(src_lang)
    tgt_code = LANG_CODES.get(tgt_lang)

    if not src_code or not tgt_code:
        print(f"⚠️  Unsupported language pair: {src_lang} → {tgt_lang}")
        return text

    try:
        translator = _get_translator()
        tokenizer = translator["tokenizer"]
        model = translator["model"]
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        target_id = tokenizer.convert_tokens_to_ids(tgt_code)
        outputs = model.generate(
            **inputs,
            forced_bos_token_id=target_id,
            max_length=512,
        )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print(f"⚠️  Translation failed ({e}), returning original text.")
        return text


def process_multilingual_query(question: str, target_language: str = "en") -> tuple[str, str]:
    """
    Detect the language of the question and translate to English for RAG.

    Returns:
        (english_question, detected_language)
    """
    detected = detect_language(question)
    print(f"🌐  Detected language: {LANG_NAMES.get(detected, detected)}")

    if detected == "en":
        return question, "en"

    print(f"    Translating {LANG_NAMES.get(detected)} → English...")
    english_question = translate(question, src_lang=detected, tgt_lang="en")
    print(f"    Translated: {english_question}")
    return english_question, detected


def translate_answer(answer: str, src_lang: str, tgt_lang: str) -> str:
    """
    Translate the LLM answer back to the user's language.
    Skips translation if target is English.
    """
    if tgt_lang == "en" or src_lang == tgt_lang:
        return answer

    print(f"🌐  Translating answer → {LANG_NAMES.get(tgt_lang, tgt_lang)}...")
    translated = translate(answer, src_lang=src_lang, tgt_lang=tgt_lang)
    return translated
