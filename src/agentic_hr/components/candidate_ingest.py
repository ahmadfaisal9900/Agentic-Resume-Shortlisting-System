import json
from pathlib import Path

import pandas as pd
from langchain_core.documents import Document

CAND_TABLE = "candidates_meta"
TEXT_TABLE = "candidate_texts"


# --- Metadata ingest ---
def load_meta_docs(meta_dir: Path) -> list[Document]:
    docs = []
    for p in sorted(meta_dir.glob("*.json")):
        j = json.loads(p.read_text(encoding="utf-8"))
        text = " | ".join(
            [
                str(j.get("job_title", "")).strip(),
                str(j.get("university", "")).strip(),
                str(j.get("candidate_name", "")).strip(),
                str(j.get("doc_type", "")).strip(),
                str(j.get("source", "")).strip(),
            ]
        )
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "resume_id": str(j.get("resume_id", "")).strip(),
                    "candidate_name": str(j.get("candidate_name", "")).strip(),
                    "university": str(j.get("university", "")).strip(),
                    "job_title": str(j.get("job_title", "")).strip(),
                    "doc_type": str(j.get("doc_type", "")).strip(),
                    "source": str(j.get("source", "")).strip(),
                },
            )
        )
    return docs


# --- Resume text ingest ---
def build_text_rows(csv_path: Path) -> list[dict]:
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]
    id_col = (
        "id"
        if "id" in df.columns
        else ("resume_id" if "resume_id" in df.columns else None)
    )
    text_col = (
        "resume_str"
        if "resume_str" in df.columns
        else ("resume_text" if "resume_text" in df.columns else None)
    )
    if not id_col or not text_col:
        raise ValueError(
            "CSV must contain columns: ID/resume_id and resume_str/resume_text"
        )
    rows = []
    for _, r in df.iterrows():
        rid = str(r[id_col]).strip()
        txt = "" if pd.isna(r[text_col]) else str(r[text_col]).strip()
        if rid:
            rows.append({"resume_id": rid, "text": txt})
    return rows
