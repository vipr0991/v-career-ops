"""
QUICK FIX: Replace the call_llm_with_fallback function in career_ops_api.py
This version prioritizes Kimi (which is always configured) and includes fallback scoring
"""

# Add this import at the top if not already there:
# import json

async def call_llm_with_fallback(task_type: str, messages: list, temperature: float = 0.3, timeout: float = 120.0) -> str:
    """Try Kimi first (always configured), then fallback to keyword-based scoring"""
    
    # Priority 1: Try Kimi (most reliable, always configured)
    try:
        print(f"[Scoring] Trying Kimi API...")
        kimi_key = os.getenv("KIMI_API_KEY")
        if kimi_key and not kimi_key.startswith("[REDACTED"):
            response = await acompletion(
                model="openai/moonshot-v1-128k",
                messages=messages,
                temperature=temperature,
                api_key=kimi_key,
                api_base="https://api.moonshot.ai/v1",
                timeout=timeout
            )
            print(f"[Scoring] ✓ Kimi succeeded")
            return response.choices[0].message.content
    except Exception as e:
        print(f"[Scoring] Kimi failed: {type(e).__name__}")
    
    # Priority 2: Try LiteLLM if available
    try:
        print(f"[Scoring] Trying LiteLLM...")
        model_name = await resolve_model(task_type)
        url = "http://localhost:4000/v1/chat/completions"
        data = {"model": model_name, "messages": messages, "temperature": temperature}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=data, headers={"Authorization": "Bearer local-secret"})
            response.raise_for_status()
            print(f"[Scoring] ✓ LiteLLM succeeded")
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[Scoring] LiteLLM failed: {type(e).__name__}")
    
    # Priority 3: Fallback to keyword-based scoring (never fails)
    print(f"[Scoring] Using fallback keyword-based scoring")
    user_msg = messages[-1].get("content", "") if messages else ""
    lower_msg = user_msg.lower()
    
    # Simple keyword scoring
    score = 65
    positive_keywords = ["marketing", "ai", "automation", "senior", "manager", "lead", "strategy"]
    negative_keywords = ["entry", "junior", "intern", "support"]
    location_keywords = ["dubai", "uae", "gcc"]
    
    for kw in positive_keywords:
        if kw in lower_msg:
            score += 5
    for kw in negative_keywords:
        if kw in lower_msg:
            score -= 10
    for kw in location_keywords:
        if kw in lower_msg:
            score += 10
    
    score = max(0, min(100, score))
    
    return json.dumps({
        "overall_score": score,
        "category_scores": {
            "skills_match": max(0, score - 5),
            "experience_match": max(0, score - 3),
            "industry_fit": max(0, score - 2),
            "location_fit": 80,
            "seniority_match": score
        },
        "strengths": ["Experience match", "Location fit"],
        "gaps": ["Limited AI analysis"],
        "recommendation": "apply" if score >= 70 else "consider",
        "summary": f"Fallback scoring: {score}% based on keyword analysis. Full AI scoring unavailable."
    })
