import argparse
import json
from pathlib import Path
from jazzhr.downloader import download_resumes


def main():
    ap = argparse.ArgumentParser(description="Download a small number of resumes from JazzHR")
    ap.add_argument("--headers", required=True, help="Path to headers JSON file copied from browser network tab")
    ap.add_argument("--out", required=True, help="Output directory for downloaded resumes")
    ap.add_argument("--limit", type=int, default=5, help="Max number of resumes to download")
    ap.add_argument("--per_page", type=int, default=25, help="Per-page size for pagination")
    args = ap.parse_args()

    headers = json.loads(Path(args.headers).read_text())
    out_dir = Path(args.out)

    files = download_resumes(headers, out_dir, limit=args.limit, per_page=args.per_page)
    print(f"Downloaded {len(files)} file(s):")
    for name, path in files:
        print(f" - {name} -> {path}")

if __name__ == "__main__":
    main()
