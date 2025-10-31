import mimetypes
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("JAZZHR_API_KEY")
BASE = "https://api.resumatorapi.com/v1"
OUTDIR = "resumes"
MAX_WORKERS = 8  # tune for your bandwidth/API limits
REQUEST_TIMEOUT = 45
RETRY_MAX = 4

os.makedirs(OUTDIR, exist_ok=True)


def clean(name: str) -> str:
    # safe-ish filename
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name or "").strip("_") or "unknown"


def get_applicants():
    """Yield applicants across all pages until an empty list is returned."""
    page = 1
    while page < 2:
        path = "/applicants" if page == 1 else f"/applicants/page/{page}"
        url = f"{BASE}{path}?apikey={API_KEY}"
        r = requests.get(url, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        for a in data:
            yield a
        page += 1


def fetch_resume(app):
    """Download a single applicant's resume, with retries/backoff."""
    app_id = app.get("id")
    display_name = app.get("name") or app.get("first_name", "") + " " + app.get(
        "last_name", ""
    )
    base_name = clean(f"{display_name}__{app_id}")
    url = f"{BASE}/applicants/{app_id}/resume?apikey={API_KEY}"

    delay = 1.5
    for attempt in range(1, RETRY_MAX + 1):
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT)
            # 200: got file; 404: likely no resume on file; 429/5xx: retryable
            if r.status_code == 200:
                # infer extension from content-type if possible
                ctype = r.headers.get("Content-Type", "").split(";")[0]
                ext = mimetypes.guess_extension(ctype) or ".bin"
                # harmonize common office types
                if ctype in ("application/pdf",):
                    ext = ".pdf"
                if ctype in ("application/msword",):
                    ext = ".doc"
                if ctype in (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ):
                    ext = ".docx"

                out_path = os.path.join(OUTDIR, f"{base_name}{ext}")
                with open(out_path, "wb") as f:
                    f.write(r.content)
                return ("ok", app_id, out_path)

            if r.status_code == 404:
                return ("missing", app_id, "no resume")

            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 2, 20)
                continue

            # other non-OK
            return ("error", app_id, f"HTTP {r.status_code}")

        except requests.RequestException as e:
            time.sleep(delay)
            delay = min(delay * 2, 20)
            if attempt == RETRY_MAX:
                return ("error", app_id, f"{type(e).__name__}: {e}")


def main():
    # 1) pull all applicants
    applicants = list(get_applicants())
    total = len(applicants)
    print(f"Found {total} applicants")

    # 2) parallel download resumes
    results = {"ok": 0, "missing": 0, "error": 0}
    details = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(fetch_resume, a) for a in applicants]
        for fut in as_completed(futs):
            status, app_id, info = fut.result()
            results[status] = results.get(status, 0) + 1
            details.append((status, app_id, info))
            if status == "ok":
                print(f"✓ {app_id} -> {info}")
            elif status == "missing":
                print(f"– {app_id} (no resume)")
            else:
                print(f"! {app_id} ({info})")

    print("\nSummary:")
    print(f"  Saved:   {results['ok']}")
    print(f"  Missing: {results['missing']} (no resume on file)")
    print(f"  Errors:  {results['error']}")
    # Optional: write a CSV manifest
    try:
        import csv

        with open(os.path.join(OUTDIR, "manifest.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["status", "applicant_id", "path_or_reason"])
            w.writerows(details)
        print(f"Manifest: {os.path.join(OUTDIR, 'manifest.csv')}")
    except Exception:
        pass


if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit("Set JAZZHR_API_KEY in your environment")
    main()
