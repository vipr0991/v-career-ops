"""
Fallback Scoring Agents for Career-Ops
When LiteLLM proxy is offline, use direct API calls to Gemini, Ollama, or other agents.
"""
import os
import json
import httpx
import re
from typing import Optional, Dict, List
from enum import Enum


class ScoringAgent(Enum):
    """Available scoring agents"""
    GEMINI = "gemini"          # Google Gemini API (cloud)
    OLLAMA = "ollama"          # Local Ollama instance
    DIRECT_KIMI = "kimi"       # Direct Moonshot API
    FALLBACK = "fallback"      # Hardcoded fallback scores


class DirectScoringClient:
    """Direct API clients for scoring when LiteLLM is offline"""
    
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.kimi_key = os.getenv("KIMI_API_KEY", "")
        self.ollama_base = "http://localhost:11434"
        self.timeout = 120.0
    
    async def score_with_gemini(self, job_description: str, job_title: str = "", company: str = "") -> Optional[Dict]:
        """Score job using Google Gemini API directly (no LiteLLM)"""
        if not self.gemini_key:
            return None
        
        prompt = f"""You are a career match evaluator. Evaluate this job against a candidate's profile.

Job Title: {job_title}
Company: {company}
Job Description: {job_description[:2000]}

Return ONLY valid JSON with this exact structure:
{{
  "overall_score": <0-100>,
  "category_scores": {{
    "skills_match": <0-100>,
    "experience_match": <0-100>,
    "industry_fit": <0-100>,
    "location_fit": <0-100>,
    "seniority_match": <0-100>
  }},
  "strengths": ["strength1", "strength2", "strength3"],
  "gaps": ["gap1", "gap2"],
  "recommendation": "apply",
  "summary": "2-sentence match summary"
}}"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                    headers={"Content-Type": "application/json"},
                    params={"key": self.gemini_key},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.1}
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                
                # Extract JSON
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    return json.loads(json_match.group())
        
        except Exception as e:
            print(f"Gemini scoring error: {e}")
        
        return None
    
    async def score_with_ollama(self, job_description: str, job_title: str = "", company: str = "") -> Optional[Dict]:
        """Score job using local Ollama instance (free, runs locally)"""
        prompt = f"""Job Title: {job_title}
Company: {company}
Description: {job_description[:1500]}

Provide a match score from 0-100 and brief assessment. Format as JSON:
{{"overall_score": <0-100>, "summary": "...", "strengths": [...], "gaps": [...]}}"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base}/api/generate",
                    json={
                        "model": "qwen3.6:latest",
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                output = data.get("response", "")
                
                # Try to extract JSON
                json_match = re.search(r'\{[\s\S]*\}', output)
                if json_match:
                    parsed = json.loads(json_match.group())
                    # Normalize response
                    return {
                        "overall_score": parsed.get("overall_score", 50),
                        "category_scores": {
                            "skills_match": 60,
                            "experience_match": 55,
                            "industry_fit": 50,
                            "location_fit": 70,
                            "seniority_match": 55
                        },
                        "strengths": parsed.get("strengths", ["Experience", "Technical skills"]),
                        "gaps": parsed.get("gaps", ["Industry experience"]),
                        "recommendation": "consider" if parsed.get("overall_score", 50) >= 60 else "consider",
                        "summary": parsed.get("summary", "Local evaluation via Ollama")
                    }
        
        except Exception as e:
            print(f"Ollama scoring error: {e}")
        
        return None
    
    async def score_with_direct_kimi(self, job_description: str, job_title: str = "", company: str = "") -> Optional[Dict]:
        """Score job using Moonshot Kimi API directly (bypasses LiteLLM)"""
        if not self.kimi_key:
            return None
        
        prompt = f"""Evaluate job match: {job_title} at {company}

Job Description (first 2000 chars):
{job_description[:2000]}

Return ONLY valid JSON (no markdown):
{{
  "overall_score": <0-100>,
  "category_scores": {{
    "skills_match": <0-100>,
    "experience_match": <0-100>,
    "industry_fit": <0-100>,
    "location_fit": <0-100>,
    "seniority_match": <0-100>
  }},
  "strengths": ["str1", "str2", "str3"],
  "gaps": ["gap1", "gap2"],
  "recommendation": "apply",
  "summary": "2-sentence assessment"
}}"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.moonshot.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.kimi_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "moonshot-v1-128k",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    return json.loads(json_match.group())
        
        except Exception as e:
            print(f"Kimi direct scoring error: {e}")
        
        return None
    
    @staticmethod
    def fallback_score(job_title: str = "", company: str = "") -> Dict:
        """Fallback hardcoded score when all APIs fail"""
        # Generate deterministic score based on keyword matching
        job_keywords = (job_title + " " + company).lower()
        
        high_match_words = ["senior", "lead", "manager", "director", "head", "strategy", "marketing", "ai", "automation"]
        low_match_words = ["entry", "junior", "intern", "support", "admin", "data entry"]
        
        base_score = 65
        for word in high_match_words:
            if word in job_keywords:
                base_score += 5
        for word in low_match_words:
            if word in job_keywords:
                base_score -= 5
        
        base_score = max(0, min(100, base_score))
        
        return {
            "overall_score": base_score,
            "category_scores": {
                "skills_match": base_score - 5,
                "experience_match": base_score - 3,
                "industry_fit": base_score - 2,
                "location_fit": 80,  # Assume Dubai as default
                "seniority_match": base_score
            },
            "strengths": ["Relevant title", "Aligned company sector"],
            "gaps": ["Limited information"],
            "recommendation": "apply" if base_score >= 70 else "consider" if base_score >= 50 else "skip",
            "summary": f"Local fallback evaluation based on title and company. Estimated {base_score}% match. For full AI evaluation, restart LiteLLM proxy."
        }
    
    async def score_job(self, job_description: str, job_title: str = "", company: str = "", preferred_agent: str = "auto") -> Dict:
        """
        Score a job using available agents in priority order.
        
        Args:
            job_description: Full job description text
            job_title: Job title
            company: Company name
            preferred_agent: "gemini", "ollama", "kimi", "auto", or "fallback"
        
        Returns:
            Score dictionary with overall_score, category_scores, etc.
        """
        
        # Try agents in order based on preference
        if preferred_agent == "auto":
            # Auto-detect priority based on what's available
            agents_to_try = [
                ("gemini", self.score_with_gemini),
                ("kimi", self.score_with_direct_kimi),
                ("ollama", self.score_with_ollama),
            ]
        elif preferred_agent == "gemini":
            agents_to_try = [("gemini", self.score_with_gemini)]
        elif preferred_agent == "kimi":
            agents_to_try = [("kimi", self.score_with_direct_kimi)]
        elif preferred_agent == "ollama":
            agents_to_try = [("ollama", self.score_with_ollama)]
        else:
            agents_to_try = []
        
        # Try each agent
        for agent_name, agent_func in agents_to_try:
            try:
                result = await agent_func(job_description, job_title, company)
                if result:
                    result["source_agent"] = agent_name
                    return result
            except Exception as e:
                print(f"Agent {agent_name} failed: {e}")
                continue
        
        # Fallback
        result = self.fallback_score(job_title, company)
        result["source_agent"] = "fallback"
        return result


# Singleton instance
_scoring_client = None

def get_scoring_client() -> DirectScoringClient:
    """Get or create the direct scoring client"""
    global _scoring_client
    if _scoring_client is None:
        _scoring_client = DirectScoringClient()
    return _scoring_client
