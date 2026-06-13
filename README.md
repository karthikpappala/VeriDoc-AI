# VeriDoc AI

**Multilingual RAG Assistant for Legal, Government, and College Documents**

Ask questions about PDF documents in English, Hindi, Telugu, or Tamil.
Get answers grounded in the document with exact citations and hallucination scores.

---

## What it does

- Upload any PDF (government schemes, circulars, legal notices, insurance policies)
- Ask a question in any supported language
- Get a cited answer with a confidence score and hallucination risk flag
- Admin dashboard shows which chunks were retrieved, similarity scores, and RAGAS metrics

---

## Architecture

```
PDF Upload
    │
    ▼
[ingestion.py]          ← PyMuPDF extracts text, splits into chunks
    │
    ▼
[embedder.py]           ← sentence-transformers encodes chunks → vectors
    │
    ▼
[vector_store.py]       ← FAISS indexes vectors, finds top-k similar chunks
    │
[user question]
    │
    ▼
[language_utils.py]     ← detects language, translates to English if needed
    │
    ▼
[rag_pipeline.py]       ← builds prompt with retrieved chunks, calls LLM
    │
    ▼
[evaluator.py]          ← RAGAS scores faithfulness + answer relevancy
    │
    ▼
[language_utils.py]     ← translates answer back to user's language
    │
    ▼
Response: {answer, citations, confidence, hallucination_risk}
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| PDF parsing | PyMuPDF (fitz) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | FAISS (CPU) |
| LLM | Groq API (llama3-8b / mixtral) |
| RAG framework | LangChain |
| Evaluation | RAGAS (faithfulness, answer_relevancy) |
| Multilingual | NLLB-200 (Hindi · Telugu · Tamil) |
| API | FastAPI |
| UI | Streamlit |

---

## Setup

```bash
git clone https://github.com/yourusername/veridoc-ai
cd veridoc-ai

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get a free Groq API key at [console.groq.com](https://console.groq.com) (no credit card).

---

## Run

```bash
# Test the ingestion pipeline
python tests/test_ingestion.py

# Start the API server (Day 8+)
uvicorn api.main:app --reload

# Launch the UI (Day 13+)
streamlit run ui/app.py
```

---

## 20-Day Build Plan

| Days | What gets built |
|---|---|
| 1–5 | Environment, PDF parsing, embeddings, FAISS, LLM |
| 6–10 | RAG pipeline, citations, FastAPI, RAGAS evaluation |
| 11–15 | Hindi/Telugu/Tamil, Streamlit UI, admin dashboard |
| 16–20 | Docker, deployment, demo data, interview prep |

---

## Sample Questions (Hindi)

> **Q:** इस योजना में किसे लाभ मिलता है?
> **A:** इस योजना का लाभ छोटे और सीमांत किसानों को मिलता है... [स्रोत: पृष्ठ 3]

---

## Resume Bullet

> Built a multilingual RAG assistant (VeriDoc AI) for document Q&A with citation-grounded responses, hallucination evaluation via RAGAS, FAISS vector search, and Indic language support (Hindi/Telugu/Tamil) across user-uploaded PDFs — deployed with a real-time admin dashboard showing chunk retrieval, similarity scores, and confidence metrics.
