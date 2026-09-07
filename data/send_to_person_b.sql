-- ============================================================
-- SQL TO SEND TO PERSON B
-- Add this block to schema.sql (append with date comment)
-- ============================================================
-- Added 04 Sep 2026 — Person C AI feature support

-- 1. RLS SELECT policies for AI tables (needed for build_embeddings.py and ae_assist.py)
create policy meddra_terms_select on meddra_terms for select
  to authenticated using (true);

create policy guideline_chunks_select on guideline_chunks for select
  to authenticated using (true);

-- 2. RLS INSERT policies for AI tables (needed for insert_seed.py)
--    Using 'authenticated' — your script signs in first, or use service_role
--    For hackathon simplicity, allow any authenticated user:
create policy meddra_terms_insert on meddra_terms for insert
  to authenticated with check (true);

create policy guideline_chunks_insert on guideline_chunks for insert
  to authenticated with check (true);

-- 3. UPDATE policy on adverse_events (needed for ae_assist.py --write-back)
create policy adverse_events_update_meddra on adverse_events for update
  to authenticated using (true) with check (true);

-- 4. FIX: Vector dimension mismatch
--    Option A (RECOMMENDED): alter columns to match all-MiniLM-L6-v2 (384-dim)
--    This drops existing vectors in those columns (fine — we store locally as .npy)
alter table meddra_terms alter column embedding type vector(384);
alter table guideline_chunks alter column embedding type vector(384);

--    Option B (alternative): switch to OpenAI embeddings in Person C's code
--    Then keep vector(1536) and have Person C use OpenAI API instead of local model
--    (slower, requires API key, not recommended for hackathon)

-- 5. Optional: RPC for atomic AE write-back (cleaner than raw UPDATE)
create or replace function mark_ae_meddra(p_ae_id uuid, p_meddra_term text)
returns adverse_events as $$
  update adverse_events
  set meddra_term = p_meddra_term
  where id = p_ae_id
  returning *;
$$ language sql security definer;
