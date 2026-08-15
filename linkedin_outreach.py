"""
LinkedIn MCP Outreach Helper
Generates 200-character connection notes and manages LinkedIn outreach lifecycle.
"""
import os
import json
import httpx
import re
from typing import Dict, Any, Optional

class LinkedInOutreachHelper:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.max_chars = 200

    async def generate_invite_note(
        self,
        recipient_name: str,
        company_name: str,
        job_title: str,
        role_type: str = "Hiring Manager"
    ) -> str:
        """
        Generates a personalized LinkedIn connection invitation strictly under 200 characters.
        """
        first_name = recipient_name.split()[0] if recipient_name else "there"
        safe_company = company_name or "your team"

        if not self.gemini_key:
            return self._fallback_note(first_name, safe_company, job_title)

        prompt = f"""Write a compelling, professional LinkedIn connection request note for:
- Recipient First Name: {first_name}
- Target Company: {safe_company}
- Target Role: {job_title}
- Sender: Vinay Prakash (AI & MarTech Leader based in Dubai, UAE)

CRITICAL CONSTRAINT: The message MUST be strictly 200 CHARACTERS OR FEWER. No exceptions.
Return ONLY the exact invitation text without quotes."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
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
                    if len(note) <= self.max_chars and len(note) > 10:
                        return note
                    elif len(note) > self.max_chars:
                        return note[:197] + "..."
        except Exception as e:
            print(f"[LinkedIn] Invite note generation error: {e}")

        return self._fallback_note(first_name, safe_company, job_title)

    def _fallback_note(self, first_name: str, company: str, job_title: str) -> str:
        templates = [
            f"Hi {first_name}, loved {company}'s growth! As an AI & MarTech Lead in Dubai, I'd value connecting to share pipeline insights.",
            f"Hi {first_name}, following {company}'s expansion with great interest. I lead AI & marketing workflows in the UAE—let's connect!",
            f"Hi {first_name}, reaching out regarding {job_title} initiatives at {company}. Excited about your team's work—would love to connect."
        ]
        for t in templates:
            if len(t) <= self.max_chars:
                return t
        return f"Hi {first_name}, following {company}'s work with great interest. Let's connect!"

linkedin_outreach = LinkedInOutreachHelper()
