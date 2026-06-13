---
title: VeriDoc AI
emoji: 📜
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
---

# VeriDoc AI 📜

**Multilingual RAG Assistant for Legal, Government & College Documents**

🔴 **Live Demo:** https://huggingface.co/spaces/Karthikp1703/VeriDoc-AI  
📹 **Demo Video:** https://drive.google.com/file/d/1mi70rZZBD-SkVnYqiPxVBd_jByD5SUd-/view  

## What it does
- Upload any PDF (government schemes, legal notices, policy documents)
- Ask questions in English, Hindi, Telugu, or Tamil
- Get answers grounded in the document with exact page citations
- Hallucination detection and confidence scoring via RAGAS
- Admin dashboard showing retrieved chunks and similarity scores

## Tech Stack
| Layer | Technology |
|---|---|
| PDF Parsing | PyMuPDF |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | FAISS |
| LLM | Groq API (llama-3.1-8b-instant) |
| Evaluation | RAGAS (faithfulness, relevancy) |
| Multilingual | NLLB-200 (Hindi · Telugu · Tamil) |
| API | FastAPI |
| UI | Streamlit |
| Deployment | Docker · HuggingFace Spaces |

## Setup
\`\`\`bash
git clone https://github.com/karthikpappala/VeriDoc-AI
cd VeriDoc-AI
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add GROQ_API_KEY
\`\`\`

## Run locally
\`\`\`bash
# Terminal 1
uvicorn api.main:app --reload

# Terminal 2
streamlit run ui/app.py
\`\`\`

## Resume Bullet
> Built and deployed VeriDoc AI — a multilingual RAG assistant for document Q&A with citation-grounded responses, hallucination evaluation via RAGAS, FAISS vector search, and Indic language support (Hindi/Telugu/Tamil) via NLLB-200 — served via FastAPI with a Streamlit admin dashboard, deployed on HuggingFace Spaces.
