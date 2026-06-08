"""
VeriDoc AI — RAG Pipeline (Days 6 + 9)
Orchestrates: query → embed → retrieve → generate → evaluate → structured response.
"""

import os
from dataclasses import dataclass, field
from core.embedder import Embedder
from core.vector_store import VectorStore
from core.llm import LLMClient
from core.ingestion import parse_pdf
from core.document_store import DocumentStore
from core.evaluator import evaluate_response, EvalResult
from dotenv import load_dotenv

load_dotenv()

TOP_K = int(os.getenv("TOP_K", 5))


@dataclass
class Citation:
    text: str
    page: int
    source_file: str
    similarity_score: float
    rank: int

    def to_dict(self) -> dict:
        return {
            "text": self.text[:300],
            "page": self.page,
            "source_file": self.source_file,
            "similarity_score": round(self.similarity_score, 4),
            "rank": self.rank,
        }


@dataclass
class RAGResponse:
    question: str
    answer: str
    citations: list[Citation]
    doc_id: str
    top_score: float
    language: str = "en"
    eval: EvalResult = None

    def to_dict(self) -> dict:
        d = {
            "question": self.question,
            "answer": self.answer,
            "citations": [c.to_dict() for c in self.citations],
            "doc_id": self.doc_id,
            "top_score": round(self.top_score, 4),
            "language": self.language,
        }
        if self.eval:
            d["evaluation"] = self.eval.to_dict()
        return d

    def pretty_print(self):
        print(f"\n{'='*55}")
        print(f"Q: {self.question}")
        print(f"{'='*55}")
        print(f"\nA: {self.answer}")
        print(f"\n── Citations ({'─'*38})")
        for c in self.citations:
            print(f"  [{c.rank}] Page {c.page} | score={c.similarity_score:.3f}")
            print(f"      {c.text[:120].replace(chr(10), ' ')}...")
        print(f"\n  Top similarity : {self.top_score:.3f}")
        if self.eval:
            self.eval.pretty_print()


class RAGPipeline:
    def __init__(self, verbose: bool = True):
        self.embedder  = Embedder(verbose=verbose)
        self.llm       = LLMClient(verbose=verbose)
        self.doc_store = DocumentStore()
        self._vector_stores: dict[str, VectorStore] = {}

    def load_pdf(self, file_path: str, force_reparse: bool = False) -> str:
        from core.ingestion import generate_doc_id
        doc_id = generate_doc_id(file_path)

        if doc_id in self._vector_stores and not force_reparse:
            print(f"✓  Already loaded: {doc_id}")
            return doc_id

        if VectorStore.exists(doc_id) and not force_reparse:
            print(f"📂  Loading existing index for {doc_id}")
            self._vector_stores[doc_id] = VectorStore.load(doc_id)
            return doc_id

        print(f"📄  First load — parsing and indexing {file_path}")
        doc        = parse_pdf(file_path, verbose=True)
        self.doc_store.add(doc)
        embeddings = self.embedder.embed_chunks(doc.chunks, verbose=True)
        store      = VectorStore(doc_id=doc_id, dimension=self.embedder.dimension)
        store.add(doc.chunks, embeddings)
        store.save()
        self._vector_stores[doc_id] = store
        return doc_id

    def query(
        self,
        question: str,
        doc_id: str,
        k: int = TOP_K,
        language: str = "en",
        run_eval: bool = False,
    ) -> RAGResponse:
        if doc_id not in self._vector_stores:
            raise ValueError(f"Document {doc_id} not loaded. Call load_pdf() first.")

        store       = self._vector_stores[doc_id]
        q_embedding = self.embedder.embed_query(question)
        results     = store.search(q_embedding, k=k)

        if not results:
            return RAGResponse(
                question=question,
                answer="No relevant content found in the document.",
                citations=[], doc_id=doc_id, top_score=0.0, language=language,
            )

        answer = self.llm.generate_rag_answer(question, results)

        citations = [
            Citation(
                text=r["chunk"].text,
                page=r["chunk"].page,
                source_file=r["chunk"].source_file,
                similarity_score=r["score"],
                rank=r["rank"],
            )
            for r in results
        ]

        eval_result = None
        if run_eval:
            print("📊  Running RAGAS evaluation...")
            contexts = [r["chunk"].text for r in results]
            eval_result = evaluate_response(
                question=question,
                answer=answer,
                contexts=contexts,
                top_similarity=results[0]["score"],
            )

        return RAGResponse(
            question=question,
            answer=answer,
            citations=citations,
            doc_id=doc_id,
            top_score=results[0]["score"],
            language=language,
            eval=eval_result,
        )

    def list_documents(self) -> list[dict]:
        return self.doc_store.list_docs()
