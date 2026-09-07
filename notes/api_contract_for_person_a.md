# AI Feature API Contract — For Person A (Frontend)

## How to call the AI feature from React

### Option 1: Direct Supabase query (read-only)
```javascript
// Fetch suggested MedDRA terms and guidelines
// (Person C's similarity search runs server-side via RPC or client-side)

// Get all meddra terms
const { data: terms } = await supabase.from('meddra_terms').select('*');

// Get all guideline chunks
const { data: chunks } = await supabase.from('guideline_chunks').select('*');
```

### Option 2: Call Person C's Python script (if running locally)
```bash
# From your frontend or a serverless function:
# POST to a local endpoint, or run the script via shell

python scripts/ae_assist.py --text "patient headache and nausea" --llm
```

### Option 3: Person B adds an RPC (recommended for integration)
```sql
-- Person B can add this RPC so frontend calls it directly:
create or replace function suggest_meddra_for_ae(p_ae_id uuid)
returns jsonb as $$
  -- This would call the embedding model internally
  -- OR return pre-computed suggestions
$$ language plpgsql;
```

## Data Flow
```
Frontend (React)
  -> Supabase: fetch AE description
  -> [Option A] Send text to Person C's script (if co-located)
  -> [Option B] Person C's script runs separately, writes meddra_term back
  -> Frontend re-fetches AE to show updated meddra_term
```

## Key Fields
| Field | Table | Type | Notes |
|-------|-------|------|-------|
| description | adverse_events | text | AI input — the raw AE description |
| meddra_term | adverse_events | text | AI output — the chosen MedDRA term |
| term | meddra_terms | text | Candidate terms for matching |
| code | meddra_terms | text | Synthetic MedDRA code (not licensed) |
| content | guideline_chunks | text | Guideline text for RAG retrieval |
| source | guideline_chunks | text | Source document (GCP, Ayush SOP, etc.) |

## Important Notes
- All MedDRA codes are **synthetic/demo only** — not licensed real MedDRA
- All deadline values are **DEMO PLACEHOLDER** — not legal facts
- The AI feature uses **all-MiniLM-L6-v2** (384-dim) embeddings stored locally
