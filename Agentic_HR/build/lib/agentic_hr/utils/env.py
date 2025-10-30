import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path('/home/ahmad-faisal/lang/HR/.env'), override=True)
LANCE_URI = os.getenv("LANCE_URI")
LANCE_API_KEY = os.getenv("LANCE_API_KEY")
LANCE_REGION = os.getenv("LANCE_REGION")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DOCS_FOLDER = "/home/ahmad-faisal/lang/HR/Agentic_HR/agentic_hr/docs/JD"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

if LANGSMITH_API_KEY:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_TRACING"] = "true"

# Data directories for JD/resume ingestion
META_JSON_DIR = Path(os.getenv("META_JSON_DIR", "/home/ahmad-faisal/lang/HR/Agentic_HR/agentic_hr/docs/Resumes/metadata"))
RESUME_CSV = Path(os.getenv("RESUME_TEXTS_CSV", "/home/ahmad-faisal/lang/HR/Agentic_HR/agentic_hr/docs/Resumes/archive/Resume/random_50_rows.csv"))
