# backend/rag/vector_store.py

import os
import pickle
import faiss
from typing import List, Dict, Any
import numpy as np

from .embedder import embed_texts


# ---------------------------------------------------------
# File Paths
# ---------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
INDEX_DIR = os.path.join(BASE_DIR, "data", "rag_index")
INDEX_FILE = os.path.join(INDEX_DIR, "index.faiss")
META_FILE = os.path.join(INDEX_DIR, "meta.pkl")

os.makedirs(INDEX_DIR, exist_ok=True)


# ---------------------------------------------------------
# Vector Store Class (RAG + Semantic Cache)
# ---------------------------------------------------------
class VectorStore:
    def __init__(self):
        self.index = None           # RAG index
        self.meta = []              # List of dicts with {text, source}

        # Semantic Cache
        self.cache_index = faiss.IndexFlatL2(1536)  # embedding dimension
        self.cache_ids: List[str] = []

        self._load()

    # -----------------------------------------------------
    # Load FAISS + metadata for RAG
    # -----------------------------------------------------
    def _load(self):
        if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(META_FILE, "rb") as f:
                self.meta = pickle.load(f)
        else:
            # Empty FAISS index for RAG
            self.index = faiss.IndexFlatL2(1536)
            self.meta = []

    # -----------------------------------------------------
    # Add documents to RAG vector store
    # -----------------------------------------------------
    def add_documents(self, texts: List[str], sources: List[str]):
        embeddings = embed_texts(texts)
        embeddings = np.array(embeddings).astype("float32")

        self.index.add(embeddings)

        for text, src in zip(texts, sources):
            self.meta.append({"text": text, "source": src})

        self._save()

    # -----------------------------------------------------
    # Save FAISS + metadata
    # -----------------------------------------------------
    def _save(self):
        faiss.write_index(self.index, INDEX_FILE)
        with open(META_FILE, "wb") as f:
            pickle.dump(self.meta, f)

    # -----------------------------------------------------
    # RAG Semantic Search
    # -----------------------------------------------------
    def search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        query_vec = embed_texts([query])[0]
        query_vec = np.array([query_vec]).astype("float32")

        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.meta):
                results.append(self.meta[idx])

        return results

    # -----------------------------------------------------
    # SEMANTIC CACHE SECTION (FAISS-based)
    # -----------------------------------------------------

    def add_cache_embedding(self, cache_id: str, vector: np.ndarray):
        """
        Add embedding to semantic cache FAISS index.
        """
        vec = np.array([vector], dtype=np.float32)
        self.cache_index.add(vec)
        self.cache_ids.append(cache_id)

    def search_semantic_cache(self, query_vec: np.ndarray, top_k: int = 1):
        """
        Search the semantic cache using FAISS.
        Returns (similarity_scores, cache_ids)
        """
        if self.cache_index.ntotal == 0:
            return [], []

        q = np.array([query_vec], dtype=np.float32)
        distances, idxs = self.cache_index.search(q, top_k)

        # convert L2 distances → similarity scores
        similarities = 1.0 - distances[0]

        ids = []
        for idx in idxs[0]:
            ids.append(self.cache_ids[idx])

        return similarities, ids


# ---------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------
vector_store = VectorStore()
