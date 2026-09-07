# Schema Recon Notes

Date: 04 Sep 2026

## Verified Tables (from backend/schema.sql)

### meddra_terms
- id: uuid (auto)
- term: text
- code: text
- embedding: vector(1536)  <-- MISMATCH: our model emits 384-dim

### guideline_chunks
- id: uuid (auto)
- source: text
- content: text
- embedding: vector(1536)  <-- MISMATCH: our model emits 384-dim

### adverse_events
- id: uuid (auto)
- description: text (AI input)
- meddra_term: text -- reserved for AI coding output
- is_serious: boolean
- status: text
- regulatory_deadline: timestamp (auto-filled by trigger)

## Open Decisions

1. **Vector dimension mismatch**: schema has vector(1536), model emits 384.
   - Option A: Alter column to vector(384) [RECOMMENDED for hackathon]
   - Option B: Switch to OpenAI embeddings (requires API key, slower)
   - Current workaround: store vectors locally as .npy files

2. **RLS policies needed** (Person B):
   - SELECT/INSERT on meddra_terms and guideline_chunks
   - UPDATE on adverse_events (for --write-back)

3. **AE deadline trigger**: SAE 24h / non-serious 15d -- marked DEMO PLACEHOLDER
