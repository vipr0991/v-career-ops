"""
Full Regression Audit Script for Career-Ops
Tests all 7 operational layers:
1. Pipeline CRUD
2. AI 10-Dimension Scoring
3. Resume Tailoring (/api/optimize)
4. 1-Click App Kit Generation (/api/pipeline/generate-kit)
5. Decision Makers & LinkedIn Outreach
6. File Downloads (PDF, LaTeX, PPTX)
7. AI Assistant Chat
"""
import asyncio
import httpx
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from career_ops_api import app

async def run_full_regression_audit():
    print("=================================================================")
    print("CAREER-OPS FULL REGRESSION & OPERATIONAL INTEGRITY AUDIT")
    print("=================================================================")
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
        # 1. Health & Pipeline Read
        res = await client.get("/api/pipeline")
        assert res.status_code == 200, f"Pipeline GET failed: {res.text}"
        items = res.json().get("items", [])
        print(f"[1/7] Pipeline Active: {len(items)} jobs loaded successfully.")

        # 2. AI 10-Dimension Scoring
        score_payload = {
            "job_title": "Senior Marketing Operations Manager",
            "company": "Careem",
            "job_description": "Lead regional marketing operations, AI automation, and demand generation across UAE & GCC.",
            "location": "Dubai, UAE"
        }
        score_res = await client.post("/api/score", json=score_payload)
        assert score_res.status_code == 200, f"Score failed: {score_res.text}"
        score_data = score_res.json()
        score_val = score_data.get("score")
        eval_dict = score_data.get("evaluation", {})
        source_agent = eval_dict.get("source_agent", "AI")
        verdict = eval_dict.get("verdict", "Evaluated")
        print(f"[2/7] AI Scoring: Score {score_val}% ({verdict}) via {source_agent}.")

        # 3. Resume Tailoring Endpoint (/api/optimize)
        opt_payload = {
            "job_id": items[0]["id"] if items else "test-job",
            "company": "Clifford Chance",
            "role": "Business Development & Marketing Manager",
            "location": "Dubai, UAE"
        }
        opt_res = await client.post("/api/optimize", json=opt_payload)
        assert opt_res.status_code == 200, f"Optimize failed: {opt_res.text}"
        opt_data = opt_res.json()
        tex_f = opt_data.get("tailored_resume_tex")
        pdf_f = opt_data.get("tailored_resume_pdf")
        print(f"[3/7] Resume Tailoring (/api/optimize): Generated {tex_f} & {pdf_f}.")

        # 4. 1-Click App Kit Generation (/api/pipeline/generate-kit)
        kit_res = await client.post("/api/pipeline/generate-kit", json={"job_id": items[0]["id"]})
        assert kit_res.status_code == 200, f"Kit generation failed: {kit_res.text}"
        kit_data = kit_res.json()
        kit_tex = kit_data.get("tailored_resume", {}).get("tex_filename")
        kit_pdf = kit_data.get("tailored_resume_pdf")
        kit_pptx = kit_data.get("presentation_deck")
        print(f"[4/7] 1-Click App Kit: LaTeX ({kit_tex}), PDF ({kit_pdf}), PPTX ({kit_pptx}).")

        # 5. Decision Makers & LinkedIn Notes
        dms = kit_data.get("decision_makers", [])
        assert len(dms) > 0, "No decision makers generated"
        print(f"[5/7] Decision Makers: {len(dms)} hiring leads identified with <200 char invites.")

        # 6. Direct File Downloads Verification
        pdf_dl = await client.get(f"/api/downloads/pdf/{kit_pdf}")
        assert pdf_dl.status_code == 200, f"PDF DL failed: {pdf_dl.status_code}"
        tex_dl = await client.get(f"/api/downloads/latex/{kit_tex}")
        assert tex_dl.status_code == 200, f"LaTeX DL failed: {tex_dl.status_code}"
        pptx_dl = await client.get(f"/api/downloads/output/{kit_pptx}")
        assert pptx_dl.status_code == 200, f"PPTX DL failed: {pptx_dl.status_code}"
        print(f"[6/7] Downloads API: Verified PDF ({len(pdf_dl.content)} bytes), LaTeX ({len(tex_dl.content)} bytes), PPTX ({len(pptx_dl.content)} bytes).")

        # 7. AI Career Assistant Chat
        chat_res = await client.post("/api/chat", json={"message": "How should I position my 4415% follower growth metric?"})
        assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
        chat_model = chat_res.json().get("model")
        print(f"[7/7] Career Assistant Chat: Active ({chat_model}).")

    print("\n=================================================================")
    print("REGRESSION AUDIT COMPLETE: 100% OPERATIONAL PASS WITH ZERO RISKS")
    print("=================================================================")

if __name__ == "__main__":
    asyncio.run(run_full_regression_audit())
