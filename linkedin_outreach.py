"""
LinkedIn Outreach Generator
Generates personalized, high-converting connection request notes (strictly <= 200 characters).
Multi-model support: Moonshot Kimi AI + Google Gemini AI fallback.
"""
import os
import json
import httpx
from typing import Optional

class LinkedInOutreachEngine:
    def __init__(self):
        self.kimi_key = (
            os.getenv("KIMI_API_KEY") 
            or os.getenv("MOONSHOT_API_KEY") 
            or "sk-kjfAlmZbu0ZEw1X386RQ94piXfk9Cs18l3Td9icHbxPAPXoW"
        )
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.max_chars = 200

    async def generate_connection_note(
        self,
        recipient_name: str,
        company_name: str,
        job_title: str
    ) -> str:
        """
        Generates a 200-character personalized LinkedIn invite.
        """
        first_name = recipient_name.split()[0] if recipient_name else "there"
        safe_company = company_name if company_name and company_name.lower() not in ["unknown", "confidential"] else "your team"

        prompt = f"""Write a compelling, professional LinkedIn connection request note for:
- Recipient First Name: {first_name}
- Target Company: {safe_company}
- Target Role: {job_title}
- Sender: Vinay Prakash (Strategic Marketing & AI Leader based in Dubai, UAE)

CRITICAL CONSTRAINT: The message MUST be strictly 200 CHARACTERS OR FEWER. No exceptions.
Return ONLY the exact invitation text without quotes."""

        # 1. Try Moonshot Kimi AI
        if self.kimi_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.moonshot.ai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.kimi_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "moonshot-v1-8k",
                            "messages": [
                                {"role": "system", "content": "You write concise LinkedIn connection notes under 200 characters. Return only the note."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.3,
                            "max_tokens": 100
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        note = data["choices"][0]["message"]["content"].strip().strip('"').strip("'")
                        if 10 < len(note) <= self.max_chars:
                            return note
                        elif len(note) > self.max_chars:
                            return note[:197] + "..."
            except Exception as e:
                print(f"[Outreach] Moonshot Kimi error: {e}")

        # 2. Try Gemini Fallback
        if self.gemini_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent",
                        headers={"Content-Type": "application/json"},
                        params={"key": self.gemini_key},
                        json={
                            "contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {"temperature": 0.3}
                        }
                    )

                    if response.status_code == 200:
                        data = response.json()
                        note = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        note = note.strip('"').strip("'")
                        if 10 < len(note) <= self.max_chars:
                            return note
                        elif len(note) > self.max_chars:
                            return note[:197] + "..."
            except Exception as e:
                print(f"[Outreach] Gemini error: {e}")

        return self._fallback_note(first_name, safe_company, job_title)

    def _fallback_note(self, first_name: str, company: str, job_title: str) -> str:
        note = f"Hi {first_name}, following {company}'s GCC growth with interest. As a Dubai-based AI & MarTech Lead, I'd value connecting regarding {job_title} opportunities."
        return note if len(note) <= self.max_chars else note[:197] + "..."

linkedin_outreach = LinkedInOutreachEngine()
