import re
import pandas as pd
import json
from bs4 import BeautifulSoup
HAVE_BS4 = True


def textnorm(s): return re.sub(r"\s+", " ", (s or "").strip())

def parse_html(html: str):
    if not isinstance(html, str) or not html.strip():
        return "", "", ""
    if HAVE_BS4:
        soup = BeautifulSoup(html, "html.parser")
        # candidate name
        name = ""
        name_div = soup.select_one("div.name")
        if name_div:
            name = textnorm(name_div.get_text(" "))
        if not name:
            nb = soup.select_one(".namebox [itemprop='name']") or soup.select_one(".namebox")
            if nb: name = textnorm(nb.get_text(" "))

        # universities from Education section
        unis = []
        for edu in soup.select(".companyname.companyname_educ, [id^='SECTION_EDUC'] .companyname"):
            t = textnorm(edu.get_text(" "))
            if t and t not in unis: unis.append(t)
        universities = ", ".join(unis)

        # job title (first under Experience)
        job_title = ""
        expr = soup.select_one("[id^='SECTION_EXPR'] .jobtitle")
        if expr:
            job_title = textnorm(expr.get_text(" "))
        if not job_title:
            jt = soup.select_one(".jobtitle")
            if jt: job_title = textnorm(jt.get_text(" "))
        return name, universities, job_title
    else:
        # minimal regex fallback if bs4 isn't available
        NAME_PAT = re.compile(r'<div class="name">(.+?)</div>', re.S|re.I)
        SPAN_PAT = re.compile(r"<span[^>]*>(.*?)</span>", re.S|re.I)
        EDU_SCHOOL_PAT = re.compile(r'class="companyname companyname_educ"[^>]*>(.*?)</span>', re.S|re.I)
        JOBTITLE_PAT = re.compile(r'(?:SECTION_EXPR[^>]*>.*?|)class="jobtitle"[^>]*>(.*?)</span>', re.S|re.I)
        name = ""
        m = NAME_PAT.search(html or "")
        if m:
            raw = m.group(1)
            spans = SPAN_PAT.findall(raw)
            name = textnorm(" ".join([re.sub("<.*?>","",s) for s in spans]))
        unis = [textnorm(re.sub("<.*?>","",u)) for u in EDU_SCHOOL_PAT.findall(html or "")]
        universities = ", ".join([u for u in unis if u])
        job_title = ""
        jm = JOBTITLE_PAT.search(html or "")
        if jm: job_title = textnorm(re.sub("<.*?>","",jm.group(1)))
        return name, universities, job_title

# text fallback (resume_str) for robustness
ROLE_KEYS = ["engineer","developer","scientist","analyst","manager","consultant","designer","architect",
             "technician","administrator","coordinator","supervisor","director","officer","specialist",
             "professor","teacher","accountant","operations","data","software","product","project"]
UNI_TXT_PAT = re.compile(
    r"(?i)\b([A-Z][A-Za-z\.\-&']+(?:\s+[A-Z][A-Za-z\.\-&']+){0,6}\s+"
    r"(University|College|Institute|Polytechnic|School of [A-Z][A-Za-z]+|Academy|Institute of Technology))\b"
)
def looks_like_name_line(s):
    low = s.lower()
    if any(tok in low for tok in ["@", "http", "www", "linkedin", "github", "resume", "curriculum vitae", "cv"]): return False
    if any(ch.isdigit() for ch in s): return False
    tokens = re.findall(r"[A-Za-z][A-Za-z\.'\-]+", s)
    if not (1 < len(tokens) <= 5): return False
    words = s.split()
    return (sum(1 for w in words if w[:1].isupper())/max(1,len(words)) > 0.6) or s.isupper()

def parse_text_fallback(text: str):
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    # name
    name = next((ln for ln in lines[:20] if looks_like_name_line(ln)), "")
    # universities
    universities = ", ".join(dict.fromkeys([textnorm(m.group(0)) for m in UNI_TXT_PAT.finditer(text or "")]))  # de-dup
    # job title
    job = ""
    for ln in lines[:30]:
        low = ln.lower()
        if any(k in low for k in ROLE_KEYS) and 2 <= len(ln.split()) <= 8:
            job = " ".join([w if (w.isupper() and len(w) <= 4) else w.capitalize() for w in ln.split()])
            break
    return name, universities, job

def extract_metadata(row):
    name, universities, job_title = parse_html(row.get("Resume_html", ""))
    if not name or not universities or not job_title:
        tname, tunis, tjob = parse_text_fallback(str(row.get("resume_str", "")))
        name = name or tname
        universities = universities or tunis
        job_title = job_title or tjob
    category = (str(row.get("category","")) if pd.notna(row.get("category","")) else "").strip()
    return {
        "resume_id": str(row.get("ID","")).strip(),
        "candidate_name": name,
        "university": universities,
        "job_title": (category or job_title),
        "doc_type": "resume",
        "source": "structured_data",
    }
if __name__ == "__main__":
    df = pd.read_csv("random_50_rows.csv")
    metadata = [extract_metadata(r) for _, r in df.iterrows()]
    pd.DataFrame(metadata).to_csv("metadata_from_html.csv", index=False)
    with open("metadata_from_html.jsonl", "w", encoding="utf-8") as f:
        for m in metadata:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print("✅ Saved metadata_from_html.csv and metadata_from_html.jsonl")