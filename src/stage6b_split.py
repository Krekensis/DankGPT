
from pathlib import Path

CHUNK = 100_000
in_file = Path(__file__).parent.parent / "data" / "filtered_conversations.jsonl"
out_dir = Path(__file__).parent.parent / "data" / "filtered_split"
out_dir.mkdir(exist_ok=True)

chunk_idx = 1
out_f = None

with open(in_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i % CHUNK == 0:
            if out_f:
                out_f.close()
            out_f = open(out_dir / f"filtered_{chunk_idx}.jsonl", "w", encoding="utf-8")
            print(f"Writing chunk {chunk_idx}...")
            chunk_idx += 1
        out_f.write(line)

if out_f:
    out_f.close()

print(f"Done. {chunk_idx - 1} chunks written to {out_dir}")
