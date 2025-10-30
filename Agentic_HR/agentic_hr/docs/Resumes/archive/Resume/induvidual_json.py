import json
from pathlib import Path
import sys

INPUT = Path("/home/ahmad-faisal/lang/HR/docs/Resumes/archive/Resume/metadata_from_html.jsonl")
OUT_DIR = Path("/home/ahmad-faisal/lang/HR/docs/Resumes/metadata")

OUT_DIR.mkdir(parents=True, exist_ok=True)

if not INPUT.exists():
    print(f"Input not found: {INPUT}", file=sys.stderr)
    sys.exit(1)

with INPUT.open("r", encoding="utf-8") as f:
    for i, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Skipping line {i}: JSON error: {e}", file=sys.stderr)
            continue

        rid = obj.get("resume_id") or obj.get("id") or f"unknown_{i}"
        fname = OUT_DIR / f"resume_{rid}.json"

        with fname.open("w", encoding="utf-8") as out:
            json.dump(obj, out, ensure_ascii=False, indent=2)

print(f"Wrote JSON files to: {OUT_DIR}")