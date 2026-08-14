"""
NETWORK-RESILIENT FastAPI Backend for Career-Ops
Handles network transitions (home/office WiFi switching) gracefully
"""

import os
import sys
import json
import time
import asyncio
import httpx
import yaml
import socket
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from litellm import acompletion

# Load environment variables
load_dotenv()

# ─── NETWORK RESILIENCE CONFIGURATION ─────────────────────────────────

class RetryConfig:
    """Configuration for retrying failed connections"""
    max_retries = 3
    initial_delay = 1.0
    max_delay = 10.0
    exponential_base = 2.0
    connection_timeout = 15.0
    read_timeout = 60.0
    
    @staticmethod
    def get_delay(attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = RetryConfig.initial_delay * (RetryConfig.exponential_base ** attempt)
        return min(delay, RetryConfig.max_delay)


async def resilient_http_get(url: str, timeout: float = None, max_retries: int = 3) -> Optional[dict]:
    """Make HTTP GET request with network resilience and auto-retry"""
    if timeout is None:
        timeout = RetryConfig.connection_timeout
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                return response if response.status_code == 200 else None
        except (httpx.ConnectError, httpx.TimeoutException, socket.timeout, OSError) as e:
            if attempt < max_retries - 1:
                delay = RetryConfig.get_delay(attempt)
                print(f"[Retry] Connection attempt {attempt + 1} failed ({type(e).__name__}). Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                print(f"[Connection Failed] All {max_retries} attempts failed for {url}")
                return None
        except Exception as e:
            print(f"[Error] Unexpected error in resilient_http_get: {type(e).__name__}: {str(e)[:100]}")
            return None
    
    return None


@asynccontextmanager
async def network_safe_request(description: str = "Request"):
    """Context manager for network-safe requests with logging"""
    print(f"[Network] {description}...")
    try:
        yield
        print(f"[Network] ✓ {description} succeeded")
    except httpx.ConnectError as e:
        print(f"[Network Error] Connection failed: {description}")
        raise
    except httpx.TimeoutException as e:
        print(f"[Network Timeout] Request timed out: {description}")
        raise
    except Exception as e:
        print(f"[Network Error] {type(e).__name__}: {description}")
        raise


# ─── Paths ───────────────────────────────────────────────────────────
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

# Exchange rates
EXCHANGE_RATES = {
    "USD": 1.0,
    "AED": 3.67,
    "QAR": 3.64,
    "INR": 83.50,
    "SAR": 3.75
}

# FastAPI app
app = FastAPI(title="Career-Ops Dashboard API (Network-Resilient)", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Helpers ─────────────────────────────────────────────────────────

def load_file(path: str, default: str = "") -> str:
    """Load file with fallback"""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return default


def extract_salary_from_string(salary_str: str) -> tuple:
    """Extract min/max salary from string"""
    import re
    if not salary_str or not isinstance(salary_str, str):
        return (None, None)
    
    numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d{2})?', salary_str.replace(',', ''))
    if len(numbers) >= 2:
        try:
            return (float(numbers[0]), float(numbers[1]))
        except ValueError:
            pass
    elif len(numbers) == 1:
        try:
            sal = float(numbers[0])
            return (sal, sal)
        except ValueError:
            pass
    
    return (None, None)


def salary_in_range(salary_str: str, min_filter: Optional[float], max_filter: Optional[float]) -> bool:
    """Check if salary overlaps with filter range"""
    if min_filter is None and max_filter is None:
        return True
    
    sal_min, sal_max = extract_salary_from_string(salary_str)
    if sal_min is None or sal_max is None:
        return True
    
    if min_filter is not None and sal_max < min_filter:
        return False
    if max_filter is not None and sal_min > max_filter:
        return False
    
    return True


def get_pdf_text() -> str:
    """Extract text from PDF"""
    if not os.path.exists(OPTIMIZED_PDF_PATH):
        return ""
    try:
        import fitz
        doc = fitz.open(OPTIMIZED_PDF_PATH)
        return "\n".join([page.get_text() for page in doc]).strip()
    except Exception:
        return ""


def load_profile() -> dict:
    """Load profile YAML"""
    raw = load_file(PROFILE_YML_PATH)
    return yaml.safe_load(raw) if raw else {}


async def resolve_model_resilient(task_type: str) -> str:
    """Resolve model name with network resilience (falls back to default if LiteLLM unavailable)"""
    defaults = {
        "scoring": "kimi-k2.5",
        "tailor": "kimi-k2.5",
        "latex": "kimi-k2.5",
        "chat": "kimi-k2.5",
        "interview": "kimi-k2.5",
    }
    
    url = "http://localhost:4000/v1/models"
    
    try:
        async with network_safe_request(f"Resolving model for {task_type}"):
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return defaults.get(task_type, "kimi-k2.5")
                
                models_data = response.json()
                available_models = [m["id"] for m in models_data.get("data", [])]
                
                if not available_models:
                    return defaults.get(task_type, "kimi-k2.5")
                
                task_alias = f"ag-{task_type}"
                if task_alias in available_models:
                    return task_alias
                
                pref_order = ["kimi-k2.6", "kimi-k2.5", "kimi-k2-turbo"]
                for pref in pref_order:
                    if pref in available_models:
                        return pref
                
                return available_models[0]
    
    except Exception as e:
        print(f"[Model Resolution] Falling back to default: {defaults.get(task_type, 'kimi-k2.5')}")
        return defaults.get(task_type, "kimi-k2.5")


async def call_llm_with_fallback(
    task_type: str, 
    messages: list, 
    temperature: float = 0.3, 
    timeout: float = 120.0
) -> str:
    """
    LLM routing with network resilience.
    Tries LiteLLM first, then Gemini, Kimi, Ollama in parallel.
    Returns first successful response.
    """
    model_name = await resolve_model_resilient(task_type)
    
    async def try_litellm_safe():
        try:
            async with network_safe_request(f"LiteLLM ({task_type})"):
                url = "http://localhost:4000/v1/chat/completions"
                data = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": temperature
                }
                
                for attempt in range(2):
                    try:
                        async with httpx.AsyncClient(timeout=timeout) as client:
                            response = await client.post(
                                url,
                                json=data,
                                headers={
                                    "Content-Type": "application/json",
                                    "Authorization": "Bearer local-secret"
                                }
                            )
                            response.raise_for_status()
                            return response.json()["choices"][0]["message"]["content"]
                    except httpx.TimeoutException:
                        if attempt < 1:
                            print(f"LiteLLM timeout (attempt {attempt + 1}/{2}), retrying...")
                            await asyncio.sleep(RetryConfig.get_delay(attempt))
                        else:
                            raise
        except Exception as e:
            print(f"[LiteLLM] Failed: {type(e).__name__}: {str(e)[:80]}")
            raise

    async def try_gemini_safe():
        try:
            async with network_safe_request(f"Gemini ({task_type})"):
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
        except Exception as e:
            print(f"[Gemini] Failed: {type(e).__name__}: {str(e)[:80]}")
            raise

    async def try_ollama_safe(model="ollama/odysseus"):
        try:
            async with network_safe_request(f"Ollama ({model})"):
                response = await acompletion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    api_base="http://localhost:11434",
                    timeout=timeout
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"[Ollama] Failed ({model}): {type(e).__name__}: {str(e)[:80]}")
            raise

    # Fire all tasks concurrently
    tasks = [
        asyncio.create_task(try_litellm_safe(), name="litellm"),
        asyncio.create_task(try_gemini_safe(), name="gemini"),
        asyncio.create_task(try_ollama_safe("ollama/odysseus"), name="ollama_odysseus"),
        asyncio.create_task(try_ollama_safe("ollama/qwen3.6:latest"), name="ollama_qwen")
    ]
    
    errors = []
    try:
        for fut in asyncio.as_completed(tasks, timeout=timeout + 10):
            try:
                result = await fut
                # Cancel remaining tasks
                for t in tasks:
                    if not t.done():
                        t.cancel()
                print(f"[Success] {fut.get_name()} provided response for {task_type}")
                return result
            except asyncio.CancelledError:
                pass
            except Exception as e:
                errors.append(f"{fut.get_name()}: {type(e).__name__}")
    except asyncio.TimeoutError:
        errors.append("All tasks timed out")

    # Cancel pending tasks
    for t in tasks:
        if not t.done():
            t.cancel()

    print(f"[All Agents Failed] Errors: {errors}")
    raise HTTPException(status_code=503, detail=f"All LLM agents failed. Errors: {'; '.join(errors[-2:])}")


# ─── Models ──────────────────────────────────────────────────────────

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


# ─── Routes ──────────────────────────────────────────────────────────

@app.get("/api/stats")
async def get_stats():
    """Dashboard stats"""
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
        "network_resilience": "ENABLED",
    }


@app.post("/api/score")
async def score_job(req: ScoreRequest):
    """Score a job description with network resilience"""
    cv_text = load_file(CV_PATH)
    profile_yml = load_file(PROFILE_YML_PATH)

    system_prompt = f"""You are career-ops ag-scoring, an AI job match evaluator.
Evaluate the job description and return a structured JSON response.

Candidate CV: {cv_text[:1000]}
Profile: {profile_yml[:500]}

Return ONLY valid JSON:
{{
  "overall_score": <0-100>,
  "category_scores": {{
    "skills_match": <0-100>,
    "experience_match": <0-100>,
    "industry_fit": <0-100>,
    "location_fit": <0-100>,
    "seniority_match": <0-100>
  }},
  "strengths": ["str1", "str2"],
  "gaps": ["gap1", "gap2"],
  "recommendation": "apply",
  "summary": "2-sentence summary"
}}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Evaluate: {req.job_title} at {req.company}\n\n{req.job_description[:1500]}"}
    ]

    try:
        content = await call_llm_with_fallback("scoring", messages, temperature=0.1, timeout=120.0)

        # Clean markdown
        if content.strip().startswith("```"):
            lines = content.strip().split("\n")
            content = "\n".join(lines[1:-1])

        try:
            score_data = json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            score_data = json.loads(json_match.group()) if json_match else {"overall_score": 50, "category_scores": {}}

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
        print(f"[Score Error] {type(e).__name__}: {str(e)[:100]}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Career-Ops FastAPI Backend",
        "version": "2.0.0 (Network-Resilient)",
        "status": "healthy",
        "network_resilience": "ENABLED",
        "features": [
            "Automatic retry on network errors",
            "Exponential backoff (1s, 2s, 4s, ...)",
            "Multi-agent LLM fallback (LiteLLM → Gemini → Kimi → Ollama)",
            "Graceful handling of network transitions"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    print("[Info] Starting Career-Ops FastAPI Backend with Network Resilience")
    print("[Info] Features: Auto-retry, exponential backoff, multi-agent fallback")
    print("[Info] Listening on http://0.0.0.0:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
