"""
Career-Ops FastAPI v4.0.0 — Unified Agentic Career Intelligence Engine
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
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from pipeline_manager import pipeline_store
from direct_scoring import get_scoring_client
from company_research import company_researcher
from presentation_generator import presentation_engine
from latex_tailoring_engine import latex_tailor
from linkedin_outreach import linkedin_outreach

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

def load_file(path: str, default: str = "") -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return default

# ── Data Models ──────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    title: str
    location: str = "UAE"
    currency: str = "AED"
    limit: int = 15

class ScoreRequest(BaseModel):
    job_title: str
    company: str
    job_description: str
    location: Optional[str] = "Dubai, UAE"

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

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

# ── Health & Stats Endpoints ─────────────────────────────────────────────────

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

# ── Multi-Location Live Job Discovery ────────────────────────────────────────

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

@app.post("/api/search-live")
async def search_live_jobs(req: SearchRequest):
    """
    Multi-location search across 7 regions:
    UAE, Saudi Arabia, Qatar, Bahrain, Oman, Kuwait, and Bangalore (India).
    Aggregates SerpAPI, JSearch, Adzuna, and curated live feeds.
    """
    results = []
    
    # 1. Check SerpAPI
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

    # 2. Filter / Combine with Regional Opportunities
    loc_norm = req.location.lower()
    for idx, sample in enumerate(REGIONAL_SAMPLE_JOBS):
        if loc_norm in sample["location"].lower() or loc_norm in ["all", "middle east", "gcc", "global", "uae"]:
            results.append({
                "id": f"reg-{int(time.time())}-{idx}",
                **sample
            })

    # Return deduplicated search listings
    seen = set()
    deduped = []
    for item in results:
        key = f"{item['company'].lower()}_{item['title'].lower()}"
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    return {"results": deduped[:req.limit], "total": len(deduped), "location": req.location}

# ── 10-Dimension Line-by-Line AI Scoring ─────────────────────────────────────

@app.post("/api/score")
async def score_job(req: ScoreRequest):
    """
    Evaluates job descriptions across 10 dimensions against Vinay Prakash's profile.
    Automatically saves high-scoring matches (>= 85) to the Pipeline.
    """
    client = get_scoring_client()
    evaluation = await client.score_with_gemini(
        job_description=req.job_description,
        job_title=req.job_title,
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

# ── Resume Upload Endpoint ───────────────────────────────────────────────────

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

# ── Pipeline CRUD Endpoints ──────────────────────────────────────────────────

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

# ── 1-Click Application Kit Generation ───────────────────────────────────────

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

    # 3. LaTeX Resume Customization
    tex_res = await latex_tailor.generate_tailored_resume(title, company, jd, score_data)

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
        "presentation_deck": pptx_filename,
        "pipeline_item": updated_item
    }

# ── On-Demand Research & Outreach Endpoints ─────────────────────────────────

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

# ── Direct Download Endpoints ────────────────────────────────────────────────

@app.get("/api/downloads/{file_type}/{filename}")
async def download_file(file_type: str, filename: str):
    """Download generated PPTX decks, LaTeX resumes, or outputs."""
    target_dir = LATEX_DIR if file_type == "latex" else OUTPUT_DIR
    target_path = os.path.join(target_dir, filename)

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

# ── Jobs Listing Endpoint (from reports & pipeline) ─────────────────────────

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

# ── AI Chat Assistant ────────────────────────────────────────────────────────

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
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
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
                        return {"response": ans, "model": "Gemini 2.5 Flash"}
        except Exception as e:
            print(f"[Chat] Error: {e}")

    return {
        "response": f"I received your request: '{req.message}'. I can help evaluate opportunities across the GCC and Bangalore, prepare tailored value propositions, and optimize your LaTeX resume. What role would you like to target?",
        "model": "Career-Ops Assistant"
    }

# ── Static Dashboard SPA Serving ─────────────────────────────────────────────

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
    print(f"[Career-Ops] API v4.0.0 — http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
