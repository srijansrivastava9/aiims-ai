"""AE Coding Assist — the demo-ready AI feature.

Usage:
  python scripts/ae_assist.py --dummy
  python scripts/ae_assist.py --text "patient experienced severe headache and nausea"
  python scripts/ae_assist.py --ae-id <uuid>
  python scripts/ae_assist.py --ae-id <uuid> --write-back
  python scripts/ae_assist.py --text "..." --llm
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    get_supabase_client,
    DATA_DIR,
    OPENAI_API_KEY,
    TABLE_MEDDRA,
    TABLE_GUIDELINES,
    TABLE_ADVERSE_EVENTS,
    TOP_K_MEDDRA,
    TOP_K_GUIDELINES,
)
from similarity import search_meddra, search_guidelines

# Dummy fallback data for offline demo
DUMMY_MEDDRA = [
    {"term": "Headache", "code": "M001", "score": 0.92},
    {"term": "Nausea", "code": "M002", "score": 0.88},
    {"term": "Dizziness", "code": "M005", "score": 0.75},
    {"term": "Vomiting", "code": "M003", "score": 0.72},
    {"term": "Fatigue", "code": "M006", "score": 0.65},
]

DUMMY_GUIDELINES = [
    {"source": "Pharmacovigilance", "content": "Serious adverse events must be reported within 24 hours. [DEMO PLACEHOLDER: 24h SAE deadline]", "score": 0.81},
    {"source": "Pharmacovigilance", "content": "Non-serious adverse events must be reported within 15 days. [DEMO PLACEHOLDER: 15d AE deadline]", "score": 0.78},
    {"source": "GCP", "content": "All adverse events must be reported to the sponsor and ethics committee promptly.", "score": 0.70},
]


def get_ae_description(sb, ae_id):
    """Fetch AE description from Supabase by ID."""
    resp = sb.table(TABLE_ADVERSE_EVENTS).select("id,description,is_serious,status").eq("id", ae_id).execute()
    rows = resp.data or []
    if not rows:
        raise ValueError(f"No adverse event found with id={ae_id}")
    return rows[0]


def fetch_meddra_details(sb, results):
    """Enrich similarity results with full term/code from Supabase."""
    enriched = []
    for r in results:
        try:
            resp = sb.table(TABLE_MEDDRA).select("term,code").eq("id", r["id"]).execute()
            row = (resp.data or [{}])[0]
            enriched.append({
                "term": row.get("term", "Unknown"),
                "code": row.get("code", "?"),
                "score": round(r["score"], 3),
            })
        except Exception:
            enriched.append({"term": "Unknown", "code": "?", "score": round(r["score"], 3)})
    return enriched


def fetch_guideline_details(sb, results):
    """Enrich similarity results with full source/content from Supabase."""
    enriched = []
    for r in results:
        try:
            resp = sb.table(TABLE_GUIDELINES).select("source,content").eq("id", r["id"]).execute()
            row = (resp.data or [{}])[0]
            enriched.append({
                "source": row.get("source", "Unknown"),
                "content": row.get("content", ""),
                "score": round(r["score"], 3),
            })
        except Exception:
            enriched.append({"source": "Unknown", "content": "", "score": round(r["score"], 3)})
    return enriched


def llm_summarize(ae_description, meddra_terms, guidelines):
    """Optional LLM summary using OpenAI."""
    if not OPENAI_API_KEY:
        return "[LLM skipped — no OPENAI_API_KEY set]"

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        meddra_text = "\n".join([f"- {t['term']} ({t['code']}) [score: {t['score']}]" for t in meddra_terms])
        guide_text = "\n".join([f"- [{g['source']}] {g['content']}" for g in guidelines])

        prompt = f"""You are a clinical trial safety assistant. Given an adverse event description, suggested MedDRA terms, and relevant guideline chunks, provide a concise summary.

**Adverse Event:** {ae_description}

**Suggested MedDRA Terms:**
{meddra_text}

**Relevant Guidelines:**
{guide_text}

**Instructions:**
1. Recommend the best MedDRA term and explain why.
2. Flag any DEMO PLACEHOLDER deadlines explicitly.
3. Keep the response under 150 words.
"""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM error: {e}]"


def write_back_meddra(sb, ae_id, meddra_term):
    """Write the chosen MedDRA term back to adverse_events.meddra_term."""
    try:
        sb.table(TABLE_ADVERSE_EVENTS).update({"meddra_term": meddra_term}).eq("id", ae_id).execute()
        return True
    except Exception as e:
        return False, str(e)


def run(ae_description, ae_id=None, use_llm=False, write_back=False, dummy=False):
    """Main pipeline: embed AE -> suggest MedDRA -> retrieve guidelines -> optional LLM -> optional write-back."""
    sb = get_supabase_client()

    print("=" * 60)
    print("AE CODING ASSIST")
    print("=" * 60)
    print(f"AE Description: {ae_description}")
    if ae_id:
        print(f"AE ID: {ae_id}")
    print()

    # --- MedDRA Suggestion ---
    print("─" * 40)
    print("MEDDRA SUGGESTIONS (top {}):".format(TOP_K_MEDDRA))
    print("─" * 40)

    if dummy:
        meddra_results = DUMMY_MEDDRA
    else:
        raw = search_meddra(ae_description, TOP_K_MEDDRA)
        meddra_results = fetch_meddra_details(sb, raw) if raw else DUMMY_MEDDRA

    for i, r in enumerate(meddra_results, 1):
        print(f"  {i}. {r['term']} ({r['code']}) — score: {r['score']}")
    best_term = meddra_results[0]["term"] if meddra_results else None
    print()

    # --- Guideline RAG ---
    print("─" * 40)
    print("RELEVANT GUIDELINES (top {}):".format(TOP_K_GUIDELINES))
    print("─" * 40)

    if dummy:
        guideline_results = DUMMY_GUIDELINES
    else:
        raw = search_guidelines(ae_description, TOP_K_GUIDELINES)
        guideline_results = fetch_guideline_details(sb, raw) if raw else DUMMY_GUIDELINES

    for i, g in enumerate(guideline_results, 1):
        print(f"  {i}. [{g['source']}] {g['content'][:120]}...")
        print(f"     score: {g['score']}")
    print()

    # --- Optional LLM Summary ---
    if use_llm:
        print("─" * 40)
        print("LLM SUMMARY:")
        print("─" * 40)
        summary = llm_summarize(ae_description, meddra_results, guideline_results)
        print(summary)
        print()

    # --- Optional Write-Back ---
    if write_back and ae_id and best_term:
        print("─" * 40)
        print("WRITE-BACK:")
        print("─" * 40)
        result = write_back_meddra(sb, ae_id, best_term)
        if result is True:
            print(f"  ✅ Saved '{best_term}' to adverse_events.meddra_term for AE {ae_id}")
        else:
            ok, err = result if isinstance(result, tuple) else (False, str(result))
            print(f"  ❌ FAILED to write back: {err}")
            print("  >>> Person B needs to add UPDATE policy or RPC on adverse_events <<<")
        print()

    print("=" * 60)
    print("Done.")
    print("=" * 60)

    # Return structured result (useful if called programmatically)
    return {
        "ae_description": ae_description,
        "ae_id": ae_id,
        "meddra_suggestions": meddra_results,
        "guidelines": guideline_results,
        "best_term": best_term,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AE Coding Assist — suggest MedDRA terms and retrieve guidelines")
    parser.add_argument("--dummy", action="store_true", help="Use dummy data (no Supabase needed)")
    parser.add_argument("--text", type=str, help="AE description text")
    parser.add_argument("--ae-id", type=str, help="UUID of an existing adverse event row")
    parser.add_argument("--llm", action="store_true", help="Include OpenAI LLM summary")
    parser.add_argument("--write-back", action="store_true", help="Write best term back to adverse_events.meddra_term")
    args = parser.parse_args()

    # Determine AE description
    if args.dummy:
        ae_description = args.text or "Patient experienced severe headache and nausea after herbal dose"
        ae_id = args.ae_id
    elif args.ae_id:
        sb = get_supabase_client()
        ae = get_ae_description(sb, args.ae_id)
        ae_description = ae["description"]
        ae_id = args.ae_id
    elif args.text:
        ae_description = args.text
        ae_id = None
    else:
        print("Usage:")
        print("  python scripts/ae_assist.py --dummy")
        print('  python scripts/ae_assist.py --text "..."')
        print("  python scripts/ae_assist.py --ae-id <uuid>")
        print("  python scripts/ae_assist.py --ae-id <uuid> --write-back")
        sys.exit(1)

    run(ae_description, ae_id=ae_id, use_llm=args.llm, write_back=args.write_back, dummy=args.dummy)


if __name__ == "__main__":
    main()
