# Demo-Day Runbook — Person C AI Feature

## Prerequisites
1. `.env` file configured with SUPABASE_URL and SUPABASE_ANON_KEY
2. Python dependencies installed: `pip install -r requirements.txt`
3. Seed data inserted into Supabase (via SQL Editor)

## Step-by-Step Demo Flow

### Step 1: Insert Seed Data (one-time)
```bash
# Option A: SQL Editor (recommended — bypasses RLS)
# Open Supabase -> SQL Editor -> paste data/seed_insert.sql -> Run

# Option B: Python script (requires RLS policies from Person B)
python scripts/insert_seed.py all
```

### Step 2: Build Local Embeddings Cache
```bash
python scripts/build_embeddings.py
```
Expected output:
```
Loading embedding model: all-MiniLM-L6-v2 ...
[live] meddra_terms: 75 rows
  Encoding 75 texts...
  Saved meddra_terms: 75 vectors, dim=384
[live] guideline_chunks: 40 rows
  Encoding 40 texts...
  Saved guideline_chunks: 40 vectors, dim=384
```

### Step 3: Test AE Assist (Offline/Dummy Mode)
```bash
python scripts/ae_assist.py --dummy
python scripts/ae_assist.py --text "patient experienced severe headache and nausea after herbal dose"
```

### Step 4: Test AE Assist (Live Mode)
```bash
# With a real AE row ID from the database
python scripts/ae_assist.py --ae-id <uuid>

# With LLM summary
python scripts/ae_assist.py --ae-id <uuid> --llm

# With write-back (requires Person B's UPDATE policy)
python scripts/ae_assist.py --ae-id <uuid> --write-back
```

### Step 5: Full Pipeline Test
```bash
# Verify everything works end-to-end
python scripts/test_read.py
python scripts/build_embeddings.py
python scripts/ae_assist.py --dummy
python scripts/ae_assist.py --text "severe chest pain and shortness of breath"
```

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `42501 RLS` on insert | No INSERT policy | Run `data/seed_insert.sql` in SQL Editor |
| `0 rows` from live fetch | No SELECT policy | Ask Person B to add SELECT policies |
| `IndexError: tuple index out of range` | Empty table + no fallback | Use fixed `build_embeddings.py` (handles 0 rows) |
| Write-back fails | No UPDATE policy | Ask Person B to add UPDATE policy or RPC |
| `No such file` for ae_assist.py | File missing | Copy `scripts/ae_assist.py` from this package |

## Files Delivered
```
ai/
├── requirements.txt
├── .env.example
├── scripts/
│   ├── config.py
│   ├── test_read.py
│   ├── seed_generate.py
│   ├── insert_seed.py
│   ├── build_embeddings.py      <-- FIXED: handles empty tables
│   ├── similarity.py
│   └── ae_assist.py             <-- NEW: was missing!
├── data/
│   ├── seed_meddra_terms.json
│   ├── seed_guideline_chunks.json
│   ├── seed_insert.sql
│   ├── dummy_meddra.json
│   ├── dummy_guidelines.json
│   └── send_to_person_b.sql     <-- SQL to give Person B
├── embeddings/                  <-- .npy cache (auto-created)
└── notes/
    ├── schema_recon.md
    └── api_contract_for_person_a.md
```
