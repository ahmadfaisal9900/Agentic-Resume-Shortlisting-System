import os
from pathlib import Path
from typing import Dict, List, Tuple
import requests
from .client import JazzHRClient


def download_resumes(headers: Dict[str, str], out_dir: Path, *, limit: int = 5, per_page: int = 25) -> List[Tuple[str, Path]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    client = JazzHRClient(headers=headers, per_page=per_page)
    saved: List[Tuple[str, Path]] = []
    for item in client.iter_resume_entries(max_pages=None):
        if len(saved) >= limit:
            break
        url = item.get("downloadUrl")
        fname = item.get("fileName") or item.get("id") or "resume.bin"
        if not url:
            continue
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            # heuristic: ensure safe filename
            safe = "".join(c if c.isalnum() or c in ("_", "-", ".") else "_" for c in fname)
            path = out_dir / safe
            path.write_bytes(r.content)
            saved.append((fname, path))
        except Exception:
            # skip failures to keep sample robust
            continue
    return saved
