import math
import os
from typing import Dict, Iterable, List, Tuple
import requests

DEFAULT_BASE_URL = "https://api.jazzhr.com"
DEFAULT_ENDPOINT = "/api/v1.0/recruitment/partials/run"

class JazzHRClient:
    def __init__(self, headers: Dict[str, str], *, base_url: str = DEFAULT_BASE_URL, per_page: int = 25):
        self.base_url = base_url.rstrip("/")
        self.endpoint = DEFAULT_ENDPOINT
        self.headers = headers
        self.per_page = per_page
        self.last_page = 99999  # sentinel for discovery

    def _build_url(self, page: int) -> str:
        # endpoint=jobs&q=projects:jobs&q=projects.workflow&refresh=resume
        # per_page and page control pagination
        return (
            f"{self.base_url}{self.endpoint}"
            f"?endpoint=jobs&q=projects:jobs&q=projects.workflow&refresh=resume"
            f"&per_page={self.per_page}&page={page}"
        )

    def fetch_page(self, page: int) -> Tuple[requests.Response, dict]:
        url = self._build_url(page)
        resp = requests.get(url, headers=self.headers, timeout=45)
        resp.raise_for_status()
        data = resp.json()
        return resp, data

    def iter_pages(self, *, max_pages: int | None = None) -> Iterable[dict]:
        page = 1
        seen = 0
        while True:
            resp, data = self.fetch_page(page)
            if self.last_page == 99999:
                total_items_str = resp.headers.get("X-Pagination-Total-Items") or resp.headers.get("x-pagination-total-items")
                if total_items_str is None:
                    # fallback: stop if header missing
                    self.last_page = page
                else:
                    total_items = int(total_items_str)
                    self.last_page = max(1, math.ceil(total_items / self.per_page))
            yield data
            seen += 1
            if page >= self.last_page:
                break
            if max_pages is not None and seen >= max_pages:
                break
            page += 1

    def iter_resume_entries(self, *, max_pages: int | None = None) -> Iterable[dict]:
        for payload in self.iter_pages(max_pages=max_pages):
            # payload is expected to have "data": [...]
            items = payload.get("data") or []
            for item in items:
                yield item
