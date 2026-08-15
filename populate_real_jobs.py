import json
import time
import os

PIPELINE_STORE_PATH = os.path.join(os.path.dirname(__file__), "data", "pipeline_store.json")

jobs = [
    {
        "id": "job-eval-003-confidential",
        "title": "Digital Marketing Executive/Manager",
        "company": "Confidential Company",
        "location": "Dubai, UAE",
        "salary_range": "AED 25,000 - 35,000 / month",
        "url": "https://dubai.dubizzle.com/jobs/sales-business-development/business-development/2026/6/4/marketing-manager-2-213---41d4e4a3f8bb4a468898eb0f3df9cde8/?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic",
        "source": "Dubizzle / Google Jobs",
        "description": "Lead multi-channel digital performance marketing across Google Ads, Meta, SEO/SEM, and marketing automation. Drive customer acquisition, lead funnels, and revenue attribution across the UAE and GCC.",
        "stage": "pipeline_saved",
        "score": 95,
        "report_file": "003-confidential-company-2026-08-15.md",
        "created_at": time.time() - 3600 * 2,
        "updated_at": time.time()
    },
    {
        "id": "job-eval-001-clifford-chance",
        "title": "Business Development & Marketing Manager - 12-month Fixed-Term Contract | Dubai, UAE",
        "company": "Clifford Chance",
        "location": "Dubai, UAE",
        "salary_range": "AED 35,000 - 45,000 / month",
        "url": "https://ae.indeed.com/viewjob?jk=65d70056adfc30a3&utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic",
        "source": "Indeed / LinkedIn",
        "description": "Drive high-stakes business development pursuit, RFP proposals, practice group marketing, and client relationship management across Middle East legal operations for Clifford Chance in Dubai.",
        "stage": "pipeline_saved",
        "score": 90,
        "report_file": "001-clifford-chance-2026-08-14.md",
        "created_at": time.time() - 3600 * 24,
        "updated_at": time.time()
    },
    {
        "id": "job-eval-002-deal-holdings",
        "title": "Head of Marketing & Communications (F&B / Hospitality)",
        "company": "DEAL Holdings",
        "location": "Dubai, UAE",
        "salary_range": "AED 30,000 - 42,000 / month",
        "url": "https://www.gulftalent.com/uae/jobs/social-media-and-brand-marketing-manager-591897?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic",
        "source": "GulfTalent",
        "description": "Oversee 360-degree marketing, brand positioning, influencer networks, loyalty CRM, and digital campaign execution for multi-brand hospitality and premium dining venues in Dubai.",
        "stage": "pipeline_saved",
        "score": 85,
        "report_file": "002-deal-holdings-2026-08-14.md",
        "created_at": time.time() - 3600 * 20,
        "updated_at": time.time()
    },
    {
        "id": "job-eval-004-marriott",
        "title": "Senior Digital Marketing Executive",
        "company": "Marriott",
        "location": "Dubai, UAE",
        "salary_range": "AED 18,000 - 24,000 / month",
        "url": "https://ae.linkedin.com/jobs/view/assistant-product-marketing-manager-at-kayali-4424747103?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic",
        "source": "LinkedIn / Marriott Careers",
        "description": "Execute property-level digital advertising, search engine marketing, social media campaigns, and Marriott Bonvoy loyalty program promotions across luxury hotel clusters in Dubai.",
        "stage": "pipeline_saved",
        "score": 75,
        "report_file": "004-marriott-2026-08-15.md",
        "created_at": time.time() - 3600 * 5,
        "updated_at": time.time()
    },
    {
        "id": "job-eval-005-accorhotel",
        "title": "Digital and Communications Marketing Manager",
        "company": "AccorHotel",
        "location": "Dubai, UAE",
        "salary_range": "AED 22,000 - 28,000 / month",
        "url": "https://www.naukrigulf.com/marketing-manager-jobs-in-dubai-uae-in-client-of-nadia-global-5-to-10-years-n-cd-10050140-jid-040626501822?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic",
        "source": "NaukriGulf / Accor Careers",
        "description": "Manage integrated PR communications, digital media strategies, brand storytelling, and ALL loyalty engagement campaigns across UAE hospitality properties.",
        "stage": "pipeline_saved",
        "score": 75,
        "report_file": "005-accorhotel-2026-08-15.md",
        "created_at": time.time() - 3600 * 4,
        "updated_at": time.time()
    },
    {
        "id": "job-eval-006-quantum-talent-group",
        "title": "AVP – Marketing Business Partnerships, Credit Cards - 6 months",
        "company": "Quantum Talent Group",
        "location": "Dubai, UAE",
        "salary_range": "AED 35,000 - 45,000 / month",
        "url": "https://www.gulftalent.com/uae/jobs/global-influencer-marketing-manager-593305?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic",
        "source": "GulfTalent / Banking Direct",
        "description": "Lead strategic co-brand card alliances, merchant partnership acquisitions, and fintech portfolio marketing for a premier UAE banking institution.",
        "stage": "pipeline_saved",
        "score": 75,
        "report_file": "006-quantum-talent-group-2026-08-15.md",
        "created_at": time.time() - 3600 * 3,
        "updated_at": time.time()
    },
    {
        "id": "job-scan-001-revolut",
        "title": "Lead Product Marketing Manager",
        "company": "Revolut Ltd",
        "location": "Dubai, UAE",
        "salary_range": "AED 38,000 - 50,000 / month",
        "url": "https://indyama.careerwebsite.com/job/lead-product-marketing-manager/84519783/?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic",
        "source": "Google Jobs / Revolut",
        "description": "Lead regional GTM strategy, product marketing lifecycle, user onboarding funnels, and marketing automation for Revolut's Middle East fintech expansion.",
        "stage": "pipeline_saved",
        "score": 88,
        "report_file": "",
        "created_at": time.time() - 3600 * 48,
        "updated_at": time.time()
    },
    {
        "id": "job-scan-002-belgravia",
        "title": "Growth & Performance Marketing Manager",
        "company": "Belgravia Home Healthcare",
        "location": "Dubai, UAE",
        "salary_range": "AED 26,000 - 34,000 / month",
        "url": "https://ae.indeed.com/viewjob?jk=ab6cc2e70b6bb548&utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic",
        "source": "Indeed",
        "description": "Scale patient acquisition funnels, oversee Google Ads and Meta conversion campaigns, and implement automated marketing tracking across UAE healthcare operations.",
        "stage": "pipeline_saved",
        "score": 84,
        "report_file": "",
        "created_at": time.time() - 3600 * 40,
        "updated_at": time.time()
    }
]

with open(PIPELINE_STORE_PATH, "w", encoding="utf-8") as f:
    json.dump({"items": jobs, "updated_at": time.time()}, f, indent=2)

print(f"Successfully populated {len(jobs)} real evaluated jobs into {PIPELINE_STORE_PATH}")
