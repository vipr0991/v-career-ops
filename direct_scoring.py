"""
Direct Scoring Engine for Career-Ops
Implements deep line-by-line evaluation across 10 dimensions for Vinay Prakash's profile.
"""
import os
import json
import httpx
import re
from typing import Optional, Dict, Any, List

CANDIDATE_PROFILE_SUMMARY = """
Candidate: Vinay Prakash (Dubai, UAE / GCC / Bangalore)
Headline: Strategic Marketing & Editorial Leader specializing in AI Workflows & MarTech Automation
Experience: 13+ years overall (8+ in Marketing, Editorial Leadership, Demand Generation, SEO/PPC, Campaigns)
Core Superpowers:
- AI-enabled workflow automation & prompt engineering (Antigravity 2.0, Gemini, Claude, LiteLLM)
- MarTech & Demand Gen (SEO/SEM, HubSpot, Google Analytics, Paid Media, Conversion Optimization)
- Multi-market campaign leadership across UAE, GCC, and global tech ecosystems
- Proven Hero Metrics: 50%+ reduction in revision cycles via AI pipelines; 90K+ reach increase & 1000% newsletter growth; 4415% follower growth on SEO/paid media.
Target Roles: AI Content & Automation Specialist, AI Strategy & Enablement Lead, Marketing Operations Manager, Senior Marketing Manager – MarTech, Head of Digital Marketing.
Locations: UAE (Primary), Saudi Arabia, Qatar, Bahrain, Oman, Kuwait, Bangalore (India).
"""

class DirectScoringClient:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.timeout = 45.0

    async def score_with_gemini(self, job_description: str, job_title: str = "", company: str = "", location: str = "") -> Optional[Dict[str, Any]]:
        """Score job using Google Gemini API with 10-dimension evaluation rubric."""
        if not self.gemini_key:
            return self._heuristic_fallback_score(job_description, job_title, company, location)

        prompt = f"""You are an executive career evaluator and ATS algorithm specialist.
Evaluate the following job description line-by-line against the candidate profile.

Candidate Profile:
{CANDIDATE_PROFILE_SUMMARY}

Target Job:
- Title: {job_title}
- Company: {company}
- Location: {location}
- Description:
{job_description[:3500]}

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
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        parsed["source_agent"] = "Gemini 2.5 Flash"
                        return parsed
        except Exception as e:
            print(f"[Scoring] Gemini evaluation error: {e}")

        return self._heuristic_fallback_score(job_description, job_title, company, location)

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
                keywords_matched.append(kw)
            else:
                keywords_missing.append(kw)

        loc_kw = ["dubai", "uae", "abu dhabi", "saudi", "riyadh", "qatar", "doha", "bangalore", "bengaluru", "remote"]
        loc_score = 70
        for lkw in loc_kw:
            if lkw in text:
                score += 5
                loc_score = 95
                break

        overall = max(40, min(95, score))
        verdict = "Strong Match (Apply Immediately)" if overall >= 80 else "Stretch Match" if overall >= 65 else "Low Match"

        return {
            "overall_score": overall,
            "verdict": verdict,
            "category_scores": {
                "skills_match": min(95, overall + 2),
                "experience_match": min(90, overall),
                "industry_fit": 85,
                "keyword_ats_match": min(90, overall - 2),
                "problem_solving_fit": 88,
                "seniority_fit": 85,
                "location_visa_fit": loc_score,
                "education_certification_fit": 85
            },
            "strengths": [
                f"Strong match for {title or 'target role'} with 13+ years multidisciplinary experience.",
                "Deep background in AI workflow automation and multi-channel marketing campaigns.",
                "Strategic location alignment in the GCC / Bangalore operational footprint."
            ],
            "missing_gaps": [
                "Verify specific niche MarTech vendor certifications if explicitly mandated by the job post."
            ],
            "ats_keywords_found": keywords_matched[:6],
            "ats_keywords_missing": keywords_missing[:3],
            "interview_talking_points": [
                "Highlight 50%+ reduction in revision cycles using multi-model AI pipelines.",
                "Discuss experience driving 90K+ audience reach and high-conversion demand generation."
            ],
            "line_by_line_summary": f"Strong strategic fit for {company or 'the organization'}, with immediate readiness to lead AI-driven marketing and operational expansion.",
            "source_agent": "Career-Ops Heuristic Evaluator"
        }

def get_scoring_client() -> DirectScoringClient:
    return DirectScoringClient()
