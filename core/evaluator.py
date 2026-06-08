"""
VeriDoc AI — RAGAS Evaluator (Day 9, updated for ragas 0.4.x)
Faithfulness  : is the answer grounded in the retrieved context?
Answer Relevancy: does the answer actually address the question?
"""

import os
import math
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class EvalResult:
    faithfulness: float
    answer_relevancy: float
    confidence: float
    hallucination_risk: str
    top_similarity: float

    def to_dict(self) -> dict:
        return {
            "faithfulness": round(self.faithfulness, 3),
            "answer_relevancy": round(self.answer_relevancy, 3),
            "confidence": round(self.confidence, 3),
            "hallucination_risk": self.hallucination_risk,
            "top_similarity": round(self.top_similarity, 3),
        }

    def pretty_print(self):
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        print(f"\n── Evaluation Scores ───────────────────────────────────")
        print(f"  Faithfulness     : {self.faithfulness:.3f}  (hallucination check)")
        print(f"  Answer Relevancy : {self.answer_relevancy:.3f}  (answers the question?)")
        print(f"  Top Similarity   : {self.top_similarity:.3f}  (retrieval quality)")
        print(f"  Confidence       : {self.confidence:.3f}")
        print(f"  Hallucination    : {risk_emoji.get(self.hallucination_risk,'?')}  {self.hallucination_risk.upper()}")


def _risk(faithfulness: float, confidence: float) -> str:
    if faithfulness >= 0.7 and confidence >= 0.6:
        return "low"
    elif faithfulness >= 0.4 or confidence >= 0.4:
        return "medium"
    return "high"


def evaluate_response(
    question: str,
    answer: str,
    contexts: list[str],
    top_similarity: float,
) -> EvalResult:
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from langchain_groq import ChatGroq
        from langchain_huggingface import HuggingFaceEmbeddings
        from datasets import Dataset

        eval_data = Dataset.from_dict({
            "question": [question],
            "answer":   [answer],
            "contexts": [contexts],
        })

        ragas_llm = LangchainLLMWrapper(
            ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model_name=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
                temperature=0,
            )
        )
        ragas_emb = LangchainEmbeddingsWrapper(
            HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        )

        # Set LLM/embeddings on each metric explicitly (ragas 0.4.x style)
        faithfulness.llm       = ragas_llm
        answer_relevancy.llm   = ragas_llm
        answer_relevancy.embeddings = ragas_emb

        result = evaluate(
            dataset=eval_data,
            metrics=[faithfulness, answer_relevancy],
            raise_exceptions=False,
        )

        df = result.to_pandas()
        faith = float(df["faithfulness"].iloc[0])
        relev = float(df["answer_relevancy"].iloc[0])

        if math.isnan(faith):
            faith = _fallback_faithfulness(answer, contexts)
        if math.isnan(relev):
            relev = top_similarity

    except Exception as e:
        print(f"⚠️  RAGAS evaluation failed ({e}), using fallback scoring.")
        faith = _fallback_faithfulness(answer, contexts)
        relev = top_similarity

    confidence = 0.5 * faith + 0.3 * relev + 0.2 * top_similarity

    return EvalResult(
        faithfulness=faith,
        answer_relevancy=relev,
        confidence=confidence,
        hallucination_risk=_risk(faith, confidence),
        top_similarity=top_similarity,
    )


def _fallback_faithfulness(answer: str, contexts: list[str]) -> float:
    """Word-overlap faithfulness when RAGAS API is unavailable."""
    if not answer or not contexts:
        return 0.0
    combined = " ".join(contexts).lower()
    sentences = [s.strip() for s in answer.replace("\n", " ").split(".") if len(s.strip()) > 10]
    if not sentences:
        return 0.5
    grounded = 0
    for sentence in sentences:
        words = [w.lower() for w in sentence.split() if len(w) > 4]
        if not words:
            continue
        if sum(1 for w in words if w in combined) / len(words) >= 0.5:
            grounded += 1
    return grounded / len(sentences)
