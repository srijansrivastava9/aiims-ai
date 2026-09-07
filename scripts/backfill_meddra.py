#!/usr/bin/env python3
"""
backfill_meddra.py — batch MedDRA coding for adverse events.

Runs the same suggest-then-write step as ae_assist.py, but over every eligible AE
at once, so the dashboard shows populated meddra_term values instead of nulls.

Follows BACKEND_SPEC.md:
  - authenticates with signInWithPassword() so auth.uid() is set and RLS applies
    (the anon key on its own leaves auth.uid() null and every policy fails closed)
  - anon key only; refuses to run with the service_role key
  - reads meddra_terms per the API contract, similarity computed in app code
  - writes only adverse_events.meddra_term, the column reserved for this feature

Safe by default: nothing is written unless --apply is passed.
Idempotent: skips rows that already have a meddra_term unless --overwrite.

.env needs:
    SUPABASE_URL=...
    SUPABASE_ANON_KEY=...
    AI_USER_EMAIL=...
    AI_USER_PASSWORD=...

Usage:
    python scripts/backfill_meddra.py                    # dry run
    python scripts/backfill_meddra.py --limit 5          # dry run, first 5
    python scripts/backfill_meddra.py --apply
    python scripts/backfill_meddra.py --apply --min-score 0.40
    python scripts/backfill_meddra.py --apply --study <uuid>
"""

import argparse
import base64
import json
import os
import sys

import numpy as np
from dotenv import load_dotenv
from supabase import create_client

MODEL_NAME = "all-MiniLM-L6-v2"


def assert_not_service_role(key: str) -> None:
    """BACKEND_SPEC rule 5: the service_role key must never appear in AI code.

    It also bypasses RLS, which would hide exactly the permission problems we
    want to surface before demo day.
    """
    try:
        payload = key.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return  # not a JWT we can read; let Supabase reject it if it's wrong
    if claims.get("role") == "service_role":
        sys.exit(
            "Refusing to run: SUPABASE_ANON_KEY holds a service_role key.\n"
            "That key bypasses RLS and must not be used in /ai (BACKEND_SPEC.md).\n"
            "Copy the anon/public key from Project Settings -> API instead."
        )


def get_client():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")
    email = os.environ.get("AI_USER_EMAIL")
    password = os.environ.get("AI_USER_PASSWORD")

    missing = [n for n, v in [
        ("SUPABASE_URL", url), ("SUPABASE_ANON_KEY", key),
        ("AI_USER_EMAIL", email), ("AI_USER_PASSWORD", password),
    ] if not v]
    if missing:
        sys.exit("Missing in .env: " + ", ".join(missing))

    assert_not_service_role(key)

    sb = create_client(url, key)
    try:
        sb.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        sys.exit(f"Sign-in failed for {email}: {e}")

    uid = sb.auth.get_user().user.id
    role = "unknown"
    try:
        prof = sb.table("profiles").select("role").eq("id", uid).single().execute()
        role = (prof.data or {}).get("role", "unknown")
    except Exception:
        pass

    print(f"Signed in as {email}  (role: {role})")
    if role in ("regulator_readonly", "ethics_committee", "monitor"):
        print(f"  Warning: '{role}' is a narrow/read-oriented role under the spec's\n"
              f"  RLS design. Selects may return fewer rows than expected and the\n"
              f"  write may be denied. 'pharmacovigilance' or 'admin' fits better.")
    return sb


def embed(model, texts):
    """L2-normalised embeddings, so cosine similarity is a plain dot product."""
    vecs = np.asarray(model.encode(texts, show_progress_bar=False), dtype=np.float32)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms


def fetch_meddra_terms(sb):
    # Contract: select from meddra_terms, similarity in app code. The embedding
    # column is vector(1536) and unused by us, so we don't pull it.
    rows = sb.table("meddra_terms").select("id, term, code").execute().data or []
    if not rows:
        sys.exit(
            "meddra_terms returned 0 rows.\n"
            "Either it isn't seeded (run data/seed_insert.sql in the SQL editor),\n"
            "or this role has no select policy on it — Person B, open item 3."
        )
    return rows


def fetch_adverse_events(sb, overwrite, study_id, limit):
    q = sb.table("adverse_events").select(
        "id, study_id, description, meddra_term, is_serious, status"
    )
    if study_id:
        q = q.eq("study_id", study_id)
    rows = q.execute().data or []

    todo, no_desc, already = [], 0, 0
    for r in rows:
        if not (r.get("description") or "").strip():
            no_desc += 1
            continue
        if r.get("meddra_term") and not overwrite:
            already += 1
            continue
        todo.append(r)

    return (todo[:limit] if limit else todo), no_desc, already, len(rows)


def main():
    p = argparse.ArgumentParser(description="Batch MedDRA coding for adverse events.")
    p.add_argument("--apply", action="store_true",
                   help="Actually write. Without this it's a dry run.")
    p.add_argument("--overwrite", action="store_true",
                   help="Recode AEs that already have a meddra_term.")
    p.add_argument("--study", metavar="UUID", default=None,
                   help="Restrict to one study_id.")
    p.add_argument("--limit", type=int, default=0,
                   help="Only process the first N eligible rows.")
    p.add_argument("--min-score", type=float, default=0.0,
                   help="Leave meddra_term null below this cosine score (0-1).")
    args = p.parse_args()

    sb = get_client()

    from sentence_transformers import SentenceTransformer  # keeps --help fast
    print(f"Loading {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)

    terms = fetch_meddra_terms(sb)
    print(f"Loaded {len(terms)} MedDRA terms.")
    term_vecs = embed(model, [t["term"] for t in terms])

    todo, no_desc, already, total = fetch_adverse_events(
        sb, args.overwrite, args.study, args.limit)
    print(f"AEs visible under RLS: {total}   eligible: {len(todo)}   "
          f"(skipped {already} already coded, {no_desc} with no description)")

    if total == 0:
        print("\nNo adverse_events visible. Either none are seeded, or this role's\n"
              "RLS scope excludes them. Confirm with a plain select before debugging here.")
        return
    if not todo:
        print("Nothing to do.")
        return

    ae_vecs = embed(model, [r["description"] for r in todo])
    sims = ae_vecs @ term_vecs.T
    best_idx = sims.argmax(axis=1)
    best_score = sims.max(axis=1)

    print(f"\n--- {'APPLY' if args.apply else 'DRY RUN'} ---")

    applied = low_conf = failed = 0
    rls_hit = False

    for row, ti, score in zip(todo, best_idx, best_score):
        term = terms[ti]
        flag = "SAE" if row.get("is_serious") else "ae "
        snippet = row["description"][:50].replace("\n", " ")
        line = f"{flag} {score:.3f}  {snippet:<52} -> {term['term']} ({term['code']})"

        if score < args.min_score:
            print(f"  skip  {line}")
            low_conf += 1
            continue

        if not args.apply:
            print(f"  plan  {line}")
            continue

        try:
            sb.table("adverse_events") \
              .update({"meddra_term": term["term"]}) \
              .eq("id", row["id"]) \
              .execute()
            print(f"  ok    {line}")
            applied += 1
        except Exception as e:
            msg = str(e)
            print(f"  FAIL  {line}\n        {msg}")
            failed += 1
            if "42501" in msg or "row-level security" in msg.lower():
                rls_hit = True
                break

    print(f"\nWritten: {applied}   Low-confidence skips: {low_conf}   Failed: {failed}")

    if rls_hit:
        print(
            "\nStopped on row-level security (42501).\n"
            "Person B needs an UPDATE policy on adverse_events letting this role set\n"
            "meddra_term, or an RPC that does the write. Nothing is half-written —\n"
            "re-run once the policy exists."
        )
        sys.exit(1)

    if applied:
        print("\nNote: the audit trigger fires per update, so this added "
              f"{applied} audit_log rows.")
    if not args.apply:
        print("\nDry run only. Re-run with --apply to write these values.")


if __name__ == "__main__":
    main()
