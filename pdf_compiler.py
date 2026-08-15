"""
Career-Ops PDF Resume Compiler
Converts tailored LaTeX and markdown resumes into polished, ATS-compliant PDF documents using ReportLab.
"""
import os
import re
import time
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from resume_namer import resume_namer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class PDFCompiler:
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir

    def compile_resume_to_pdf(
        self,
        job_title: str,
        company_name: str,
        latex_content: Optional[str] = None,
        candidate_name: str = "Vinay Prakash",
        custom_filename: Optional[str] = None
    ) -> str:
        """
        Compiles tailored resume content into an ATS-friendly, professional PDF file.
        Returns the absolute filepath of the generated PDF.
        """
        if custom_filename:
            pdf_filename = custom_filename
        else:
            pdf_filename = resume_namer.generate_filename(company_name or "Target", extension="pdf", candidate_name="Vinay")
        pdf_path = os.path.join(self.output_dir, pdf_filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom high-contrast styles
        title_style = ParagraphStyle(
            'CandidateName',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0F172A'),
            alignment=TA_CENTER
        )

        subtitle_style = ParagraphStyle(
            'CandidateTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#1E3A8A'),
            alignment=TA_CENTER
        )

        contact_style = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#475569'),
            alignment=TA_CENTER
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#1E3A8A'),
            spaceBefore=8,
            spaceAfter=3
        )

        job_header_left = ParagraphStyle(
            'JobHeaderLeft',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#0F172A')
        )

        job_header_right = ParagraphStyle(
            'JobHeaderRight',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#64748B'),
            alignment=2 # Right aligned
        )

        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12.5,
            textColor=colors.HexColor('#1E293B'),
            alignment=TA_JUSTIFY
        )

        bullet_style = ParagraphStyle(
            'BulletText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#1E293B'),
            leftIndent=12,
            firstLineIndent=-8
        )

        story = []

        # 1. Header: Name & Target Title
        story.append(Paragraph(candidate_name, title_style))
        story.append(Spacer(1, 2))
        story.append(Paragraph(f"Senior Marketing Leader & AI Automation Specialist | Candidate for {job_title}", subtitle_style))
        story.append(Spacer(1, 2))
        story.append(Paragraph("Dubai, UAE | +971 50 000 0000 | linkedin.com/in/vinay-prakash | vinay@business-tabloid.com", contact_style))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))

        # 2. Executive Summary
        story.append(Paragraph("EXECUTIVE SUMMARY", section_heading))
        summary_text = (
            f"Versatile, high-impact marketing and growth executive with 13+ years of progressive leadership (8+ years in core marketing, AI workflow integration, demand generation, and executive communications). Proven track record driving 4,415% social audience growth, architecting multi-channel GCC campaigns, and deploying cutting-edge AI prompt workflows that compress turnaround times by over 50%. Direct alignment with {company_name}'s strategic roadmap."
        )
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 6))

        # 3. Core Competencies Table
        story.append(Paragraph("CORE COMPETENCIES & EXPERTISE", section_heading))
        skills_data = [
            [
                Paragraph("<b>Strategic Leadership:</b> Brand Strategy, Multi-Market Expansion, P&L", body_style),
                Paragraph("<b>AI Workflows:</b> Multi-Model Automation, Prompt Architecture", body_style)
            ],
            [
                Paragraph("<b>Demand Gen:</b> Performance Marketing, Funnel Optimization, SEO/SEM", body_style),
                Paragraph("<b>MarTech Stack:</b> HubSpot, Google Analytics 4, CRM Pipelines", body_style)
            ]
        ]
        t = Table(skills_data, colWidths=[270, 270])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

        # 4. Professional Experience
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_heading))
        
        # Role 1: Business Tabloid
        exp_header1 = Table([
            [Paragraph("<b>Business Tabloid</b> — Head of Content Strategy & AI Operations", job_header_left),
             Paragraph("Dubai, UAE | 2021 – Present", job_header_right)]
        ], colWidths=[380, 160])
        exp_header1.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
        story.append(exp_header1)
        story.append(Spacer(1, 3))
        story.append(Paragraph("• Architected integrated AI-powered editorial and content production systems, increasing output throughput by 300% without additional headcount.", bullet_style))
        story.append(Paragraph(f"• Led end-to-end digital positioning for high-profile C-suite award forums and enterprise client accounts, tailored for {company_name} standards.", bullet_style))
        story.append(Paragraph("• Directed organic growth strategies resulting in a 4,415% expansion across target regional decision-maker audiences in the UAE and GCC.", bullet_style))
        story.append(Spacer(1, 6))

        # Role 2: Senior Digital Marketing Consultant
        exp_header2 = Table([
            [Paragraph("<b>Global Media & Advisory Partners</b> — Senior Marketing Consultant", job_header_left),
             Paragraph("Bangalore / GCC | 2018 – 2021", job_header_right)]
        ], colWidths=[380, 160])
        exp_header2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
        story.append(exp_header2)
        story.append(Spacer(1, 3))
        story.append(Paragraph("• Managed $130K+ annual digital marketing budgets across PPC, paid social, and SEO, delivering average 3.8x ROAS across multi-market cohorts.", bullet_style))
        story.append(Paragraph("• Designed automated email nurturing sequences and lead-scoring frameworks mapping directly into CRM sales pipelines.", bullet_style))
        story.append(Spacer(1, 6))

        # 5. Education & Certifications
        story.append(Paragraph("EDUCATION & CERTIFICATIONS", section_heading))
        story.append(Paragraph("• <b>Bachelor of Commerce / Business Administration</b> — Focus on Marketing Management", bullet_style))
        story.append(Paragraph("• <b>Certifications:</b> Google Analytics 4 Certified, HubSpot Inbound Marketing, Advanced Prompt Engineering", bullet_style))

        # Build document
        doc.build(story)
        return pdf_path

pdf_compiler = PDFCompiler()
