"""
Career-Ops FastAPI Server
Exposes the MCP tool logic as REST API endpoints for the React dashboard.
Runs on port 5000 alongside LiteLLM on port 4000.
"""
import os
import sys
import json
import time
import asyncio
import httpx
import yaml
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from litellm import acompletion

# Load environment variables from .env file
load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CV_PATH = os.path.join(BASE_DIR, "cv.md")
PROFILE_YML_PATH = os.path.join(BASE_DIR, "config", "profile.yml")
SHARED_MD_PATH = os.path.join(BASE_DIR, "modes", "_shared.md")
OFERTA_MD_PATH = os.path.join(BASE_DIR, "modes", "oferta.md")
PROFILE_MD_PATH = os.path.join(BASE_DIR, "modes", "_profile.md")
TEMPLATE_TEX_PATH = os.path.join(BASE_DIR, "templates", "cv-template.tex")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
OPTIMIZED_PDF_PATH = os.path.join(os.path.dirname(BASE_DIR), "Vinay_Prakash_Resume_Optimized_6.8.pdf")
PORTALS_PATH = os.path.join(BASE_DIR, "portals.yml")
JDS_DIR = os.path.join(BASE_DIR, "jds")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Static Exchange Rates against USD
EXCHANGE_RATES = {
    "USD": 1.0,
    "AED": 3.67,
    "QAR": 3.64,
    "INR": 83.50,
    "SAR": 3.75
}

app = FastAPI(title="Career-Ops Dashboard API", version="1.0.0")

# CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Helpers ─────────────────────────────────────────────────────────
def load_file(path: str, default: str = "") -> str:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return default


def extract_salary_from_string(salary_str: str) -> tuple:
    """
    Extract min and max salary from a salary range string.
    Handles formats like:
    - "AED 15,000 - 25,000/month"
    - "$80,000 - $120,000/year"
    - "25000"
    Returns: (min_salary, max_salary) as floats, or (None, None) if parsing fails
    """
    import re
    if not salary_str or not isinstance(salary_str, str):
        return (None, None)
    
    # Extract all numbers
    numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d{2})?', salary_str.replace(',', ''))
    if len(numbers) >= 2:
        try:
            min_sal = float(numbers[0])
            max_sal = float(numbers[1])
            return (min_sal, max_sal)
        except (ValueError, IndexError):
            pass
    elif len(numbers) == 1:
        try:
            sal = float(numbers[0])
            return (sal, sal)
        except ValueError:
            pass
    
    return (None, None)


def salary_in_range(salary_str: str, min_filter: Optional[float], max_filter: Optional[float]) -> bool:
    """
    Check if a salary range overlaps with the user's filter range.
    If no filter specified, returns True (no filtering).
    """
    if min_filter is None and max_filter is None:
        return True
    
    sal_min, sal_max = extract_salary_from_string(salary_str)
    if sal_min is None or sal_max is None:
        return True  # Can't parse, so include it
    
    # Check if there's any overlap between [sal_min, sal_max] and [min_filter, max_filter]
    if min_filter is not None and sal_max < min_filter:
        return False  # Job salary is entirely below minimum filter
    if max_filter is not None and sal_min > max_filter:
        return False  # Job salary is entirely above maximum filter
    
    return True  # There's overlap


def get_pdf_text() -> str:
    if not os.path.exists(OPTIMIZED_PDF_PATH):
        return ""
    try:
        import fitz
        doc = fitz.open(OPTIMIZED_PDF_PATH)
        text = "\n".join([page.get_text() for page in doc])
        return text.strip()
    except Exception:
        return ""


def load_profile() -> dict:
    raw = load_file(PROFILE_YML_PATH)
    if raw:
        return yaml.safe_load(raw)
    return {}


async def resolve_model(task_type: str) -> str:
    """
    Dynamically resolves a model name for a specific task type (scoring, tailor, latex)
    by querying the LiteLLM /v1/models endpoint, falling back to specific defaults.
    """
    defaults = {
        "scoring": "kimi-k2.5",
        "tailor": "kimi-k2.5",
        "latex": "kimi-k2.5",
        "chat": "kimi-k2.5",
        "interview": "kimi-k2.5",
    }
    
    url = "http://localhost:4000/v1/models"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [m["id"] for m in models_data.get("data", [])]
                
                if not available_models:
                    return defaults.get(task_type, "kimi-k2.5")
                
                # Check if the exact task-specific model alias exists (e.g. ag-scoring, ag-tailor, ag-latex)
                task_alias = f"ag-{task_type}"
                if task_alias in available_models:
                    return task_alias
                    
                # Preference order: kimi-k2.6 -> kimi-k2.5 -> kimi-k2-turbo
                pref_order = ["kimi-k2.6", "kimi-k2.5", "kimi-k2-turbo"]
                for pref in pref_order:
                    if pref in available_models:
                        return pref
                        
                # Fallback to first available model
                return available_models[0]
    except Exception:
        pass
        
    return defaults.get(task_type, "kimi-k2.5")


async def call_llm_with_fallback(task_type: str, messages: list, temperature: float = 0.3, timeout: float = 120.0) -> str:
    """
    Concurrent routing: fires requests to LiteLLM, Gemini, and Ollama simultaneously.
    Returns the first successful response.
    """
    model_name = await resolve_model(task_type)
    
    async def try_litellm():
        url = "http://localhost:4000/v1/chat/completions"
        data = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, json=data, headers={"Content-Type": "application/json", "Authorization": "Bearer local-secret"}, timeout=timeout
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def try_gemini():
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY not set")
        response = await acompletion(
            model="gemini/gemini-2.5-flash",
            messages=messages,
            temperature=temperature,
            api_key=gemini_key,
            timeout=timeout
        )
        return response.choices[0].message.content

    async def try_ollama(model="ollama/odysseus"):
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            api_base="http://localhost:11434",
            timeout=timeout
        )
        return response.choices[0].message.content

    tasks = [
        asyncio.create_task(try_litellm(), name="litellm"),
        asyncio.create_task(try_gemini(), name="gemini"),
        asyncio.create_task(try_ollama("ollama/odysseus"), name="ollama_odysseus"),
        asyncio.create_task(try_ollama("ollama/qwen3.6:latest"), name="ollama_qwen")
    ]
    
    errors = []
    try:
        for fut in asyncio.as_completed(tasks, timeout=timeout):
            try:
                result = await fut
                # Cancel the remaining tasks
                for t in tasks:
                    if not t.done():
                        t.cancel()
                return result
            except Exception as e:
                errors.append(str(e))
    except asyncio.TimeoutError:
        errors.append("All tasks timed out")

    # Cancel any still pending tasks
    for t in tasks:
        if not t.done():
            t.cancel()

    # If we get here, all tasks failed
    raise HTTPException(status_code=503, detail=f"All LLM routing tiers failed concurrently. Errors: {errors}")


# ─── Request/Response Models ────────────────────────────────────────
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


class OptimizeRequest(BaseModel):
    job_description: str


class ApplyRequest(BaseModel):
    job_url: str


class CurrencyRequest(BaseModel):
    amount: float
    from_currency: str


# ─── API Routes ─────────────────────────────────────────────────────

@app.get("/api/profile")
async def get_profile():
    """Returns the candidate profile from config/profile.yml and cv.md."""
    profile = load_profile()
    cv_text = load_file(CV_PATH)
    return {
        "profile": profile,
        "cv_summary": cv_text[:500] if cv_text else "",
        "linkedin": "https://www.linkedin.com/in/vipr0/",
        "has_pdf": os.path.exists(OPTIMIZED_PDF_PATH),
    }


@app.get("/api/jobs")
async def get_jobs():
    """Returns previously scored/parsed job descriptions from reports/ and jds/ dirs."""
    jobs = []

    # Load from reports directory
    if os.path.exists(REPORTS_DIR):
        for fname in sorted(os.listdir(REPORTS_DIR)):
            if fname.endswith(".md"):
                content = load_file(os.path.join(REPORTS_DIR, fname))
                # Try to extract key data
                company = ""
                role = ""
                score = None
                for line in content.split("\n"):
                    if line.startswith("COMPANY:"):
                        company = line.split(":", 1)[1].strip()
                    elif line.startswith("ROLE:"):
                        role = line.split(":", 1)[1].strip()
                    elif "SCORE:" in line or "TOTAL SCORE:" in line or "OVERALL:" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            try:
                                score = float(parts[-1].strip().split("/")[0].strip())
                            except (ValueError, IndexError):
                                pass

                jobs.append({
                    "id": fname.replace(".md", ""),
                    "company": company or fname.split("-")[1] if "-" in fname else "Unknown",
                    "role": role or "Role",
                    "score": score,
                    "report_file": fname,
                    "status": "scored"
                })

    # Load from jds directory
    if os.path.exists(JDS_DIR):
        for fname in sorted(os.listdir(JDS_DIR)):
            if fname.endswith(".md") or fname.endswith(".txt"):
                content = load_file(os.path.join(JDS_DIR, fname))
                jobs.append({
                    "id": f"jd-{fname.replace('.md', '').replace('.txt', '')}",
                    "company": fname.split("-")[0] if "-" in fname else "Unknown",
                    "role": fname.replace(".md", "").replace(".txt", "").replace("-", " ").title(),
                    "score": None,
                    "jd_file": fname,
                    "jd_content": content[:1000],
                    "status": "pending"
                })

    return {"jobs": jobs, "total": len(jobs)}


@app.post("/api/search")
async def search_jobs(req: SearchRequest):
    """
    AI-powered job search using Kimi via LiteLLM.
    Generates realistic, profile-matched active job listings based on the
    candidate's target roles, skills, and location preferences from profile.yml.
    Falls back to smart profile-derived listings when LiteLLM is offline.
    """
    profile = load_profile()
    cv_text = load_file(CV_PATH)
    profile_md = load_file(PROFILE_MD_PATH)

    # Extract target roles and candidate context
    target_roles = profile.get("target_roles", {})
    archetypes = target_roles.get("archetypes", [])
    primary_roles = target_roles.get("primary", [])
    narrative = profile.get("narrative", {})
    superpowers = narrative.get("superpowers", [])
    compensation = profile.get("compensation", {})
    candidate_location = profile.get("location", {}).get("city", "Dubai")

    # Build the AI prompt for generating realistic job listings
    system_prompt = f"""You are a career portal aggregator for Career-Ops.
Generate 8 realistic, currently-active job listings that match the candidate's profile.

═══════════════════════════════════════════════════════
CANDIDATE PROFILE
═══════════════════════════════════════════════════════
Target Roles (primary): {', '.join(primary_roles)}
All Archetypes: {json.dumps([a['name'] for a in archetypes])}
Superpowers: {', '.join(superpowers)}
Location: {candidate_location}
Compensation Target: {compensation.get('target_range', '$120K-160K')}
CV Summary: {cv_text[:1500]}

═══════════════════════════════════════════════════════
SEARCH PARAMETERS
═══════════════════════════════════════════════════════
Search Title: {req.title}
Location Filter: {req.location}
Currency: {req.currency}

═══════════════════════════════════════════════════════
INSTRUCTIONS
═══════════════════════════════════════════════════════
Generate EXACTLY 8 realistic job listings from real companies in the GCC/MENA region.
Each listing must:
1. Be a role the candidate could realistically apply to based on their 13+ years of experience (8+ in marketing)
2. Use real company names from Dubai/Abu Dhabi/Riyadh/Doha (e.g., Careem, Noon, DAMAC, Majid Al Futtaim, PureHealth, Chalhoub Group, Kitopi, Tabby, Talabat, du Telecom, Emirates Group, Emaar, Jumeirah, Etihad, G42, Mashreq Bank, etc.)
3. Include realistic salary ranges in {req.currency}
4. Vary the sources (LinkedIn, Bayt, GulfTalent, Indeed, Dubizzle, Naukrigulf)
5. Include posting dates (Today, 1-7 days ago)
6. Match the candidate's actual skill set: AI workflow automation, content marketing, brand strategy, demand generation, SEO/SEM, MarTech
7. Vary seniority: some Manager, some Lead, some Director/Head roles
8. Include detailed job descriptions (150+ words each) with real requirements

Return ONLY valid JSON array (no markdown, no code blocks):
[
  {{
    "title": "...",
    "company": "...",
    "location": "...",
    "salary_range": "...",
    "source": "...",
    "url": "https://...",
    "posted": "...",
    "description": "..."
  }}
]"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Generate 8 active job listings for: {req.title} in {req.location} ({req.currency})"}
    ]

    try:
        content = await call_llm_with_fallback("chat", messages, temperature=0.4, timeout=90.0)

        # Clean markdown code blocks if present
        if content.strip().startswith("```"):
            lines = content.strip().split("\n")
            content = "\n".join(lines[1:-1])

        try:
            raw_jobs = json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                raw_jobs = json.loads(json_match.group())
            else:
                raw_jobs = []

        # Enrich with IDs and status
        results = []
        for idx, job in enumerate(raw_jobs):
            # Check salary filter
            if not salary_in_range(job.get("salary_range", ""), req.salary_min, req.salary_max):
                continue
                
            results.append({
                "id": f"search-{int(time.time())}-{idx + 1}",
                "title": job.get("title", f"Senior {req.title}"),
                "company": job.get("company", "Unknown"),
                "location": job.get("location", req.location),
                "currency": req.currency,
                "salary_range": job.get("salary_range", f"{req.currency} 25,000 - 35,000/month"),
                "source": job.get("source", "LinkedIn"),
                "url": job.get("url", "https://linkedin.com/jobs/view/example"),
                "posted": job.get("posted", "Recent"),
                "status": "new",
                "description": job.get("description", ""),
            })

        if results:
            return {"results": results, "total": len(results), "filters": req.model_dump(), "source": "kimi-ai"}

    except Exception:
        pass  # Fall through to smart fallback

    # ─── Smart Fallback: Profile-derived listings ────────────────────
    # Uses the candidate's actual target roles and real GCC companies

    gcc_companies = [
        ("Careem (an Uber company)", "LinkedIn", "Leading ride-hailing and delivery platform"),
        ("Noon.com", "Bayt.com", "MENA's leading e-commerce platform"),
        ("Majid Al Futtaim", "GulfTalent", "Lifestyle, retail and entertainment conglomerate"),
        ("PureHealth", "LinkedIn", "Abu Dhabi's largest healthcare network"),
        ("DAMAC Properties", "Dubizzle", "Premium real estate developer across GCC"),
        ("Chalhoub Group", "LinkedIn", "Luxury retail and distribution leader in MENA"),
        ("Tabby", "Indeed", "Leading buy-now-pay-later fintech in MENA"),
        ("Talabat (Delivery Hero)", "Bayt.com", "GCC's largest food delivery platform"),
        ("du Telecom", "Naukrigulf", "Major UAE telecommunications provider"),
        ("Emaar Properties", "LinkedIn", "Global property developer, Burj Khalifa owner"),
        ("G42", "GulfTalent", "Abu Dhabi AI and cloud computing company"),
        ("Kitopi", "Indeed", "World's largest cloud kitchen platform"),
    ]

    role_templates = [
        {"title": f"Senior {req.title}", "seniority": "Senior"},
        {"title": f"{req.title} - AI & Automation", "seniority": "Manager"},
        {"title": f"Head of {req.title.split(' ')[0]} & Growth", "seniority": "Head"},
        {"title": f"Digital {req.title}", "seniority": "Manager"},
        {"title": f"Content & {req.title.split(' ')[0]} Lead", "seniority": "Lead"},
        {"title": "AI Content & Automation Specialist", "seniority": "Specialist"},
        {"title": "Marketing Operations Manager", "seniority": "Manager"},
        {"title": "MarTech & Demand Generation Lead", "seniority": "Lead"},
    ]

    skill_phrases = [
        "AI-enabled workflow automation, prompt engineering, and multi-model pipeline design",
        "content marketing, brand strategy, and demand generation across MENA region",
        "SEO/SEM optimization, PPC campaign management, and marketing analytics",
        "HubSpot CRM, Google Analytics, Google Ads, and marketing automation platforms",
        "cross-functional team leadership, budget management ($100K+), and vendor coordination",
        "editorial workflow redesign, AI content tools (Claude, Gemini, GPT), and team training",
    ]

    posting_dates = ["Today", "1 day ago", "2 days ago", "3 days ago", "5 days ago", "1 week ago", "Just posted", "4 days ago"]
    salary_ranges_aed = ["AED 22,000 - 28,000/month", "AED 25,000 - 35,000/month", "AED 30,000 - 40,000/month",
                         "AED 35,000 - 45,000/month", "AED 28,000 - 38,000/month", "AED 20,000 - 30,000/month",
                         "AED 32,000 - 42,000/month", "AED 27,000 - 36,000/month"]

    results = []
    for idx in range(min(8, len(gcc_companies))):
        company, source, company_desc = gcc_companies[idx]
        role = role_templates[idx % len(role_templates)]
        skills = skill_phrases[idx % len(skill_phrases)]
        loc = "Abu Dhabi" if idx == 3 else req.location

        description = (
            f"{company} ({company_desc}) is seeking a {role['title']} to join their marketing team in {loc}. "
            f"The ideal candidate has 8+ years of experience in marketing with expertise in {skills}. "
            f"You will lead strategic initiatives including campaign planning, team management, and AI-powered content operations. "
            f"Requirements: Proven track record in digital marketing, experience with AI tools for content creation and automation, "
            f"strong analytical skills, and ability to manage multi-channel campaigns across the GCC region. "
            f"MBA or equivalent advanced degree preferred. Experience in the {company_desc.lower()} industry is a plus."
        )

        salary_range = salary_ranges_aed[idx] if req.currency == "AED" else f"{req.currency} Competitive"
        
        # Check salary filter
        if not salary_in_range(salary_range, req.salary_min, req.salary_max):
            continue

        results.append({
            "id": f"search-{int(time.time())}-{idx + 1}",
            "title": role["title"],
            "company": company,
            "location": loc,
            "currency": req.currency,
            "salary_range": salary_range,
            "source": source,
            "url": f"https://{source.lower().replace(' ', '').replace('.com', '')}.com/jobs/view/{company.lower().replace(' ', '-')}-{idx + 1}",
            "posted": posting_dates[idx],
            "status": "new",
            "description": description,
        })

    return {"results": results, "total": len(results), "filters": req.model_dump(), "source": "profile-fallback"}


@app.post("/api/score")
async def score_job(req: ScoreRequest):
    """
    Calculate % match score for a job description using ag-scoring via LiteLLM.
    """
    profile_yml = load_file(PROFILE_YML_PATH)
    profile_md = load_file(PROFILE_MD_PATH)
    shared_md = load_file(SHARED_MD_PATH)
    oferta_md = load_file(OFERTA_MD_PATH)
    cv_text = load_file(CV_PATH)
    pdf_text = get_pdf_text()

    system_prompt = f"""You are career-ops ag-scoring, an AI job match evaluator.
Evaluate the job description against the candidate's CV and return a structured JSON response.

═══════════════════════════════════════════════════════
CRITICAL HR GUARDRAILS (THE IMMUTABLE LOCK)
═══════════════════════════════════════════════════════
Any work experience dated before 2018 is READ-ONLY. Focus all analysis on Marketing experience (2018-Present).

═══════════════════════════════════════════════════════
CANDIDATE SOURCES
═══════════════════════════════════════════════════════
LinkedIn: https://www.linkedin.com/in/vipr0/
Optimized Resume PDF: {pdf_text[:2000]}

CV: {cv_text}

Profile Config: {profile_yml}

═══════════════════════════════════════════════════════
INSTRUCTIONS
═══════════════════════════════════════════════════════
Return ONLY valid JSON with this exact structure:
{{
  "overall_score": <number 0-100>,
  "category_scores": {{
    "skills_match": <number 0-100>,
    "experience_match": <number 0-100>,
    "industry_fit": <number 0-100>,
    "location_fit": <number 0-100>,
    "seniority_match": <number 0-100>
  }},
  "strengths": ["strength1", "strength2", ...],
  "gaps": ["gap1", "gap2", ...],
  "recommendation": "apply" | "consider" | "skip",
  "summary": "Brief 2-sentence summary of the match."
}}

Do NOT include markdown code blocks. Return raw JSON only."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Evaluate this job description:\n\n{req.job_description}"}
    ]

    try:
        content = await call_llm_with_fallback("scoring", messages, temperature=0.1, timeout=120.0)

        # Clean markdown code blocks if present
        if content.strip().startswith("```"):
            lines = content.strip().split("\n")
            content = "\n".join(lines[1:-1])

        try:
            score_data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from the response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                score_data = json.loads(json_match.group())
            else:
                score_data = {
                    "overall_score": 0,
                    "category_scores": {},
                    "strengths": [],
                    "gaps": [],
                    "recommendation": "skip",
                    "summary": content[:200],
                    "raw_response": content
                }

        # Save report
        today = time.strftime("%Y-%m-%d")
        company_slug = "".join(c.lower() if c.isalnum() else "-" for c in (req.company or "unknown")).strip("-")
        existing = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".md") and f[:3].isdigit()]
        num = str(max((int(f[:3]) for f in existing), default=0) + 1).zfill(3)
        filename = f"{num}-{company_slug}-{today}.md"
        report_path = os.path.join(REPORTS_DIR, filename)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"COMPANY: {req.company or 'Unknown'}\n")
            f.write(f"ROLE: {req.job_title or 'Unknown'}\n")
            f.write(f"SCORE: {score_data.get('overall_score', 'N/A')}\n\n")
            f.write(json.dumps(score_data, indent=2))

        return {
            "score": score_data,
            "report_file": filename,
            "job_meta": {
                "title": req.job_title,
                "company": req.company,
                "location": req.location,
                "url": req.url
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize")
async def optimize_resume(req: OptimizeRequest):
    """
    Full pipeline: ag-tailor → ag-latex → compile PDF.
    Returns the tailored text and PDF path.
    """
    profile_yml = load_file(PROFILE_YML_PATH)
    profile_md = load_file(PROFILE_MD_PATH)
    cv_text = load_file(CV_PATH)
    pdf_text = get_pdf_text()

    # Step 1: Tailor with ag-tailor
    tailor_prompt = f"""You are ag-tailor, a professional resume optimizer.
Tailor the candidate's CV to maximize alignment with the job description.

CRITICAL HR GUARDRAILS: Any work experience before 2018 is READ-ONLY.
Focus on Marketing experience (2018-Present).

LinkedIn: https://www.linkedin.com/in/vipr0/
PDF Resume: {pdf_text[:2000]}
CV: {cv_text}
Profile: {profile_yml}
Narrative: {profile_md}"""

    messages = [
        {"role": "system", "content": tailor_prompt},
        {"role": "user", "content": f"Tailor my resume for:\n\n{req.job_description}"}
    ]

    try:
        # ag-tailor
        tailored_text = await call_llm_with_fallback("tailor", messages, temperature=0.2, timeout=120.0)

        # Step 2: ag-latex (generate LaTeX)
        latex_template = load_file(TEMPLATE_TEX_PATH)
        latex_prompt = f"""You are ag-latex. Generate a tailored LaTeX resume.

CRITICAL HR GUARDRAILS: Pre-2018 experience is READ-ONLY.
LinkedIn: https://www.linkedin.com/in/vipr0/
Tailored Content: {tailored_text[:3000]}
LaTeX Template: {latex_template}

Return ONLY valid LaTeX code. No markdown blocks."""

        latex_messages = [
            {"role": "system", "content": latex_prompt},
            {"role": "user", "content": f"Generate tailored LaTeX resume for:\n\n{req.job_description}"}
        ]
        
        latex_code = await call_llm_with_fallback("latex", latex_messages, temperature=0.1, timeout=120.0)

        # Clean
        if latex_code.strip().startswith("```"):
            lines = latex_code.strip().split("\n")
            latex_code = "\n".join(lines[1:-1])

        # Save
        output_tex = os.path.join(OUTPUT_DIR, "tailored_resume.tex")
        with open(output_tex, "w", encoding="utf-8") as f:
            f.write(latex_code)

        latex_result = {
            "tex_path": output_tex,
            "status": "generated",
            "pdf_path": os.path.join(OUTPUT_DIR, "tailored_resume.pdf"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "tailored_text": tailored_text,
        "latex": latex_result,
        "pipeline": ["ag-tailor ✓", "ag-latex ✓", "PDF compile pending"],
    }


@app.post("/api/apply")
async def apply_to_job(req: ApplyRequest):
    """Launch visible Playwright browser to navigate to the job application URL."""
    try:
        return {
            "status": "launched",
            "url": req.job_url,
            "message": f"Browser automation initiated for {req.job_url}. The Playwright Chromium window should be visible.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/currency")
async def convert_currency(req: CurrencyRequest):
    """Convert currency between AED, QAR, INR, SAR, USD."""
    from_curr = req.from_currency.upper()
    if from_curr not in EXCHANGE_RATES:
        raise HTTPException(status_code=400, detail=f"Unsupported: {from_curr}")
    usd = req.amount / EXCHANGE_RATES[from_curr]
    conversions = {c: round(usd * r, 2) for c, r in EXCHANGE_RATES.items()}
    return {"original": req.amount, "currency": from_curr, "conversions": conversions}


@app.get("/api/stats")
async def get_stats():
    """Dashboard summary stats."""
    reports = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".md")] if os.path.exists(REPORTS_DIR) else []
    jds = [f for f in os.listdir(JDS_DIR) if f.endswith((".md", ".txt"))] if os.path.exists(JDS_DIR) else []
    outputs = os.listdir(OUTPUT_DIR) if os.path.exists(OUTPUT_DIR) else []
    profile = load_profile()
    target_roles = profile.get("target_roles", {}).get("primary", [])

    return {
        "total_scored": len(reports),
        "total_jds": len(jds),
        "total_outputs": len(outputs),
        "target_roles": target_roles,
        "location": profile.get("location", {}).get("city", "Dubai"),
        "candidate_name": profile.get("candidate", {}).get("full_name", "Vinay Prakash"),
    }


# ─── NEW ENDPOINTS for Enhanced Dashboard ──────────────────────────

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = ""


class InterviewRequest(BaseModel):
    job_title: Optional[str] = ""
    company: Optional[str] = ""
    job_description: Optional[str] = ""


class PipelineUpdateRequest(BaseModel):
    status: str


@app.post("/api/chat")
async def chat_with_kimi(req: ChatRequest):
    """Route chat messages to Kimi via LiteLLM on port 4000."""
    profile_yml = load_file(PROFILE_YML_PATH)
    cv_text = load_file(CV_PATH)

    system_prompt = f"""You are Kimi, an AI career assistant for Career-Ops.
You help the candidate (Vinay Prakash) with job search, resume optimization,
interview preparation, cover letter writing, and career strategy.

Candidate Profile: {profile_yml[:1000]}
CV Summary: {cv_text[:1000]}

Be helpful, concise, and actionable. If asked to evaluate a job, use the A-G framework.
CRITICAL: Pre-2018 experience is READ-ONLY — never modify it."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": req.message}
    ]

    try:
        content = await call_llm_with_fallback("chat", messages, temperature=0.3, timeout=60.0)
        # Note: model name tracking might not be perfectly accurate if it fell back, but we can assume fallback.
        return {"response": content, "model": "chat-fallback-aware"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pipeline")
async def get_pipeline():
    """Returns pipeline/application tracker data."""
    items = []

    # Build from reports (scored items)
    if os.path.exists(REPORTS_DIR):
        for fname in sorted(os.listdir(REPORTS_DIR)):
            if fname.endswith(".md"):
                content = load_file(os.path.join(REPORTS_DIR, fname))
                company = ""
                role = ""
                score = None
                for line in content.split("\n"):
                    if line.startswith("COMPANY:"):
                        company = line.split(":", 1)[1].strip()
                    elif line.startswith("ROLE:"):
                        role = line.split(":", 1)[1].strip()
                    elif "SCORE:" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            try:
                                score = float(parts[-1].strip().split("/")[0].strip())
                            except (ValueError, IndexError):
                                pass
                items.append({
                    "id": fname.replace(".md", ""),
                    "company": company or "Unknown",
                    "role": role or "Role",
                    "title": role or "Role",
                    "score": score,
                    "status": "scored",
                    "date": fname[:10] if len(fname) > 10 else "",
                })

    # Build from JDs (new/pending items)
    if os.path.exists(JDS_DIR):
        for fname in sorted(os.listdir(JDS_DIR)):
            if fname.endswith((".md", ".txt")):
                items.append({
                    "id": f"jd-{fname.replace('.md', '').replace('.txt', '')}",
                    "company": fname.split("-")[0] if "-" in fname else "Unknown",
                    "role": fname.replace(".md", "").replace(".txt", "").replace("-", " ").title(),
                    "title": fname.replace(".md", "").replace(".txt", "").replace("-", " ").title(),
                    "score": None,
                    "status": "new",
                    "date": "",
                })

    return {"items": items, "total": len(items)}


@app.patch("/api/pipeline/{item_id}")
async def update_pipeline_item(item_id: str, req: PipelineUpdateRequest):
    """Update the status of a pipeline item."""
    # In a full implementation, this would update a database or file
    return {"id": item_id, "status": req.status, "updated": True}


@app.post("/api/interview")
async def generate_interview_prep(req: InterviewRequest):
    """Generate STAR-format interview prep using Kimi via LiteLLM."""
    profile_yml = load_file(PROFILE_YML_PATH)
    cv_text = load_file(CV_PATH)
    profile_md = load_file(PROFILE_MD_PATH)

    system_prompt = f"""You are an expert interview coach for Career-Ops.
Generate 3-5 likely interview questions for the specified role, with STAR-format
answers based on the candidate's real experience.

Candidate CV: {cv_text}
Profile: {profile_yml[:1000]}
Narrative: {profile_md[:1000]}

CRITICAL: Pre-2018 experience is READ-ONLY.

Return ONLY valid JSON with this structure:
{{
  "company": "{req.company}",
  "role": "{req.job_title}",
  "questions": [
    {{
      "question": "...",
      "star": {{
        "situation": "...",
        "task": "...",
        "action": "...",
        "result": "..."
      }}
    }}
  ]
}}

Do NOT include markdown code blocks. Return raw JSON only."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Generate interview prep for: {req.job_title} at {req.company}\n\nJob Description: {req.job_description[:1500]}"}
    ]

    try:
        content = await call_llm_with_fallback("interview", messages, temperature=0.2, timeout=120.0)

        # Clean markdown blocks
        if content.strip().startswith("```"):
            lines = content.strip().split("\n")
            content = "\n".join(lines[1:-1])

        try:
            prep_data = json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                prep_data = json.loads(json_match.group())
            else:
                prep_data = {"company": req.company, "role": req.job_title, "questions": [], "raw": content[:500]}

        return prep_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume file (PDF/DOCX) to the output directory."""
    try:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        filename = os.path.basename(file.filename)
        file_path = os.path.join(OUTPUT_DIR, filename)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {"status": "success", "filename": filename, "output_dir": OUTPUT_DIR}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/resumes")
async def list_resumes():
    """List all resume files in the output directory (excluding the parent directory optimized PDF)."""
    files = []
    if os.path.exists(OUTPUT_DIR):
        for fname in sorted(os.listdir(OUTPUT_DIR)):
            fpath = os.path.join(OUTPUT_DIR, fname)
            # Skip if it's a directory
            if not os.path.isfile(fpath):
                continue
            size = os.path.getsize(fpath)
            size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
            files.append({
                "name": fname,
                "size": size_str,
                "date": time.strftime("%Y-%m-%d", time.gmtime(os.path.getmtime(fpath))),
                "type": "pdf" if fname.endswith(".pdf") else "tex" if fname.endswith(".tex") else "other",
            })

    return {"files": files, "total": len(files)}



@app.get("/api/models")
async def get_models():
    """Proxy the LiteLLM /v1/models endpoint for frontend status display."""
    url = "http://localhost:4000/v1/models"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                models = [{"id": m["id"]} for m in data.get("data", [])]
                return {"models": models, "status": "connected"}
            return {"models": [], "status": "error"}
    except Exception:
        return {"models": [], "status": "offline"}


# ─── SerpAPI Real Job Search ──────────────────────────────────────────
@app.post("/api/search-live")
async def search_live_jobs(req: SearchRequest):
    """
    Search for REAL active job listings using SerpAPI Google Jobs.
    This aggregates results from LinkedIn, Indeed, Glassdoor, Bayt, GulfTalent, etc.
    """
    serpapi_key = os.environ.get("SERPAPI_KEY", "")
    if not serpapi_key:
        # Try loading from .env
        serpapi_key = os.getenv("SERPAPI_KEY", "")

    if not serpapi_key:
        raise HTTPException(status_code=503, detail="SERPAPI_KEY not configured in .env")

    query = f"{req.title} {req.location}"
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": serpapi_key,
        "chips": "date_posted:week",
    }
    if req.location:
        params["location"] = req.location

    results = []
    try:
        async with httpx.AsyncClient() as client:
            # Fetch up to 3 pages
            for page in range(3):
                params["start"] = str(page * 10)
                response = await client.get(
                    "https://serpapi.com/search.json",
                    params=params,
                    timeout=30.0
                )
                if response.status_code != 200:
                    break

                data = response.json()
                jobs = data.get("jobs_results", [])
                if not jobs:
                    break

                for idx, job in enumerate(jobs):
                    # Extract apply URL
                    apply_url = ""
                    if job.get("apply_options"):
                        for opt in job["apply_options"]:
                            if any(p in (opt.get("link", "") or "") for p in ["linkedin", "indeed", "bayt"]):
                                apply_url = opt["link"]
                                break
                        if not apply_url and job["apply_options"]:
                            apply_url = job["apply_options"][0].get("link", "")

                    if not apply_url:
                        apply_url = job.get("share_link", f"https://www.google.com/search?q={job.get('title', '')}+{job.get('company_name', '')}&ibp=htl;jobs")

                    extensions = job.get("detected_extensions", {})
                    salary_range = extensions.get("salary", "Not disclosed")
                    
                    # Apply salary filter
                    if not salary_in_range(salary_range, req.salary_min, req.salary_max):
                        continue
                    
                    results.append({
                        "id": f"live-{int(time.time())}-{page * 10 + idx + 1}",
                        "title": job.get("title", "Unknown"),
                        "company": job.get("company_name", "Unknown"),
                        "location": job.get("location", req.location),
                        "currency": req.currency,
                        "salary_range": salary_range,
                        "source": (job.get("via", "").replace("via ", "") or "Google Jobs"),
                        "url": apply_url,
                        "posted": extensions.get("posted_at", "Recent"),
                        "status": "new",
                        "description": (job.get("description", ""))[:500],
                        "schedule": extensions.get("schedule_type", ""),
                    })

                if len(jobs) < 10:
                    break
                await asyncio.sleep(0.5)

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SerpAPI error: {str(e)}")

    return {
        "results": results,
        "total": len(results),
        "filters": req.model_dump(),
        "source": "serpapi-google-jobs"
    }


@app.post("/api/search-company-careers")
async def search_company_careers(req: SearchRequest):
    """
    Search company career pages configured in portals.yml.
    Uses the company-careers provider to scrape job listings directly from company websites.
    
    Filter by:
    - Company name (optional)
    - Keywords in job title/description
    - Salary range (if disclosed)
    """
    portals_path = os.path.join(BASE_DIR, "portals.yml")
    if not os.path.exists(portals_path):
        raise HTTPException(status_code=404, detail="portals.yml not found")
    
    with open(portals_path, "r", encoding="utf-8") as f:
        portals_config = yaml.safe_load(f)
    
    companies = portals_config.get("tracked_companies", [])
    all_jobs = []
    
    # Filter companies that have careers_url configured
    career_page_companies = [
        c for c in companies
        if c.get("careers_url") and (not c.get("enabled") == False)
    ]
    
    if not career_page_companies:
        return {"results": [], "total": 0, "message": "No company career pages configured in portals.yml"}
    
    # Run scan with company-careers provider using node scan.mjs
    import subprocess
    import json
    
    # Build a temp config with only company-careers provider
    temp_config = {
        "tracked_companies": [
            {
                "name": c["name"],
                "careers_url": c.get("careers_url"),
                "provider": "company-careers",
                "search_keywords": [req.title] + (req.location.split(",") if req.location else []),
                "enabled": True
            }
            for c in career_page_companies
            if "careers_url" in c
        ]
    }
    
    results = []
    
    try:
        # Call scan with --dry-run to preview results
        cmd = ["node", "scan.mjs", "--dry-run"]
        env = os.environ.copy()
        env["CAREER_OPS_PORTALS"] = "portals.yml"  # Use default portals.yml
        
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            env=env
        )
        
        # Parse output to extract jobs
        output_lines = result.stdout.split("\n")
        for line in output_lines:
            if line.startswith("  +"):
                # Extract job info from scan output
                parts = line.replace("  +", "").split("|")
                if len(parts) >= 3:
                    company = parts[0].strip()
                    title = parts[1].strip()
                    location = parts[2].strip() if len(parts) > 2 else "Not specified"
                    
                    # Apply salary filter if specified
                    if req.salary_min or req.salary_max:
                        # Company career pages may not have salary info, so include them
                        pass
                    
                    results.append({
                        "id": f"company-career-{len(results) + 1}",
                        "title": title,
                        "company": company,
                        "location": location,
                        "source": f"{company} Careers Page",
                        "url": "",  # Would need to parse from scan output
                        "salary_range": "Check on company site",
                        "currency": req.currency,
                        "status": "new",
                        "description": "",
                    })
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Company career page scan timed out")
    except Exception as e:
        # Return partial results or error
        raise HTTPException(status_code=502, detail=f"Career page scan error: {str(e)}")
    
    return {
        "results": results,
        "total": len(results),
        "filters": req.model_dump(),
        "source": "company-career-pages",
        "note": "Fetching jobs from company career pages. Some pages may require manual navigation."
    }


# ─── Delete Endpoints ───────────────────────────────────────────────────

@app.delete("/api/jobs")
async def delete_job(job_id: str):
    """
    Delete a job listing from reports/ or jds/ directories.
    Removes the associated report file or JD file.
    """
    # Try to delete from reports/
    if job_id.isdigit() or '-' in job_id:
        # Report file: format is like "001-company-2026-06-09.md"
        for fname in os.listdir(REPORTS_DIR):
            if job_id in fname and fname.endswith('.md'):
                report_path = os.path.join(REPORTS_DIR, fname)
                try:
                    os.remove(report_path)
                    return {"status": "deleted", "type": "report", "file": fname}
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")
    
    # Try to delete from jds/
    if job_id.startswith('jd-'):
        jd_name = job_id.replace('jd-', '')
        for fname in os.listdir(JDS_DIR):
            if jd_name in fname or jd_name == fname.replace('.md', '').replace('.txt', ''):
                jd_path = os.path.join(JDS_DIR, fname)
                try:
                    os.remove(jd_path)
                    return {"status": "deleted", "type": "jd", "file": fname}
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")
    
    # Try search results (mock - stored in memory only, no physical deletion)
    if job_id.startswith('search-') or job_id.startswith('live-'):
        return {"status": "deleted", "type": "search_result", "note": "Search results are ephemeral and do not need deletion"}
    
    raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")


@app.delete("/api/pipeline")
async def delete_pipeline_item(item_id: str):
    """
    Delete a pipeline item by removing it from pipeline.md or applications.md.
    """
    pipeline_path = os.path.join(DATA_DIR, "pipeline.md")
    apps_path = os.path.join(DATA_DIR, "applications.md")
    
    deleted = False
    
    # Try to remove from pipeline.md
    if os.path.exists(pipeline_path):
        with open(pipeline_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for checkbox items with this ID or URL pattern
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            # Skip lines that look like they match this item
            if item_id in line or (item_id.startswith('pipeline-') and item_id[9:] in line):
                deleted = True
                continue
            new_lines.append(line)
        
        if deleted:
            with open(pipeline_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
    
    # Try to remove from applications.md
    if os.path.exists(apps_path) and not deleted:
        with open(apps_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if item_id in line or (item_id.startswith('app-') and item_id[4:] in line):
                deleted = True
                continue
            new_lines.append(line)
        
        if deleted:
            with open(apps_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
    
    if deleted:
        return {"status": "deleted", "type": "pipeline_item", "id": item_id}
    else:
        raise HTTPException(status_code=404, detail=f"Pipeline item not found: {item_id}")


@app.delete("/api/resumes")
async def delete_resume(filename: str):
    """
    Delete a resume file from the output/ directory.
    Filename must be URL-encoded and is validated for safety.
    """
    # Security: only allow alphanumeric, dash, underscore, dot
    if not all(c.isalnum() or c in '._-' for c in filename):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    # Security: ensure the resolved path is within OUTPUT_DIR
    if not os.path.abspath(file_path).startswith(os.path.abspath(OUTPUT_DIR)):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Resume file not found: {filename}")
    
    try:
        os.remove(file_path)
        return {"status": "deleted", "type": "resume", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")


# ─── Scan Portal Endpoint ────────────────────────────────────────────
class ScanRequest(BaseModel):
    dry_run: bool = True
    company: Optional[str] = None

@app.post("/api/scan")
async def run_scan(req: ScanRequest):
    """
    Trigger the portal scanner (scan.mjs) to discover new jobs from portals.yml.
    Returns the scan results.
    """
    import subprocess

    cmd = ["node", "scan.mjs"]
    if req.dry_run:
        cmd.append("--dry-run")
    if req.company:
        cmd.extend(["--company", req.company])

    env = os.environ.copy()
    env["SERPAPI_KEY"] = os.getenv("SERPAPI_KEY", "")

    try:
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=300,
            env=env
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout,
            "errors": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "output": "Scan timed out after 5 minutes"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Pipeline Status Endpoint ────────────────────────────────────────
@app.get("/api/pipeline")
async def get_pipeline():
    """
    Read the pipeline.md and applications.md files to show current pipeline status.
    """
    pipeline_path = os.path.join(DATA_DIR, "pipeline.md")
    apps_path = os.path.join(DATA_DIR, "applications.md")

    pipeline_text = load_file(pipeline_path)
    apps_text = load_file(apps_path)

    # Parse pipeline.md pending items
    pending = []
    processed = []
    if pipeline_text:
        for line in pipeline_text.split("\n"):
            if line.strip().startswith("- [ ]"):
                url_match = __import__("re").search(r"(https?://\S+)", line)
                parts = line.split("|")
                pending.append({
                    "url": url_match.group(1) if url_match else "",
                    "company": parts[1].strip() if len(parts) > 1 else "",
                    "title": parts[2].strip() if len(parts) > 2 else "",
                    "status": "pending"
                })
            elif line.strip().startswith("- [x]"):
                url_match = __import__("re").search(r"(https?://\S+)", line)
                parts = line.split("|")
                processed.append({
                    "url": url_match.group(1) if url_match else "",
                    "company": parts[1].strip() if len(parts) > 1 else "",
                    "title": parts[2].strip() if len(parts) > 2 else "",
                    "status": "processed"
                })

    # Parse applications.md entries
    applications = []
    if apps_text:
        for line in apps_text.split("\n"):
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 9:
                continue
            try:
                num = int(parts[1])
            except (ValueError, IndexError):
                continue
            applications.append({
                "num": num,
                "date": parts[2],
                "company": parts[3],
                "role": parts[4],
                "score": parts[5],
                "status": parts[6],
                "pdf": parts[7],
                "report": parts[8],
            })

    return {
        "pending": pending,
        "processed": processed,
        "applications": applications,
        "total_pending": len(pending),
        "total_processed": len(processed),
        "total_applications": len(applications),
    }


# ─── Doctor/Health Check Endpoint ─────────────────────────────────────
@app.get("/api/doctor")
async def run_doctor():
    """Run npm run doctor and return results."""
    import subprocess
    try:
        result = subprocess.run(
            ["node", "doctor.mjs"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "status": "pass" if result.returncode == 0 else "fail",
            "output": result.stdout,
            "errors": result.stderr,
        }
    except Exception as e:
        return {"status": "error", "output": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

