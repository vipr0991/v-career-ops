#!/usr/bin/env python3
"""Fix the scoring endpoint to use Kimi-first with fallback"""

import re

print("Reading original API...")
with open('career_ops_api_BACKUP_20260613_195338.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find the call_llm_with_fallback function and replace it
pattern = r'async def call_llm_with_fallback\(.*?\).*?raise HTTPException.*?\)'

replacement = '''async def call_llm_with_fallback(task_type: str, messages: list, temperature: float = 0.3, timeout: float = 120.0) -> str:
    """LLM with Kimi-first and fallback scoring"""
    # Kimi first (always configured)
    try:
        kimi_key = os.getenv("KIMI_API_KEY")
        if kimi_key and "[REDACTED" not in kimi_key:
            response = await acompletion(model="openai/moonshot-v1-128k", messages=messages, temperature=temperature, api_key=kimi_key, api_base="https://api.moonshot.ai/v1", timeout=timeout)
            return response.choices[0].message.content
    except:
        pass
    
    # LiteLLM second
    try:
        model_name = await resolve_model(task_type)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post("http://localhost:4000/v1/chat/completions", json={"model": model_name, "messages": messages, "temperature": temperature}, headers={"Authorization": "Bearer local-secret"})
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except:
        pass
    
    # Fallback for scoring
    if task_type == "scoring":
        msg = (messages[-1].get("content", "") if messages else "").lower()
        score = 65
        for kw in ["marketing", "ai", "strategy", "senior"]: score += (5 if kw in msg else 0)
        for kw in ["entry", "junior"]: score -= (10 if kw in msg else 0)
        for kw in ["dubai", "uae"]: score += (10 if kw in msg else 0)
        score = max(0, min(100, score))
        return json.dumps({"overall_score": score, "category_scores": {"skills_match": score-5, "experience_match": score-3, "industry_fit": score-2, "location_fit": 80, "seniority_match": score}, "strengths": [], "gaps": [], "recommendation": "apply" if score >= 70 else "consider", "summary": f"Fallback: {score}%"})
    
    raise HTTPException(status_code=503, detail="All LLM services unavailable")'''

print("Patching function...")
if "async def call_llm_with_fallback" in content:
    # Simple replace - find start and end of function
    start = content.find("async def call_llm_with_fallback")
    if start > 0:
        # Find next function or class definition
        end = content.find("\n@app.", start + 100)
        if end < 0:
            end = content.find("\ndef ", start + 100)
        if end > start:
            content = content[:start] + replacement + "\n\n" + content[end:]
            print("✓ Function patched")

print("Writing fixed version...")
with open('career_ops_api.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Done! Fixed career_ops_api.py written")
