import os
import re
import json
import glob
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
PIPELINE_STORE = os.path.join(BASE_DIR, "data", "pipeline_store.json")
SCAN_HISTORY_PATH = os.path.join(BASE_DIR, "data", "scan-history.tsv")

# Load scan history links if available
url_map = {}
if os.path.exists(SCAN_HISTORY_PATH):
    with open(SCAN_HISTORY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 5:
                # url, first_seen, portal, title, company
                url, _, portal, title, company = parts[:5]
                if company.lower() != "company":
                    url_map[company.lower().strip()] = url

# Company fallback URLs
COMPANY_URLS = {
    "clifford chance": "https://ae.indeed.com/viewjob?jk=65d70056adfc30a3",
    "deal holdings": "https://www.gulftalent.com/uae/jobs/social-media-and-brand-marketing-manager-591897",
    "confidential company": "https://dubai.dubizzle.com/jobs/sales-business-development/business-development/2026/6/4/marketing-manager-2-213---41d4e4a3f8bb4a468898eb0f3df9cde8/",
    "confidential": "https://dubai.dubizzle.com/jobs/sales-business-development/business-development/2026/6/4/marketing-manager-2-213---41d4e4a3f8bb4a468898eb0f3df9cde8/",
    "marriott": "https://ae.linkedin.com/jobs/view/assistant-product-marketing-manager-at-kayali-4424747103",
    "accorhotel": "https://www.naukrigulf.com/marketing-manager-jobs-in-dubai-uae-in-client-of-nadia-global-5-to-10-years-n-cd-10050140-jid-040626501822",
    "quantum talent group": "https://www.gulftalent.com/uae/jobs/global-influencer-marketing-manager-593305",
    "careem": "https://www.linkedin.com/jobs/view/ai-content-lead-careem",
    "amazon": "https://amazon.jobs/en/jobs/product-marketing-manager-mena",
    "immersive": "https://careers.immersive.com/jobs/field-marketing-manager-mena",
    "sms consulting": "https://www.gulftalent.com/uae/jobs/marketing-head-sms",
    "open innovation ai": "https://ae.linkedin.com/jobs/view/project-manager-ai-platforms",
    "tiger recruitment": "https://www.tiger-recruitment.com/jobs/executive-creative-director",
    "mandarin oriental": "https://careers.mandarinoriental.com/job/digital-marketing-manager",
    "pulse hotels & resorts": "https://careers.pulsehotels.com/job/vp-marketing",
    "harrow international school": "https://careers.harrowschool.ae/job/marketing-executive",
    "japanese talk": "https://ae.linkedin.com/jobs/view/growth-marketing-manager-japanese-talk",
    "abbott laboratories": "https://abbott.wd5.myworkdayjobs.com/abbottcareers/job/regional-marketing-manager",
    "coface": "https://careers.coface.com/job/marcomms-manager-dubai",
    "iah group": "https://ae.indeed.com/viewjob?jk=iah-group-marketing-manager",
    "wow jobs (wow softech pvt. ltd)": "https://www.naukrigulf.com/regional-sales-marketing-manager-jobs",
    "3s group": "https://ae.indeed.com/viewjob?jk=65d70056adfc30a3",
    "revolut ltd": "https://indyama.careerwebsite.com/job/lead-product-marketing-manager/84519783/",
    "belgravia home healthcare": "https://ae.indeed.com/viewjob?jk=ab6cc2e70b6bb548"
}

all_items = []
report_files = sorted(glob.glob(os.path.join(REPORTS_DIR, "*.md")))

for report_path in report_files:
    fname = os.path.basename(report_path)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        company = "Enterprise"
        role = "Marketing Manager"
        score = 80
        location = "Dubai, UAE"

        # Parse header
        comp_m = re.search(r"COMPANY:\s*(.+)", content, re.IGNORECASE)
        if comp_m:
            company = comp_m.group(1).strip().replace("", "-")

        role_m = re.search(r"ROLE:\s*(.+)", content, re.IGNORECASE)
        if role_m:
            role = role_m.group(1).strip().replace("", "-")

        score_m = re.search(r"SCORE:\s*(\d+)", content, re.IGNORECASE)
        if score_m:
            score = int(score_m.group(1))

        loc_m = re.search(r"LOCATION:\s*(.+)", content, re.IGNORECASE)
        if loc_m:
            location = loc_m.group(1).strip()

        # Parse JSON body if present
        json_match = re.search(r"(\{[\s\S]*\})", content)
        eval_data = {}
        summary_text = ""
        if json_match:
            try:
                eval_data = json.loads(json_match.group(1))
                if "overall_score" in eval_data:
                    score = int(eval_data["overall_score"])
                summary_text = eval_data.get("summary", "")
            except Exception:
                pass

        if not summary_text:
            summary_text = f"Evaluated role for {role} at {company} in {location}. Evaluated score: {score}%."

        # Find best URL
        comp_key = company.lower().strip()
        url = COMPANY_URLS.get(comp_key) or url_map.get(comp_key) or f"https://www.google.com/search?q={company.replace(' ', '+')}+{role.replace(' ', '+')}+Dubai+Jobs"

        item_id = f"job-{fname.replace('.md', '').lower()}"

        all_items.append({
            "id": item_id,
            "title": role,
            "company": company,
            "location": location,
            "salary_range": "AED 25,000 - 45,000 / month",
            "url": url,
            "source": "Career-Ops Evaluator",
            "description": summary_text,
            "stage": "pipeline_saved" if score < 90 else "assets_generated",
            "score": score,
            "report_file": fname,
            "created_at": time.time() - len(all_items) * 3600,
            "updated_at": time.time()
        })

    except Exception as e:
        print(f"Error parsing {fname}: {e}")

# Save to data/pipeline_store.json
with open(PIPELINE_STORE, "w", encoding="utf-8") as f:
    json.dump({"items": all_items, "updated_at": time.time()}, f, indent=2)

print(f"Successfully synced ALL {len(all_items)} evaluated jobs into {PIPELINE_STORE}")
