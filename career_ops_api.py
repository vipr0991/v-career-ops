"""
Career-Ops FastAPI v4.0.0 â€” Unified Agentic Career Intelligence Engine
Supports Multi-Location Search (UAE, KSA, Qatar, Bahrain, Oman, Kuwait, Bangalore),
10-Dimension Line-by-Line AI Scoring, Live Pipeline Management, Deep Company Research,
LaTeX Resume Tailoring, 6-Slide Value Proposition PPTX Generation, and LinkedIn Outreach.
"""
import os
import json
import time
import httpx
import yaml
import re
from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import secrets

from pipeline_manager import pipeline_store, exclusion_store
from direct_scoring import get_scoring_client
from company_research import company_researcher
from presentation_generator import presentation_engine
from latex_tailoring_engine import latex_tailor
from linkedin_outreach import linkedin_outreach
from link_verifier import link_verifier
from pdf_compiler import pdf_compiler

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
RESUMES_DIR = os.path.join(BASE_DIR, "resumes")
LATEX_DIR = os.path.join(BASE_DIR, "latex_resumes")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
PROFILE_YML_PATH = os.path.join(CONFIG_DIR, "profile.yml")

for d in [REPORTS_DIR, OUTPUT_DIR, RESUMES_DIR, LATEX_DIR, CONFIG_DIR]:
    os.makedirs(d, exist_ok=True)

app = FastAPI(title="Career-Ops API", version="4.0.0", description="Production Agentic Job Search Engine")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class NoIndexMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response

app.add_middleware(NoIndexMiddleware)

session_secret = os.getenv("SESSION_SECRET_KEY", secrets.token_hex(32))
app.add_middleware(SessionMiddleware, secret_key=session_secret, max_age=86400 * 30)

def load_file(path: str, default: str = "") -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return default

# â”€â”€ Data Models â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class SearchRequest(BaseModel):
    title: str
    location: str = "UAE"
    currency: str = "AED"
    limit: int = 15

class ScoreRequest(BaseModel):
    job_title: Optional[str] = None
    role: Optional[str] = None
    company: str
    job_description: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = "Dubai, UAE"
    job_id: Optional[str] = None

class PipelineItemRequest(BaseModel):
    title: str
    company: str
    location: str
    salary_range: Optional[str] = "Not Disclosed"
    url: Optional[str] = ""
    source: Optional[str] = "Manual Search"
    description: Optional[str] = ""
    stage: Optional[str] = "pipeline_saved"
    score: Optional[Any] = None

class PipelineStatusRequest(BaseModel):
    status: str

class ResearchRequest(BaseModel):
    company_name: str
    job_title: Optional[str] = ""
    location: Optional[str] = ""

class GenerateKitRequest(BaseModel):
    job_id: str

class InviteRequest(BaseModel):
    recipient_name: str
    company_name: str
    job_title: str

class ExcludeJobRequest(BaseModel):
    company: str
    title: str
    url: Optional[str] = ""
    reason: Optional[str] = "User excluded"

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class OptimizeRequest(BaseModel):
    job_id: str
    role: str
    company: str
    location: Optional[str] = "Dubai, UAE"
    resume_filename: Optional[str] = None  # uploaded resume to use as base

# â”€â”€ LinkedIn OAuth Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/auth/linkedin/login")
async def linkedin_login(request: Request):
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "https://v-career-ops.up.railway.app/auth/linkedin/callback")
    if not client_id:
        raise HTTPException(500, "LinkedIn Client ID not configured")
    
    state = secrets.token_urlsafe(32)
    request.session["linkedin_state"] = state
    
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        f"&scope=openid%20profile%20email"
    )
    return RedirectResponse(auth_url)

@app.get("/auth/linkedin/callback")
async def linkedin_callback(request: Request, code: str = None, state: str = None, error: str = None, error_description: str = None):
    if error:
        return {"error": error, "description": error_description}
    if not code or not state:
        raise HTTPException(400, "Missing code or state")
    
    saved_state = request.session.get("linkedin_state")
    if not saved_state or state != saved_state:
        raise HTTPException(400, "Invalid OAuth state")
    
    del request.session["linkedin_state"]
    
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "https://v-career-ops.up.railway.app/auth/linkedin/callback")
    
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if token_res.status_code != 200:
            raise HTTPException(502, f"Token exchange failed: {token_res.text}")
        
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        
        user_res = await client.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_res.status_code != 200:
            raise HTTPException(502, "Failed to fetch user profile")
            
        profile = user_res.json()
        
        allowed_email = os.getenv("ALLOWED_LINKEDIN_EMAIL")
        user_email = profile.get("email")
        if allowed_email and user_email != allowed_email:
            raise HTTPException(403, f"Unauthorized email: {user_email}")
            
        request.session["authenticated"] = True
        request.session["user_email"] = user_email
        request.session["user_name"] = profile.get("name")
        request.session["user_sub"] = profile.get("sub")
        
    return RedirectResponse("/")

@app.get("/api/auth/me")
async def get_current_user(request: Request):
    if request.session.get("authenticated"):
        return {
            "authenticated": True, 
            "email": request.session.get("user_email"),
            "name": request.session.get("user_name")
        }
    return {"authenticated": False}

@app.post("/api/auth/login")
async def manual_login(req: LoginRequest, request: Request):
    valid_users = {
        "6vinay9@gmail.com": "#g0!ng2AUS",
        "voommen@my.madonna.edu": "IamLegend-waitf0rit-Dary"
    }
    if req.email in valid_users and (req.password == valid_users[req.email] or req.password == "#g0!ng2AUS"):
        request.session["authenticated"] = True
        request.session["user_email"] = req.email
        request.session["user_name"] = "Vinay Prakash"
        return {"status": "success", "email": req.email}
    
    raise HTTPException(401, "Invalid credentials")

@app.post("/api/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return {"status": "logged_out"}

# â”€â”€ Health & Stats Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"service": "Career-Ops API", "version": "4.0.0", "status": "online"}

@app.get("/api/stats")
async def get_stats():
    pipeline_items = pipeline_store.get_all()
    reports = len([f for f in os.listdir(REPORTS_DIR) if f.endswith(".md")])
    outputs = len(os.listdir(OUTPUT_DIR))
    latex_count = len([f for f in os.listdir(LATEX_DIR) if f.endswith(".tex")])

    profile = {}
    try:
        raw = load_file(PROFILE_YML_PATH)
        profile = yaml.safe_load(raw) or {}
    except Exception:
        pass

    return {
        "total_scored": max(reports, len(pipeline_items)),
        "pipeline_count": len(pipeline_items),
        "total_outputs": outputs,
        "total_latex": latex_count,
        "location": profile.get("location", {}).get("city", "Dubai"),
        "target_regions": ["UAE", "Saudi Arabia", "Qatar", "Bahrain", "Oman", "Kuwait", "Bangalore"],
        "candidate_name": profile.get("candidate", {}).get("full_name", "Vinay Prakash"),
        "status": "online"
    }

# â”€â”€ Multi-Location Live Job Discovery â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REGIONAL_SAMPLE_JOBS = [
    {
        "title": "AI Content & Automation Lead",
        "company": "Careem (Uber)",
        "location": "Dubai, UAE",
        "salary_range": "AED 28,000 - 38,000 / month",
        "source": "LinkedIn / JSearch",
        "url": "https://www.linkedin.com/jobs/view/ai-content-lead-careem",
        "description": "Looking for an AI marketing lead to build automated multi-model pipelines with Gemini and Claude, cutting content turnaround by 50% across UAE and Saudi operations."
    },
    {
        "title": "Marketing Operations & Growth Manager",
        "company": "NEOM Digital Solutions",
        "location": "Riyadh, Saudi Arabia",
        "salary_range": "SAR 32,000 - 45,000 / month",
        "source": "Google Jobs",
        "url": "https://careers.neom.com/job/marketing-operations",
        "description": "Drive MarTech automation, multi-channel demand generation, and automated reporting systems for enterprise digital transformation in KSA."
    },
    {
        "title": "Senior MarTech & Automation Specialist",
        "company": "Qatar Airways (Digital Brand)",
        "location": "Doha, Qatar",
        "salary_range": "QAR 25,000 - 35,000 / month",
        "source": "Adzuna",
        "url": "https://careers.qatarairways.com/job/martech-lead",
        "description": "Lead regional paid campaigns (SEO/SEM, PPC), implement conversion workflows, and manage cross-channel brand audience scaling."
    },
    {
        "title": "Head of AI Marketing & Growth",
        "company": "Talabat / Delivery Hero",
        "location": "Dubai, UAE",
        "salary_range": "AED 35,000 - 48,000 / month",
        "source": "LinkedIn",
        "url": "https://www.linkedin.com/jobs/view/head-ai-marketing-talabat",
        "description": "Oversee creative automation, customer acquisition funnels, and prompt-engineered marketing pipelines across the GCC."
    },
    {
        "title": "AI & MarTech Strategy Lead",
        "company": "Infosys AI Hub",
        "location": "Bangalore, India",
        "salary_range": "INR 35,00,000 - 50,00,000 / year",
        "source": "Google Jobs",
        "url": "https://careers.infosys.com/job/ai-strategy-lead",
        "description": "Architect scalable AI content operations and executive MarTech consulting for global enterprise clients."
    },
    {
        "title": "Digital Growth & Automation Director",
        "company": "Zain Group Digital",
        "location": "Kuwait City, Kuwait",
        "salary_range": "KWD 2,800 - 3,800 / month",
        "source": "JSearch",
        "url": "https://careers.zain.com/job/digital-growth",
        "description": "Build high-impact automated marketing campaigns and data-driven customer acquisition strategies across Middle East business units."
    }
]

# â”€â”€ Multi-Location Live Job Discovery (3-Provider Aggregator) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
from jsearch_provider import search_jsearch
from adzuna_provider import search_adzuna

@app.post("/api/search")
@app.post("/api/search-live")
async def search_live_jobs(req: SearchRequest):
    """
    Multi-location live search across 7 regions:
    UAE, Saudi Arabia, Qatar, Bahrain, Oman, Kuwait, and Bangalore (India).
    Aggregates:
      1. JSearch API (RapidAPI - LinkedIn, Indeed, Glassdoor)
      2. Adzuna API (RapidAPI - Global job board aggregator)
      3. SerpAPI (Google Jobs search engine)
      4. Live verified opportunity store (with sendable direct application URLs)
    """
    results = []
    
    # 1. Query JSearch API
    jsearch_key = os.getenv("JSEARCH_API_KEY", "")
    if jsearch_key:
        try:
            j_res = await search_jsearch(title=req.title, location=req.location, currency=req.currency)
            for j in j_res:
                results.append({
                    "id": j.id,
                    "title": j.title,
                    "company": j.company,
                    "location": j.location,
                    "salary_range": j.salary_range,
                    "source": f"JSearch ({j.source})",
                    "url": j.url,
                    "description": j.description
                })
        except Exception as e:
            print(f"[Search] JSearch provider error: {e}")

    # 2. Query Adzuna API
    adzuna_key = os.getenv("ADZUNA_API_KEY", "")
    if adzuna_key:
        try:
            a_res = await search_adzuna(title=req.title, location=req.location, currency=req.currency)
            for a in a_res:
                results.append({
                    "id": a.id,
                    "title": a.title,
                    "company": a.company,
                    "location": a.location,
                    "salary_range": a.salary_range,
                    "source": f"Adzuna ({a.source})",
                    "url": a.url,
                    "description": a.description
                })
        except Exception as e:
            print(f"[Search] Adzuna provider error: {e}")

    # 3. Query SerpAPI (Google Jobs)
    serpapi_key = os.getenv("SERPAPI_KEY", "")
    if serpapi_key:
        try:
            params = {"engine": "google_jobs", "q": f"{req.title} {req.location}", "api_key": serpapi_key, "chips": "date_posted:week"}
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get("https://serpapi.com/search.json", params=params)
                if r.status_code == 200:
                    for idx, j in enumerate(r.json().get("jobs_results", [])[:req.limit]):
                        results.append({
                            "id": f"serp-{int(time.time())}-{idx}",
                            "title": j.get("title", req.title),
                            "company": j.get("company_name", "Enterprise"),
                            "location": j.get("location", req.location),
                            "salary_range": j.get("detected_extensions", {}).get("salary", "Not disclosed"),
                            "source": "Google Jobs",
                            "url": j.get("share_link", ""),
                            "description": j.get("description", "")[:1000]
                        })
        except Exception as e:
            print(f"[Search] SerpAPI error: {e}")

    # 4. Include verified saved opportunities from pipeline_store & scan-history
    saved_items = pipeline_store.get_all()
    for s in saved_items:
        results.append({
            "id": s.get("id", f"pip-{int(time.time())}"),
            "title": s.get("title", "Target Role"),
            "company": s.get("company", "Enterprise"),
            "location": s.get("location", "Dubai, UAE"),
            "salary_range": s.get("salary_range", "Not Disclosed"),
            "source": s.get("source", "Verified Match"),
            "url": s.get("url", ""),
            "description": s.get("description", ""),
            "score": s.get("score")
        })

    # Deduplicate and filter out permanently excluded jobs
    seen = set()
    deduped = []
    for item in results:
        comp = item.get("company", "").strip()
        tit = item.get("title", "").strip()
        u = item.get("url", "")
        if exclusion_store.is_excluded(comp, tit, u):
            continue
        key = f"{comp.lower()}_{tit.lower()}"
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    # Verify links and filter out dead/expired jobs
    verified_results = await link_verifier.filter_and_verify_jobs(deduped[:req.limit])

    return {"results": verified_results, "total": len(verified_results), "location": req.location}

# â”€â”€ 10-Dimension Line-by-Line AI Scoring â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/score")
async def score_job(req: ScoreRequest):
    """
    Evaluates job descriptions across 10 dimensions against Vinay Prakash's profile.
    Automatically saves high-scoring matches (>= 85) to the Pipeline.
    """
    title = req.job_title or req.role or "Target Role"
    jd = req.job_description or req.description or f"Role: {title} at {req.company}"

    client = get_scoring_client()
    evaluation = await client.score_job(
        job_description=jd,
        job_title=title,
        company=req.company,
        location=req.location or "Dubai, UAE"
    )

    # Save evaluation report to /reports/
    today = time.strftime("%Y-%m-%d")
    company_slug = "".join(c.lower() if c.isalnum() else "-" for c in (req.company or "unknown")).strip("-")
    filename = f"{int(time.time())}-{company_slug}-{today}.md"
    report_path = os.path.join(REPORTS_DIR, filename)

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"COMPANY: {req.company}\n")
            f.write(f"ROLE: {req.job_title}\n")
            f.write(f"LOCATION: {req.location}\n")
            f.write(f"SCORE: {evaluation.get('overall_score', 0)}\n\n")
            f.write(json.dumps(evaluation, indent=2))
    except Exception as e:
        print(f"[Scoring] Save report error: {e}")

    # Upsert into Pipeline (Auto-saves if score >= 85)
    pipeline_item = pipeline_store.upsert_job({
        "title": req.job_title,
        "company": req.company,
        "location": req.location or "Dubai, UAE",
        "description": req.job_description,
        "score": evaluation,
        "source": "AI Scored Evaluation"
    }, auto_pipeline_threshold=85.0)

    return {
        "score": evaluation,
        "report_file": filename,
        "pipeline_item": pipeline_item,
        "source_agent": evaluation.get("source_agent", "Career-Ops AI Evaluator")
    }

# â”€â”€ Resume Upload Endpoint â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/upload-resume")
async def upload_resume_endpoint(file: UploadFile = File(...)):
    """Upload PDF, DOCX, DOC, or TEX resume to RESUMES_DIR."""
    allowed_extensions = [".pdf", ".docx", ".doc", ".tex"]
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed_extensions}")
        
    file_path = os.path.join(RESUMES_DIR, file.filename)
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        return {"status": "success", "filename": file.filename, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resumes")
async def list_resumes():
    """List all resumes uploaded to RESUMES_DIR."""
    files = []
    if os.path.exists(RESUMES_DIR):
        for f in sorted(os.listdir(RESUMES_DIR), reverse=True):
            fpath = os.path.join(RESUMES_DIR, f)
            if os.path.isfile(fpath) and not f.startswith("."):
                stat = os.stat(fpath)
                size_kb = round(stat.st_size / 1024, 1)
                size_str = f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb/1024, 1)} MB"
                mod_time = time.strftime("%b %d, %Y", time.localtime(stat.st_mtime))
                files.append({
                    "name": f,
                    "size": size_str,
                    "date": mod_time
                })
    return {"files": files, "total": len(files)}

@app.delete("/api/resumes")
async def delete_resume(filename: str = Query(...)):
    """Delete a resume file from RESUMES_DIR."""
    # Prevent directory traversal
    clean_name = os.path.basename(filename)
    fpath = os.path.join(RESUMES_DIR, clean_name)
    if os.path.exists(fpath):
        try:
            os.remove(fpath)
            return {"status": "deleted", "filename": clean_name}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {e}")
    raise HTTPException(status_code=404, detail="File not found")

# Serve uploaded resumes for direct preview and download
app.mount("/resumes", StaticFiles(directory=RESUMES_DIR), name="resumes")

# â”€â”€ Resume Active Selection (persistent across sessions) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_active_resume_store_path = os.path.join(BASE_DIR, "data", "active_resume.json")

# Master source of truth — used as fallback when no resume is explicitly selected
MASTER_RESUME_BASENAME = "Vinay_Prakash_Resume_Optimized_6.8"

def _get_active_resume() -> Optional[str]:
    try:
        with open(_active_resume_store_path, "r") as f:
            fname = json.load(f).get("filename")
            if fname:
                return fname
    except Exception:
        pass
    # Fallback: auto-detect the master resume in resumes/
    for ext in (".tex", ".docx", ".pdf"):
        candidate = MASTER_RESUME_BASENAME + ext
        if os.path.exists(os.path.join(RESUMES_DIR, candidate)):
            return candidate
    return None

def _set_active_resume(filename: Optional[str]):
    os.makedirs(os.path.dirname(_active_resume_store_path), exist_ok=True)
    with open(_active_resume_store_path, "w") as f:
        json.dump({"filename": filename}, f)

@app.get("/api/resumes/active")
async def get_active_resume():
    """Return the currently selected/active uploaded resume for tailoring."""
    filename = _get_active_resume()
    if filename:
        fpath = os.path.join(RESUMES_DIR, filename)
        if os.path.exists(fpath):
            return {"filename": filename, "exists": True}
    return {"filename": None, "exists": False}

@app.post("/api/resumes/active")
async def set_active_resume(data: dict = Body(...)):
    """Mark a specific uploaded resume as the active base for tailoring."""
    filename = os.path.basename(data.get("filename", ""))
    if not filename:
        _set_active_resume(None)
        return {"status": "cleared"}
    fpath = os.path.join(RESUMES_DIR, filename)
    if not os.path.exists(fpath):
        raise HTTPException(404, f"Resume file not found: {filename}")
    _set_active_resume(filename)
    return {"status": "set", "filename": filename}

# â”€â”€ Tailor / Optimize Resume from Job Card â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/optimize")
async def optimize_resume(req: OptimizeRequest):
    """
    Called by the Tailor button on the Jobs page.
    Uses BOTH the active uploaded resume (primary) AND cv-template (structure)
    to generate a tailored LaTeX resume preserving every authentic detail.
    """
    # 1. Get job description + scoring data from pipeline
    item = pipeline_store.get_by_id(req.job_id) or {}
    jd = item.get("description", "")
    score_data = item.get("score") if isinstance(item.get("score"), dict) else {}

    # 2. Read the active uploaded resume content (PRIMARY SOURCE)
    uploaded_resume_content = ""
    active_file = req.resume_filename or _get_active_resume()
    if active_file:
        fpath = os.path.join(RESUMES_DIR, os.path.basename(active_file))
        if os.path.exists(fpath):
            try:
                if fpath.endswith(".tex"):
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        uploaded_resume_content = f.read()
                elif fpath.endswith((".pdf", ".docx", ".doc")):
                    uploaded_resume_content = (
                        f"[Uploaded resume '{active_file}' is a {fpath.split('.')[-1].upper()} file. "
                        f"Use the cv-template.tex below as the verified experience source and tailor it.]"
                    )
            except Exception:
                pass

    # 3. Generate tailored LaTeX resume using both sources
    tex_res = await latex_tailor.generate_tailored_resume(
        job_title=req.role,
        company_name=req.company,
        job_description=jd or f"Role: {req.role} at {req.company}, Location: {req.location}",
        evaluation_data=score_data,
        uploaded_resume_content=uploaded_resume_content or None,
    )

    # 4. Compile PDF
    pdf_path = pdf_compiler.compile_resume_to_pdf(
        req.role, req.company, tex_res.get("tex_code", ""), "Vinay Prakash"
    )
    pdf_filename = os.path.basename(pdf_path) if pdf_path else None
    tex_filename = tex_res.get("tex_filename", "")

    return {
        "status": "success",
        "message": f"Resume tailored for {req.role} at {req.company}",
        "tailored_resume_tex": tex_filename,
        "tailored_resume_pdf": pdf_filename,
        "base_resume_used": active_file or "cv-template.tex (default)",
        "tex_download_url": f"/api/downloads/latex/{tex_filename}" if tex_filename else None,
        "pdf_download_url": f"/api/downloads/pdf/{pdf_filename}" if pdf_filename else None,
    }

# â”€â”€ Reports Direct Serving â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/reports/{filename}")
@app.get("/api/reports/{filename}")
async def get_report_file(filename: str):
    """Serve full STAR-metrics evaluation markdown reports."""
    clean_name = os.path.basename(filename)
    report_path = os.path.join(REPORTS_DIR, clean_name)
    if os.path.exists(report_path):
        return FileResponse(report_path, media_type="text/markdown")
    raise HTTPException(status_code=404, detail="Report not found")

app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")

# ── Pipeline CRUD Endpoints ──────────────────────────────────────────────────

@app.get("/api/pipeline/stats")
async def get_pipeline_stats():
    """Retrieve summary metrics and stage breakdown for the active Pipeline."""
    return pipeline_store.get_stats()

@app.get("/api/pipeline")
async def get_pipeline(stage: Optional[str] = None, location: Optional[str] = None):
    """Retrieve all jobs in the active Pipeline."""
    items = pipeline_store.get_all(stage=stage, location=location)
    return {"items": items, "total": len(items)}

@app.post("/api/pipeline")
async def add_to_pipeline(req: PipelineItemRequest):
    """Manually add or save a job to the Pipeline."""
    item = pipeline_store.upsert_job(req.model_dump())
    return {"status": "saved", "item": item}

@app.patch("/api/pipeline/{item_id}")
async def update_pipeline_status(item_id: str, req: PipelineStatusRequest):
    """Update pipeline item stage."""
    item = pipeline_store.update_stage(item_id, req.status)
    if not item:
        raise HTTPException(404, "Pipeline item not found")
    return {"status": "updated", "item": item}

@app.delete("/api/pipeline")
async def delete_pipeline_item(item_id: str = Query(...)):
    """Remove or archive a job from the Pipeline."""
    deleted = pipeline_store.delete_item(item_id)
    if not deleted:
        raise HTTPException(404, "Item not found in pipeline")
    return {"status": "deleted", "item_id": item_id}

# â”€â”€ 1-Click Application Kit Generation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/pipeline/generate-kit")
async def generate_application_kit(req: GenerateKitRequest):
    """
    1-Click complete kit generator:
    1. Conducts deep company research & identifies pain points.
    2. Identifies key decision makers & generates 200-char LinkedIn invites.
    3. Customizes LaTeX resume and compiles PDF.
    4. Generates 6-slide PowerPoint value proposition presentation.
    5. Updates pipeline item with all generated asset links.
    """
    item = pipeline_store.get_by_id(req.job_id)
    if not item:
        raise HTTPException(404, "Job not found in pipeline")

    company = item.get("company", "Enterprise")
    title = item.get("title", "Target Role")
    location = item.get("location", "Dubai, UAE")
    jd = item.get("description", "")
    score_data = item.get("score") if isinstance(item.get("score"), dict) else {}

    # 1. Company Research
    research = await company_researcher.research_company(company, title, location)

    # 2. Decision Makers
    decision_makers = await company_researcher.find_decision_makers(company)

    # 3. LaTeX Resume Customization & PDF Compilation
    active_resume_content = ""
    active_file = _get_active_resume()
    if active_file:
        fpath = os.path.join(RESUMES_DIR, os.path.basename(active_file))
        if os.path.exists(fpath):
            try:
                if fpath.endswith(".tex"):
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        active_resume_content = f.read()
                elif fpath.endswith((".pdf", ".docx", ".doc")):
                    active_resume_content = (
                        f"[Uploaded resume '{active_file}' is a {fpath.split('.')[-1].upper()} file. "
                        f"Use the cv-template.tex below as the verified experience source and tailor it.]"
                    )
            except Exception:
                pass

    tex_res = await latex_tailor.generate_tailored_resume(
        job_title=title,
        company_name=company,
        job_description=jd or f"Role: {title} at {company}, Location: {location}",
        evaluation_data=score_data,
        uploaded_resume_content=active_resume_content or None
    )
    pdf_path = pdf_compiler.compile_resume_to_pdf(
        job_title=title,
        company_name=company,
        latex_content=tex_res.get("tex_code"),
        candidate_name="Vinay Prakash"
    )
    pdf_filename = os.path.basename(pdf_path)

    # 4. PowerPoint Presentation Deck Generation
    pptx_path = presentation_engine.generate_value_prop_deck(company, title, research)
    pptx_filename = os.path.basename(pptx_path)

    # 5. Update Pipeline Record
    updated_item = pipeline_store.upsert_job({
        "id": req.job_id,
        "company": company,
        "title": title,
        "location": location,
        "stage": "assets_generated",
        "company_research": research,
        "decision_makers": decision_makers,
        "tailored_resume_tex": tex_res.get("tex_filename"),
        "tailored_resume_pdf": pdf_filename,
        "presentation_deck": pptx_filename,
        "linkedin_outreach": {
            "status": "prepared",
            "prepared_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    })

    return {
        "status": "success",
        "job_id": req.job_id,
        "company_research": research,
        "decision_makers": decision_makers,
        "tailored_resume": tex_res,
        "tailored_resume_pdf": pdf_filename,
        "presentation_deck": pptx_filename,
        "pipeline_item": updated_item
    }

# â”€â”€ On-Demand Research & Outreach Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/research/company")
async def research_company_endpoint(req: ResearchRequest):
    """Run standalone deep research for a company."""
    res = await company_researcher.research_company(req.company_name, req.job_title or "", req.location or "")
    return {"research": res}

@app.post("/api/research/decision-makers")
async def decision_makers_endpoint(req: ResearchRequest):
    """Find decision makers and recruiters for a company."""
    dms = await company_researcher.find_decision_makers(req.company_name)
    return {"decision_makers": dms}

@app.post("/api/outreach/generate-invite")
async def generate_invite_endpoint(req: InviteRequest):
    """Generate a LinkedIn invite note strictly under 200 characters."""
    note = await linkedin_outreach.generate_invite_note(
        recipient_name=req.recipient_name,
        company_name=req.company_name,
        job_title=req.job_title
    )
    return {"invite_note": note, "char_count": len(note), "max_limit": 200}

# â”€â”€ Job Exclusion & Removal Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/jobs/exclude")
async def exclude_job_endpoint(req: ExcludeJobRequest):
    """Permanently exclude a job so it is never resurfaced or recommended."""
    entry = exclusion_store.add_exclusion(
        company=req.company,
        title=req.title,
        url=req.url or "",
        reason=req.reason or "User excluded"
    )
    # Remove from pipeline if present
    items = pipeline_store.get_all()
    for it in items:
        if exclusion_store.is_excluded(it.get("company", ""), it.get("title", ""), it.get("url", "")):
            pipeline_store.delete_item(it.get("id"))
    return {"status": "success", "excluded_item": entry}

@app.get("/api/jobs/excluded")
async def get_excluded_jobs_endpoint():
    """Retrieve all permanently excluded job signatures."""
    items = exclusion_store.get_all()
    return {"excluded_jobs": items, "total": len(items)}

@app.delete("/api/jobs/exclude/{item_id}")
async def remove_exclusion_endpoint(item_id: str):
    """Restore an excluded job if desired."""
    res = exclusion_store.remove_exclusion(item_id)
    return {"status": "success" if res else "not_found"}

# â”€â”€ Direct Download Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/api/downloads/{file_type}/{filename}")
async def download_file(file_type: str, filename: str):
    """Download generated PPTX decks, LaTeX resumes, or compiled PDFs with standardized naming."""
    target_path = ""
    if file_type == "latex":
        target_path = os.path.join(LATEX_DIR, filename)
        if not os.path.exists(target_path):
            # Extract company name
            if "_" in filename:
                parts = filename.replace(".tex", "").split("_")
                comp = parts[2] if len(parts) >= 3 else parts[-1]
            else:
                comp = filename.replace("resume-", "").replace(".tex", "")
            tex_res = await latex_tailor.generate_tailored_resume("Senior Marketing Manager", comp, "")
            target_path = tex_res.get("tex_path")
    elif file_type == "pdf":
        target_path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(target_path):
            if "_" in filename:
                parts = filename.replace(".pdf", "").split("_")
                comp = parts[2] if len(parts) >= 3 else parts[-1]
            else:
                comp = filename.replace("resume-", "").replace(".pdf", "")
            target_path = pdf_compiler.compile_resume_to_pdf("Senior Marketing Manager", comp, custom_filename=filename)
    else:
        target_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        raise HTTPException(404, f"File {filename} not found")

    media_type = "application/octet-stream"
    if filename.endswith(".pptx"):
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif filename.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.endswith(".tex"):
        media_type = "text/x-tex"

    return FileResponse(target_path, media_type=media_type, filename=filename)

# â”€â”€ Jobs Listing Endpoint (from reports & pipeline) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/api/jobs")
async def get_jobs():
    """Retrieve all jobs from pipeline and saved reports."""
    pipeline_jobs = pipeline_store.get_all()
    if pipeline_jobs:
        return {"jobs": pipeline_jobs, "total": len(pipeline_jobs)}

    # Fallback to reports directory if pipeline is empty
    jobs = []
    for fname in sorted(os.listdir(REPORTS_DIR)):
        if not fname.endswith(".md"):
            continue
        try:
            content = load_file(os.path.join(REPORTS_DIR, fname))
            company = role = ""
            score = None
            for line in content.split("\n"):
                if line.startswith("COMPANY:"):
                    company = line.split(":", 1)[1].strip()
                elif line.startswith("ROLE:"):
                    role = line.split(":", 1)[1].strip()
                elif line.startswith("SCORE:"):
                    try:
                        score = float(line.split(":", 1)[1].strip())
                    except Exception:
                        pass
            jobs.append({
                "id": fname[:-3],
                "company": company or "Unknown",
                "role": role or "Role",
                "score": score,
                "report_file": fname,
                "stage": "scored"
            })
        except Exception:
            pass
    return {"jobs": jobs, "total": len(jobs)}

# â”€â”€ AI Chat Assistant â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/chat")
async def chat_with_assistant(req: ChatRequest):
    """AI Career Assistant connected to Gemini."""
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        prompt = f"""You are Career-Ops AI, the executive career strategist for Vinay Prakash.
Candidate: 13+ years overall (8+ in Marketing, AI Automation, Demand Gen, SEO/PPC). Based in Dubai, UAE.
Target Markets: UAE, Saudi Arabia, Qatar, Bahrain, Oman, Kuwait, Bangalore.
Answer questions on job targeting, interview prep, resume strategy, or market positioning clearly and concisely.

User: {req.message}"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent",
                    headers={"Content-Type": "application/json"},
                    params={"key": gemini_key},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.3}
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    ans = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if ans:
                        return {"response": ans, "model": "Gemini Flash"}
        except Exception as e:
            print(f"[Chat] Error: {e}")

    return {
        "response": f"I received your request: '{req.message}'. I can help evaluate opportunities across the GCC and Bangalore, prepare tailored value propositions, and optimize your LaTeX resume. What role would you like to target?",
        "model": "Career-Ops Assistant"
    }

# â”€â”€ Static Dashboard SPA Serving â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

STATIC_DIST = os.path.join(BASE_DIR, "dashboard-web", "dist")
ASSETS_DIR = os.path.join(STATIC_DIST, "assets")

if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api/") or full_path == "api" or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        raise HTTPException(404, "API endpoint not found")

    target = os.path.join(STATIC_DIST, full_path)
    if os.path.isfile(target):
        return FileResponse(target)

    index_file = os.path.join(STATIC_DIST, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)

    return {"service": "Career-Ops API", "version": "4.0.0", "status": "online"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "5000"))
    print(f"[Career-Ops] API v4.0.0 â€” http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

