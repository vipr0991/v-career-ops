import os
import sys
import json
import time
import httpx
import yaml
import subprocess
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("career-ops")

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

# Ensure directories exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Static Exchange Rates against USD for currency conversion
EXCHANGE_RATES = {
    "USD": 1.0,
    "AED": 3.67,
    "QAR": 3.64,
    "INR": 83.50,
    "SAR": 3.75
}

def load_file_content(path: str, default: str = "") -> str:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
    return default

def get_optimized_pdf_text() -> str:
    """Extracts text from the optimized PDF resume of Vinay Prakash."""
    if not os.path.exists(OPTIMIZED_PDF_PATH):
        return ""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(OPTIMIZED_PDF_PATH)
        text = "\n".join([page.get_text() for page in doc])
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}", file=sys.stderr)
        return ""


async def resolve_model(task_type: str) -> str:
    """
    Dynamically resolves a model name for a specific task type (scoring, tailor, latex)
    by querying the LiteLLM /v1/models endpoint, falling back to specific defaults.
    """
    defaults = {
        "scoring": "kimi-k2.5",
        "tailor": "kimi-k2.5",
        "latex": "kimi-k2.5"
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


@mcp.tool()
def convert_currency(amount: float, from_currency: str) -> dict:
    """
    Convert a salary/amount from AED, QAR, INR, SAR, or USD to all other supported currencies.
    
    Args:
        amount: The numerical value to convert.
        from_currency: The currency of the amount (e.g., 'AED', 'QAR', 'INR', 'SAR', 'USD').
    """
    from_curr = from_currency.upper()
    if from_curr not in EXCHANGE_RATES:
        return {"error": f"Unsupported currency '{from_curr}'. Supported: {list(EXCHANGE_RATES.keys())}"}
        
    # Convert to USD first
    amount_in_usd = amount / EXCHANGE_RATES[from_curr]
    
    conversions = {}
    for currency, rate in EXCHANGE_RATES.items():
        conversions[currency] = round(amount_in_usd * rate, 2)
        
    return {
        "original_amount": amount,
        "original_currency": from_curr,
        "conversions": conversions
    }

@mcp.tool()
def prioritize_by_geo(job_location: str) -> dict:
    """
    Prioritize a job listing location against Vinay's target regions (Dubai, Abu Dhabi, Riyadh, Jeddah, Doha, Bangalore).
    
    Args:
        job_location: The location string from the job description.
    """
    loc = job_location.lower()
    target_locations = ["dubai", "abu dhabi", "riyadh", "jeddah", "doha", "bangalore", "bengaluru"]
    
    matched_target = None
    for target in target_locations:
        if target in loc:
            matched_target = target
            break
            
    is_gcc = any(gcc_country in loc for gcc_country in ["uae", "united arab emirates", "saudi", "riyadh", "jeddah", "qatar", "doha", "dubai", "abu dhabi"])
    
    if matched_target:
        priority = "High"
        reason = f"Location matches target city: {matched_target.title()}"
    elif is_gcc:
        priority = "Medium"
        reason = "Location is within preferred GCC region"
    else:
        priority = "Low"
        reason = "Location is outside preferred regions (consider remote terms)"
        
    return {
        "location": job_location,
        "priority_score": priority,
        "reason": reason,
        "is_preferred_region": matched_target is not None or is_gcc
    }

@mcp.tool()
async def analyze_job_match(job_description: str, cv_text: str = None) -> str:
    """
    Evaluates a job description against the candidate's CV and profile context using ag-scoring.
    
    Args:
        job_description: The job description text to evaluate.
        cv_text: Optional override for the candidate's CV. If not provided, cv.md is read.
    """
    # Load profile configurations
    profile_yml = load_file_content(PROFILE_YML_PATH)
    profile_md = load_file_content(PROFILE_MD_PATH)
    shared_md = load_file_content(SHARED_MD_PATH)
    oferta_md = load_file_content(OFERTA_MD_PATH)
    
    # Prioritize CV: Use cv_text if passed, else read cv.md
    if not cv_text:
        cv_text = load_file_content(CV_PATH)
        
    # Read optimized PDF resume and add as supplemental data
    pdf_resume_text = get_optimized_pdf_text()
    
    # System prompt enforcing HR guardrails and target contexts
    system_prompt = f"""You are career-ops, an AI-powered job search assistant.
You evaluate job offers against the user's CV using a structured A-G scoring system.

═══════════════════════════════════════════════════════
CRITICAL HR GUARDRAILS (THE IMMUTABLE LOCK)
═══════════════════════════════════════════════════════
Any work experience dated before 2018 is READ-ONLY. Do not modify. Focus all optimization on Marketing experience (2018-Present).
Do not suggest any sales positions, sales manager or account manager modifications.

═══════════════════════════════════════════════════════
SYSTEM CONTEXT (_shared.md)
═══════════════════════════════════════════════════════
{shared_md}

═══════════════════════════════════════════════════════
EVALUATION MODE (oferta.md)
═══════════════════════════════════════════════════════
{oferta_md}

═══════════════════════════════════════════════════════
CANDIDATE PRIMARY SOURCES (cv.md + LinkedIn + PDF)
═══════════════════════════════════════════════════════
LinkedIn verified profile: https://www.linkedin.com/in/vipr0/
Source Text from Optimized Resume PDF:
{pdf_resume_text}

Markdown CV Context:
{cv_text}

═══════════════════════════════════════════════════════
CANDIDATE PROFILE & TARGETS (config/profile.yml)
═══════════════════════════════════════════════════════
{profile_yml}

═══════════════════════════════════════════════════════
USER ARCHETYPES & NARRATIVE (_profile.md)
═══════════════════════════════════════════════════════
{profile_md}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please evaluate the following job description:\n\n{job_description}"}
    ]
    
    # Send request to LiteLLM proxy ag-scoring model
    url = "http://localhost:4000/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer local-secret"}
    model_name = await resolve_model("scoring")
    data = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.2
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=120.0)
            response.raise_for_status()
            result = response.json()
            evaluation = result["choices"][0]["message"]["content"]
            
            # Save the report sequentially
            # Try to extract company name from the response or prompt
            company_name = "unknown"
            role_name = "unknown"
            for line in evaluation.split("\n"):
                if line.startswith("COMPANY:"):
                    company_name = line.split(":", 1)[1].strip()
                elif line.startswith("ROLE:"):
                    role_name = line.split(":", 1)[1].strip()
            
            # Sequence numbering
            existing_files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".md") and f[:3].isdigit()]
            num = "001"
            if existing_files:
                num = str(max(int(f[:3]) for f in existing_files) + 1).zfill(3)
                
            today = time.strftime("%Y-%m-%d")
            company_slug = "".join(c.lower() if c.isalnum() else "-" for c in company_name).strip("-")
            filename = f"{num}-{company_slug}-{today}.md"
            report_path = os.path.join(REPORTS_DIR, filename)
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(evaluation)
                
            return f"Job Match Evaluation Completed.\n\nReport saved to: reports/{filename}\n\n{evaluation}"
    except Exception as e:
        return f"Error connecting to LiteLLM proxy: {e}. Make sure litellm proxy is running on port 4000."

@mcp.tool()
async def generate_latex_resume(job_description: str, cv_text: str = None) -> dict:
    """
    Generates a tailored LaTeX CV file using the templates/cv-template.tex and compiles it.
    
    Args:
        job_description: The job description to optimize the resume for.
        cv_text: Optional override for the candidate's CV. If not provided, cv.md is used.
    """
    # Load templates and resources
    profile_yml = load_file_content(PROFILE_YML_PATH)
    profile_md = load_file_content(PROFILE_MD_PATH)
    latex_template = load_file_content(TEMPLATE_TEX_PATH)
    
    if not cv_text:
        cv_text = load_file_content(CV_PATH)
        
    pdf_resume_text = get_optimized_pdf_text()
    
    system_prompt = f"""You are ag-latex, a LaTeX resume generation assistant.
Your job is to tailor the candidate's CV experience to match the job description, fill the placeholders in the provided LaTeX template, and output the EXACT tailored LaTeX code.

═══════════════════════════════════════════════════════
CRITICAL HR GUARDRAILS (THE IMMUTABLE LOCK)
═══════════════════════════════════════════════════════
Any work experience dated before 2018 is READ-ONLY. Do not modify. Focus all optimization on Marketing experience (2018-Present).
Do not change, rename or omit these pre-2018 roles (Account Manager at Green Energy Solutions, Sales Manager at Zomato, and internships).
Focus your optimization on the professional experience from 2018 to Present (Marketing & Editorial Director at Business Tabloid, Marketing Manager at Green Earth Action Foundation, and Digital Marketing Manager at Medialogic, etc.).

═══════════════════════════════════════════════════════
CANDIDATE PRIMARY SOURCES
═══════════════════════════════════════════════════════
LinkedIn: https://www.linkedin.com/in/vipr0/
Source Text from Optimized Resume PDF:
{pdf_resume_text}

Markdown CV Context:
{cv_text}

═══════════════════════════════════════════════════════
LATEX TEMPLATE TO FILL
═══════════════════════════════════════════════════════
{latex_template}

Return ONLY valid LaTeX code matching the template structure. Do not wrap in markdown code blocks.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please generate the tailored LaTeX resume for this Job Description:\n\n{job_description}"}
    ]
    
    url = "http://localhost:4000/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer local-secret"}
    model_name = await resolve_model("latex")
    data = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.1
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=120.0)
            response.raise_for_status()
            result = response.json()
            latex_code = result["choices"][0]["message"]["content"]
            
            # Clean markdown code blocks if the model returned them
            if latex_code.startswith("```"):
                lines = latex_code.split("\n")
                if lines[0].startswith("```latex") or lines[0].startswith("```"):
                    latex_code = "\n".join(lines[1:-1])
            
            # Save output .tex file
            output_tex_path = os.path.join(OUTPUT_DIR, "tailored_resume.tex")
            with open(output_tex_path, "w", encoding="utf-8") as f:
                f.write(latex_code)
                
            # Compile using generate-latex.mjs
            compilation_result = subprocess.run(
                ["node", "generate-latex.mjs", output_tex_path],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            
            compiled_successfully = compilation_result.returncode == 0
            
            return {
                "status": "success" if compiled_successfully else "failed",
                "tex_path": output_tex_path,
                "pdf_path": os.path.join(OUTPUT_DIR, "tailored_resume.pdf") if compiled_successfully else None,
                "stdout": compilation_result.stdout,
                "stderr": compilation_result.stderr
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"LaTeX Resume Generation failed: {e}"
        }

@mcp.tool()
async def tailor_resume(job_description: str, cv_text: str = None) -> str:
    """
    Tailors the candidate's resume to align with a job description using ag-tailor (Kimi).
    
    Args:
        job_description: The target job description.
        cv_text: Optional override for the candidate's CV. If not provided, cv.md is used.
    """
    profile_yml = load_file_content(PROFILE_YML_PATH)
    profile_md = load_file_content(PROFILE_MD_PATH)
    
    if not cv_text:
        cv_text = load_file_content(CV_PATH)
        
    pdf_resume_text = get_optimized_pdf_text()
    
    system_prompt = f"""You are ag-tailor, a professional resume optimizer.
Your job is to tailor the candidate's CV experience to maximize alignment with the job description.

═══════════════════════════════════════════════════════
CRITICAL HR GUARDRAILS (THE IMMUTABLE LOCK)
═══════════════════════════════════════════════════════
Any work experience dated before 2018 is READ-ONLY. Do not modify. Focus all optimization on Marketing experience (2018-Present).
Do not modify or rewrite pre-2018 experience.

═══════════════════════════════════════════════════════
CANDIDATE PRIMARY SOURCES
═══════════════════════════════════════════════════════
LinkedIn: https://www.linkedin.com/in/vipr0/
Source Text from Optimized Resume PDF:
{pdf_resume_text}

Markdown CV Context:
{cv_text}

═══════════════════════════════════════════════════════
CANDIDATE PROFILE & TARGETS (config/profile.yml)
═══════════════════════════════════════════════════════
{profile_yml}

═══════════════════════════════════════════════════════
USER ARCHETYPES & NARRATIVE (_profile.md)
═══════════════════════════════════════════════════════
{profile_md}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please tailor my resume for this Job Description:\n\n{job_description}"}
    ]
    
    url = "http://localhost:4000/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer local-secret"}
    model_name = await resolve_model("tailor")
    data = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.2
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=120.0)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Tailoring failed: {e}. Make sure litellm proxy is running on port 4000."

@mcp.tool()
def apply_to_job(job_url: str) -> str:
    """
    Launches a visible Chromium browser window using Playwright to navigate to the job application URL.
    This allows the user to review and submit the application form interactively.
    
    Args:
        job_url: The application form or listing URL.
    """
    from playwright.sync_api import sync_playwright
    import time
    
    try:
        # Launch visible browser
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(job_url)
            
            # Monitor loop until browser or page is closed
            # Provide standard timeout of 10 minutes to avoid hanging indefinitely
            timeout = 600  # 10 minutes
            start_time = time.time()
            while time.time() - start_time < timeout:
                if page.is_closed():
                    break
                time.sleep(1)
                
        return f"Browser session ended for URL: {job_url}"
    except Exception as e:
        return f"Failed to execute browser automation: {e}"

if __name__ == "__main__":
    mcp.run()
