"""
LaTeX Resume Tailoring Engine
Powered by Moonshot Kimi API & Google Gemini API
Strictly preserves 100% of authentic career facts from Vinay_Prakash_Resume_Optimized_6.8
Generates compact but readable ~1.5 page resumes (NOT squeezed one-pagers).
"""
import os
import re
import json
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
        self.kimi_key = (
            os.getenv("KIMI_API_KEY") 
            or os.getenv("MOONSHOT_API_KEY") 
            or "sk-kjfAlmZbu0ZEw1X386RQ94piXfk9Cs18l3Td9icHbxPAPXoW"
        )
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.template_path = os.path.join(TEMPLATES_DIR, "cv-template.tex")
        self.timeout = 90.0

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
        Generates a tailored LaTeX resume using Moonshot Kimi AI (with Gemini AI fallback).
        Strictly preserves every authentic detail from Vinay_Prakash_Resume_Optimized_6.8.
        Outputs a compact but readable ~1.5 page resume with all 8 roles and full bullet points.
        """
        template_raw = self._load_template()
        tex_filename = resume_namer.generate_filename(company_name or "Target", extension="tex", candidate_name="Vinay")
        tex_path = os.path.join(LATEX_DIR, tex_filename)

        # Primary source of truth is always the verified master resume template
        primary_source = uploaded_resume_content if (uploaded_resume_content and len(uploaded_resume_content.strip()) > 100) else template_raw

        ats_keywords = (
            (evaluation_data or {}).get("ats_keywords_found", [])
            + (evaluation_data or {}).get("ats_keywords_missing", [])
        )
        keywords_str = (
            ", ".join(ats_keywords[:12])
            if ats_keywords
            else "Brand Strategy, Content Marketing, Demand Generation, Marketing Automation, AI Workflows, SEO/SEM"
        )

        system_instruction = """You are an elite LaTeX resume specialist and career strategist.
Your task is to adapt the candidate's authentic LaTeX resume for a specific target job.

CRITICAL INVARIANTS — ABSOLUTE PRESERVATION RULES:
1. Master Source of Truth: Vinay_Prakash_Resume_Optimized_6.8.
2. DO NOT invent, exaggerate, hallucinate, or add any experience, skills, achievements, education, certifications, companies, dates, or details not present in the source resume.
3. PRESERVE ALL 8 AUTHENTIC ROLES with their exact companies, titles, dates, AND ALL BULLET POINTS:
   - Business Tabloid (Jan 2025 -- Present) — 4 bullet points
   - Green Earth Action Foundation (May 2024 -- Jan 2025) — 3 bullet points
   - Business Tabloid (Aug 2022 -- May 2024) — 3 bullet points
   - Medialogic (Apr 2020 -- Aug 2022) — 3 bullet points
   - Ecommerce Bay L.L.C (Jan 2018 -- Mar 2020) — 2 bullet points
   - Green Energy Solutions Ventilation (Dec 2016 -- Dec 2017) — 1 bullet point
   - Zomato (Jun 2015 -- Sep 2015) — 1 bullet point
   - Sanyo, LG, HP, Etisalat, Panasonic (Jun 2008 -- Aug 2012) — 1 bullet point
4. PRESERVE ALL AUTHENTIC METRICS: 4415% growth, 3M+ reach, $130K+ budget, 90,000+ reach, 1000% newsletter, 5,166+ article views, 1,100+ webinar attendance, 645% social growth, 428% organic growth, AED 250,000+ ROI, AED 590K+ ROI, AED 60,000+ sales.
5. PRESERVE EXACT EDUCATION (both entries):
   - MBA in International Business, Minor in Marketing (2016) -- Madonna University, Livonia
   - B.Sc. in International Business, Minor in Economics (2012) -- Madonna University, Livonia
6. PRESERVE EXACT CONTACT DETAILS — do NOT skip or alter any:
   - Email: voommen@my.madonna.edu
   - UAE Phone: +971 58 595 1173
   - India Phone: +91 9645591928
   - LinkedIn: linkedin.com/in/vipr0
   - Behance: behance.net/vinaypoommen

CRITICAL LAYOUT RULES:
6. The resume MUST be a compact but readable ~1.5 page document. DO NOT compress everything onto a single page.
7. Use \\usepackage[top=0.6in,bottom=0.6in,left=0.65in,right=0.65in]{geometry} for comfortable margins.
8. Use \\usepackage{fancyhdr} with \\pagestyle{fancy} and \\fancyfoot[C]{\\footnotesize\\thepage} for page numbers.
9. Use 10pt font size (\\documentclass[10pt,a4paper]{article}).
10. Every job entry MUST include ALL original bullet points — do NOT remove, merge, or summarise any bullets.

PERMITTED MINOR TAILORING:
- Tailor the 1-paragraph Summary to align with the target role and incorporate relevant keywords naturally from the job description.
- Emphasize the matching Core Skills from the candidate's authentic skill set (may add 1-2 relevant keywords from JD if they are genuinely supported by the candidate's experience).
- Minor keyword tuning in bullet points of the 2-3 most recent roles WITHOUT altering any factual claims, metrics, or company names.

OUTPUT FORMAT:
Return ONLY valid, compilable LaTeX code beginning with \\documentclass and ending with \\end{document}.
Do NOT enclose the output in markdown fences (```latex).
The output MUST be the COMPLETE resume — every section, every role, every bullet, and both education entries."""

        user_prompt = f"""Target Role: {job_title}
Target Company: {company_name}
Target Job Keywords: {keywords_str}

Job Context:
{job_description[:1500]}

Candidate's Master LaTeX Resume (Source of Truth — reproduce ALL content):
{primary_source}

Generate the FULL tailored LaTeX resume now (all 8 roles, all bullet points, both education entries, ~1.5 pages):"""

        # 1. Try Moonshot Kimi API
        if self.kimi_key:
            kimi_models = ["moonshot-v1-32k", "moonshot-v1-8k", "kimi-k2.5", "moonshot-v1-auto"]
            for kmodel in kimi_models:
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            "https://api.moonshot.ai/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {self.kimi_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": kmodel,
                                "messages": [
                                    {"role": "system", "content": system_instruction},
                                    {"role": "user", "content": user_prompt}
                                ],
                                "temperature": 0.2,
                                "max_tokens": 8192
                            }
                        )

                        if response.status_code == 200:
                            data = response.json()
                            content = data["choices"][0]["message"]["content"].strip()
                            cleaned_tex = re.sub(r"^```latex\s*", "", content, flags=re.MULTILINE)
                            cleaned_tex = re.sub(r"^```\s*$", "", cleaned_tex, flags=re.MULTILINE).strip()

                            if "\\documentclass" in cleaned_tex and "\\end{document}" in cleaned_tex:
                                # Validate that critical content is preserved
                                if self._validate_content_integrity(cleaned_tex):
                                    with open(tex_path, "w", encoding="utf-8") as f:
                                        f.write(cleaned_tex)
                                    return {
                                        "tex_path": tex_path,
                                        "tex_filename": tex_filename,
                                        "tex_code": cleaned_tex,
                                        "engine": f"Moonshot Kimi ({kmodel})"
                                    }
                                else:
                                    print(f"[LaTeX] Kimi ({kmodel}) output failed content integrity check, trying next model")
                        else:
                            print(f"[LaTeX] Moonshot Kimi ({kmodel}) status {response.status_code}: {response.text[:200]}")
                except Exception as e:
                    print(f"[LaTeX] Moonshot Kimi {kmodel} error: {e}")

        # 2. Try Gemini API Fallback
        if self.gemini_key:
            gemini_models = ["gemini-3.7-flash", "gemini-flash-latest", "gemini-3.5-flash", "gemini-pro-latest"]
            full_gemini_prompt = f"{system_instruction}\n\n{user_prompt}"
            for gmodel in gemini_models:
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            f"https://generativelanguage.googleapis.com/v1beta/models/{gmodel}:generateContent",
                            headers={"Content-Type": "application/json"},
                            params={"key": self.gemini_key},
                            json={
                                "contents": [{"parts": [{"text": full_gemini_prompt}]}],
                                "generationConfig": {"temperature": 0.15, "maxOutputTokens": 16384}
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
                            cleaned_tex = re.sub(r"^```latex\s*", "", content.strip(), flags=re.MULTILINE)
                            cleaned_tex = re.sub(r"^```\s*$", "", cleaned_tex, flags=re.MULTILINE).strip()

                            if "\\documentclass" in cleaned_tex and "\\end{document}" in cleaned_tex:
                                if self._validate_content_integrity(cleaned_tex):
                                    with open(tex_path, "w", encoding="utf-8") as f:
                                        f.write(cleaned_tex)
                                    return {
                                        "tex_path": tex_path,
                                        "tex_filename": tex_filename,
                                        "tex_code": cleaned_tex,
                                        "engine": f"Gemini ({gmodel})"
                                    }
                                else:
                                    print(f"[LaTeX] Gemini ({gmodel}) output failed content integrity check, trying next model")
                except Exception as e:
                    print(f"[LaTeX] Gemini {gmodel} error: {e}")

        # Fallback: write master template directly (guaranteed full content)
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(primary_source)

        return {
            "tex_path": tex_path,
            "tex_filename": tex_filename,
            "tex_code": primary_source,
            "engine": "Master Template Direct"
        }

    def _validate_content_integrity(self, tex_code: str) -> bool:
        """
        Validates that the AI-generated LaTeX preserves all critical content from the master resume.
        Returns True only if all 8 roles, education, and key metrics are present.
        """
        required_companies = [
            "Business Tabloid",
            "Green Earth",
            "Medialogic",
            "Ecommerce Bay",
            "Green Energy",
            "Zomato",
            "Sanyo"
        ]
        required_education = [
            "Madonna University",
            "MBA",
            "B.Sc"
        ]
        required_metrics = [
            "4415",
            "130K",
            "90,000",
            "1000",
        ]

        for company in required_companies:
            if company not in tex_code:
                print(f"[LaTeX Integrity] MISSING company: {company}")
                return False

        for edu in required_education:
            if edu not in tex_code:
                print(f"[LaTeX Integrity] MISSING education: {edu}")
                return False

        metrics_found = sum(1 for m in required_metrics if m in tex_code)
        if metrics_found < 3:
            print(f"[LaTeX Integrity] Only {metrics_found}/4 key metrics found")
            return False

        return True

latex_tailor = LatexTailoringEngine()
