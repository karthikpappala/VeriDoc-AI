# VeriDoc AI 📜

**Multilingual RAG Assistant for Legal, Government & College Documents**

Ask questions about PDF documents in English, Hindi, Telugu, or Tamil.
Get answers grounded in the document with exact citations and hallucination scores.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-orange)
![RAGAS](https://img.shields.io/badge/RAGAS-Hallucination_Eval-red)

## Features
- PDF upload and semantic chunking
- FAISS vector search with similarity scores
- RAG-based Q&A with exact page citations
- RAGAS hallucination detection and confidence scoring
- Multilingual support (Hindi, Telugu, Tamil)
- Admin dashboard showing retrieved chunks and eval metrics

## Tech Stack
| Layer | Technology |
|---|---|
| PDF Parsing | PyMuPDF |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | FAISS |
| LLM | Groq API (llama-3.1-8b-instant) |
| Evaluation | RAGAS |
| API | FastAPI |
| UI | Streamlit |

## Setup
```bash
git clone https://github.com/karthikpappala/VeriDoc-AI
cd VeriDoc-AI
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your GROQ_API_KEY
```

## Run
```bash
# Terminal 1 - API
uvicorn api.main:app --reload

# Terminal 2 - UI
streamlit run ui/app.py
```

## Demo
Upload any government or legal PDF and ask questions in your language.
