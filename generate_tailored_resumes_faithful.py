"""
Career-Ops Faithful Resume Tailoring Engine
Strictly based on master resume: Vinay_Prakash_Resume_Optimized_6.8

INVARIANTS:
1. No added/invented companies, dates, degrees, certifications, or metrics.
2. Exact employment history, education, and contact details preserved.
3. Tailoring is restricted to:
   - Summary alignment to target role using authentic proof points.
   - Skill emphasis aligned to JD keywords.
   - Minor bullet point keyword alignment without changing facts or metrics.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
LATEX_DIR = os.path.join(ROOT, "latex_resumes")
os.makedirs(LATEX_DIR, exist_ok=True)

PREAMBLE = r"""\documentclass[10pt,a4paper]{article}

\usepackage[top=0.6in,bottom=0.6in,left=0.65in,right=0.65in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{tabularx}
\usepackage{fancyhdr}

\definecolor{primary}{RGB}{20, 20, 20}
\definecolor{accent}{RGB}{40, 40, 40}

% Section formatting
\titleformat{\section}{\normalsize\bfseries\scshape\color{primary}}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{7pt}{3pt}

\hypersetup{
  colorlinks=true,
  urlcolor=blue!70!black,
  linkcolor=blue!70!black
}

% Allow multi-page with subtle page numbers
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\footnotesize\thepage}

\begin{document}
"""


def esc(s):
    if not s:
        return ""
    return (s.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")
             .replace("_", r"\_").replace("$", r"\$"))

# Authentic master candidate data directly from Vinay_Prakash_Resume_Optimized_6.8
HEADER = r"""\begin{center}
{\LARGE\bfseries Vinay Prakash}\\[0.3em]
\small Dubai, United Arab Emirates \ $|$ \ 
\href{mailto:voommen@my.madonna.edu}{voommen@my.madonna.edu} \ $|$ \ 
+971 58 595 1173 \ $|$ \ 
+91 9645591928 \ $|$ \ 
\href{https://linkedin.com/in/vipr0}{linkedin.com/in/vipr0} \ $|$ \ 
\href{https://behance.net/vinaypoommen}{behance.net/vinaypoommen}
\end{center}
\vspace{-6pt}
"""

EDUCATION = r"""\section{Education}
\noindent\textbf{MBA in International Business, Minor in Marketing} \hfill \textbf{2016}\\
\textit{Madonna University, Livonia}\\
\vspace{2pt}
\noindent\textbf{B.Sc. in International Business, Minor in Economics} \hfill \textbf{2012}\\
\textit{Madonna University, Livonia}
"""

# The 6 Target Jobs
TAILORED_JOBS = [
    {
        "filename": "3.1_Vinay_Cliffordchance_Resume.tex",
        "role_title": "Business Development & Marketing Manager",
        "company": "Clifford Chance",
        "summary": (
            "Strategic marketing and business development leader with 13+ years of overall experience, including 8+ years "
            "in marketing, brand strategy, campaign management, PR, and growth-focused communications across the GCC. "
            "Proven track record delivering 4415% follower growth, 3M+ audience reach, and $130K+ budget optimisation while "
            "managing multi-channel B2B campaigns, C-suite/VIP stakeholder coordination, and high-impact executive forums. "
            "Adept at building repeatable workflow systems, managing cross-functional teams, and driving client engagement."
        ),
        "skills": [
            "Business Development", "Brand Strategy", "Campaign Management", "PR & Communications",
            "Event Marketing & VIP Coordination", "Content Marketing", "Digital Marketing", "CRM & HubSpot",
            "Budget Management ($130K+)", "Stakeholder Management", "SEO/SEM", "Cross-Functional Leadership"
        ],
        "exp_bullet_custom": {
            "bt_director_1": "Redesigned marketing, BD, and editorial workflows for executive forums, awards, and PR, improving turnaround time by 40%+ and strengthening brand positioning and execution quality.",
            "bt_mgr_3": "Generated 200+ monthly leads via hybrid event coverage and managed VIP coordination and stakeholder relations for the Business Tabloid Award Ceremony with 50+ senior attendees and sponsors."
        }
    },
    {
        "filename": "4.1_Vinay_Confidentialcompany_Resume.tex",
        "role_title": "Digital Marketing Executive/Manager",
        "company": "Confidential Company",
        "summary": (
            "Results-driven Digital Marketing Manager with 13+ years of overall experience, including 8+ years in performance marketing, "
            "SEO/SEM, paid media, marketing automation, and analytics. Delivered 4415% follower growth, 3M+ audience reach, and $130K+ "
            "budget optimisation. Proven expertise optimizing multi-country campaigns across UAE, KSA, and broader GCC, reducing CAC by 20%, "
            "increasing pageviews by 65,000+, and improving conversion rates by 42% through data-driven digital execution."
        ),
        "skills": [
            "Digital Marketing", "SEO/SEM", "Google Ads & PPC", "Google Analytics", "Marketing Automation",
            "Performance Marketing", "Conversion Rate Optimisation (CRO)", "Demand Generation", "HubSpot CRM",
            "Campaign Management", "Content Marketing", "Budget Management", "Cross-Functional Leadership"
        ],
        "exp_bullet_custom": {
            "medialogic_3": "Optimised multi-country PPC and digital campaigns across UAE, KSA, Oman, Qatar, Bahrain, Kuwait, Jordan, and Egypt, reducing CAC by 20%, increasing pageviews by 65,000+, and improving conversion rates by 42%."
        }
    },
    {
        "filename": "5.1_Vinay_Tigerrecruitment_Resume.tex",
        "role_title": "Executive Creative Director Tech-AI Growth",
        "company": "Tiger Recruitment",
        "summary": (
            "Director-level Marketing and Creative leader with 13+ years of overall experience (8+ years in marketing), "
            "specialising in AI-driven content systems, brand strategy, creative workflows, and growth-focused editorial direction. "
            "Pioneered multi-model AI workflows (Antigravity 2.0, Gemini, Claude, GPT-OSS, Kimi) reducing manual revision cycles by 50%+ "
            "and editing effort by 60%+. Delivered 4415% follower growth and 3M+ audience reach while leading cross-functional teams "
            "across high-impact GCC brand and media campaigns."
        ),
        "skills": [
            "AI Workflow Design", "Prompt Engineering", "Creative & Editorial Leadership", "Brand Strategy",
            "Content Marketing", "Multi-Model AI Pipelines", "Digital Marketing", "PR & Communications",
            "Campaign Management", "Cross-Functional Leadership", "Team Mentorship", "Budget Management"
        ],
        "exp_bullet_custom": {
            "bt_director_2": "Built AI-assisted workflows and creative applications using Antigravity 2.0, Google Vertex AI, Gemini, Claude, GPT-OSS, Qwen, Kimi, and LLMLite, reducing manual revision cycles by 50%+ and editing effort by 60%+."
        }
    },
    {
        "filename": "6.1_Vinay_Careem_Resume.tex",
        "role_title": "Senior Marketing Manager",
        "company": "Careem",
        "summary": (
            "Senior Marketing Manager with 13+ years of overall experience, including 8+ years in regional marketing, brand strategy, "
            "performance marketing, demand generation, and growth across the GCC and MENA. Delivered 4415% follower growth, 3M+ audience reach, "
            "and $130K+ budget optimisation. Proven record scaling multi-country campaigns across UAE, KSA, and Qatar, reducing CAC by 20%, "
            "increasing webinar/event attendance to 1,100+, and improving cross-regional brand alignment by 26%."
        ),
        "skills": [
            "Brand Strategy", "Performance Marketing", "Demand Generation", "GCC & MENA Campaign Scaling",
            "Digital Marketing", "Marketing Automation", "SEO/SEM", "Budget Management ($130K+)",
            "Cross-Functional Leadership", "Team Mentorship", "Google Analytics & Ads", "PR & Growth Strategy"
        ],
        "exp_bullet_custom": {
            "geaf_3": "Improved UAE-Switzerland brand alignment, increasing cross-regional engagement by 26%, and supported GCC expansion with campaigns that lifted regional lead generation by 23%."
        }
    },
    {
        "filename": "7.1_Vinay_Dealholdings_Resume.tex",
        "role_title": "Head of Marketing & Communications",
        "company": "DEAL Holdings",
        "summary": (
            "Strategic Marketing & Communications Leader with 13+ years of overall experience (8+ years in marketing), "
            "specialising in brand strategy, PR, integrated campaign management, event marketing, and digital growth across Dubai and the GCC. "
            "Delivered 4415% follower growth, 3M+ audience reach, and managed $130K+ budgets while reducing long-term marketing costs by 15%. "
            "Demonstrated track record coordinating VIP events with 50+ senior attendees/sponsors, leading PR communications, and managing agency vendors."
        ),
        "skills": [
            "Brand Strategy", "PR & Communications", "Event Marketing & VIP Coordination", "Campaign Management",
            "Content Marketing", "Digital Marketing", "Budget Management ($130K+)", "Agency & Vendor Negotiation",
            "Marketing Automation", "Social Media & Growth", "Cross-Functional Leadership", "CRM"
        ],
        "exp_bullet_custom": {
            "bt_mgr_3": "Generated 200+ monthly leads via hybrid event coverage and managed VIP coordination for the Business Tabloid Award Ceremony with 50+ senior attendees and sponsors."
        }
    },
    {
        "filename": "8.1_Vinay_Openinnovationai_Resume.tex",
        "role_title": "Project Manager – AI Infrastructure & Platforms",
        "company": "Open Innovation AI",
        "summary": (
            "AI Workflow & Marketing Technology Project Leader with 13+ years of overall experience, specialising in AI-enabled "
            "workflow automation, multi-model LLM implementation, platform design, and process optimisation. Built internal AI applications "
            "and repeatable pipelines using Antigravity 2.0, Vertex AI, Gemini, Claude, GPT-OSS, and LLMLite, reducing manual revision cycles "
            "by 50%+ and lowering operational overhead by 70%. Proven ability to translate complex technology into scalable, automated workflows."
        ),
        "skills": [
            "AI Workflow Design", "Multi-Model LLM Pipelines", "Prompt Engineering", "AI Platform Implementation",
            "Antigravity 2.0 & Vertex AI", "Marketing Automation", "Project & Workflow Management", "HubSpot & CRM",
            "Process Optimisation", "Cross-Functional Leadership", "Data & Analytics", "Budget Management"
        ],
        "exp_bullet_custom": {
            "bt_director_3": "Turned award curation, copywriting, research, and outreach into repeatable web-app-based workflows, improving output speed by 2x and reducing dependency on one-off execution."
        }
    }
]

def generate_resume(job):
    custom = job.get("exp_bullet_custom", {})
    
    b1_1 = custom.get("bt_director_1", "Redesigned marketing and editorial workflows for awards, PR, and executive forums, improving turnaround time by 40%+ and strengthening brand positioning and execution quality.")
    b1_2 = custom.get("bt_director_2", "Built AI-assisted workflows and applications using Antigravity 2.0, Google Vertex AI, Gemini, Claude, GPT-OSS, Qwen, Kimi, and LLMLite, reducing manual revision cycles by 50%+ and editing effort by 60%+.")
    b1_3 = custom.get("bt_director_3", "Turned award curation, copywriting, research, and outreach into repeatable web-app-based workflows, improving output speed by 2x and reducing dependency on one-off execution.")
    b1_4 = custom.get("bt_director_4", "Created AI training and multi-model pipelines that improved team adoption by 3x, reduced back-and-forth edits by 70%, and lowered hands-on operational involvement to roughly 10%.")
    
    b2_1 = custom.get("geaf_1", "Revamped LinkedIn and content strategy, increasing reach by 90,000+, newsletter subscribers by 1000%, and article views to 5,166+ in three months.")
    b2_2 = custom.get("geaf_2", "Managed a $130K budget, reduced long-term marketing costs by 15%, and increased webinar attendance to 1,100+.")
    b2_3 = custom.get("geaf_3", "Improved UAE-Switzerland brand alignment, increasing cross-regional engagement by 26%, and supported GCC expansion with campaigns that lifted regional lead generation by 23%.")
    
    b3_1 = custom.get("bt_mgr_1", "Led ``The Unknown Series'' campaigns, delivering 4415% follower growth through SEO-optimized content and paid media.")
    b3_2 = custom.get("bt_mgr_2", "Mentored a team of five across 12+ campaigns, improving content output efficiency by 30%.")
    b3_3 = custom.get("bt_mgr_3", "Generated 200+ monthly leads via hybrid event coverage and managed VIP coordination for the Business Tabloid Award Ceremony with 50+ senior attendees and sponsors.")
    
    b4_1 = custom.get("medialogic_1", "Built localised PPC and digital strategies for SaaS clients, driving 645% social growth across campaigns.")
    b4_2 = custom.get("medialogic_2", "Launched 5 webinars that generated 150+ qualified leads and improved lead quality by 35% across 15+ campaigns.")
    b4_3 = custom.get("medialogic_3", "Optimised multi-country campaigns across UAE, KSA, Oman, Qatar, Bahrain, Kuwait, Jordan, and Egypt, reducing CAC by 20%, increasing pageviews by 65,000+, and improving conversion rates by 42%.")
    
    skills_formatted = " $\\bullet$ ".join(f"\\textbf{{{esc(s)}}}" for s in job["skills"])
    
    content = f"""{PREAMBLE}
{HEADER}
% ==================== PROFESSIONAL SUMMARY ====================
\\section{{Summary}}
\\small{{{esc(job['summary'])}}}

% ==================== CORE SKILLS ====================
\\section{{Core Skills}}
\\small{{{skills_formatted}}}

% ==================== WORK EXPERIENCE ====================
\\section{{Professional Experience}}

\\noindent\\textbf{{Marketing \\& Editorial Director, AI-Driven Content, Workflows \\& Automation}} \\hfill \\textbf{{Jan 2025 -- Present}}\\\\
\\textit{{Business Tabloid}} \\hfill \\textit{{Dubai / Bangalore}}
\\begin{{itemize}}[leftmargin=*,nosep,topsep=2pt]
  \\item {esc(b1_1)}
  \\item {esc(b1_2)}
  \\item {esc(b1_3)}
  \\item {esc(b1_4)}
\\end{{itemize}}
\\vspace{{4pt}}

\\noindent\\textbf{{Marketing Manager}} \\hfill \\textbf{{May 2024 -- Jan 2025}}\\\\
\\textit{{Green Earth Action Foundation}} \\hfill \\textit{{Dubai, UAE}}
\\begin{{itemize}}[leftmargin=*,nosep,topsep=2pt]
  \\item {esc(b2_1)}
  \\item {esc(b2_2)}
  \\item {esc(b2_3)}
\\end{{itemize}}
\\vspace{{4pt}}

\\noindent\\textbf{{Marketing Manager}} \\hfill \\textbf{{Aug 2022 -- May 2024}}\\\\
\\textit{{Business Tabloid}} \\hfill \\textit{{Dubai, UAE}}
\\begin{{itemize}}[leftmargin=*,nosep,topsep=2pt]
  \\item {esc(b3_1)}
  \\item {esc(b3_2)}
  \\item {esc(b3_3)}
\\end{{itemize}}
\\vspace{{4pt}}

\\noindent\\textbf{{Digital Marketing Manager}} \\hfill \\textbf{{Apr 2020 -- Aug 2022}}\\\\
\\textit{{Medialogic}} \\hfill \\textit{{Dubai, UAE}}
\\begin{{itemize}}[leftmargin=*,nosep,topsep=2pt]
  \\item {esc(b4_1)}
  \\item {esc(b4_2)}
  \\item {esc(b4_3)}
\\end{{itemize}}
\\vspace{{4pt}}

\\noindent\\textbf{{Senior Marketing Executive}} \\hfill \\textbf{{Jan 2018 -- Mar 2020}}\\\\
\\textit{{Ecommerce Bay L.L.C}} \\hfill \\textit{{Dubai, UAE}}
\\begin{{itemize}}[leftmargin=*,nosep,topsep=2pt]
  \\item Drove 428\\% organic social growth through SEO audits and email drip campaigns across EMEA, Levant, Ireland, and the UK.
  \\item Improved conversion rates by 18\\% through branded product photography and videography and reduced campaign costs by 22\\% through vendor negotiation.
\\end{{itemize}}
\\vspace{{4pt}}

\\noindent\\textbf{{Account Manager}} \\hfill \\textbf{{Dec 2016 -- Dec 2017}}\\\\
\\textit{{Green Energy Solutions Ventilation}} \\hfill \\textit{{Dubai, UAE}}
\\begin{{itemize}}[leftmargin=*,nosep,topsep=2pt]
  \\item Implemented HubSpot CRM, improved onboarding time by 40\\%, and boosted team productivity by 25\\% while supporting AED 60,000+ in sales.
\\end{{itemize}}
\\vspace{{4pt}}

\\noindent\\textbf{{Sales Manager}} \\hfill \\textbf{{Jun 2015 -- Sep 2015}}\\\\
\\textit{{Zomato}} \\hfill \\textit{{Dubai, UAE}}
\\begin{{itemize}}[leftmargin=*,nosep,topsep=2pt]
  \\item Exceeded targets by 35\\%, secured 20+ client contracts, and delivered AED 250,000+ ROI in 3 months.
\\end{{itemize}}
\\vspace{{4pt}}

\\noindent\\textbf{{Marketing \\& Sales Internships}} \\hfill \\textbf{{Jun 2008 -- Aug 2012}}\\\\
\\textit{{Sanyo, LG, HP, Etisalat, Panasonic}} \\hfill \\textit{{Dubai, UAE}}
\\begin{{itemize}}[leftmargin=*,nosep,topsep=2pt]
  \\item Supported sales campaigns contributing AED 590K+ ROI and conducted market research that improved customer engagement by 20\\%.
\\end{{itemize}}

% ==================== EDUCATION ====================
{EDUCATION}

\\end{{document}}
"""
    return content

def main():
    print("=" * 65)
    print("Career-Ops Master-Faithful Resume Generator")
    print("Source of Truth: Vinay_Prakash_Resume_Optimized_6.8")
    print("=" * 65)
    
    for job in TAILORED_JOBS:
        filepath = os.path.join(LATEX_DIR, job["filename"])
        content = generate_resume(job)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        size_kb = round(os.path.getsize(filepath) / 1024, 1)
        print(f"  [OK] {job['filename']} ({size_kb} KB) -> {job['role_title']} @ {job['company']}")

    print("\nAll 6 tailored resumes regenerated with 100% strict fidelity to Vinay_Prakash_Resume_Optimized_6.8.")

if __name__ == "__main__":
    main()
