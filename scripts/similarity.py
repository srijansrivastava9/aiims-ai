"""Cosine similarity search over locally cached embeddings."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from config import EMBEDDINGS_DIR, EMBEDDING_MODEL, TOP_K_MEDDRA, TOP_K_GUIDELINES
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer(EMBEDDING_MODEL)


def cosine_similarity(a, b):
    """Compute cosine similarity between two arrays."""
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-10)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-10)
    return np.dot(a_norm, b_norm.T)


def load_embeddings(table_name):
    """Load cached ids and vectors for a table. Returns (ids, vecs) or (None, None)."""
    ids_path = EMBEDDINGS_DIR / f"{table_name}_ids.npy"
    vecs_path = EMBEDDINGS_DIR / f"{table_name}_vecs.npy"

    if not ids_path.exists() or not vecs_path.exists():
        return None, None

    ids = np.load(ids_path, allow_pickle=True)
    vecs = np.load(vecs_path)
    return ids, vecs


def search(query_text, table_name, top_k=5):
    """Return top-k most similar rows for a query text."""
    ids, vecs = load_embeddings(table_name)
    if ids is None:
        return []

    query_vec = _model.encode([query_text], convert_to_numpy=True)
    if query_vec.ndim == 1:
        query_vec = query_vec.reshape(1, -1)

    sims = cosine_similarity(query_vec, vecs)[0]
    top_idx = np.argsort(sims)[::-1][:top_k]

    return [{"id": ids[i], "score": float(sims[i])} for i in top_idx]


def search_meddra(query_text, top_k=TOP_K_MEDDRA):
    from config import TABLE_MEDDRA
    return search(query_text, TABLE_MEDDRA, top_k)


def search_guidelines(query_text, top_k=TOP_K_GUIDELINES):
    from config import TABLE_GUIDELINES
    return search(query_text, TABLE_GUIDELINES, top_k)
