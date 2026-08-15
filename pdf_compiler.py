"""
Career-Ops PDF Resume Compiler
Converts tailored LaTeX and master resume data into polished, ATS-compliant PDF documents using ReportLab.
Source of Truth: Vinay_Prakash_Resume_Optimized_6.8
"""
import os
import re
import time
from typing import Dict, Any, Optional, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from resume_namer import resume_namer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Master Data from Vinay_Prakash_Resume_Optimized_6.8
MASTER_CONTACT = "Dubai, United Arab Emirates  |  voommen@my.madonna.edu  |  +971 58 595 1173  |  +91 9645591928  |  linkedin.com/in/vipr0"

MASTER_SUMMARY_DEFAULT = (
    "Strategic marketing and editorial leader with 13+ years of overall experience, including 8+ years in marketing, "
    "specialising in brand strategy, content marketing, AI-enabled workflow automation, demand generation, SEO/SEM, PR, "
    "and growth-focused communications. Delivered 4415% follower growth, 3M+ audience reach, and $130K+ budget optimisation "
    "while building scalable systems that improved marketing efficiency, content consistency, and commercial impact."
)

MASTER_SKILLS_DEFAULT = (
    "Brand Strategy | Content Marketing | Demand Generation | Digital Marketing | SEO/SEM | Marketing Automation | "
    "AI Workflow Design | Prompt Engineering | PR & Communications | Event Marketing | Campaign Management | "
    "HubSpot | Google Analytics | Google Ads | CRM | Budget Management | Cross-Functional Leadership"
)

MASTER_EXPERIENCE = [
    {
        "company": "Business Tabloid",
        "title": "Marketing & Editorial Director, AI-Driven Content, Workflows & Automation",
        "location": "Dubai / Bangalore",
        "period": "Jan 2025 – Present",
        "bullets": [
            "Redesigned marketing and editorial workflows for awards, PR, and executive forums, improving turnaround time by 40%+ and strengthening brand positioning and execution quality.",
            "Built AI-assisted workflows and applications using Antigravity 2.0, Google Vertex AI, Gemini, Claude, GPT-OSS, Qwen, Kimi, and LLMLite, reducing manual revision cycles by 50%+ and editing effort by 60%+.",
            "Turned award curation, copywriting, research, and outreach into repeatable web-app-based workflows, improving output speed by 2x and reducing dependency on one-off execution.",
            "Created AI training and multi-model pipelines that improved team adoption by 3x, reduced back-and-forth edits by 70%, and lowered hands-on operational involvement to roughly 10%."
        ]
    },
    {
        "company": "Green Earth Action Foundation",
        "title": "Marketing Manager",
        "location": "Dubai, UAE",
        "period": "May 2024 – Jan 2025",
        "bullets": [
            "Revamped LinkedIn and content strategy, increasing reach by 90,000+, newsletter subscribers by 1000%, and article views to 5,166+ in three months.",
            "Managed a $130K budget, reduced long-term marketing costs by 15%, and increased webinar attendance to 1,100+.",
            "Improved UAE-Switzerland brand alignment, increasing cross-regional engagement by 26%, and supported GCC expansion with campaigns that lifted regional lead generation by 23%."
        ]
    },
    {
        "company": "Business Tabloid",
        "title": "Marketing Manager",
        "location": "Dubai, UAE",
        "period": "Aug 2022 – May 2024",
        "bullets": [
            "Led 'The Unknown Series' campaigns, delivering 4415% follower growth through SEO-optimized content and paid media.",
            "Mentored a team of five across 12+ campaigns, improving content output efficiency by 30%.",
            "Generated 200+ monthly leads via hybrid event coverage and managed VIP coordination for the Business Tabloid Award Ceremony with 50+ senior attendees and sponsors."
        ]
    },
    {
        "company": "Medialogic",
        "title": "Digital Marketing Manager",
        "location": "Dubai, UAE",
        "period": "Apr 2020 – Aug 2022",
        "bullets": [
            "Built localised PPC and digital strategies for SaaS clients, driving 645% social growth across campaigns.",
            "Launched 5 webinars that generated 150+ qualified leads and improved lead quality by 35% across 15+ campaigns.",
            "Optimised multi-country campaigns across UAE, KSA, Oman, Qatar, Bahrain, Kuwait, Jordan, and Egypt, reducing CAC by 20%, increasing pageviews by 65,000+, and improving conversion rates by 42%."
        ]
    },
    {
        "company": "Ecommerce Bay L.L.C",
        "title": "Senior Marketing Executive",
        "location": "Dubai, UAE",
        "period": "Jan 2018 – Mar 2020",
        "bullets": [
            "Drove 428% organic social growth through SEO audits and email drip campaigns across EMEA, Levant, Ireland, and the UK.",
            "Improved conversion rates by 18% through branded product photography and videography and reduced campaign costs by 22% through vendor negotiation."
        ]
    },
    {
        "company": "Green Energy Solutions Ventilation",
        "title": "Account Manager",
        "location": "Dubai, UAE",
        "period": "Dec 2016 – Dec 2017",
        "bullets": [
            "Implemented HubSpot CRM, improved onboarding time by 40%, and boosted team productivity by 25% while supporting AED 60,000+ in sales."
        ]
    },
    {
        "company": "Zomato",
        "title": "Sales Manager",
        "location": "Dubai, UAE",
        "period": "Jun 2015 – Sep 2015",
        "bullets": [
            "Exceeded targets by 35%, secured 20+ client contracts, and delivered AED 250,000+ ROI in 3 months."
        ]
    },
    {
        "company": "Sanyo, LG, HP, Etisalat, Panasonic",
        "title": "Marketing & Sales Internships",
        "location": "Dubai, UAE",
        "period": "Jun 2008 – Aug 2012",
        "bullets": [
            "Supported sales campaigns contributing AED 590K+ ROI and conducted market research that improved customer engagement by 20%."
        ]
    }
]

MASTER_EDUCATION = [
    {
        "degree": "MBA in International Business, Minor in Marketing",
        "institution": "Madonna University, Livonia",
        "year": "2016"
    },
    {
        "degree": "B.Sc. in International Business, Minor in Economics",
        "institution": "Madonna University, Livonia",
        "year": "2012"
    }
]

class PDFCompiler:
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir

    def _extract_from_latex(self, latex_code: str) -> Dict[str, Any]:
        """Extract tailored summary, skills, and custom bullets from LaTeX if provided."""
        extracted = {}
        if not latex_code:
            return extracted

        # Extract summary
        sum_match = re.search(r'\\section\*?\{Summary\}[\s\n]*\\small\{([\s\S]*?)\}', latex_code)
        if not sum_match:
            sum_match = re.search(r'\\section\*?\{Professional Summary\}[\s\n]*\\small\{([\s\S]*?)\}', latex_code)
        if sum_match:
            raw_summary = sum_match.group(1).strip()
            # Clean LaTeX commands
            cleaned = re.sub(r'\\textbf\{(.*?)\}', r'<b>\1</b>', raw_summary)
            cleaned = cleaned.replace(r'\%', '%').replace(r'\$', '$').replace(r'\&', '&')
            cleaned = re.sub(r'\\[a-zA-Z]+', '', cleaned)
            extracted['summary'] = cleaned

        # Extract skills
        skills_match = re.search(r'\\section\*?\{Core Skills\}[\s\n]*\\small\{([\s\S]*?)\}', latex_code)
        if skills_match:
            raw_skills = skills_match.group(1).strip()
            cleaned_skills = re.sub(r'\\textbf\{(.*?)\}', r'<b>\1</b>', raw_skills)
            cleaned_skills = cleaned_skills.replace(r'\%', '%').replace(r'\$', '$').replace(r'\&', '&')
            cleaned_skills = cleaned_skills.replace(r'$\bullet$', '•').replace(r'\bullet', '•')
            extracted['skills'] = cleaned_skills

        return extracted

    def compile_resume_to_pdf(
        self,
        job_title: str,
        company_name: str,
        latex_content: Optional[str] = None,
        candidate_name: str = "Vinay Prakash",
        custom_filename: Optional[str] = None
    ) -> str:
        """
        Compiles authentic tailored resume content into an ATS-friendly, professional PDF file.
        Strictly reflects Vinay_Prakash_Resume_Optimized_6.8.
        """
        if custom_filename:
            pdf_filename = custom_filename
        else:
            pdf_filename = resume_namer.generate_filename(company_name or "Target", extension="pdf", candidate_name="Vinay")
        pdf_path = os.path.join(self.output_dir, pdf_filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CandidateName',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=19,
            textColor=colors.HexColor('#111827'),
            alignment=TA_CENTER
        )

        contact_style = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#374151'),
            alignment=TA_CENTER
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#111827'),
            spaceBefore=6,
            spaceAfter=2
        )

        job_title_style = ParagraphStyle(
            'JobTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#111827')
        )

        job_date_style = ParagraphStyle(
            'JobDate',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#111827'),
            alignment=2
        )

        job_company_style = ParagraphStyle(
            'JobCompany',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#4B5563')
        )

        job_loc_style = ParagraphStyle(
            'JobLoc',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#4B5563'),
            alignment=2
        )

        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor('#1F2937'),
            alignment=TA_JUSTIFY
        )

        bullet_style = ParagraphStyle(
            'BulletText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor('#1F2937'),
            leftIndent=10,
            firstLineIndent=-6
        )

        story = []

        # 1. Header: Name & Authentic Contact Line
        story.append(Paragraph(candidate_name, title_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(MASTER_CONTACT, contact_style))
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#374151'), spaceAfter=4))

        # 2. Summary
        latex_info = self._extract_from_latex(latex_content) if latex_content else {}
        summary_text = latex_info.get('summary', MASTER_SUMMARY_DEFAULT)
        story.append(Paragraph("SUMMARY", section_heading))
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 4))

        # 3. Core Skills
        skills_text = latex_info.get('skills', MASTER_SKILLS_DEFAULT)
        story.append(Paragraph("CORE SKILLS", section_heading))
        story.append(Paragraph(skills_text, body_style))
        story.append(Spacer(1, 4))

        # 4. Professional Experience (All 8 Authentic Roles)
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_heading))

        for exp in MASTER_EXPERIENCE:
            # Header Row: Title & Date
            hdr_table = Table([
                [Paragraph(exp["title"], job_title_style), Paragraph(exp["period"], job_date_style)]
            ], colWidths=[385, 150])
            hdr_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(hdr_table)

            # Subheader Row: Company & Location
            sub_table = Table([
                [Paragraph(exp["company"], job_company_style), Paragraph(exp["location"], job_loc_style)]
            ], colWidths=[385, 150])
            sub_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(sub_table)

            # Bullets
            for b in exp["bullets"]:
                clean_b = b.replace(r'\%', '%').replace(r'\$', '$').replace(r'\&', '&')
                story.append(Paragraph(f"• {clean_b}", bullet_style))

            story.append(Spacer(1, 3))

        # 5. Education
        story.append(Paragraph("EDUCATION", section_heading))
        for edu in MASTER_EDUCATION:
            edu_table = Table([
                [Paragraph(f"<b>{edu['degree']}</b>", job_title_style), Paragraph(f"<b>{edu['year']}</b>", job_date_style)]
            ], colWidths=[420, 115])
            edu_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(edu_table)
            story.append(Paragraph(edu['institution'], job_company_style))
            story.append(Spacer(1, 2))

        # Build document
        doc.build(story)
        return pdf_path

pdf_compiler = PDFCompiler()
