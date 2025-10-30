from agentic_hr.components.candidate_ingest import load_meta_docs, build_text_rows
from pathlib import Path
import json
import pandas as pd

def test_load_meta_docs(tmp_path):
    json_path = tmp_path / "resume1.json"
    meta = {"resume_id": "abc123", "job_title": "Engineer", "candidate_name": "Alice", "university": "MIT", "doc_type": "Resume", "source": "portal"}
    json_path.write_text(json.dumps(meta))
    docs = load_meta_docs(tmp_path)
    assert len(docs) == 1
    assert docs[0].metadata["resume_id"] == "abc123"
    assert "Engineer" in docs[0].page_content

def test_build_text_rows(tmp_path):
    csv_path = tmp_path / "texts.csv"
    df = pd.DataFrame({"resume_id": ["r1", "r2"], "resume_str": ["One text!", "Another one!"]})
    df.to_csv(csv_path, index=False)
    rows = build_text_rows(csv_path)
    assert rows[0]["text"] == "One text!"
    assert len(rows) == 2
