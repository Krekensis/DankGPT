"""
Stage 6a — Dank Memer Keyword Pre-Filter

Reads high_quality_conversations.jsonl (from stage 5) and hard-removes any
conversation that contains zero Dank Memer keyword hits. This reduces the
dataset to only game-relevant conversations before uploading to Kaggle.

Output: data/filtered_conversations.jsonl
"""
import json
import time
from pathlib import Path

# Import the keyword index builder from stage 5 so we reuse the same list.
import sys
sys.path.insert(0, str(Path(__file__).parent))
from stage5_scorer import _build_keyword_index, keyword_bonus


def main() -> None:
    base_dir = Path(__file__).parent.parent
    in_file  = base_dir / "data" / "high_quality_conversations.jsonl"
    out_file = base_dir / "data" / "filtered_conversations.jsonl"

    if not in_file.exists():
        print(f"Error: {in_file} does not exist. Run stage 5 first.")
        return

    _build_keyword_index(base_dir)

    total = kept = 0
    start = time.time()
    passing: list[dict] = []

    print("Filtering conversations for Dank Memer relevance...")
    with open(in_file, "r", encoding="utf-8") as in_f:
        for line in in_f:
            line = line.strip()
            if not line:
                continue
            try:
                conv = json.loads(line)
            except json.JSONDecodeError:
                continue

            total += 1
            full_text = " ".join(m.get("m", "") for m in conv.get("messages", []))
            if keyword_bonus(full_text) > 0:
                passing.append(conv)
                kept += 1

    # Sort best-first so the Kaggle extraction notebook hits gold immediately.
    passing.sort(key=lambda c: c.get("quality_score", 0.0), reverse=True)

    with open(out_file, "w", encoding="utf-8") as out_f:
        for conv in passing:
            out_f.write(json.dumps(conv) + "\n")

    size_mb = out_file.stat().st_size / 1_048_576
    print(f"Filter Complete.")
    print(f"  In:  {total:,} conversations")
    print(f"  Out: {kept:,} conversations ({kept/total*100:.1f}% kept)")
    print(f"  Output size: {size_mb:.1f} MB")
    print(f"  Time: {round(time.time() - start, 2)}s")


if __name__ == "__main__":
    main()
