"""
VeriDoc AI — FastAPI Server (Days 7 & 8)
Endpoints: /upload, /query, /documents, /health
"""

import os
import shutil
import tempfile
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.rag_pipeline import RAGPipeline

# ── App lifespan (loads models once at startup) ───────────────────────────────

pipeline: RAGPipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline
    print("🚀  Starting VeriDoc AI...")
    pipeline = RAGPipeline(verbose=True)
    # Auto-reload any previously indexed documents
    from pathlib import Path
    uploads = Path("data/uploads")
    if uploads.exists():
        for pdf in uploads.glob("*.pdf"):
            try:
                pipeline.load_pdf(str(pdf))
            except Exception as e:
                print(f"⚠️  Could not reload {pdf.name}: {e}")
    print("✓   Pipeline ready\n")
    yield
    print("👋  Shutting down.")

app = FastAPI(
    title="VeriDoc AI",
    description="Multilingual RAG assistant for legal and government documents",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Request / Response models ─────────────────────────────────────────────────

class QueryRequest(BaseModel):
    doc_id: str
    question: str
    k: int = 5
    language: str = "en"
    run_eval: bool = False

class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: list[dict]
    doc_id: str
    top_score: float
    language: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Quick check that the server is running."""
    return {"status": "ok", "model": os.getenv("LLM_MODEL", "llama-3.1-8b-instant")}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF and index it.
    Returns doc_id to use in subsequent /query calls.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save uploaded file
    dest = UPLOAD_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Parse + embed + index
    try:
        doc_id = pipeline.load_pdf(str(dest))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "message": "PDF uploaded and indexed successfully.",
    }


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """
    Ask a question against an uploaded document.
    Returns answer with citations and similarity scores.
    """
    try:
        response = pipeline.query(
            question=req.question,
            doc_id=req.doc_id,
            k=req.k,
            language=req.language,
            run_eval=req.run_eval,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return QueryResponse(**response.to_dict())


@app.get("/documents")
def list_documents():
    """List all uploaded and indexed documents."""
    docs = pipeline.list_documents()
    return {"documents": docs, "count": len(docs)}


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    """Remove a document from the store."""
    deleted = pipeline.doc_store.delete(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found.")
    # Also remove from in-memory vector stores
    pipeline._vector_stores.pop(doc_id, None)
    return {"message": f"Document {doc_id} deleted."}
