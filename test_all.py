import requests, json, sys

BASE = "http://localhost:5000"
ok = 0; fail = 0

def check(label, res, expect=200):
    global ok, fail
    if res.status_code == expect:
        print(f"  PASS  {label} ({res.status_code})")
        ok += 1
    else:
        print(f"  FAIL  {label} -- got {res.status_code}: {res.text[:80]}")
        fail += 1

print("\n=== Career-Ops API Tests ===\n")

print("[1] Health")
check("GET /", requests.get(f"{BASE}/"))
check("GET /api/stats", requests.get(f"{BASE}/api/stats"))

print("\n[2] Jobs")
check("GET /api/jobs", requests.get(f"{BASE}/api/jobs"))

print("\n[3] Score")
r = requests.post(f"{BASE}/api/score", json={
    "job_description": "Senior Marketing Manager for AI company in Dubai, leading digital strategy",
    "job_title": "Senior Marketing Manager",
    "company": "TestCorp",
    "location": "Dubai"
})
check("POST /api/score", r)
if r.ok:
    d = r.json()
    print(f"       score={d['score']['overall_score']}%  rec={d['score']['recommendation']}")
    job_id = d.get("report_file","").replace(".md","")
    print(f"       saved as: {d.get('report_file')}")

print("\n[4] Optimize")
check("POST /api/optimize", requests.post(f"{BASE}/api/optimize", json={
    "job_id": "test-001", "role": "Marketing Manager", "company": "TestCorp", "location": "Dubai"
}))

print("\n[5] LaTeX")
check("POST /api/save-latex", requests.post(f"{BASE}/api/save-latex", json={
    "latex": "\\documentclass{article}\\begin{document}Test\\end{document}",
    "role": "Marketing Manager", "company": "TestCorp"
}))
check("GET /api/latex-resumes", requests.get(f"{BASE}/api/latex-resumes"))

print("\n[6] Pipeline PATCH")
check("PATCH /api/pipeline/test-id", requests.patch(
    f"{BASE}/api/pipeline/test-id",
    json={"status": "applied"}
))

print("\n[7] Delete (expect 404)")
check("DELETE /api/jobs nonexistent", requests.delete(f"{BASE}/api/jobs?job_id=nonexistent"), 404)

print(f"\n=== {ok} passed, {fail} failed ===\n")
sys.exit(0 if fail == 0 else 1)
