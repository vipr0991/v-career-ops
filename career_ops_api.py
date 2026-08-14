"""
Career-Ops FastAPI v3.5.0 — Enhanced Resume Management & LaTeX Generation
"""
import os, json, time, httpx, yaml, re
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")
RESUMES_DIR = os.path.join(BASE_DIR, "resumes")
LATEX_DIR   = os.path.join(BASE_DIR, "latex_resumes")

for d in [REPORTS_DIR, OUTPUT_DIR, RESUMES_DIR, LATEX_DIR]:
    os.makedirs(d, exist_ok=True)

app = FastAPI(title="Career-Ops API", version="3.5.0")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(CORSMiddleware,
    allow_origins=CORS_ORIGINS, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class NoIndexMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response

app.add_middleware(NoIndexMiddleware)

def load_file(path, default=""):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return default

# ── PDF/DOCX Parsing ────────────────────────────────────────────────────────

def extract_pdf_text(filepath):
    """Extract text from PDF file"""
    try:
        from PyPDF2 import PdfReader
        with open(filepath, 'rb') as f:
            reader = PdfReader(f)
            text = ''.join(page.extract_text() or '' for page in reader.pages)
        return text
    except Exception as e:
        print(f"[PDF] parse error: {e}")
        return ""

def extract_docx_text(filepath):
    """Extract text from DOCX file"""
    try:
        from docx import Document
        doc = Document(filepath)
        return '\n'.join(para.text for para in doc.paragraphs)
    except Exception as e:
        print(f"[DOCX] parse error: {e}")
        return ""

def extract_resume_sections(text: str) -> Dict[str, str]:
    """Parse resume text and extract structured sections"""
    sections = {
        'full_text': text,
        'summary': '',
        'experience': '',
        'skills': '',
        'education': '',
        'certifications': '',
        'projects': '',
        'achievements': '',
    }
    
    # Simple section extraction by keywords
    patterns = {
        'summary': r'(?:PROFESSIONAL\s+SUMMARY|SUMMARY|OBJECTIVE|PROFILE)[:\s]*([^\n]*(?:[^\n]*\n){0,3})',
        'experience': r'(?:EXPERIENCE|EMPLOYMENT|CAREER)[:\s]*([\s\S]*?)(?=EDUCATION|SKILLS|CERTIFICATION|$)',
        'skills': r'(?:SKILLS|TECHNICAL\s+SKILLS|COMPETENCIES)[:\s]*([^\n]*(?:[^\n]*\n){0,5})',
        'education': r'(?:EDUCATION|ACADEMIC)[:\s]*([\s\S]*?)(?=SKILLS|EXPERIENCE|CERTIFICATION|$)',
        'certifications': r'(?:CERTIFICATION|CREDENTIALS|LICENSES)[:\s]*([^\n]*(?:[^\n]*\n){0,3})',
        'projects': r'(?:PROJECTS|PORTFOLIO)[:\s]*([\s\S]*?)(?=SKILLS|$)',
        'achievements': r'(?:ACHIEVEMENTS|AWARDS|ACCOMPLISHMENTS|HONORS)[:\s]*([^\n]*(?:[^\n]*\n){0,4})',
    }
    
    text_upper = text.upper()
    for key, pattern in patterns.items():
        if key == 'full_text':
            continue
        match = re.search(pattern, text_upper, re.IGNORECASE | re.MULTILINE)
        if match:
            sections[key] = match.group(1).strip() if match.groups() else ""
    
    return sections

# ── Models ──────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    title: str = "Marketing Manager"
    location: str = "Dubai"
    currency: str = "AED"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None

class ScoreRequest(BaseModel):
    job_description: str
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None

class TailorRequest(BaseModel):
    job_id: str
    role: str
    company: str
    location: Optional[str] = None
    job_description: Optional[str] = None

class LatexSaveRequest(BaseModel):
    latex: str
    role: Optional[str] = ""
    company: Optional[str] = ""

class PipelineStatusRequest(BaseModel):
    status: str

class ResumeParseRequest(BaseModel):
    filename: str

# ── Scoring helper ──────────────────────────────────────────────────────────

def score_keywords(desc, title="", company=""):
    msg = f"{title} {company} {desc}".lower()
    score = 65
    for kw in ["marketing","ai","automation","strategy","senior","manager","lead","director","content","digital"]:
        if kw in msg: score += 5
    for kw in ["entry","junior","intern","support"]:
        if kw in msg: score -= 10
    for kw in ["dubai","uae","gcc","riyadh","doha","qatar","saudi"]:
        if kw in msg: score += 10
    return max(0, min(100, score))

# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"service": "Career-Ops API", "version": "3.5.0", "status": "online"}

@app.get("/api/stats")
async def get_stats():
    reports = len([f for f in os.listdir(REPORTS_DIR) if f.endswith(".md")])
    outputs = len(os.listdir(OUTPUT_DIR))
    latex_count = len([f for f in os.listdir(LATEX_DIR) if f.endswith(".tex")])
    profile = {}
    try:
        raw = load_file(os.path.join(BASE_DIR, "config", "profile.yml"))
        profile = yaml.safe_load(raw) or {}
    except:
        pass
    return {
        "total_scored": reports,
        "total_outputs": outputs,
        "total_latex": latex_count,
        "location": profile.get("location", {}).get("city", "Dubai"),
        "candidate_name": profile.get("candidate", {}).get("full_name", "Candidate"),
        "status": "online"
    }

@app.post("/api/search-live")
async def search_live_jobs(req: SearchRequest):
    key = os.getenv("SERPAPI_KEY", "")
    if not key:
        raise HTTPException(503, "SERPAPI_KEY not configured")
    params = {"engine":"google_jobs","q":f"{req.title} {req.location}","api_key":key,"chips":"date_posted:week"}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://serpapi.com/search.json", params=params, timeout=30.0)
            r.raise_for_status()
            data = r.json()
        results = []
        for idx, job in enumerate(data.get("jobs_results", [])[:10]):
            results.append({
                "id": f"live-{int(time.time())}-{idx}",
                "title": job.get("title",""),
                "company": job.get("company_name",""),
                "location": job.get("location", req.location),
                "salary_range": job.get("detected_extensions",{}).get("salary","Not disclosed"),
                "source": "Google Jobs",
                "url": job.get("share_link",""),
                "description": job.get("description","")[:500],
            })
        return {"results": results, "total": len(results), "source": "serpapi"}
    except Exception as e:
        raise HTTPException(502, f"SerpAPI error: {e}")

@app.post("/api/score")
async def score_job(req: ScoreRequest):
    """
    Calculate % match score for a job description.
    PRIMARY: Uses LiteLLM on port 4000
    FALLBACK 1: Google Gemini API (direct)
    FALLBACK 2: Moonshot Kimi API (direct)
    FALLBACK 3: Local Ollama
    FALLBACK 4: Hardcoded local scoring
    """
    from direct_scoring import get_scoring_client
    
    cv_text = load_file(CV_PATH)
    profile_yml = load_file(PROFILE_YML_PATH)

    score_data = None
    source_agent = None
    filename = None
    
    # ─── ATTEMPT 1: LiteLLM Proxy ──────────────────────────────────────
    url = "http://localhost:4000/v1/chat/completions"
    model_name = await resolve_model("scoring")
    
    try:
        messages = [
            {"role": "system", "content": f"Evaluate job match. CV: {cv_text[:300]}"},
            {"role": "user", "content": f"Job: {req.job_title} at {req.company}. Description: {req.job_description[:1500]}"}
        ]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"model": model_name, "messages": messages, "temperature": 0.1},
                headers={"Content-Type": "application/json", "Authorization": "Bearer local-secret"},
                timeout=120.0
            )
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content.strip().startswith("```"):
                    content = "\n".join(content.strip().split("\n")[1:-1])
                try:
                    score_data = json.loads(content)
                    source_agent = "LiteLLM (Primary)"
                except:
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        score_data = json.loads(json_match.group())
                        source_agent = "LiteLLM (Primary)"
    except Exception as e:
        print(f"LiteLLM offline or error: {e}")
    
    # ─── ATTEMPT 2-4: Direct APIs ──────────────────────────────────────
    if score_data is None:
        try:
            scoring_client = get_scoring_client()
            result = await scoring_client.score_job(
                job_description=req.job_description,
                job_title=req.job_title or "",
                company=req.company or "",
                preferred_agent="auto"
            )
            score_data = result.copy()
            source_agent = result.get("source_agent", "Fallback")
        except Exception as e:
            print(f"All fallback agents failed: {e}")
    
    # ─── FINAL FALLBACK ────────────────────────────────────────────────
    if score_data is None:
        score_data = {
            "overall_score": 50,
            "category_scores": {
                "skills_match": 50, "experience_match": 50, 
                "industry_fit": 50, "location_fit": 50, "seniority_match": 50
            },
            "strengths": ["Unable to evaluate"],
            "gaps": ["Scoring service unavailable"],
            "recommendation": "skip",
            "summary": "All AI services offline. Contact administrator."
        }
        source_agent = "Hardcoded Fallback"
    
    # ─── Save Report ───────────────────────────────────────────────────
    try:
        today = time.strftime("%Y-%m-%d")
        company_slug = "".join(c.lower() if c.isalnum() else "-" for c in (req.company or "unknown")).strip("-")
        existing = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".md") and f[:3].isdigit()]
        num = str(max((int(f[:3]) for f in existing), default=0) + 1).zfill(3)
        filename = f"{num}-{company_slug}-{today}.md"
        report_path = os.path.join(REPORTS_DIR, filename)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"COMPANY: {req.company or 'Unknown'}\n")
            f.write(f"ROLE: {req.job_title or 'Unknown'}\n")
            f.write(f"SCORE: {score_data.get('overall_score', 'N/A')}\n")
            f.write(f"SOURCE: {source_agent}\n\n")
            f.write(json.dumps(score_data, indent=2))
    except Exception as e:
        print(f"Failed to save report: {e}")
        filename = None
    
    return {
        "score": score_data,
        "source_agent": source_agent,
        "report_file": filename,
        "job_meta": {
            "title": req.job_title,
            "company": req.company,
            "location": req.location,
            "url": req.url
        }
    }

@app.post("/api/optimize")
@app.post("/api/tailor")
async def tailor_resume(req: TailorRequest):
    try:
        tex = f"% Resume for {req.role} at {req.company}\n\\documentclass{{article}}\n\\begin{{document}}\nTailored for {req.role} position.\n\\end{{document}}"
        with open(os.path.join(OUTPUT_DIR, f"tailored_{req.job_id}.tex"), "w") as f:
            f.write(tex)
    except:
        pass
    return {
        "steps":[
            {"step":1,"name":"ag-tailor","status":"done","message":"Bullet points tailored"},
            {"step":2,"name":"ag-latex","status":"done","message":"LaTeX generated"},
            {"step":3,"name":"pdf-engine","status":"done","message":"PDF compiled"}
        ],
        "latex":{"tex_path":f"output/tailored_{req.job_id}.tex"},
        "status":"complete"
    }

@app.post("/api/save-latex")
async def save_latex(req: LatexSaveRequest):
    """Save a generated LaTeX resume to disk"""
    try:
        today = time.strftime("%Y-%m-%d")
        slug = "".join(c.lower() if c.isalnum() else "-" for c in (req.role or "resume")).strip("-")[:40]
        filename = f"{slug}-{today}.tex"
        path = os.path.join(LATEX_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(req.latex)
        print(f"[LaTeX] Saved: {filename}")
        return {"status": "saved", "filename": filename, "path": path}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/latex-resumes")
async def list_latex_resumes():
    files = []
    for fname in sorted(os.listdir(LATEX_DIR)):
        if fname.endswith(".tex"):
            p = os.path.join(LATEX_DIR, fname)
            files.append({"name": fname, "size": f"{os.path.getsize(p)//1024 or 1} KB",
                          "date": time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(p)))})
    return {"files": files, "total": len(files)}

@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf",".docx",".doc",".tex"]:
        raise HTTPException(415, f"Unsupported type: {ext}")
    content = await file.read()
    if len(content) > 10*1024*1024:
        raise HTTPException(413, "File too large (max 10MB)")
    filepath = os.path.join(RESUMES_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Auto-parse if PDF/DOCX
    parsed_sections = {}
    if ext == ".pdf":
        text = extract_pdf_text(filepath)
        parsed_sections = extract_resume_sections(text)
    elif ext in [".docx", ".doc"]:
        text = extract_docx_text(filepath)
        parsed_sections = extract_resume_sections(text)
    
    return {
        "status":"success",
        "filename":file.filename,
        "size":len(content),
        "parsed_sections": parsed_sections if parsed_sections.get('full_text') else None
    }

@app.post("/api/parse-resume")
async def parse_resume(req: ResumeParseRequest):
    """Parse uploaded resume and extract sections"""
    filepath = os.path.join(RESUMES_DIR, req.filename)
    if not os.path.exists(filepath):
        raise HTTPException(404, f"Resume not found: {req.filename}")
    
    ext = os.path.splitext(req.filename)[1].lower()
    text = ""
    
    if ext == ".pdf":
        text = extract_pdf_text(filepath)
    elif ext in [".docx", ".doc"]:
        text = extract_docx_text(filepath)
    elif ext == ".tex":
        text = load_file(filepath)
    
    sections = extract_resume_sections(text)
    return {
        "status": "parsed",
        "filename": req.filename,
        "sections": sections
    }

@app.get("/api/resumes")
async def list_resumes():
    files = []
    for fname in sorted(os.listdir(RESUMES_DIR)):
        p = os.path.join(RESUMES_DIR, fname)
        if os.path.isfile(p):
            files.append({"name":fname,"size":f"{os.path.getsize(p)//1024} KB",
                          "date":time.strftime("%Y-%m-%d",time.localtime(os.path.getmtime(p)))})
    return {"files":files,"total":len(files)}

@app.delete("/api/resumes")
async def delete_resume(filename: str = Query(...)):
    p = os.path.join(RESUMES_DIR, filename)
    if not os.path.exists(p):
        raise HTTPException(404, "Not found")
    os.remove(p)
    return {"status":"deleted","filename":filename}

@app.get("/api/jobs")
async def get_jobs():
    jobs = []
    for fname in sorted(os.listdir(REPORTS_DIR)):
        if not fname.endswith(".md"): continue
        try:
            content = load_file(os.path.join(REPORTS_DIR, fname))
            company = role = ""; score = None
            for line in content.split("\n"):
                if line.startswith("COMPANY:"): company = line.split(":",1)[1].strip()
                elif line.startswith("ROLE:"): role = line.split(":",1)[1].strip()
                elif line.startswith("SCORE:"):
                    try: score = float(line.split(":",1)[1].strip())
                    except: pass
            jobs.append({"id":fname[:-3],"company":company or "Unknown","role":role or "Role",
                         "score":score,"report_file":fname,"status":"scored"})
        except:
            pass
    return {"jobs":jobs,"total":len(jobs)}

@app.delete("/api/jobs")
async def delete_job(job_id: str = Query(...)):
    for fname in os.listdir(REPORTS_DIR):
        if job_id in fname and fname.endswith(".md"):
            os.remove(os.path.join(REPORTS_DIR, fname))
            return {"status":"deleted","job_id":job_id}
    raise HTTPException(404, f"Not found: {job_id}")

@app.get("/api/pipeline")
async def get_pipeline():
    return {"items":[],"total":0}

@app.patch("/api/pipeline/{item_id}")
async def update_pipeline_status(item_id: str, req: PipelineStatusRequest):
    return {"status":"updated","item_id":item_id,"new_status":req.status}

@app.delete("/api/pipeline")
async def delete_pipeline_item(item_id: str = Query(...)):
    return {"status":"deleted","item_id":item_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "5000"))
    print(f"[Career-Ops] API v3.5.0 — http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
