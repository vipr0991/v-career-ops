"""
Company Deep Research & Decision-Maker Discovery Module
Conducts multi-angle business intelligence and identifies key hiring contacts.
"""
import os
import json
import httpx
import re
from typing import Dict, Any, List, Optional

class CompanyResearchEngine:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.timeout = 45.0

    async def research_company(self, company_name: str, job_title: str = "", location: str = "") -> Dict[str, Any]:
        """Conduct deep research on the target company using Gemini with structured intelligence output."""
        if not company_name or company_name.lower() in ["unknown", "confidential"]:
            return self._default_research(company_name, job_title, location)

        if not self.gemini_key:
            return self._default_research(company_name, job_title, location)

        prompt = f"""You are an elite corporate intelligence analyst and executive headhunter.
Conduct a deep research analysis on '{company_name}' in the context of the '{job_title}' role in '{location}'.

Return ONLY valid JSON with this exact structure:
{{
  "company_name": "{company_name}",
  "business_model": "<How the company monetizes and their core value proposition>",
  "key_products_services": [
    "<product or service line 1>",
    "<product or service line 2>",
    "<product or service line 3>"
  ],
  "market_position_and_competitors": "<Summary of market standing and 3 main competitors>",
  "recent_initiatives_news": [
    "<recent expansion, strategic pivot, tech adoption, or funding milestone>"
  ],
  "strategic_pain_points": [
    "<specific operational, marketing, or AI automation bottleneck the company likely faces>"
  ],
  "hiring_signals": "<Why they are hiring for this role now and their growth trajectory>",
  "candidate_solutions_to_pitch": [
    "<high-impact solution 1 Vinay Prakash can deliver>",
    "<high-impact solution 2 Vinay Prakash can deliver>",
    "<high-impact solution 3 Vinay Prakash can deliver>"
  ],
  "interview_talking_points": [
    "<executive question or strategic talking point to impress the hiring committee>"
  ]
}}"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent",
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
                        return json.loads(json_match.group())
        except Exception as e:
            print(f"[Research] Company research error: {e}")

        return self._default_research(company_name, job_title, location)

    async def find_decision_makers(self, company_name: str, department: str = "Marketing") -> List[Dict[str, Any]]:
        """Identify recommended decision makers and draft LinkedIn outreach angles."""
        if not company_name:
            return []

        if not self.gemini_key:
            return self._default_decision_makers(company_name)

        prompt = f"""Identify the top 3-4 typical decision-maker roles at '{company_name}' relevant to {department} / AI Operations / Executive Leadership.
For each, provide the target title, why they matter, and a LinkedIn search query string.

Return ONLY valid JSON with this exact structure:
{{
  "decision_makers": [
    {{
      "role_category": "Executive / Founder",
      "target_title": "CEO / Founder / Managing Director",
      "relevance": "Final strategic decision maker",
      "recommended_angle": "Focus on ROI, margin improvement, and rapid AI workflow implementation",
      "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords={company_name}+CEO",
      "outreach_note_200_char": "Hi [Name], congrats on {company_name}'s GCC growth! As an AI & MarTech Lead in Dubai, I'd love to connect & share workflow optimization ideas."
    }},
    {{
      "role_category": "Hiring Manager",
      "target_title": "VP of Marketing / Head of Growth / CMO",
      "relevance": "Direct functional manager for the role",
      "recommended_angle": "Highlight multi-channel conversion growth and 50%+ reduction in revision cycles",
      "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords={company_name}+VP+Marketing",
      "outreach_note_200_char": "Hi [Name], loved your recent campaigns at {company_name}. I lead AI-powered MarTech pipelines in the UAE and would value connecting!"
    }},
    {{
      "role_category": "Talent Acquisition",
      "target_title": "Lead Executive Recruiter / Head of Talent",
      "relevance": "Primary gatekeeper and pipeline coordinator",
      "recommended_angle": "Immediate availability in UAE/GCC with verified leadership track record",
      "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords={company_name}+Recruiter",
      "outreach_note_200_char": "Hi [Name], reaching out regarding senior AI & marketing roles at {company_name}. Excited about your team's expansion—let's connect!"
    }}
  ]
}}"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent",
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
                        return parsed.get("decision_makers", [])
        except Exception as e:
            print(f"[Research] Decision maker error: {e}")

        return self._default_decision_makers(company_name)

    def _default_research(self, company_name: str, job_title: str, location: str) -> Dict[str, Any]:
        return {
            "company_name": company_name or "Target Enterprise",
            "business_model": f"{company_name} operates high-growth enterprise/consumer operations in the {location or 'MENA / Global'} market.",
            "key_products_services": [
                "Digital Products & Technology Services",
                "Regional Market Operations",
                "Strategic Customer Solutions"
            ],
            "market_position_and_competitors": f"Recognized player in regional expansion, competing with tier-1 market leaders.",
            "recent_initiatives_news": [
                f"Active regional hiring and expansion in {location or 'GCC markets'}.",
                "Digital transformation and automation upgrades across marketing and operations."
            ],
            "strategic_pain_points": [
                "Scaling marketing output without linear headcount increases.",
                "Integrating AI-assisted pipelines to streamline campaign iteration cycles."
            ],
            "hiring_signals": f"High demand for strategic talent in {job_title or 'Marketing & AI Operations'} to drive market capture.",
            "candidate_solutions_to_pitch": [
                "Implement automated multi-model AI workflows (50%+ reduction in revision turnaround).",
                "Deploy targeted demand-generation funnels to accelerate lead acquisition.",
                "Build scalable editorial and content systems for multi-market reach."
            ],
            "interview_talking_points": [
                f"How {company_name} currently handles cross-channel content velocity and AI pipeline integration.",
                "Proven strategies for accelerating GCC campaign reach and brand authority."
            ]
        }

    def _default_decision_makers(self, company_name: str) -> List[Dict[str, Any]]:
        safe_name = company_name.replace(" ", "+") if company_name else "Company"
        return [
            {
                "role_category": "Executive / Founder",
                "target_title": "CEO / Founder / Managing Director",
                "relevance": "Strategic business leader",
                "recommended_angle": "Focus on high-leverage ROI, automation, and regional scale",
                "linkedin_search_url": f"https://www.linkedin.com/search/results/people/?keywords={safe_name}+CEO",
                "outreach_note_200_char": f"Hi [Name], loved {company_name}'s recent growth! As an AI & MarTech Lead in Dubai, I'd love to connect & share workflow optimization ideas."
            },
            {
                "role_category": "Hiring Manager",
                "target_title": "VP of Marketing / CMO / Head of Growth",
                "relevance": "Direct leadership for marketing & operations",
                "recommended_angle": "Pitch AI campaign automation and multi-channel demand gen",
                "linkedin_search_url": f"https://www.linkedin.com/search/results/people/?keywords={safe_name}+Marketing+Head",
                "outreach_note_200_char": f"Hi [Name], impressed by your team's work at {company_name}. I lead AI MarTech pipelines in the UAE and would value connecting!"
            },
            {
                "role_category": "Talent Acquisition",
                "target_title": "Lead Talent Acquisition / Executive Recruiter",
                "relevance": "Hiring coordinator and pipeline gatekeeper",
                "recommended_angle": "Immediate availability for UAE/GCC leadership roles",
                "linkedin_search_url": f"https://www.linkedin.com/search/results/people/?keywords={safe_name}+Recruiter",
                "outreach_note_200_char": f"Hi [Name], reaching out regarding senior AI & marketing roles at {company_name}. Excited about your team's expansion—let's connect!"
            }
        ]

company_researcher = CompanyResearchEngine()
