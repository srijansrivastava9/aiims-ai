# Person C — AI / RAG / Seed Data (AIIA Clinical Trials Dashboard)

Owner: Person C. Do NOT touch /frontend or /backend without asking first.

## Scope (from PROJECT_CONTEXT.md + BACKEND_SPEC.md)
- AI feature: AE description → MedDRA term suggestion + guideline RAG lookup
- Tables you may use: `adverse_events.description`, `guideline_chunks`, `meddra_terms`
- Synthetic/demo data ONLY. No real patient data, ever.
- Embedding + similarity run in YOUR app code, not in Postgres.

## Setup
```bash
cd ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Get SUPABASE_URL and SUPABASE_ANON_KEY from Person B. Never use service_role.

```bash
cp .env.example .env   # then fill in the two values
export $(grep -v '^#' .env | xargs)   # or use python-dotenv (included)
```

## Segment 1 — smoke test
```bash
python scripts/test_read.py          # real Supabase read
python scripts/test_read.py --dummy  # offline fallback (no Supabase needed)
```

## Folder layout
- `scripts/` — all code
- `data/` — dummy JSON data (offline dev), seed data generators output here
- `embeddings/` — .npy vector stores keyed by row id (local, no schema change)
- `notes/` — schema recon + decisions log
