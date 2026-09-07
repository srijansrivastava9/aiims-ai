"""Build and cache local .npy embeddings from Supabase tables.

Handles:
- Empty tables (0 rows) gracefully
- Offline fallback using seed JSON files
- 384-dim all-MiniLM-L6-v2 vectors (NOT 1536-dim OpenAI)
- Auto-creates embeddings/ directory
"""
import json
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    get_supabase_client,
    DATA_DIR,
    EMBEDDINGS_DIR,
    EMBEDDING_MODEL,
    EMBEDDING_DIM,
    TABLE_MEDDRA,
    TABLE_GUIDELINES,
)

# Load model once
print(f"Loading embedding model: {EMBEDDING_MODEL} ...")
_model = SentenceTransformer(EMBEDDING_MODEL)


def fetch_rows(sb, table_name, text_column):
    """Fetch rows from Supabase. Returns list of dicts with 'id' and text_column."""
    try:
        resp = sb.table(table_name).select(f"id,{text_column}").execute()
        rows = resp.data or []
        print(f"  [live] {table_name}: {len(rows)} rows")
        return rows
    except Exception as e:
        print(f"  [live] {table_name}: FAILED — {e}")
        return []


def fetch_from_json(table_name, text_column):
    """Fallback: load from seed JSON files."""
    if table_name == TABLE_MEDDRA:
        filename = "seed_meddra_terms.json"
        text_key = "term"
    elif table_name == TABLE_GUIDELINES:
        filename = "seed_guideline_chunks.json"
        text_key = "content"
    else:
        return []

    path = DATA_DIR / filename
    if not path.exists():
        print(f"  [fallback] {filename} not found")
        return []

    rows = json.loads(path.read_text(encoding="utf-8"))
    # Add synthetic IDs since JSON doesn't have them
    for i, r in enumerate(rows):
        r["id"] = f"local_{i}"
    print(f"  [fallback] {table_name}: {len(rows)} rows from {filename}")
    return rows


def build(table_name, text_column):
    """Build embeddings for a table and save as .npy files."""
    sb = get_supabase_client()
    rows = fetch_rows(sb, table_name, text_column)

    if not rows:
        print(f"  -> Live fetch returned 0 rows. Trying fallback...")
        rows = fetch_from_json(table_name, text_column)

    if not rows:
        print(f"  -> WARNING: No data available for {table_name}. Skipping.")
        print(f"     (Did you run seed_insert.sql in Supabase SQL Editor?)")
        return

    texts = [r[text_column] for r in rows]
    ids = [r["id"] for r in rows]

    print(f"  Encoding {len(texts)} texts...")
    vecs = _model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

    # vecs is 2D array (n, 384) — but handle edge case of single row
    if vecs.ndim == 1:
        vecs = vecs.reshape(1, -1)

    print(f"  Saved {table_name}: {len(ids)} vectors, dim={vecs.shape[1]}")

    np.save(EMBEDDINGS_DIR / f"{table_name}_ids.npy", np.array(ids, dtype=object))
    np.save(EMBEDDINGS_DIR / f"{table_name}_vecs.npy", vecs)


def main():
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Embeddings will be cached in: {EMBEDDINGS_DIR}")
    print(f"Model dimension: {EMBEDDING_DIM}")
    print()

    build(TABLE_MEDDRA, "term")
    build(TABLE_GUIDELINES, "content")

    print("\nDone. Files in embeddings/:")
    for f in sorted(EMBEDDINGS_DIR.glob("*.npy")):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
