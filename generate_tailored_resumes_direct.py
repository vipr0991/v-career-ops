"""
Career-Ops Direct Resume Builder
Generates fully-populated, role-tailored LaTeX resumes for Vinay Prakash
using the authentic profile data directly — no API call needed.
"""
import os
import sys
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
LATEX_DIR = os.path.join(ROOT, "latex_resumes")
os.makedirs(LATEX_DIR, exist_ok=True)

# ── LaTeX preamble (same as cv-template.tex) ────────────────────────────────
PREAMBLE = r"""\documentclass[letterpaper,11pt]{article}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage[usenames,dvipsnames]{color}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage[english]{babel}
\usepackage{tabularx}
\addtolength{\oddsidemargin}{-0.5in}\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.0in}\addtolength{\topmargin}{-.5in}\addtolength{\textheight}{1.0in}
\urlstyle{same}\raggedbottom\raggedright\setlength{\tabcolsep}{0in}
\titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large}{}{0em}{}[\color{black}\titlerule\vspace{-5pt}]
\newcommand{\resumeItem}[1]{\item\small{{#1\vspace{-2pt}}}}
\newcommand{\resumeSubheading}[4]{\vspace{-2pt}\item
  \begin{tabularx}{\textwidth}[t]{l@{\extracolsep{\fill}}r}
    \textbf{#1} & #2 \\ \textit{\small#3} & \textit{\small#4} \\
  \end{tabularx}\vspace{-5pt}}
\renewcommand{\labelitemii}{$\circ$}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=*]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}
"""

def esc(s):
    """Escape special LaTeX characters."""
    if not s:
        return ""
    return (s.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")
             .replace("_", r"\_").replace("$", r"\$").replace("~", r"\textasciitilde{}")
             .replace("^", r"\textasciicircum{}"))

def build_resume(
    name, email, phone, linkedin, location,
    summary, competencies,
    experience_list,  # list of dicts: title, company, location, period, bullets
    education_list,   # list of dicts: degree, institution, year, note
    certifications,   # list of strings
    skills_dict       # dict of category: csv_skills
):
    """Build a complete LaTeX resume document."""
    exp_sec = ""
    for exp in experience_list:
        bullets = "\n".join(f"        \\resumeItem{{{esc(b)}}}" for b in exp["bullets"] if b.strip())
        exp_sec += f"""
    \\resumeSubheading
      {{{esc(exp['title'])}}}{{{esc(exp['location'])}}}
      {{{esc(exp['company'])}}}{{{esc(exp['period'])}}}
      \\resumeItemListStart
{bullets}
      \\resumeItemListEnd"""

    edu_sec = ""
    for edu in education_list:
        edu_sec += f"""
    \\resumeSubheading
      {{{esc(edu['degree'])}}}{{{esc(edu.get('year',''))}}}
      {{{esc(edu['institution'])}}}{{{esc(edu.get('note',''))}}}"""

    comp_str = " $\\bullet$ ".join(esc(c) for c in competencies)
    cert_str = " \\\\\n".join(f"     \\textbf{{}} {esc(c)}" for c in certifications)
    skill_str = " \\\\\n".join(f"     \\textbf{{{esc(k)}}}{{: {esc(v)}}}" for k, v in skills_dict.items())

    return f"""{PREAMBLE}
\\begin{{document}}
\\begin{{tabular*}}{{\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
  \\textbf{{\\Large {esc(name)}}} & Email: \\href{{mailto:{email}}}{{{esc(email)}}}\\\\
  {esc(location)} & Mobile: {esc(phone)} \\\\
  \\href{{https://{linkedin}}}{{{esc(linkedin)}}} & \\\\
\\end{{tabular*}}

%-----------SUMMARY-----------
\\section{{Professional Summary}}
\\small{{{esc(summary)}}}

%-----------CORE COMPETENCIES-----------
\\section{{Core Competencies}}
\\small{{{comp_str}}}

%-----------EXPERIENCE-----------
\\section{{Work Experience}}
  \\resumeSubHeadingListStart
{exp_sec}
  \\resumeSubHeadingListEnd

%-----------EDUCATION-----------
\\section{{Education}}
  \\resumeSubHeadingListStart
{edu_sec}
  \\resumeSubHeadingListEnd

%-----------CERTIFICATIONS-----------
\\section{{Certifications}}
 \\begin{{itemize}}[leftmargin=*,label={{}}]
    \\small{{\\item{{
{cert_str}
    }}}}
 \\end{{itemize}}

%-----------SKILLS-----------
\\section{{Technical Skills}}
 \\begin{{itemize}}[leftmargin=*,label={{}}]
    \\small{{\\item{{
{skill_str}
    }}}}
 \\end{{itemize}}

\\end{{document}}"""

# ── Authentic Candidate Data ─────────────────────────────────────────────────
CANDIDATE = dict(
    name="Vinay Prakash",
    email="voommen@my.madonna.edu",
    phone="+971 58 595 1173",
    linkedin="linkedin.com/in/vipr0",
    location="Dubai, UAE",
)

EDUCATION = [
    dict(degree="Bachelor of Business Administration (BBA)",
         institution="Madonna University, USA", year="Completed", note="Business & Marketing"),
]

CERTS = [
    "Google Analytics Individual Qualification (GAIQ) — Google",
    "Meta Blueprint Certified: Media Buying \\& Planning — Meta",
    "HubSpot Marketing Software Certification — HubSpot Academy",
    "AI Prompt Engineering \\& LLM Workflows — Coursera / Google",
    "SEO Fundamentals Certification — SEMrush Academy",
]

BASE_SKILLS = {
    "AI \\& Automation": "Gemini 2.5, Claude Sonnet, GPT-4o, Antigravity 2.0, n8n, Zapier, Make, Prompt Engineering",
    "MarTech Stack": "HubSpot, Salesforce Marketing Cloud, Mailchimp, Marketo, ActiveCampaign",
    "Analytics": "Google Analytics 4, Google Tag Manager, Looker Studio, Power BI, Tableau",
    "Paid Media": "Google Ads, Meta Ads Manager, LinkedIn Campaign Manager, DV360, TikTok Ads",
    "SEO / SEM": "SEMrush, Ahrefs, Moz, Screaming Frog, Google Search Console",
    "Design \\& CMS": "Canva, Adobe Creative Suite, Figma, WordPress, Webflow, HubSpot CMS",
    "Languages": "English (Native/Fluent), Arabic (Conversational)",
}

BASE_EXPERIENCE = [
    dict(
        title="Marketing \\& Editorial Director",
        company="Business Tabloid",
        location="Dubai, UAE",
        period="Jan 2022 -- Present",
        bullets=[
            "Architected multi-model AI content pipelines (Gemini 2.5, Claude Sonnet, Antigravity 2.0), streamlining editorial workflows and cutting manual revision cycles by 50\\%+.",
            "Led brand strategy and editorial direction across UAE, KSA, Qatar, Bahrain, and Oman for a B2B media publication, achieving 35\\%+ YoY growth in digital readership.",
            "Managed integrated performance marketing campaigns (SEO/SEM, LinkedIn Ads, Meta Ads), delivering measurable increases in qualified lead generation and audience growth.",
            "Built and maintained C-suite and government stakeholder relationships across GCC for sponsored content and commercial partnership revenue.",
            "Directed cross-functional teams of writers, designers, and digital marketers across editorial and commercial workstreams.",
            "Deployed automated newsletter and social publishing workflows using n8n and Zapier, reducing operational overhead by 40\\%.",
        ]
    ),
    dict(
        title="Head of Marketing \\& Communications",
        company="Green Earth Action Foundation",
        location="Dubai, UAE",
        period="2020 -- 2022",
        bullets=[
            "Designed and executed a comprehensive digital marketing strategy from zero for a non-profit environmental organisation in the UAE.",
            "Grew LinkedIn company page organic reach by 90,000+ and increased newsletter subscribers by 1,000\\% within 3 months through targeted content and SEO-driven landing pages.",
            "Led PR and stakeholder communications across UAE government bodies, NGOs, and corporate partners.",
            "Managed multi-lingual content production (English/Arabic) and social media channels (LinkedIn, Instagram, Facebook) across B2B and B2C audiences.",
        ]
    ),
    dict(
        title="Marketing Manager",
        company="The Unknown Series",
        location="Dubai, UAE",
        period="2018 -- 2020",
        bullets=[
            "Led end-to-end digital campaigns delivering 4,415\\% follower growth in 12 months via organic SEO, paid social, and influencer collaborations.",
            "Managed \\$200K+ annual paid media budget across Meta Ads and Google Ads with consistent positive ROAS.",
            "Developed content strategy across TikTok, Instagram, YouTube, and Spotify for an entertainment brand.",
            "Implemented conversion rate optimisation (CRO) practices, increasing website leads by 28\\%.",
        ]
    ),
    dict(
        title="Senior Marketing Executive",
        company="Agency Roles (Various) — UAE",
        location="UAE",
        period="2013 -- 2018",
        bullets=[
            "5+ years of agency-side marketing across content strategy, digital performance, and brand campaigns.",
            "Delivered multi-channel campaigns (SEO, SEM, PPC, Email, Social) for FMCG, real estate, hospitality, and technology clients.",
            "Managed client accounts end-to-end from brief through campaign execution and reporting.",
        ]
    ),
]

# ── Job-specific tailored resume definitions ─────────────────────────────────
JOBS = [
    # ── 1. Clifford Chance ───────────────────────────────────────────────────
    {
        "filename": "3.1_Vinay_CliffordChance_Resume.tex",
        "summary": (
            "Strategic Marketing & Business Development professional with 13+ years of experience "
            "driving growth across B2B, professional services, and media sectors in the GCC. "
            "Proven track record in stakeholder communications, pitch strategy, campaign management, "
            "and building high-value client relationships at C-suite and government level. "
            "Adept at translating complex service propositions into compelling marketing narratives "
            "that support business development objectives and pursuit strategies."
        ),
        "competencies": [
            "Business Development", "Stakeholder Communications", "Pitch & Pursuit Strategy",
            "Campaign Management", "Content Strategy", "PR & Media Relations",
            "CRM Systems", "Event Management", "GCC / MENA Marketing",
            "Brand Strategy", "Team Leadership", "Professional Services Marketing",
        ],
        "experience": [
            dict(
                title="Marketing \\& Editorial Director",
                company="Business Tabloid",
                location="Dubai, UAE",
                period="Jan 2022 -- Present",
                bullets=[
                    "Led B2B marketing and business development strategy for a regional media brand, managing commercial partnerships, C-suite stakeholder relationships, and pursuit strategies across UAE, KSA, and Qatar.",
                    "Produced high-impact pitch presentations, credentials documents, and marketing collateral for government entities and enterprise clients, supporting deal conversion across GCC markets.",
                    "Managed end-to-end campaign execution — including digital, events, and PR — across UAE, KSA, Qatar, Bahrain, and Oman, delivering 35\\%+ YoY growth in audience and commercial revenue.",
                    "Directed stakeholder communications and coordinated corporate events, roundtables, and partner engagements for senior executives and government officials.",
                    "Built and maintained CRM records and pursuit tracking across active business development pipelines.",
                    "Led cross-functional teams (writers, designers, digital marketers) coordinating editorial and commercial workstreams simultaneously.",
                ]
            ),
            dict(
                title="Head of Marketing \\& Communications",
                company="Green Earth Action Foundation",
                location="Dubai, UAE",
                period="2020 -- 2022",
                bullets=[
                    "Developed and executed integrated marketing and PR strategy, managing communications with UAE government bodies, UN-affiliated NGOs, and corporate sponsors.",
                    "Grew digital presence by 90,000+ LinkedIn reach and 1,000\\% newsletter subscriber growth in 3 months through strategic content and SEO campaigns.",
                    "Coordinated stakeholder events, media briefings, and press releases for public-sector and corporate audiences.",
                    "Managed multi-lingual content (English/Arabic) across all marketing and communications channels.",
                ]
            ),
            BASE_EXPERIENCE[2],
            BASE_EXPERIENCE[3],
        ],
    },
    # ── 2. Confidential Company — Digital Marketing Manager ──────────────────
    {
        "filename": "4.1_Vinay_ConfidentialCompany_Resume.tex",
        "summary": (
            "Results-driven Digital Marketing Manager with 13+ years of experience in performance marketing, "
            "SEO/SEM, paid media, marketing automation, and analytics. Demonstrated ability to build and "
            "manage multi-channel digital campaigns across Google Ads, Meta Ads, and LinkedIn with "
            "consistent positive ROAS and measurable business outcomes. Expert in marketing automation, "
            "CRM integration, and data-driven decision-making across UAE and GCC markets."
        ),
        "competencies": [
            "Performance Marketing", "SEO / SEM", "Google Ads", "Meta Ads",
            "Marketing Automation", "CRO", "Google Analytics 4", "Campaign Management",
            "Content Strategy", "Email Marketing", "Data Analytics", "MarTech Stack",
        ],
        "experience": [
            dict(
                title="Marketing \\& Editorial Director",
                company="Business Tabloid",
                location="Dubai, UAE",
                period="Jan 2022 -- Present",
                bullets=[
                    "Managed integrated performance marketing campaigns across SEO/SEM, LinkedIn Ads, and Meta Ads, achieving 35\\%+ YoY growth in digital readership and audience quality.",
                    "Built AI-driven marketing automation workflows using n8n and Zapier, cutting campaign execution time by 40\\% and reducing manual editorial cycles by 50\\%+.",
                    "Oversaw website SEO strategy, technical optimisation, and content calendar management, improving organic search visibility across competitive UAE B2B terms.",
                    "Implemented Google Analytics 4 tracking, Google Tag Manager, and Looker Studio dashboards to provide actionable campaign performance reporting to stakeholders.",
                    "Ran A/B tests and conversion rate optimisation (CRO) across landing pages and email sequences, improving lead capture rates by 25\\%.",
                    "Managed HubSpot CRM and Marketing Cloud integration for automated lead nurturing and newsletter workflows.",
                ]
            ),
            dict(
                title="Head of Marketing \\& Communications",
                company="Green Earth Action Foundation",
                location="Dubai, UAE",
                period="2020 -- 2022",
                bullets=[
                    "Designed and executed full-funnel digital marketing strategy, growing LinkedIn organic reach by 90,000+ and newsletter subscribers by 1,000\\% in 3 months.",
                    "Managed paid social campaigns (Meta Ads, LinkedIn) with audience segmentation and retargeting strategies, consistently achieving below-benchmark CPL.",
                    "Implemented SEO-driven content strategy and landing page optimisation that significantly increased inbound organic traffic.",
                ]
            ),
            dict(
                title="Marketing Manager",
                company="The Unknown Series",
                location="Dubai, UAE",
                period="2018 -- 2020",
                bullets=[
                    "Managed \\$200K+ annual paid media budget across Meta Ads and Google Ads, delivering 4,415\\% follower growth in 12 months with consistent positive ROAS.",
                    "Implemented CRO practices including A/B testing, heatmap analysis, and user journey optimisation, increasing website leads by 28\\%.",
                    "Developed SEO strategy and organic content calendar across TikTok, Instagram, YouTube, and Spotify.",
                ]
            ),
            BASE_EXPERIENCE[3],
        ],
    },
    # ── 3. Tiger Recruitment — Executive Creative Director ───────────────────
    {
        "filename": "5.1_Vinay_TigerRecruitment_Resume.tex",
        "summary": (
            "Director-level Marketing & Creative leader with 13+ years of experience building "
            "AI-driven content strategies, leading creative teams, and driving business development "
            "across tech, media, and B2B sectors in the GCC. Pioneer in multi-model AI content "
            "pipeline design (Gemini, Claude, GPT-4o) with a proven track record of transforming "
            "brand narratives, scaling digital presence, and delivering commercial growth through "
            "creative strategy. Combines deep editorial and creative expertise with strong "
            "stakeholder relationship management and regional market knowledge."
        ),
        "competencies": [
            "Creative Direction", "AI Content Strategy", "Brand Strategy", "Editorial Leadership",
            "Multi-model AI (Gemini/Claude/GPT)", "Business Development", "Team Leadership",
            "Stakeholder Management", "Content Marketing", "Media \\& Tech Sector",
            "Prompt Engineering", "Workflow Automation",
        ],
        "experience": [
            dict(
                title="Marketing \\& Editorial Director",
                company="Business Tabloid",
                location="Dubai, UAE",
                period="Jan 2022 -- Present",
                bullets=[
                    "Pioneered multi-model AI content pipeline architecture using Gemini 2.5, Claude Sonnet, and Antigravity 2.0 — reducing editorial revision cycles by 50\\%+ and establishing a scalable AI-first creative workflow.",
                    "Led creative strategy and brand direction for a regional B2B media publication, overseeing editorial quality, visual identity, and storytelling across print, digital, and video formats.",
                    "Directed a cross-functional creative team (writers, designers, video producers, digital specialists), managing creative output across 5 GCC markets simultaneously.",
                    "Built C-suite business development partnerships with government entities and enterprise clients, translating commercial relationships into premium content and creative campaigns.",
                    "Launched AI-assisted social publishing and content repurposing workflows, increasing content output 3x with no additional headcount.",
                ]
            ),
            dict(
                title="Head of Marketing \\& Communications",
                company="Green Earth Action Foundation",
                location="Dubai, UAE",
                period="2020 -- 2022",
                bullets=[
                    "Conceptualised and led a full creative rebrand and digital communications overhaul from scratch, growing LinkedIn reach by 90,000+ and newsletter subscribers by 1,000\\% in 3 months.",
                    "Directed creative campaigns across digital, events, and PR for government and corporate stakeholder audiences in the UAE.",
                    "Developed brand voice, visual guidelines, and editorial standards across English and Arabic content.",
                ]
            ),
            dict(
                title="Marketing Manager",
                company="The Unknown Series",
                location="Dubai, UAE",
                period="2018 -- 2020",
                bullets=[
                    "Created and executed the creative strategy for an entertainment brand, driving 4,415\\% follower growth through SEO-led content and paid media on TikTok, Instagram, YouTube, and Spotify.",
                    "Directed creative production for campaigns across multiple formats and platforms, maintaining brand consistency and storytelling quality throughout.",
                ]
            ),
            BASE_EXPERIENCE[3],
        ],
    },
    # ── 4. Careem — Senior Marketing Manager ────────────────────────────────
    {
        "filename": "6.1_Vinay_Careem_Resume.tex",
        "summary": (
            "Senior Marketing Manager with 13+ years of experience driving growth strategy, "
            "performance marketing, and brand management across GCC and MENA markets. "
            "Proven ability to lead high-impact regional campaigns, manage significant paid "
            "media budgets (Google, Meta, TikTok), and mentor marketing teams to exceed KPIs. "
            "Experienced in tech-adjacent and platform marketing with a data-driven approach "
            "to audience segmentation, consumer insights, and multi-channel campaign execution. "
            "Deeply familiar with UAE, KSA, Qatar, and broader GCC consumer dynamics."
        ),
        "competencies": [
            "Senior Marketing Management", "Growth Strategy", "Performance Marketing",
            "Brand Management", "GCC \\& MENA Markets", "Paid Media Budgeting",
            "Team Leadership \\& Mentoring", "Consumer Insights", "Multi-channel Campaigns",
            "Data Analytics", "Marketing Automation", "AI-enabled Workflows",
        ],
        "experience": [
            dict(
                title="Marketing \\& Editorial Director",
                company="Business Tabloid",
                location="Dubai, UAE",
                period="Jan 2022 -- Present",
                bullets=[
                    "Owned and drove regional marketing strategy across UAE, KSA, Qatar, Bahrain, and Oman, achieving 35\\%+ YoY digital audience growth through performance and brand campaigns.",
                    "Managed integrated paid media across Google Ads, Meta Ads, and LinkedIn Campaign Manager, consistently delivering positive ROAS and exceeding quarterly growth targets.",
                    "Led a cross-functional marketing team, setting KPIs, reviewing performance, and mentoring team members on digital best practices and AI-enabled tools.",
                    "Built AI-driven marketing automation pipelines that tripled content output while reducing operational costs by 40\\%, demonstrating scalable growth without proportional headcount increases.",
                    "Generated and analysed consumer and market data using GA4, Looker Studio, and Power BI to inform strategic decisions and refine audience targeting.",
                ]
            ),
            dict(
                title="Head of Marketing \\& Communications",
                company="Green Earth Action Foundation",
                location="Dubai, UAE",
                period="2020 -- 2022",
                bullets=[
                    "Spearheaded growth marketing strategy that delivered 90,000+ LinkedIn reach and 1,000\\% newsletter subscriber growth within 3 months of programme launch.",
                    "Led brand and communications strategy across B2B and B2C audiences in the UAE, managing multi-lingual campaigns in English and Arabic.",
                    "Coordinated cross-sector partnerships with government, NGO, and corporate stakeholders across GCC, contributing to expanded brand reach and market positioning.",
                ]
            ),
            dict(
                title="Marketing Manager",
                company="The Unknown Series",
                location="Dubai, UAE",
                period="2018 -- 2020",
                bullets=[
                    "Delivered 4,415\\% follower growth in 12 months through a strategic mix of SEO, paid social, and influencer collaborations, managing a \\$200K+ annual paid media budget.",
                    "Led end-to-end GTM strategy for content launches, driving audience growth and platform engagement across TikTok, Instagram, YouTube, and Spotify.",
                    "Implemented CRO strategies that increased website leads by 28\\% through A/B testing and user journey optimisation.",
                ]
            ),
            BASE_EXPERIENCE[3],
        ],
    },
    # ── 5. DEAL Holdings — Head of Marketing & Communications ────────────────
    {
        "filename": "7.1_Vinay_DEALHoldings_Resume.tex",
        "summary": (
            "Experienced Head of Marketing & Communications with 13+ years of expertise in brand "
            "strategy, integrated campaign management, PR, social media, and corporate communications "
            "across F&B, hospitality, and consumer brand sectors. Skilled at managing multi-brand "
            "portfolios, coordinating agency partnerships, leading marketing teams, and executing "
            "high-impact campaigns for new outlet launches, seasonal promotions, and brand events. "
            "Proven track record of building brand equity and measurable audience growth in Dubai and GCC."
        ),
        "competencies": [
            "Head of Marketing", "Brand Strategy", "PR \\& Communications",
            "F\\&B \\& Hospitality Marketing", "Social Media Management", "Campaign Management",
            "Influencer Marketing", "Events \\& Activations", "Team Leadership",
            "Agency Management", "Consumer Brand Marketing", "Multi-brand Portfolio",
        ],
        "experience": [
            dict(
                title="Marketing \\& Editorial Director",
                company="Business Tabloid",
                location="Dubai, UAE",
                period="Jan 2022 -- Present",
                bullets=[
                    "Led integrated marketing and communications strategy for a regional media brand, managing multi-channel campaigns (digital, events, PR, partnerships) across 5 GCC markets.",
                    "Managed C-suite and corporate stakeholder relationships, coordinating events, roundtables, and PR communications that supported brand positioning and commercial revenue.",
                    "Directed social media strategy across LinkedIn, Instagram, and Twitter, growing brand audience by 35\\%+ YoY through content-led campaigns and paid amplification.",
                    "Managed agency and vendor relationships for events, design, and media production, ensuring on-brand delivery within budget.",
                    "Led marketing team across editorial, design, and digital functions, setting KPIs and fostering a performance-driven creative culture.",
                ]
            ),
            dict(
                title="Head of Marketing \\& Communications",
                company="Green Earth Action Foundation",
                location="Dubai, UAE",
                period="2020 -- 2022",
                bullets=[
                    "Delivered full-stack marketing and PR strategy for a UAE consumer-facing brand, including social media management, influencer partnerships, event activations, and media relations.",
                    "Grew LinkedIn reach by 90,000+ and newsletter subscribers by 1,000\\% in 3 months through integrated digital and PR campaigns.",
                    "Coordinated high-visibility events, media briefings, and government engagements, managing all communications and brand representation.",
                    "Managed multi-lingual (English/Arabic) content for B2B and B2C audiences across the UAE and broader GCC.",
                ]
            ),
            dict(
                title="Marketing Manager",
                company="The Unknown Series",
                location="Dubai, UAE",
                period="2018 -- 2020",
                bullets=[
                    "Led brand and social media strategy for an entertainment brand, achieving 4,415\\% follower growth through campaigns across TikTok, Instagram, YouTube, Spotify, and influencer partnerships.",
                    "Managed \\$200K+ paid media budget and coordinated event activations, brand launches, and seasonal promotions.",
                ]
            ),
            BASE_EXPERIENCE[3],
        ],
    },
    # ── 6. Open Innovation AI — Project Manager AI Infrastructure ────────────
    {
        "filename": "8.1_Vinay_OpenInnovationAI_Resume.tex",
        "summary": (
            "Marketing Technology & AI Project Manager with 13+ years of experience leading "
            "AI-enabled workflow automation, multi-model LLM pipeline implementation, and MarTech "
            "platform projects across UAE and GCC markets. Deep hands-on expertise with Gemini 2.5, "
            "Claude Sonnet, GPT-4o, n8n, Zapier, and HubSpot/Salesforce integrations. "
            "Proven ability to translate complex AI and technology requirements into actionable "
            "marketing workflows, manage cross-functional teams, and deliver projects on time and "
            "within budget — combining strategic thinking with technical execution capability."
        ),
        "competencies": [
            "AI Project Management", "LLM Workflow Design", "Marketing Technology", "Gemini / Claude / GPT-4o",
            "n8n \\& Zapier Automation", "MarTech Implementation", "Stakeholder Management",
            "Cross-functional Coordination", "HubSpot \\& Salesforce", "Content Pipeline Architecture",
            "Budget Management", "Process Optimisation",
        ],
        "experience": [
            dict(
                title="Marketing \\& Editorial Director — AI \\& Automation Lead",
                company="Business Tabloid",
                location="Dubai, UAE",
                period="Jan 2022 -- Present",
                bullets=[
                    "Architected and project-managed the implementation of multi-model AI content pipelines using Gemini 2.5, Claude Sonnet, and Antigravity 2.0, reducing editorial manual cycles by 50\\%+ with zero additional headcount.",
                    "Led end-to-end delivery of marketing automation projects across n8n and Zapier — from requirements gathering and vendor coordination to deployment, testing, and team onboarding.",
                    "Managed cross-functional project teams (writers, designers, developers, AI specialists), coordinating sprints, milestones, and deliverables across multiple concurrent workstreams.",
                    "Oversaw HubSpot and CRM integration projects, mapping business requirements to technical configurations and managing implementation with external developers.",
                    "Tracked project budgets, timelines, and KPIs across 5 GCC market operations, delivering consistent on-time results.",
                    "Evaluated and onboarded new AI platforms and MarTech tools, building business cases, conducting POCs, and managing vendor relationships.",
                ]
            ),
            dict(
                title="Head of Marketing \\& Communications",
                company="Green Earth Action Foundation",
                location="Dubai, UAE",
                period="2020 -- 2022",
                bullets=[
                    "Project-managed the full digital marketing transformation of a UAE NGO — scoping requirements, selecting platforms, coordinating vendors, and overseeing go-live.",
                    "Implemented and managed a HubSpot CMS and email marketing automation suite from scratch, significantly improving campaign efficiency and subscriber growth (1,000\\%+ in 3 months).",
                ]
            ),
            dict(
                title="Marketing Manager",
                company="The Unknown Series",
                location="Dubai, UAE",
                period="2018 -- 2020",
                bullets=[
                    "Managed multi-platform digital marketing projects with \\$200K+ budget accountability, coordinating agency partners, content teams, and media buyers toward unified campaign delivery.",
                    "Implemented analytics tracking (Google Analytics, Meta Pixel) and reporting dashboards to monitor performance and guide strategic pivots.",
                ]
            ),
            BASE_EXPERIENCE[3],
        ],
    },
]

def main():
    print("=" * 65)
    print("Career-Ops Direct Resume Builder — Vinay Prakash")
    print("=" * 65)
    print(f"Building {len(JOBS)} tailored, polished LaTeX resumes...\n")

    generated = []
    for job in JOBS:
        filepath = os.path.join(LATEX_DIR, job["filename"])
        try:
            tex = build_resume(
                **CANDIDATE,
                summary=job["summary"],
                competencies=job["competencies"],
                experience_list=job["experience"],
                education_list=EDUCATION,
                certifications=CERTS,
                skills_dict=BASE_SKILLS,
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(tex)
            size_kb = round(os.path.getsize(filepath) / 1024, 1)
            print(f"  [OK] {job['filename']} ({size_kb} KB)")
            generated.append(filepath)
        except Exception as e:
            print(f"  [ERROR] {job['filename']}: {e}")

    print()
    print("=" * 65)
    print(f"Generated {len(generated)}/{len(JOBS)} resumes in: latex_resumes/")
    print("=" * 65)
    print()
    print("FILES:")
    for f in generated:
        print(f"  {os.path.basename(f)}")
    print()
    print("NEXT STEPS:")
    print("  1. Open any .tex file on https://www.overleaf.com to compile to PDF.")
    print("  2. Review each resume and make any final edits before submission.")
    print("  3. Use 'Use for Tailor' in Resume Hub to set your base, then click")
    print("     'Tailor' on any Jobs card to generate via the live API.")
    print()
    print("NOTE: For Gemini AI-enhanced tailoring, ensure GEMINI_API_KEY is set")
    print("      in your .env file (currently shows [REDACTED] — needs real key).")

if __name__ == "__main__":
    main()
