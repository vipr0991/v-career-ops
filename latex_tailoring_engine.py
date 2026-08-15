"""
LaTeX Resume Tailoring Engine
Customizes LaTeX resume based on cv-template.tex for specific target roles.
"""
import os
import time
import re
import httpx
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
LATEX_DIR = os.path.join(BASE_DIR, "latex_resumes")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(LATEX_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class LatexTailoringEngine:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.template_path = os.path.join(TEMPLATES_DIR, "cv-template.tex")
        self.timeout = 45.0

    def _load_template(self) -> str:
        if os.path.exists(self.template_path):
            with open(self.template_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    async def generate_tailored_resume(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        evaluation_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generates customized LaTeX code tailored to target job.
        Saves .tex file in latex_resumes/ and returns paths.
        """
        template_raw = self._load_template()
        company_slug = "".join(c.lower() if c.isalnum() else "-" for c in (company_name or "target")).strip("-")
        tex_filename = f"resume-{company_slug}-{int(time.time())}.tex"
        tex_path = os.path.join(LATEX_DIR, tex_filename)

        if not self.gemini_key or not template_raw:
            # Clean template fallback
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(template_raw or "% Career-Ops LaTeX Resume\n\\documentclass{article}\n\\begin{document}\nVinay Prakash\n\\end{document}")
            return {"tex_path": tex_path, "tex_filename": tex_filename}

        ats_keywords = (evaluation_data or {}).get("ats_keywords_found", []) + (evaluation_data or {}).get("ats_keywords_missing", [])
        keywords_str = ", ".join(ats_keywords[:8]) if ats_keywords else "AI Workflows, MarTech, Demand Generation, SEO/SEM"

        prompt = f"""You are a master LaTeX resume specialist.
Tailor this LaTeX resume for the role: '{job_title}' at '{company_name}'.

Target Job Keywords: {keywords_str}
Job Description Snippet: {job_description[:1200]}

Rules:
1. Preserve strict valid LaTeX syntax and all documentclass/package definitions.
2. Customize the Executive Summary and recent experience bullet points to highlight relevant impact and keywords for '{job_title}'.
3. CRITICAL: Do NOT alter personal facts or pre-2018 historical foundations.
4. Return ONLY valid compilable LaTeX code with no markdown formatting around it (or wrapped in ```latex ... ```).

Base LaTeX Template:
{template_raw}"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                    headers={"Content-Type": "application/json"},
                    params={"key": self.gemini_key},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.2}
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    cleaned_tex = re.sub(r'^```latex\s*', '', content, flags=re.MULTILINE)
                    cleaned_tex = re.sub(r'^```\s*', '', cleaned_tex, flags=re.MULTILINE)
                    
                    if "\\documentclass" in cleaned_tex and "\\end{document}" in cleaned_tex:
                        with open(tex_path, "w", encoding="utf-8") as f:
                            f.write(cleaned_tex.strip())
                        return {"tex_path": tex_path, "tex_filename": tex_filename}
        except Exception as e:
            print(f"[LaTeX] Tailoring error: {e}")

        # Fallback to saving original template
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(template_raw)

        return {"tex_path": tex_path, "tex_filename": tex_filename}

latex_tailor = LatexTailoringEngine()
