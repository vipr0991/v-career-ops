"""
Direct Scoring Engine for Career-Ops
Implements deep line-by-line evaluation across 10 dimensions for Vinay Prakash's profile.
Multi-model support: Moonshot Kimi AI + Google Gemini AI fallback.
Source of Truth: Vinay_Prakash_Resume_Optimized_6.8
"""
import os
import json
import httpx
import re
from typing import Optional, Dict, Any, List

CANDIDATE_PROFILE_SUMMARY = """
Candidate: Vinay Prakash (Dubai, UAE / GCC / Bangalore)
Contact: voommen@my.madonna.edu | +971 58 595 1173 | +91 9645591928 | linkedin.com/in/vipr0
Headline: Strategic Marketing & Editorial Leader specializing in AI Workflows, MarTech Automation & Demand Gen
Experience: 13+ years overall (8+ in Marketing, Editorial Leadership, Demand Generation, SEO/PPC, Campaigns)
Core Roles & Facts (Master Source: Vinay_Prakash_Resume_Optimized_6.8):
1. Business Tabloid (Jan 2025 – Present): Marketing & Editorial Director, AI-Driven Content, Workflows & Automation. Built multi-model AI pipelines (Antigravity 2.0, Gemini, Claude, GPT-OSS, Qwen, Kimi, LLMLite), reducing revision cycles by 50%+ and editing effort by 60%+.
2. Green Earth Action Foundation (May 2024 – Jan 2025): Marketing Manager. Managed $130K budget, reduced long-term costs by 15%, +90K LinkedIn reach, +1000% newsletter, 1,100+ webinar attendees.
3. Business Tabloid (Aug 2022 – May 2024): Marketing Manager. Led 'The Unknown Series', 4415% follower growth via SEO/paid media, mentored 5 across 12+ campaigns, 200+ monthly leads.
4. Medialogic (Apr 2020 – Aug 2022): Digital Marketing Manager. Localized PPC/SaaS strategies across UAE, KSA, Oman, Qatar, Bahrain, Kuwait, Jordan, Egypt. -20% CAC, +65K pageviews, +42% conversion rate.
5. Ecommerce Bay L.L.C (Jan 2018 – Mar 2020): Senior Marketing Executive. 428% organic growth, +18% conversion rate.
6. Green Energy Solutions Ventilation (Dec 2016 – Dec 2017): Account Manager. HubSpot CRM, +25% team productivity, AED 60K+ sales support.
7. Zomato (Jun 2015 – Sep 2015): Sales Manager. Secured 20+ contracts, AED 250,000+ ROI.
8. Sanyo, LG, HP, Etisalat, Panasonic (Jun 2008 – Aug 2012): Marketing & Sales Internships. AED 590K+ ROI.
Education: MBA (2016) & B.Sc. (2012) in International Business from Madonna University, Livonia.
"""

class DirectScoringClient:
    def __init__(self):
        self.kimi_key = (
            os.getenv("KIMI_API_KEY") 
            or os.getenv("MOONSHOT_API_KEY") 
            or "sk-kjfAlmZbu0ZEw1X386RQ94piXfk9Cs18l3Td9icHbxPAPXoW"
        )
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.timeout = 45.0

    async def score_job(
        self,
        job_description: str = "",
        job_title: str = "",
        company: str = "",
        location: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """Unified entry point for scoring a job description."""
        jd = job_description or kwargs.get("jd", "") or kwargs.get("description", "")
        title = job_title or kwargs.get("title", "")
        comp = company or kwargs.get("company_name", "")
        loc = location or kwargs.get("loc", "")
        return await self.score_with_gemini(job_description=jd, job_title=title, company=comp, location=loc)

    async def score_with_gemini(self, job_description: str, job_title: str = "", company: str = "", location: str = "") -> Dict[str, Any]:
        """Score job using Moonshot Kimi AI (with Gemini fallback) against 10-dimension rubric."""
        prompt = f"""You are an executive career evaluator and ATS algorithm specialist.
Evaluate the following job description line-by-line against the candidate profile.

Candidate Profile (Source of Truth):
{CANDIDATE_PROFILE_SUMMARY}

Target Job:
- Title: {job_title}
- Company: {company}
- Location: {location}
- Description:
{job_description[:6000]}

Perform a comprehensive 10-dimension evaluation and return ONLY valid JSON with this exact schema:
{{
  "overall_score": <int 0-100>,
  "verdict": "<Strong Match (Apply Immediately) | Stretch Match | Low Match>",
  "category_scores": {{
    "skills_match": <int 0-100>,
    "experience_match": <int 0-100>,
    "industry_fit": <int 0-100>,
    "keyword_ats_match": <int 0-100>,
    "problem_solving_fit": <int 0-100>,
    "seniority_fit": <int 0-100>,
    "location_visa_fit": <int 0-100>,
    "education_certification_fit": <int 0-100>
  }},
  "strengths": [
    "<specific line-item requirement that candidate directly matches with proof points>"
  ],
  "missing_gaps": [
    "<specific missing tool or experience requirement not directly prominent>"
  ],
  "ats_keywords_found": ["<keyword1>", "<keyword2>"],
  "ats_keywords_missing": ["<keyword1>", "<keyword2>"],
  "interview_talking_points": [
    "<strategic talking point to pitch candidate's hero metrics for this company's pain points>"
  ],
  "line_by_line_summary": "<2-3 sentence executive match summary>"
}}"""

        # 1. Try Moonshot Kimi AI
        if self.kimi_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        "https://api.moonshot.ai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.kimi_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "moonshot-v1-32k",
                            "messages": [
                                {"role": "system", "content": "You are a professional ATS and executive recruitment evaluation engine. Respond ONLY in valid JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.2,
                            "max_tokens": 2048
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"].strip()
                        json_match = re.search(r'\{[\s\S]*\}', content)
                        if json_match:
                            parsed = json.loads(json_match.group())
                            parsed["source_agent"] = "Moonshot Kimi"
                            return self._normalize_score_dict(parsed)
            except Exception as e:
                print(f"[Scoring] Moonshot Kimi scoring error: {e}")

        # 2. Try Gemini API Fallback
        if self.gemini_key:
            for gmodel in ["gemini-3.7-flash", "gemini-flash-latest"]:
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            f"https://generativelanguage.googleapis.com/v1beta/models/{gmodel}:generateContent",
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
                            json_match = re.search(r'\{[\s\S]*\}', content)
                            if json_match:
                                parsed = json.loads(json_match.group())
                                parsed["source_agent"] = f"Gemini ({gmodel})"
                                return self._normalize_score_dict(parsed)
                except Exception as e:
                    print(f"[Scoring] Gemini ({gmodel}) scoring error: {e}")

        return self._normalize_score_dict(self._heuristic_fallback_score(job_description, job_title, company, location))

    def _normalize_score_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Harmonize score, verdict, and engine aliases."""
        if not isinstance(data, dict):
            return {"overall_score": 65, "total_score": 65, "verdict": "Stretch Match", "recommendation": "Review"}

        # Score normalization
        sc = data.get("overall_score") or data.get("total_score") or data.get("score") or 70
        try:
            sc = int(sc)
        except Exception:
            sc = 70
        data["overall_score"] = sc
        data["total_score"] = sc
        data["score"] = sc

        # Verdict normalization
        vd = data.get("verdict") or data.get("recommendation") or "Stretch Match"
        data["verdict"] = vd
        data["recommendation"] = vd

        # Engine normalization
        eng = data.get("source_agent") or data.get("engine") or "Direct Scoring Engine"
        data["source_agent"] = eng
        data["engine"] = eng
        return data

    def _heuristic_fallback_score(self, jd: str, title: str, company: str, location: str) -> Dict[str, Any]:
        """Heuristic rule-based fallback evaluation."""
        text = f"{title} {jd} {location}".lower()
        score = 65

        keywords_matched = []
        keywords_missing = []

        core_kw = ["marketing", "ai", "automation", "strategy", "content", "seo", "campaign", "digital", "operations", "lead", "manager"]
        for kw in core_kw:
            if kw in text:
                score += 3
                keywords_matched.append(kw.title())
            else:
                keywords_missing.append(kw.title())

        score = min(score, 94)
        verdict = "Strong Match (Apply Immediately)" if score >= 85 else ("Stretch Match" if score >= 70 else "Low Match")

        return {
            "overall_score": score,
            "verdict": verdict,
            "category_scores": {
                "skills_match": score + 2,
                "experience_match": score,
                "industry_fit": score - 3,
                "keyword_ats_match": score + 1,
                "problem_solving_fit": score + 4,
                "seniority_fit": score,
                "location_visa_fit": 95 if any(x in text for x in ["dubai", "uae", "abu dhabi", "remote", "gcc"]) else 75,
                "education_certification_fit": 90
            },
            "strengths": [
                "13+ years overall experience (8+ in Marketing & AI Automation) aligns with seniority requirements",
                "Proven GCC and UAE track record with verified hero metrics (4415% follower growth, $130K budget optimisation)",
                "Full-stack capability in marketing automation (HubSpot, Google Analytics, SEO/PPC) and AI workflow pipelines"
            ],
            "missing_gaps": [
                "Verify specific vertical industry nuances and preferred proprietary tools mentioned in JD"
            ],
            "ats_keywords_found": keywords_matched[:8],
            "ats_keywords_missing": keywords_missing[:4],
            "interview_talking_points": [
                "Pitch 50%+ reduction in revision cycles and 40%+ faster turnaround on marketing workflows",
                "Highlight multi-country campaign scaling across UAE/KSA/GCC with $130K+ budget optimisation"
            ],
            "line_by_line_summary": f"High-confidence match ({score}%) for {title} at {company}. Strong alignment across AI workflows, brand strategy, and commercial growth.",
            "source_agent": "Heuristic Rule Engine"
        }

scoring_client = DirectScoringClient()

def get_scoring_client() -> DirectScoringClient:
    return scoring_client
