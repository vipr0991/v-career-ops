"""
Company Deep Research & Decision-Maker Discovery Module
Conducts multi-angle business intelligence and identifies key hiring contacts.
Multi-model support: Moonshot Kimi AI + Google Gemini AI fallback.
"""
import os
import json
import httpx
import re
from typing import Dict, Any, List, Optional

class CompanyResearchEngine:
    def __init__(self):
        self.kimi_key = (
            os.getenv("KIMI_API_KEY") 
            or os.getenv("MOONSHOT_API_KEY") 
            or "sk-kjfAlmZbu0ZEw1X386RQ94piXfk9Cs18l3Td9icHbxPAPXoW"
        )
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.timeout = 45.0

    async def research_company(self, company_name: str, job_title: str = "", location: str = "") -> Dict[str, Any]:
        """Conduct deep research on target company using Moonshot Kimi AI with Gemini fallback."""
        if not company_name or company_name.lower() in ["unknown", "confidential"]:
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
                                {"role": "system", "content": "You are a professional corporate intelligence analyst. Respond ONLY in valid JSON."},
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
                            return json.loads(json_match.group())
            except Exception as e:
                print(f"[Research] Moonshot Kimi research error: {e}")

        # 2. Try Gemini Fallback
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
                                return json.loads(json_match.group())
                except Exception as e:
                    print(f"[Research] Gemini ({gmodel}) research error: {e}")

        return self._default_research(company_name, job_title, location)

    async def find_decision_makers(self, company_name: str, department: str = "Marketing") -> List[Dict[str, Any]]:
        """Identify recommended decision makers and draft LinkedIn outreach angles."""
        if not company_name:
            return []

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
                                {"role": "system", "content": "You are an executive talent sourcer. Respond ONLY in valid JSON."},
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
                            return parsed.get("decision_makers", [])
            except Exception as e:
                print(f"[Research] Moonshot Kimi decision makers error: {e}")

        # 2. Try Gemini Fallback
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
                                return parsed.get("decision_makers", [])
                except Exception as e:
                    print(f"[Research] Gemini ({gmodel}) decision makers error: {e}")

        return self._default_decision_makers(company_name)

    def _default_research(self, company_name: str, job_title: str, location: str) -> Dict[str, Any]:
        return {
            "company_name": company_name,
            "business_model": f"{company_name} operates high-growth enterprise/consumer operations in the {location or 'UAE / GCC'} market.",
            "key_products_services": [
                f"{company_name} Enterprise Solutions",
                "Regional Market Operations",
                "Digital Customer Experience"
            ],
            "market_position_and_competitors": f"Recognized player in the {location or 'GCC'} market, navigating digital modernization and customer acquisition.",
            "recent_initiatives_news": [
                f"{company_name} regional expansion across UAE and GCC",
                "Digital transformation & operational scaling"
            ],
            "strategic_pain_points": [
                "Scaling marketing output without linear team headcount expansion",
                "Multi-channel demand generation and conversion efficiency",
                "Integrating AI workflows into day-to-day marketing and communications"
            ],
            "hiring_signals": f"Expanding leadership capacity for {job_title} to accelerate regional revenue and market presence.",
            "candidate_solutions_to_pitch": [
                "Deploy AI-assisted marketing pipelines reducing revision cycles by 50%+",
                "Scale multi-channel demand gen campaigns delivering 4000%+ follower and lead growth",
                "Optimize budget allocation and CAC across GCC markets with verified $130K+ budget leadership"
            ],
            "interview_talking_points": [
                f"How is {company_name} currently leveraging AI automation across marketing ops to accelerate time-to-market?",
                f"What are the top 3 commercial priorities for the {job_title} role in Q1/Q2?"
            ]
        }

    def _default_decision_makers(self, company_name: str) -> List[Dict[str, Any]]:
        safe_name = "+".join(company_name.split())
        return [
            {
                "role_category": "Executive / Leadership",
                "target_title": "Managing Director / CEO",
                "relevance": "Strategic sign-off and executive sponsor",
                "recommended_angle": "Focus on ROI, margin improvement, and rapid AI workflow implementation",
                "linkedin_search_url": f"https://www.linkedin.com/search/results/people/?keywords={safe_name}+Managing+Director",
                "outreach_note_200_char": f"Hi [Name], congrats on {company_name}'s GCC growth! As an AI & MarTech Lead in Dubai, I'd love to connect & share workflow optimization ideas."
            },
            {
                "role_category": "Hiring Manager",
                "target_title": "VP of Marketing / Head of Growth",
                "relevance": "Direct line manager and strategic evaluator",
                "recommended_angle": "Highlight multi-channel conversion growth and 50%+ reduction in revision cycles",
                "linkedin_search_url": f"https://www.linkedin.com/search/results/people/?keywords={safe_name}+Marketing+Director",
                "outreach_note_200_char": f"Hi [Name], loved your recent campaigns at {company_name}. I lead AI-powered MarTech pipelines in the UAE and would value connecting!"
            },
            {
                "role_category": "Talent Acquisition",
                "target_title": "Lead Talent Acquisition / Executive Recruiter",
                "relevance": "Recruitment coordinator and gatekeeper",
                "recommended_angle": "Immediate availability in UAE/GCC with verified leadership track record",
                "linkedin_search_url": f"https://www.linkedin.com/search/results/people/?keywords={safe_name}+Recruiter",
                "outreach_note_200_char": f"Hi [Name], reaching out regarding senior AI & marketing roles at {company_name}. Excited about your team's expansion—let's connect!"
            }
        ]

company_researcher = CompanyResearchEngine()
