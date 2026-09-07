"""Shared configuration for all AI scripts."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# Embedding model: 384-dim, fast, good for demo
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Local cache paths
EMBEDDINGS_DIR = ROOT / "embeddings"
DATA_DIR = ROOT / "data"

# Supabase table names (must match BACKEND_SPEC.md exactly)
TABLE_MEDDRA = "meddra_terms"
TABLE_GUIDELINES = "guideline_chunks"
TABLE_ADVERSE_EVENTS = "adverse_events"

# Top-k retrieval settings
TOP_K_MEDDRA = 5
TOP_K_GUIDELINES = 3


def get_supabase_client():
    """Return a Supabase client."""
    from supabase import create_client
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
