"""
VeriDoc AI — LLM Client (Day 5)
Connects to Groq API for fast, free LLM inference.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("LLM_MODEL", "llama3-8b-8192")


class LLMClient:
    """
    Thin wrapper around the Groq API.
    Handles prompt formatting and response parsing.
    """

    def __init__(self, model: str = DEFAULT_MODEL, verbose: bool = True):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found. Add it to your .env file.")
        self.client = Groq(api_key=api_key)
        self.model = model
        if verbose:
            print(f"✓ LLM ready  model={self.model}")

    def generate(
        self,
        prompt: str,
        system: str = "You are a helpful assistant that answers questions based on provided document context.",
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """
        Send a prompt and return the text response.
        Low temperature (0.2) keeps answers factual and grounded.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    def generate_rag_answer(
        self,
        question: str,
        context_chunks: list[dict],
    ) -> str:
        """
        Generate an answer grounded in retrieved chunks.
        Instructs the model to cite page numbers.

        Args:
            question: the user's question
            context_chunks: list of {chunk, score, rank} from VectorStore.search()
        """
        # Build context block with page references
        context_parts = []
        for item in context_chunks:
            chunk = item["chunk"]
            context_parts.append(
                f"[Source: {chunk.source_file}, Page {chunk.page}]\n{chunk.text}"
            )
        context = "\n\n---\n\n".join(context_parts)

        prompt = f"""You are a document assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I could not find this information in the document."
Always cite the page number(s) you used, like: (Source: Page 3)

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

        return self.generate(prompt)
