"""Smoke test: verify Supabase connection and table access."""
import sys
from pathlib import Path

# Add scripts folder to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_supabase_client, TABLE_MEDDRA, TABLE_GUIDELINES, TABLE_ADVERSE_EVENTS


def test_table(sb, table_name, limit=3):
    """Try to read from a table. Returns (success, count, sample)."""
    try:
        resp = sb.table(table_name).select("*").limit(limit).execute()
        rows = resp.data or []
        return True, len(rows), rows
    except Exception as e:
        return False, 0, str(e)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Smoke test Supabase tables")
    parser.add_argument("--dummy", action="store_true", help="Skip live, print dummy data")
    args = parser.parse_args()

    if args.dummy:
        print("[DUMMY MODE] Skipping live Supabase connection.")
        print(f"  {TABLE_MEDDRA}: would check here")
        print(f"  {TABLE_GUIDELINES}: would check here")
        print(f"  {TABLE_ADVERSE_EVENTS}: would check here")
        return

    sb = get_supabase_client()
    for table in [TABLE_MEDDRA, TABLE_GUIDELINES, TABLE_ADVERSE_EVENTS]:
        ok, count, sample = test_table(sb, table)
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {table}: {count} rows")
        if ok and count > 0:
            print(f"  Sample keys: {list(sample[0].keys())}")
        elif not ok:
            print(f"  Error: {sample}")


if __name__ == "__main__":
    main()
