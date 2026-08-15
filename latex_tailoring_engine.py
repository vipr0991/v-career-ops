"""
LaTeX Resume Tailoring Engine
Customizes LaTeX resume based on cv-template.tex AND any uploaded resume file
for specific target roles, preserving every authentic detail from the originals.
"""
import os
import re
import httpx
from typing import Dict, Any, Optional

from resume_namer import resume_namer

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
        self.timeout = 60.0

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
        evaluation_data: Optional[Dict[str, Any]] = None,
        uploaded_resume_content: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generates a customized LaTeX resume tailored to a specific job.

        Source priority:
          1. uploaded_resume_content (the user's actual uploaded .tex file) — PRIMARY
          2. cv-template.tex (the structured default template) — STRUCTURAL FALLBACK

        Every authentic fact, role, company, date, and achievement from the original
        resume(s) is preserved. Only phrasing, ordering, and emphasis are adapted
        to align with the target role and ATS keywords.
        """
        template_raw = self._load_template()
        tex_filename = resume_namer.generate_filename(company_name or "Target", extension="tex", candidate_name="Vinay")
        tex_path = os.path.join(LATEX_DIR, tex_filename)

        # Determine the primary source content
        if uploaded_resume_content and len(uploaded_resume_content.strip()) > 50:
            primary_source_label = "User's Uploaded Resume (PRIMARY SOURCE)"
            primary_source = uploaded_resume_content[:6000]
            secondary_source = (
                f"\n\nAdditional Structural Reference (cv-template.tex):\n{template_raw[:2000]}"
                if template_raw else ""
            )
        elif template_raw:
            primary_source_label = "cv-template.tex (Default Template)"
            primary_source = template_raw
            secondary_source = ""
        else:
            primary_source_label = "Fallback"
            primary_source = (
                "% Career-Ops LaTeX Resume\n\\documentclass{article}\n"
                "\\begin{document}\nVinay Prakash\n\\end{document}"
            )
            secondary_source = ""

        if not self.gemini_key:
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(primary_source)
            return {"tex_path": tex_path, "tex_filename": tex_filename}

        ats_keywords = (
            (evaluation_data or {}).get("ats_keywords_found", [])
            + (evaluation_data or {}).get("ats_keywords_missing", [])
        )
        keywords_str = (
            ", ".join(ats_keywords[:12])
            if ats_keywords
            else "AI Workflows, MarTech, Demand Generation, SEO/SEM, Marketing Automation"
        )

        prompt = f"""You are an elite LaTeX resume specialist and career strategist.

TASK: Tailor the candidate's resume for:
  Role: '{job_title}'
  Company: '{company_name}'

TARGET JOB KEYWORDS (embed naturally): {keywords_str}

JOB DESCRIPTION CONTEXT:
{job_description[:1500]}

SOURCE RESUME ({primary_source_label}):
{primary_source}
{secondary_source}

STRICT TAILORING RULES — FOLLOW ALL OR THE OUTPUT IS REJECTED:

PRESERVATION (never alter these):
1. ALL personal facts: full name, email, phone, LinkedIn, location.
2. ALL authentic experience entries: every company name, job title, and employment date must be 100% accurate.
3. ALL authentic achievements and metrics (percentages, dollar figures, headcounts) — do not invent new numbers.
4. ALL education, certifications, and language proficiencies exactly as stated.

TAILORING (what you CAN do):
5. Reorder and rephrase bullet points to lead with the most relevant achievements for '{job_title}'.
6. Embed the target keywords naturally into the Professional Summary and the two most recent roles.
7. Promote the most relevant skills to the top of the Skills section.
8. Tighten language for clarity and impact — remove filler words.
9. Add a concise Professional Summary (2-3 sentences) if one is absent, synthesised ONLY from real content in the source.

QUALITY CHECKLIST (review before outputting):
- Accuracy: every company, date, title, and metric matches the source.
- Clarity: every bullet is action-verb led and outcome-focused.
- Consistency: tense, capitalisation, and punctuation are uniform throughout.
- Formatting: LaTeX compiles without errors; all environments are properly closed.
- Keyword alignment: at least 5 of the target keywords appear naturally.
- Relevance: the top 3 bullets in the most recent role speak directly to '{job_title}'.

OUTPUT FORMAT:
Return ONLY valid, compilable LaTeX code.
Do NOT wrap it in markdown code fences.
The output MUST begin with \\documentclass and end with \\end{{document}}."""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                    headers={"Content-Type": "application/json"},
                    params={"key": self.gemini_key},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.15, "maxOutputTokens": 8192}
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = (
                        data.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                    )
                    # Strip any accidental markdown code fences
                    cleaned_tex = re.sub(r"^```latex\s*", "", content.strip(), flags=re.MULTILINE)
                    cleaned_tex = re.sub(r"^```\s*$", "", cleaned_tex, flags=re.MULTILINE)
                    cleaned_tex = cleaned_tex.strip()

                    if "\\documentclass" in cleaned_tex and "\\end{document}" in cleaned_tex:
                        with open(tex_path, "w", encoding="utf-8") as f:
                            f.write(cleaned_tex)
                        return {
                            "tex_path": tex_path,
                            "tex_filename": tex_filename,
                            "tex_code": cleaned_tex,
                        }
                else:
                    print(f"[LaTeX] Gemini API error {response.status_code}: {response.text[:300]}")
        except Exception as e:
            print(f"[LaTeX] Tailoring error: {e}")

        # Fallback: save the primary source as-is (preserves all real data)
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(primary_source)

        return {
            "tex_path": tex_path,
            "tex_filename": tex_filename,
            "tex_code": primary_source,
        }


latex_tailor = LatexTailoringEngine()
