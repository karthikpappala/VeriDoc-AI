"""
VeriDoc AI — Embedder (Day 3)
Converts text chunks into dense vectors using sentence-transformers.
"""

import os
import numpy as np
from sentence_transformers import SentenceTransformer
from core.ingestion import Chunk

DEFAULT_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


class Embedder:
    """
    Wraps a sentence-transformer model.
    Loads once, reused across all queries and documents.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL, verbose: bool = True):
        if verbose:
            print(f"🔄  Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.dimension = self.model.get_sentence_embedding_dimension()
        if verbose:
            print(f"    Embedding dimension : {self.dimension}")
            print(f"    ✓ Model ready")

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """
        Embed a list of strings.
        Returns numpy array of shape (len(texts), dimension).
        """
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,  # cosine similarity via dot product
        )
        return embeddings.astype(np.float32)

    def embed_chunks(self, chunks: list[Chunk], verbose: bool = True) -> np.ndarray:
        """
        Embed a list of Chunk objects.
        Returns numpy array of shape (len(chunks), dimension).
        """
        if verbose:
            print(f"🔢  Embedding {len(chunks)} chunks...")
        texts = [c.text for c in chunks]
        embeddings = self.embed_texts(texts)
        if verbose:
            print(f"    Shape : {embeddings.shape}")
            print(f"    ✓ Done")
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string.
        Returns numpy array of shape (1, dimension).
        """
        return self.embed_texts([query])
