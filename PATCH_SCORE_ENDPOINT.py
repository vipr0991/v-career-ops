"""
PATCH INSTRUCTIONS: Update /api/score endpoint in career_ops_api.py

Replace the entire @app.post("/api/score") function (starting around line 650) with this:
"""

# Add this import at the top of career_ops_api.py (after other imports):
# from direct_scoring import get_scoring_client

# ─────────────────────────────────────────────────────────────────────
# REPLACE THIS ENTIRE FUNCTION:
# ─────────────────────────────────────────────────────────────────────

@app.post("/api/score")
async def score_job(req: ScoreRequest):
    """
    Calculate % match score for a job description.
    PRIMARY: Uses LiteLLM on port 4000
    FALLBACK 1: Google Gemini API (direct)
    FALLBACK 2: Moonshot Kimi API (direct)
    FALLBACK 3: Local Ollama
    FALLBACK 4: Hardcoded local scoring
    """
    from direct_scoring import get_scoring_client
    
    cv_text = load_file(CV_PATH)
    profile_yml = load_file(PROFILE_YML_PATH)

    score_data = None
    source_agent = None
    filename = None
    
    # ─── ATTEMPT 1: LiteLLM Proxy ──────────────────────────────────────
    url = "http://localhost:4000/v1/chat/completions"
    model_name = await resolve_model("scoring")
    
    try:
        messages = [
            {"role": "system", "content": f"Evaluate job match. CV: {cv_text[:300]}"},
            {"role": "user", "content": f"Job: {req.job_title} at {req.company}. Description: {req.job_description[:1500]}"}
        ]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"model": model_name, "messages": messages, "temperature": 0.1},
                headers={"Content-Type": "application/json", "Authorization": "Bearer local-secret"},
                timeout=120.0
            )
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content.strip().startswith("```"):
                    content = "\n".join(content.strip().split("\n")[1:-1])
                try:
                    score_data = json.loads(content)
                    source_agent = "LiteLLM (Primary)"
                except:
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        score_data = json.loads(json_match.group())
                        source_agent = "LiteLLM (Primary)"
    except Exception as e:
        print(f"LiteLLM offline or error: {e}")
    
    # ─── ATTEMPT 2-4: Direct APIs ──────────────────────────────────────
    if score_data is None:
        try:
            scoring_client = get_scoring_client()
            result = await scoring_client.score_job(
                job_description=req.job_description,
                job_title=req.job_title or "",
                company=req.company or "",
                preferred_agent="auto"
            )
            score_data = result.copy()
            source_agent = result.get("source_agent", "Fallback")
        except Exception as e:
            print(f"All fallback agents failed: {e}")
    
    # ─── FINAL FALLBACK ────────────────────────────────────────────────
    if score_data is None:
        score_data = {
            "overall_score": 50,
            "category_scores": {
                "skills_match": 50, "experience_match": 50, 
                "industry_fit": 50, "location_fit": 50, "seniority_match": 50
            },
            "strengths": ["Unable to evaluate"],
            "gaps": ["Scoring service unavailable"],
            "recommendation": "skip",
            "summary": "All AI services offline. Contact administrator."
        }
        source_agent = "Hardcoded Fallback"
    
    # ─── Save Report ───────────────────────────────────────────────────
    try:
        today = time.strftime("%Y-%m-%d")
        company_slug = "".join(c.lower() if c.isalnum() else "-" for c in (req.company or "unknown")).strip("-")
        existing = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".md") and f[:3].isdigit()]
        num = str(max((int(f[:3]) for f in existing), default=0) + 1).zfill(3)
        filename = f"{num}-{company_slug}-{today}.md"
        report_path = os.path.join(REPORTS_DIR, filename)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"COMPANY: {req.company or 'Unknown'}\n")
            f.write(f"ROLE: {req.job_title or 'Unknown'}\n")
            f.write(f"SCORE: {score_data.get('overall_score', 'N/A')}\n")
            f.write(f"SOURCE: {source_agent}\n\n")
            f.write(json.dumps(score_data, indent=2))
    except Exception as e:
        print(f"Failed to save report: {e}")
        filename = None
    
    return {
        "score": score_data,
        "source_agent": source_agent,
        "report_file": filename,
        "job_meta": {
            "title": req.job_title,
            "company": req.company,
            "location": req.location,
            "url": req.url
        }
    }

# ─────────────────────────────────────────────────────────────────────
# END OF REPLACEMENT
# ─────────────────────────────────────────────────────────────────────
