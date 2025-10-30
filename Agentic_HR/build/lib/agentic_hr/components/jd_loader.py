import logging
from pathlib import Path
from typing import List, Dict, Any
import pypdf

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: Path) -> str:
    try:
        with pdf_path.open("rb") as f:
            reader = pypdf.PdfReader(f)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    except Exception as e:
        logger.error(f"Error reading {pdf_path}: {e}")
        return ""

def load_job_descriptions(folder: Path) -> List[Dict[str, Any]]:
    records = []
    if not folder.exists():
        logger.error(f"❌ Folder {folder} not found")
        return []
    for pdf in sorted(folder.glob("*.pdf")):
        logger.info(f"Processing {pdf.name}...")
        text = extract_text_from_pdf(pdf)
        if not text:
            continue
        records.append({
            "id": f"job_{pdf.stem}",
            "title": pdf.stem.replace("_", " ").replace(" JD", "").strip(),
            "description": text,
            "pdf_path": str(pdf),
            "company": "Unknown",
            "location": "Unknown"
        })
    logger.info(f"📄 Loaded {len(records)} job descriptions.")
    return records
