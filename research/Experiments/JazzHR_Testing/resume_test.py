import os, time, math, mimetypes, re
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()
API_KEY = os.getenv("JAZZHR_API_KEY")
BASE = "https://api.resumatorapi.com/v1"
OUTDIR = "resumes"
MAX_WORKERS = 8          # tune for your bandwidth/API limits
REQUEST_TIMEOUT = 45
RETRY_MAX = 4

app_id = "prospect_20251029115427_7TKL8P0XNF0OMBLG"
url = f"{BASE}/applicants/{app_id}/resume?apikey={API_KEY}"

r = requests.get(url, timeout=30)
print(r.status_code)
open("test_resume.pdf", "wb").write(r.content)
