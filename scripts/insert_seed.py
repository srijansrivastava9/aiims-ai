"""Insert seed data into Supabase with deduping. Safe to re-run."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import get_supabase_client, DATA_DIR, TABLE_MEDDRA, TABLE_GUIDELINES


def load_json(filename):
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


def insert_meddra(sb):
    rows = load_json("seed_meddra_terms.json")
    # Fetch existing codes to avoid duplicates
    existing = sb.table(TABLE_MEDDRA).select("code").execute().data or []
    existing_codes = {r["code"] for r in existing}

    new = [r for r in rows if r["code"] not in existing_codes]
    if not new:
        print(f"  {TABLE_MEDDRA}: no new rows to insert (all {len(rows)} already exist)")
        return

    try:
        sb.table(TABLE_MEDDRA).insert(new).execute()
        print(f"  {TABLE_MEDDRA}: inserted {len(new)} new rows ({len(existing_codes)} already existed)")
    except Exception as e:
        print(f"  {TABLE_MEDDRA}: INSERT FAILED — {e}")
        print("  >>> Workaround: run data/seed_insert.sql in Supabase SQL Editor <<<")


def insert_guidelines(sb):
    rows = load_json("seed_guideline_chunks.json")
    # Fetch existing (source, content) pairs
    existing = sb.table(TABLE_GUIDELINES).select("source,content").execute().data or []
    existing_keys = {(r["source"], r["content"]) for r in existing}

    new = [r for r in rows if (r["source"], r["content"]) not in existing_keys]
    if not new:
        print(f"  {TABLE_GUIDELINES}: no new rows to insert (all {len(rows)} already exist)")
        return

    try:
        sb.table(TABLE_GUIDELINES).insert(new).execute()
        print(f"  {TABLE_GUIDELINES}: inserted {len(new)} new rows ({len(existing_keys)} already existed)")
    except Exception as e:
        print(f"  {TABLE_GUIDELINES}: INSERT FAILED — {e}")
        print("  >>> Workaround: run data/seed_insert.sql in Supabase SQL Editor <<<")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Insert seed data into Supabase")
    parser.add_argument("target", nargs="?", default="all", choices=["all", "meddra", "guidelines"])
    args = parser.parse_args()

    sb = get_supabase_client()

    if args.target in ("all", "meddra"):
        insert_meddra(sb)
    if args.target in ("all", "guidelines"):
        insert_guidelines(sb)


if __name__ == "__main__":
    main()
