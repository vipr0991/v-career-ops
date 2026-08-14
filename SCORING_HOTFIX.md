# SCORING HOTFIX
# Add this code to career_ops_api.py right after imports

# Add Kimi-first fallback for scoring
async def score_job_safe(job_description: str, job_title: str, company: str) -> dict:
    """Safe scoring with Kimi-first priority and fallback"""
    
    # Try Kimi first (always works if key is valid)
    try:
        print("[Score] Trying Kimi API...")
        kimi_key = os.getenv("KIMI_API_KEY")
        if kimi_key and not "[REDACTED" in kimi_key:
            messages = [
                {"role": "user", "content": f"""Score this job match: {job_title} at {company}
Description: {job_description[:1500]}

Return ONLY JSON:
{{"overall_score": <0-100>, "category_scores": {{"skills_match": <0-100>, "experience_match": <0-100>, "industry_fit": <0-100>, "location_fit": <0-100>, "seniority_match": <0-100>}}, "strengths": [], "gaps": [], "recommendation": "apply", "summary": ""}}
"""}
            ]
            response = await acompletion(
                model="openai/moonshot-v1-128k",
                messages=messages,
                temperature=0.1,
                api_key=kimi_key,
                api_base="https://api.moonshot.ai/v1",
                timeout=120
            )
            result = response.choices[0].message.content
            print("[Score] ✓ Kimi succeeded")
            
            # Clean JSON
            if "```" in result:
                result = result.split("```")[1].replace("json", "").strip()
            
            return json.loads(result)
    except Exception as e:
        print(f"[Score] Kimi failed: {e}")
    
    # Fallback: Keyword-based scoring (never fails)
    print("[Score] Using fallback scoring")
    lower_desc = f"{job_title} {company} {job_description}".lower()
    
    score = 65
    # Boost for good matches
    for keyword in ["marketing", "ai", "automation", "strategy", "senior", "lead", "manager"]:
        if keyword in lower_desc:
            score += 5
    # Reduce for entry-level
    for keyword in ["entry", "junior", "intern"]:
        if keyword in lower_desc:
            score -= 10
    # Location bonus
    for keyword in ["dubai", "uae", "gcc"]:
        if keyword in lower_desc:
            score += 10
    
    score = max(0, min(100, score))
    
    return {
        "overall_score": score,
        "category_scores": {
            "skills_match": max(0, score - 5),
            "experience_match": max(0, score - 3),
            "industry_fit": max(0, score - 2),
            "location_fit": 80,
            "seniority_match": score
        },
        "strengths": ["Experience alignment", "Location match"],
        "gaps": ["Limited detailed analysis"],
        "recommendation": "apply" if score >= 70 else "consider",
        "summary": f"Fallback scoring: {score}% match. For AI scoring, update GEMINI_API_KEY in .env."
    }


# Then update the @app.post("/api/score") endpoint to use this:
# Replace the existing score_job function with:

@app.post("/api/score")
async def score_job(req: ScoreRequest):
    """Score a job using Kimi with fallback"""
    try:
        score_data = await score_job_safe(req.job_description, req.job_title or "", req.company or "")
        
        # Save report
        today = time.strftime("%Y-%m-%d")
        company_slug = "".join(c.lower() if c.isalnum() else "-" for c in (req.company or "unknown")).strip("-")
        existing = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".md") and f[:3].isdigit()]
        num = str(max((int(f[:3]) for f in existing), default=0) + 1).zfill(3)
        filename = f"{num}-{company_slug}-{today}.md"
        report_path = os.path.join(REPORTS_DIR, filename)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"COMPANY: {req.company or 'Unknown'}\n")
            f.write(f"ROLE: {req.job_title or 'Unknown'}\n")
            f.write(f"SCORE: {score_data.get('overall_score', 'N/A')}\n\n")
            f.write(json.dumps(score_data, indent=2))

        return {
            "score": score_data,
            "report_file": filename,
            "job_meta": {
                "title": req.job_title,
                "company": req.company,
                "location": req.location,
                "url": req.url
            }
        }
    except Exception as e:
        print(f"[Score] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
