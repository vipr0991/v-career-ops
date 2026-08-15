"""
Company Value Proposition Presentation Generator (.pptx)
Generates custom branded 6-slide strategic presentations for target employers.
"""
import os
import time
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class PresentationGenerator:
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir

    def generate_value_prop_deck(
        self,
        company_name: str,
        job_title: str,
        research_data: Optional[Dict[str, Any]] = None,
        candidate_name: str = "Vinay Prakash"
    ) -> str:
        """
        Generates a 6-slide PowerPoint presentation tailored to the company.
        Returns the absolute filepath of the generated .pptx file.
        """
        company_slug = "".join(c.lower() if c.isalnum() else "-" for c in (company_name or "company")).strip("-")
        filename = f"value-prop-{company_slug}-{int(time.time())}.pptx"
        output_path = os.path.join(self.output_dir, filename)

        try:
            from pptx import Presentation
            from pptx.util import Inches, Pt
            from pptx.enum.text import PP_ALIGN
            from pptx.dml.color import RGBColor

            prs = Presentation()
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)
            blank_layout = prs.slide_layouts[6]

            # Colors
            DARK_BG = RGBColor(15, 23, 42)      # Slate 900
            TEXT_LIGHT = RGBColor(248, 250, 252) # Slate 50
            ACCENT_BLUE = RGBColor(59, 130, 246) # Blue 500
            ACCENT_CYAN = RGBColor(6, 182, 212)  # Cyan 500
            CARD_BG = RGBColor(30, 41, 59)       # Slate 800
            TEXT_MUTED = RGBColor(148, 163, 184) # Slate 400

            def add_header(slide, title_text: str, subtitle_text: str):
                tb = slide.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.33), Inches(1.2))
                tf = tb.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.text = title_text
                p.font.size = Pt(32)
                p.font.bold = True
                p.font.color.rgb = ACCENT_CYAN
                
                if subtitle_text:
                    p2 = tf.add_paragraph()
                    p2.text = subtitle_text
                    p2.font.size = Pt(16)
                    p2.font.color.rgb = TEXT_MUTED

            # ── Slide 1: Title Slide ─────────────────────────────────────────
            s1 = prs.slides.add_slide(blank_layout)
            tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.3), Inches(3.5))
            tf1 = tb1.text_frame
            tf1.word_wrap = True
            
            p1 = tf1.paragraphs[0]
            p1.text = f"Strategic Value Proposition & Impact Plan"
            p1.font.size = Pt(38)
            p1.font.bold = True
            p1.font.color.rgb = ACCENT_BLUE

            p2 = tf1.add_paragraph()
            p2.text = f"Accelerating Growth, AI Workflows & Market Leadership at {company_name}"
            p2.font.size = Pt(22)
            p2.font.color.rgb = TEXT_LIGHT

            p3 = tf1.add_paragraph()
            p3.text = f"\nPrepared by {candidate_name} | Candidate for {job_title}\nDubai, UAE / GCC & Bangalore Footprint"
            p3.font.size = Pt(14)
            p3.font.color.rgb = TEXT_MUTED

            # ── Slide 2: Company Overview & Market Landscape ─────────────────
            s2 = prs.slides.add_slide(blank_layout)
            add_header(s2, f"1. Company Landscape & Market Context", f"Strategic alignment with {company_name}'s market position")
            
            biz_model = (research_data or {}).get("business_model", f"{company_name} drives high-growth operations across target regional markets.")
            mkt_pos = (research_data or {}).get("market_position_and_competitors", "Leading regional innovator competing with tier-1 market leaders.")
            
            tb2 = s2.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(4.5))
            tf2 = tb2.text_frame
            tf2.word_wrap = True
            
            p = tf2.paragraphs[0]
            p.text = "• Core Business Model & Value Proposition:"
            p.font.size = Pt(20)
            p.font.bold = True
            p.font.color.rgb = ACCENT_CYAN
            
            p = tf2.add_paragraph()
            p.text = f"  {biz_model}\n"
            p.font.size = Pt(16)
            p.font.color.rgb = TEXT_LIGHT

            p = tf2.add_paragraph()
            p.text = "• Market Positioning & Competitive Advantage:"
            p.font.size = Pt(20)
            p.font.bold = True
            p.font.color.rgb = ACCENT_CYAN

            p = tf2.add_paragraph()
            p.text = f"  {mkt_pos}"
            p.font.size = Pt(16)
            p.font.color.rgb = TEXT_LIGHT

            # ── Slide 3: Identified Gaps & Growth Opportunities ───────────────
            s3 = prs.slides.add_slide(blank_layout)
            add_header(s3, f"2. Key Growth Gaps & Opportunities", "Identified friction points where strategic intervention creates outsized ROI")
            
            gaps = (research_data or {}).get("strategic_pain_points", [
                "Scaling marketing content velocity without linear headcount increase.",
                "Integrating AI-assisted pipelines into legacy campaign cycles.",
                "Maximizing multi-channel conversion efficiency in competitive GCC tech markets."
            ])

            tb3 = s3.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(4.5))
            tf3 = tb3.text_frame
            tf3.word_wrap = True
            
            for idx, gap in enumerate(gaps[:3]):
                p = tf3.add_paragraph() if idx > 0 else tf3.paragraphs[0]
                p.text = f"• Opportunity {idx+1}: {gap}"
                p.font.size = Pt(18)
                p.font.color.rgb = TEXT_LIGHT

            # ── Slide 4: Candidate Problem-Solving Blueprint ──────────────────
            s4 = prs.slides.add_slide(blank_layout)
            add_header(s4, f"3. Problem-Solving Blueprint & Superpowers", f"How {candidate_name} solves core bottlenecks immediately")

            solutions = (research_data or {}).get("candidate_solutions_to_pitch", [
                "Deploy multi-model AI workflows (proven 50%+ reduction in revision turnaround).",
                "Execute data-driven multi-market demand generation funnels across UAE & GCC.",
                "Build scalable content and SEO engines that drive compounding organic inbound."
            ])

            tb4 = s4.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(4.5))
            tf4 = tb4.text_frame
            tf4.word_wrap = True

            for idx, sol in enumerate(solutions[:3]):
                p = tf4.add_paragraph() if idx > 0 else tf4.paragraphs[0]
                p.text = f"✔ Solution {idx+1}: {sol}\n"
                p.font.size = Pt(18)
                p.font.bold = True
                p.font.color.rgb = ACCENT_CYAN

            # ── Slide 5: 30 / 60 / 90 Day Impact Roadmap ──────────────────────
            s5 = prs.slides.add_slide(blank_layout)
            add_header(s5, "4. 30 / 60 / 90 Day Execution Roadmap", f"Actionable milestones to deliver early wins for {company_name}")

            tb5 = s5.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(4.5))
            tf5 = tb5.text_frame
            tf5.word_wrap = True

            roadmap = [
                ("Days 1–30 (Audit & Quick Wins):", "Audit current workflows, map high-impact content funnels, deploy initial AI automation templates to reduce revision cycles."),
                ("Days 31–60 (Scale & Optimize):", "Launch multi-channel demand generation campaigns, integrate automated reporting, optimize GCC localization."),
                ("Days 61–90 (Authority & Expansion):", "Establish sustained compounding organic traffic, scale automated lead gen, deliver full ROI report to executive leadership.")
            ]

            for idx, (phase, details) in enumerate(roadmap):
                p = tf5.add_paragraph() if idx > 0 else tf5.paragraphs[0]
                p.text = phase
                p.font.size = Pt(18)
                p.font.bold = True
                p.font.color.rgb = ACCENT_BLUE

                p_sub = tf5.add_paragraph()
                p_sub.text = f"{details}\n"
                p_sub.font.size = Pt(15)
                p_sub.font.color.rgb = TEXT_LIGHT

            # ── Slide 6: Summary & Next Steps ────────────────────────────────
            s6 = prs.slides.add_slide(blank_layout)
            add_header(s6, "5. Conclusion & Mutual Value Proposition", "Immediate readiness to drive measurable business outcomes")

            tb6 = s6.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(11.3), Inches(4.0))
            tf6 = tb6.text_frame
            tf6.word_wrap = True

            p = tf6.paragraphs[0]
            p.text = f"Why {candidate_name} for {company_name}?"
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = ACCENT_CYAN

            points = [
                "13+ years proven leadership bridging marketing strategy and cutting-edge AI automation.",
                "Zero ramp-up time: deep familiarity with UAE, Saudi Arabia, GCC, and Bangalore tech ecosystems.",
                "Commitment to measurable business impact: higher pipeline conversion, lower production costs, compounding brand reach."
            ]
            for pt in points:
                p = tf6.add_paragraph()
                p.text = f"• {pt}"
                p.font.size = Pt(17)
                p.font.color.rgb = TEXT_LIGHT

            prs.save(output_path)
            return output_path

        except ImportError:
            # Markdown/Text fallback if python-pptx is not present
            fallback_path = output_path.replace(".pptx", ".md")
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(f"# Strategic Value Proposition for {company_name}\n\nRole: {job_title}\nAuthor: {candidate_name}\n\n")
                f.write(f"## 1. Company Landscape\n{company_name} in target markets.\n\n")
                f.write("## 2. 30/60/90 Day Execution Plan\n- Days 1-30: Workflow audit\n- Days 31-60: Campaign launch\n- Days 61-90: Scale\n")
            return fallback_path

presentation_engine = PresentationGenerator()
