import tempfile
from pathlib import Path
import pytest
from agentic_hr.components.jd_loader import extract_text_from_pdf, load_job_descriptions

def test_extract_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "dummy.pdf"
    # Write a very simple PDF for testing
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Hello world", ln=True)
    pdf.output(str(pdf_path))
    extracted = extract_text_from_pdf(pdf_path)
    assert "Hello world" in extracted

def test_load_job_descriptions(tmp_path):
    # Same as above, but test batch loading from folder
    from fpdf import FPDF
    pdf_path = tmp_path / "test1.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="JD test doc", ln=True)
    pdf.output(str(pdf_path))
    docs = load_job_descriptions(tmp_path)
    assert len(docs) == 1
    assert "test1" in docs[0]["id"]
    assert "JD test doc" in docs[0]["description"]
