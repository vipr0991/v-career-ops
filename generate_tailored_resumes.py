"""
Career-Ops Batch Resume Tailoring Script
Generates tailored LaTeX .tex files for all high-priority pipeline jobs
using Vinay's authentic profile data and the Gemini tailoring engine.
"""
import asyncio
import os
import sys
import json

# Ensure we run from the career-ops root
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

os.environ.setdefault("PYTHONPATH", ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

from latex_tailoring_engine import latex_tailor
from pdf_compiler import pdf_compiler

# ── Vinay's authentic profile (sourced from profile.yml + resume) ─────────────
VINAY_AUTHENTIC_RESUME = """
CANDIDATE: Vinay Prakash
EMAIL: voommen@my.madonna.edu | PHONE: +971585951173
LINKEDIN: linkedin.com/in/vipr0 | PORTFOLIO: behance.net/vinaypoommen
LOCATION: Dubai, UAE | NATIONALITY: Indian (No sponsorship needed for UAE)

PROFESSIONAL SUMMARY:
Strategic Marketing & Editorial Leader with 13+ years of experience (8+ in marketing), 
specialising in AI-enabled workflow automation, brand strategy, content marketing, and 
multi-channel demand generation. Most recently Marketing & Editorial Director at Business 
Tabloid where I built multi-model AI pipelines (Gemini/Claude/Antigravity 2.0) reducing 
manual revision cycles by 50%+. Proven record across GCC, MENA, and global markets in 
driving revenue growth, scaling brand presence, and transforming marketing operations.

KEY ACHIEVEMENTS:
- Revamped LinkedIn strategy for Green Earth Action Foundation: +90,000 reach, 
  +1,000% newsletter subscribers in 3 months
- Led campaigns for The Unknown Series: 4,415% follower growth via SEO & paid media
- Built AI content pipelines at Business Tabloid: 50%+ reduction in manual revision cycles
- Managed integrated MarTech stacks across HubSpot, Salesforce, Google Analytics, Meta Ads

WORK EXPERIENCE:

Marketing & Editorial Director — Business Tabloid | Dubai, UAE | Jan 2022 – Present
- Architected multi-model AI content pipelines using Gemini 2.5, Claude Sonnet, and 
  Antigravity 2.0, streamlining editorial workflows and cutting revision cycles by 50%+
- Led brand strategy and editorial direction for a B2B media publication across UAE, KSA, 
  Qatar, Bahrain, and Oman markets
- Managed integrated performance marketing campaigns (SEO/SEM, LinkedIn Ads, Meta Ads) 
  delivering 35%+ YoY growth in digital readership
- Built and managed relationships with C-suite stakeholders, government entities, and 
  enterprise partners across GCC for sponsored content and commercial partnerships
- Directed a cross-functional team of writers, designers, and digital marketers
- Developed and launched automated newsletter and social publishing workflows using n8n 
  and Zapier, reducing operational overhead by 40%

Head of Marketing & Communications — Green Earth Action Foundation | Dubai, UAE | 2020–2022
- Designed and executed a comprehensive digital marketing strategy from scratch for a 
  non-profit environmental organisation
- Grew LinkedIn company page from 500 to 90,000+ organic reach within 3 months
- Increased newsletter subscriber base by 1,000% through targeted content campaigns and 
  SEO-driven landing page optimisation
- Led PR and stakeholder communications across government bodies, NGOs, and corporates in UAE
- Managed social media channels (LinkedIn, Instagram, Facebook) across B2B and B2C audiences
- Produced and managed multi-lingual content (English/Arabic) for regional campaigns

Marketing Manager — The Unknown Series | Dubai, UAE | 2018–2020
- Led end-to-end digital marketing campaigns delivering 4,415% follower growth within 
  12 months via organic SEO, paid social, and influencer collaborations
- Developed content strategy and campaign calendar across TikTok, Instagram, YouTube, 
  and Spotify for an entertainment brand
- Managed $200K+ annual paid media budget across Meta Ads and Google Ads
- Implemented conversion rate optimisation (CRO) practices increasing website leads by 28%

Senior Marketing Executive — Various Agencies (2013–2018)
- 5+ years in agency-side marketing roles across content, digital, and performance marketing
- Managed campaigns for FMCG, real estate, hospitality, and technology sector clients across UAE
- Delivered multi-channel campaign management including SEO, SEM, PPC, and email marketing

EDUCATION:
- Bachelor of Business Administration (BBA), Madonna University, USA
- Additional coursework in Digital Marketing and Business Strategy

CERTIFICATIONS:
- Google Analytics Individual Qualification (GAIQ)
- Meta Blueprint Certified — Media Buying & Planning
- HubSpot Marketing Software Certification
- AI Prompt Engineering (Coursera/Google)
- SEO Fundamentals (SEMrush Academy)

TECHNICAL SKILLS:
AI & Automation: Gemini 2.5, Claude Sonnet, GPT-4o, Antigravity 2.0, n8n, Zapier, 
                 Make (Integromat), Prompt Engineering, LLM Workflow Design
MarTech Stack: HubSpot, Salesforce Marketing Cloud, Mailchimp, Marketo, ActiveCampaign
Analytics: Google Analytics 4, Google Tag Manager, Looker Studio, Power BI, Tableau
Paid Media: Google Ads, Meta Ads Manager, LinkedIn Campaign Manager, DV360
SEO/SEM: SEMrush, Ahrefs, Moz, Screaming Frog, Google Search Console
Design: Canva, Adobe Creative Suite (Photoshop, Illustrator), Figma
CMS & Publishing: WordPress, Webflow, HubSpot CMS, Notion
Project Management: Asana, Monday.com, Trello, Jira
Languages: English (Native/Fluent), Arabic (Conversational)

CORE COMPETENCIES:
AI Content Strategy | Marketing Automation | Brand Strategy | Demand Generation
Multi-Channel Campaign Management | SEO/SEM & PPC | Content Marketing | Editorial Leadership
Stakeholder & PR Communications | MarTech Implementation | Team Leadership & Mentoring
Regional MENA Marketing | B2B & B2C Marketing | Budget Management | Data Analytics
"""

# ── Top priority jobs for tailoring ─────────────────────────────────────────
TARGET_JOBS = [
    {
        "seq": 1,
        "company": "CliffordChance",
        "title": "Business Development & Marketing Manager",
        "score": 90,
        "jd": """Business Development & Marketing Manager (12-month FTC) at Clifford Chance, Dubai.
Key requirements: Manage BD/marketing strategy for a global law firm GCC office. 
Support partners with pitch documents, credentials, and pursuits. 
Manage client entertainment, events, and stakeholder communications. 
Run digital marketing campaigns, update website, manage social media presence.
Collaborate with regional and global marketing teams. 
Required: 5+ years marketing experience, law firm or professional services preferred.
Skills: Excellent written communication, stakeholder management, campaign management, 
CRM, project management, events coordination.""",
        "keywords": ["Business Development", "Professional Services", "Stakeholder Management",
                     "Pitch Presentations", "CRM", "Campaign Management", "Events", "PR",
                     "Digital Marketing", "Content Strategy", "GCC", "Legal/Law Firm"]
    },
    {
        "seq": 2,
        "company": "ConfidentialCompany",
        "title": "Digital Marketing Executive/Manager",
        "score": 95,
        "jd": """Digital Marketing Executive/Manager in Dubai, UAE.
Lead all digital marketing channels including SEO, SEM, PPC, social media, email marketing.
Develop and execute performance marketing campaigns with measurable KPIs.
Manage Google Ads, Meta Ads, LinkedIn Campaign Manager budgets.
Analyse campaign data using Google Analytics and produce monthly performance reports.
Oversee website content, SEO optimisation, and conversion rate improvement.
Implement marketing automation workflows and CRM integrations.
Required: 5+ years digital marketing experience, strong analytics, paid media expertise.
Skills: Google Ads, Meta Ads, SEO, SEM, Marketing Automation, CRM, Data Analysis, 
Content Strategy, A/B Testing, Conversion Optimisation.""",
        "keywords": ["Digital Marketing", "SEO", "SEM", "PPC", "Google Ads", "Meta Ads",
                     "Marketing Automation", "Campaign Management", "Analytics", "CRO",
                     "Content Strategy", "CRM", "Performance Marketing", "Dubai"]
    },
    {
        "seq": 3,
        "company": "TigerRecruitment",
        "title": "Executive Creative Director Tech-AI Growth",
        "score": 92,
        "jd": """Executive Creative Director for a Tech/AI Growth company via Tiger Recruitment, Dubai/Abu Dhabi.
Lead creative strategy and brand direction for an AI-focused media and technology company.
Build and manage AI-driven content creation pipelines and editorial workflows.
Drive business development through creative strategy and stakeholder partnerships.
Oversee brand identity, visual storytelling, and multi-platform content strategy.
Lead a cross-functional creative team including designers, writers, and digital specialists.
Required: Director-level experience in creative/content leadership; AI tools proficiency;
strong business development acumen; experience in tech/media sector.
Skills: Brand Strategy, AI Content Creation, Creative Direction, Team Leadership,
Business Development, Stakeholder Management, Media/Tech experience.""",
        "keywords": ["Creative Direction", "AI Content", "Brand Strategy", "Tech/AI",
                     "Business Development", "Team Leadership", "Editorial", "Media",
                     "Multi-model AI", "Workflow Automation", "Stakeholder Management",
                     "Prompt Engineering", "Director Level"]
    },
    {
        "seq": 4,
        "company": "Careem",
        "title": "Senior Marketing Manager",
        "score": 95,
        "jd": """Senior Marketing Manager at Careem (Uber), Dubai, UAE.
Own and drive marketing strategy for GCC markets including UAE, KSA, Qatar, Kuwait.
Lead performance marketing campaigns across digital, social, and OOH channels.
Manage significant paid media budgets across Google, Meta, TikTok, and Snapchat.
Collaborate with product, engineering, and operations teams on GTM strategies.
Build and maintain brand consistency across all MENA touchpoints.
Analyse consumer insights and market data to drive strategic decisions.
Lead and mentor a regional marketing team.
Required: 7+ years marketing experience, tech/startup/e-commerce background preferred.
Skills: Performance Marketing, Brand Management, Team Leadership, Budget Management,
Regional Marketing, Growth Strategy, Data Analytics, Consumer Insights.""",
        "keywords": ["Senior Marketing Manager", "Performance Marketing", "Growth Strategy",
                     "Brand Management", "GCC", "MENA", "Team Leadership", "Paid Media",
                     "Digital Marketing", "Multi-channel", "Analytics", "Tech/Startup"]
    },
    {
        "seq": 5,
        "company": "DEALHoldings",
        "title": "Head of Marketing & Communications",
        "score": 85,
        "jd": """Head of Marketing & Communications (F&B / Hospitality) at DEAL Holdings, Dubai.
Lead all marketing and communications for a growing F&B and hospitality group in UAE.
Develop and execute integrated brand strategy across multiple restaurant and hospitality brands.
Manage PR, influencer partnerships, media relations, and corporate communications.
Oversee digital marketing including social media, website, and paid campaigns.
Lead campaign planning for new outlet launches, seasonal promotions, and brand events.
Manage marketing team and agency partners.
Required: 8+ years marketing experience with hospitality/F&B sector exposure.
Skills: Brand Strategy, PR, Communications, Social Media, Campaign Management,
Hospitality Marketing, Team Leadership, Budget Management, Events, Influencer Marketing.""",
        "keywords": ["Head of Marketing", "Marketing Communications", "Brand Strategy",
                     "PR", "Hospitality", "F&B", "Social Media", "Campaign Management",
                     "Team Leadership", "Events", "Influencer", "Dubai", "GCC", "Consumer Brands"]
    },
    {
        "seq": 6,
        "company": "OpenInnovationAI",
        "title": "Project Manager AI Infrastructure Platforms",
        "score": 90,
        "jd": """Project Manager – AI Infrastructure & Platforms at Open Innovation AI, Dubai.
Lead AI-driven marketing technology projects and platform implementations.
Coordinate cross-functional AI workflow automation initiatives.
Manage AI content pipeline projects from brief to delivery.
Build and maintain relationships with AI platform vendors and technology partners.
Translate business requirements into AI-enabled workflows and automation strategies.
Track project milestones, budgets, and deliverables across multiple workstreams.
Required: 5+ years project management; strong AI/tech marketing background; 
experience implementing AI tools (Gemini, Claude, GPT) in enterprise workflows.
Skills: AI Project Management, Marketing Technology, Workflow Automation,
Stakeholder Management, AI Platforms, Content Strategy, Team Coordination.""",
        "keywords": ["AI Project Manager", "AI Infrastructure", "Marketing Technology",
                     "Workflow Automation", "Gemini", "Claude", "LLM", "Content Pipelines",
                     "Platform Implementation", "Stakeholder Management", "MarTech", "Dubai"]
    },
]

async def generate_all():
    print("=" * 65)
    print("Career-Ops Batch Resume Tailoring — Vinay Prakash")
    print("=" * 65)
    print(f"Generating tailored resumes for {len(TARGET_JOBS)} priority roles...\n")

    results = []
    for job in TARGET_JOBS:
        print(f"[{job['seq']}] Tailoring for: {job['title']} @ {job['company']} (Score: {job['score']}%)")
        try:
            tex_res = await latex_tailor.generate_tailored_resume(
                job_title=job["title"],
                company_name=job["company"],
                job_description=job["jd"],
                evaluation_data={"ats_keywords_found": job["keywords"]},
                uploaded_resume_content=VINAY_AUTHENTIC_RESUME,
            )
            tex_file = tex_res.get("tex_filename", "")
            print(f"    ✓ LaTeX generated: {tex_file}")

            # Attempt PDF compilation
            pdf_path = pdf_compiler.compile_resume_to_pdf(
                job["title"], job["company"], tex_res.get("tex_code", ""), "Vinay Prakash"
            )
            pdf_file = os.path.basename(pdf_path) if pdf_path else None
            if pdf_file and os.path.exists(pdf_path):
                size_kb = round(os.path.getsize(pdf_path) / 1024, 1)
                print(f"    ✓ PDF compiled:    {pdf_file} ({size_kb} KB)")
            else:
                print(f"    ⚠ PDF compilation skipped (pdflatex not available — .tex ready for Overleaf)")

            results.append({
                "job": f"{job['title']} @ {job['company']}",
                "score": job["score"],
                "tex_file": tex_file,
                "pdf_file": pdf_file,
                "status": "SUCCESS"
            })
        except Exception as e:
            print(f"    ✗ Error: {e}")
            results.append({
                "job": f"{job['title']} @ {job['company']}",
                "score": job["score"],
                "status": f"ERROR: {e}"
            })
        print()

    print("=" * 65)
    print("BATCH SUMMARY")
    print("=" * 65)
    success = [r for r in results if r["status"] == "SUCCESS"]
    print(f"Generated: {len(success)}/{len(TARGET_JOBS)} resumes\n")
    for r in results:
        status_icon = "✓" if r["status"] == "SUCCESS" else "✗"
        print(f"  {status_icon} {r['job']} ({r['score']}%)")
        if r["status"] == "SUCCESS":
            print(f"      TEX: {r.get('tex_file', 'N/A')}")
            if r.get("pdf_file"):
                print(f"      PDF: {r.get('pdf_file', 'N/A')}")
    print()
    print("All .tex files saved to: latex_resumes/")
    print("All PDF files saved to:  output/")
    print("Open .tex files on Overleaf.com for free PDF compilation if pdflatex is unavailable.")

if __name__ == "__main__":
    asyncio.run(generate_all())
