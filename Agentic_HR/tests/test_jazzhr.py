import types
from pathlib import Path
import json
import builtins
import pytest

from jazzhr.client import JazzHRClient
from jazzhr.downloader import download_resumes

class DummyResp:
    def __init__(self, status=200, json_data=None, headers=None, content=b"file"):
        self.status_code = status
        self._json = json_data or {}
        self.headers = headers or {}
        self.content = content
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")
    def json(self):
        return self._json


def test_client_pagination(monkeypatch):
    # Simulate X-Pagination-Total-Items=50 with per_page=25 -> 2 pages total
    calls = {"n": 0}
    def fake_get(url, headers=None, timeout=45):
        calls["n"] += 1
        if "page=1" in url:
            return DummyResp(
                json_data={"data": [{"id": "r1", "downloadUrl": "http://x/1", "fileName": "a.pdf"}]},
                headers={"X-Pagination-Total-Items": "50"}
            )
        return DummyResp(json_data={"data": [{"id": "r2", "downloadUrl": "http://x/2", "fileName": "b.pdf"}]})
    monkeypatch.setattr("requests.get", fake_get)

    c = JazzHRClient(headers={"authorization": "Bearer X"}, per_page=25)
    pages = list(c.iter_pages())
    assert len(pages) == 2
    rows = list(c.iter_resume_entries())
    assert len(rows) == 2


def test_download_resumes(monkeypatch, tmp_path):
    # First request(s) to API endpoint; later requests are for download URLs
    # We'll branch by URL shape to return JSON for API and bytes for download
    def fake_get(url, headers=None, timeout=45):
        if "/api/v1.0/recruitment/partials/run" in url:
            # first page includes header for total
            if "page=1" in url:
                return DummyResp(
                    json_data={"data": [{"id": "r1", "downloadUrl": "http://dl/1", "fileName": "x1.pdf"}]},
                    headers={"X-Pagination-Total-Items": "1"}
                )
            return DummyResp(json_data={"data": []})
        # download url
        return DummyResp(content=b"PDFDATA")
    monkeypatch.setattr("requests.get", fake_get)

    out_dir = tmp_path / "out"
    files = download_resumes(headers={"authorization": "Bearer X"}, out_dir=out_dir, limit=2)
    assert len(files) == 1
    assert files[0][1].exists()
    assert files[0][1].read_bytes() == b"PDFDATA"
