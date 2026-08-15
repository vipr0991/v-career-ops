"""
Company Value Proposition Presentation Generator (.pptx)
Generates high-contrast, executive-ready presentations with native charts, tables, and structured data visuals.
Multi-Model Grounded & Strictly Anchored to Vinay_Prakash_Resume_Optimized_6.8.
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
        Generates a high-contrast 6-slide PowerPoint presentation with native charts and tables.
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
            from pptx.enum.shapes import MSO_SHAPE
            from pptx.chart.data import CategoryChartData
            from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

            prs = Presentation()
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)
            blank_layout = prs.slide_layouts[6]

            # High-Contrast Executive Theme Colors
            COLOR_WHITE = RGBColor(255, 255, 255)
            COLOR_LIGHT_BG = RGBColor(248, 250, 252) # Slate 50
            COLOR_TEXT_DARK = RGBColor(15, 23, 42)    # Deep Slate / Black
            COLOR_TEXT_MUTED = RGBColor(71, 85, 105)  # Slate 600
            COLOR_NAVY = RGBColor(30, 58, 138)        # Deep Royal Navy
            COLOR_RED = RGBColor(220, 38, 38)         # Bold Crimson Red
            COLOR_EMERALD = RGBColor(5, 150, 105)     # Deep Emerald
            COLOR_BORDER = RGBColor(226, 232, 240)    # Slate 200
            COLOR_CARD_BG = RGBColor(241, 245, 249)   # Slate 100

            def apply_slide_bg(slide):
                # Set clean light background
                bg_shape = slide.shapes.add_shape(
                    MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
                )
                bg_shape.fill.solid()
                bg_shape.fill.fore_color.rgb = COLOR_LIGHT_BG
                bg_shape.line.fill.background()

                # Top accent banner line
                accent_bar = slide.shapes.add_shape(
                    MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12)
                )
                accent_bar.fill.solid()
                accent_bar.fill.fore_color.rgb = COLOR_NAVY
                accent_bar.line.fill.background()

            def add_header(slide, title_text: str, subtitle_text: str, badge_text: str = ""):
                apply_slide_bg(slide)

                tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
                tf = tb.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.text = title_text
                p.font.size = Pt(26)
                p.font.bold = True
                p.font.color.rgb = COLOR_NAVY

                if subtitle_text:
                    p2 = tf.add_paragraph()
                    p2.text = subtitle_text
                    p2.font.size = Pt(13)
                    p2.font.color.rgb = COLOR_TEXT_MUTED

                if badge_text:
                    bb = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.2), Inches(0.4), Inches(2.3), Inches(0.4))
                    bb.fill.solid()
                    bb.fill.fore_color.rgb = COLOR_NAVY
                    bb.line.fill.background()
                    btf = bb.text_frame
                    bp = btf.paragraphs[0]
                    bp.text = badge_text
                    bp.font.size = Pt(10)
                    bp.font.bold = True
                    bp.font.color.rgb = COLOR_WHITE
                    bp.alignment = PP_ALIGN.CENTER

            # ── Slide 1: Title Slide ─────────────────────────────────────────
            s1 = prs.slides.add_slide(blank_layout)
            apply_slide_bg(s1)

            c1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.2), Inches(11.733), Inches(5.2))
            c1.fill.solid()
            c1.fill.fore_color.rgb = COLOR_WHITE
            c1.line.color.rgb = COLOR_BORDER
            c1.line.width = Pt(1.5)

            tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(10.9), Inches(4.4))
            tf1 = tb1.text_frame
            tf1.word_wrap = True

            p1 = tf1.paragraphs[0]
            p1.text = "STRATEGIC VALUE PROPOSITION & IMPACT ROADMAP"
            p1.font.size = Pt(13)
            p1.font.bold = True
            p1.font.color.rgb = COLOR_RED

            p2 = tf1.add_paragraph()
            p2.text = "Accelerating Market Growth, AI Workflows & Demand Generation"
            p2.font.size = Pt(28)
            p2.font.bold = True
            p2.font.color.rgb = COLOR_NAVY

            p3 = tf1.add_paragraph()
            p3.text = f"Custom Prepared for {company_name} | Target Role: {job_title}"
            p3.font.size = Pt(17)
            p3.font.bold = True
            p3.font.color.rgb = COLOR_TEXT_DARK

            p4 = tf1.add_paragraph()
            p4.text = f"\nCandidate: {candidate_name} | 13+ Years Strategic Marketing Leadership & AI Automation Systems\nRegional Footprint: Dubai, UAE / GCC Multi-Market Ecosystems & Bangalore"
            p4.font.size = Pt(12)
            p4.font.color.rgb = COLOR_TEXT_MUTED

            # ── Slide 2: Market Landscape & Growth Distribution (With Donut Chart) ──
            s2 = prs.slides.add_slide(blank_layout)
            add_header(s2, "1. Market Landscape & Growth Distribution", f"Strategic channel allocation to maximize {company_name}'s market presence", "MARKET ANALYSIS")

            biz_model = (research_data or {}).get("business_model", f"{company_name} drives high-growth enterprise operations across target regional markets.")
            mkt_pos = (research_data or {}).get("market_position_and_competitors", "Leading regional innovator competing with tier-1 enterprise market leaders.")

            tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(6.2), Inches(4.8))
            tf2 = tb2.text_frame
            tf2.word_wrap = True

            p = tf2.paragraphs[0]
            p.text = "Strategic Market Positioning:"
            p.font.size = Pt(15)
            p.font.bold = True
            p.font.color.rgb = COLOR_NAVY

            p = tf2.add_paragraph()
            p.text = f"{biz_model}\n"
            p.font.size = Pt(11.5)
            p.font.color.rgb = COLOR_TEXT_DARK

            p = tf2.add_paragraph()
            p.text = "Competitive Opportunity:"
            p.font.size = Pt(15)
            p.font.bold = True
            p.font.color.rgb = COLOR_NAVY

            p = tf2.add_paragraph()
            p.text = f"{mkt_pos}\n"
            p.font.size = Pt(11.5)
            p.font.color.rgb = COLOR_TEXT_DARK

            p = tf2.add_paragraph()
            p.text = "• AI-driven content orchestration provides an immediate 3x throughput advantage over legacy competitor workflows."
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_RED
            p.font.bold = True

            chart_data2 = CategoryChartData()
            chart_data2.categories = ['AI Automation & Content', 'Performance Marketing', 'Compounding SEO', 'Enterprise Events']
            chart_data2.add_series('Optimal Growth Mix', (0.35, 0.30, 0.20, 0.15))

            x, y, cx, cy = Inches(7.4), Inches(1.8), Inches(5.1), Inches(4.6)
            chart2 = s2.shapes.add_chart(
                XL_CHART_TYPE.DOUGHNUT, x, y, cx, cy, chart_data2
            ).chart
            chart2.has_legend = True
            chart2.legend.position = XL_LEGEND_POSITION.BOTTOM
            chart2.legend.font.size = Pt(10)
            chart2.legend.font.color.rgb = COLOR_TEXT_DARK

            # ── Slide 3: Identified Gaps (With Comparison Table) ──────────────
            s3 = prs.slides.add_slide(blank_layout)
            add_header(s3, "2. Key Growth Gaps & Impact Assessment", "Diagnosing core bottlenecks vs. the target optimized state", "FRICTION VS SOLUTION")

            rows, cols = 4, 3
            left, top, width, height = Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8)
            table_shape = s3.shapes.add_table(rows, cols, left, top, width, height)
            table = table_shape.table
            table.columns[0].width = Inches(3.2)
            table.columns[1].width = Inches(4.2)
            table.columns[2].width = Inches(4.333)

            headers = ["Operational Domain", "Current Common Bottleneck (Risk)", "Target Optimized State (Opportunity)"]
            for col_idx, text in enumerate(headers):
                cell = table.cell(0, col_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_NAVY
                p = cell.text_frame.paragraphs[0]
                p.text = text
                p.font.size = Pt(12)
                p.font.bold = True
                p.font.color.rgb = COLOR_WHITE

            table_data = [
                ("Content & Campaign Velocity", "Heavy reliance on manual copy creation and multi-week revision bottlenecks.", "Multi-model prompt engines cutting turnaround by >50% while scaling output 3x."),
                ("GCC Multi-Market Penetration", "Generic global messaging failing to resonate with nuanced UAE/KSA buyers.", "Tailored regional narratives aligned with GCC enterprise executive standards."),
                ("Marketing ROI & Attribution", "Fragmented channel reporting without unified conversion attribution.", "Closed-loop MarTech dashboard integrating lead-scoring directly into sales CRM.")
            ]

            for row_idx, row_vals in enumerate(table_data, start=1):
                for col_idx, val in enumerate(row_vals):
                    cell = table.cell(row_idx, col_idx)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = COLOR_CARD_BG if row_idx % 2 == 0 else COLOR_WHITE
                    p = cell.text_frame.paragraphs[0]
                    p.text = val
                    p.font.size = Pt(11)
                    if col_idx == 0:
                        p.font.bold = True
                        p.font.color.rgb = COLOR_TEXT_DARK
                    elif col_idx == 1:
                        p.font.color.rgb = COLOR_RED
                    else:
                        p.font.color.rgb = COLOR_EMERALD
                        p.font.bold = True

            # ── Slide 4: Candidate Blueprint (With Native Bar Chart) ─────────
            s4 = prs.slides.add_slide(blank_layout)
            add_header(s4, "3. Candidate Blueprint & Projected Impact", f"Quantifiable performance acceleration {candidate_name} delivers", "PROJECTED ROI")

            tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(6.0), Inches(4.8))
            tf4 = tb4.text_frame
            tf4.word_wrap = True

            p = tf4.paragraphs[0]
            p.text = "Proven Execution Playbook:"
            p.font.size = Pt(15)
            p.font.bold = True
            p.font.color.rgb = COLOR_NAVY

            points4 = [
                ("1. AI Operations Engine", "Deploy custom multi-step AI workflows for rapid campaign drafting, executive editorial, and automated QA."),
                ("2. Demand Generation Funnels", "Scale high-intent multi-channel acquisition funnels tailored for enterprise decision-makers in the GCC."),
                ("3. Compounding Authority", "Build high-authority thought leadership and award-winning positioning that establishes clear category dominance.")
            ]

            for title, desc in points4:
                p = tf4.add_paragraph()
                p.text = f"{title}:"
                p.font.size = Pt(12)
                p.font.bold = True
                p.font.color.rgb = COLOR_EMERALD
                p_sub = tf4.add_paragraph()
                p_sub.text = f"{desc}\n"
                p_sub.font.size = Pt(11)
                p_sub.font.color.rgb = COLOR_TEXT_DARK

            chart_data4 = CategoryChartData()
            chart_data4.categories = ['Output Speed', 'Revision Cycles', 'Audience Growth', 'ROAS Velocity']
            chart_data4.add_series('Industry Baseline', (100, 100, 100, 100))
            chart_data4.add_series('With Vinay (AI-Led)', (300, 40, 440, 280))

            x, y, cx, cy = Inches(7.2), Inches(1.8), Inches(5.3), Inches(4.6)
            chart4 = s4.shapes.add_chart(
                XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data4
            ).chart
            chart4.has_legend = True
            chart4.legend.position = XL_LEGEND_POSITION.TOP
            chart4.legend.font.size = Pt(10)
            chart4.legend.font.color.rgb = COLOR_TEXT_DARK

            # ── Slide 5: 30-60-90 Day Execution Roadmap (With Table Matrix) ──
            s5 = prs.slides.add_slide(blank_layout)
            add_header(s5, "4. 30 / 60 / 90 Day Impact & Execution Roadmap", f"Structured milestone delivery plan for {company_name}", "ACTION PLAN")

            rows5, cols5 = 4, 3
            table_shape5 = s5.shapes.add_table(rows5, cols5, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
            table5 = table_shape5.table
            table5.columns[0].width = Inches(3.911)
            table5.columns[1].width = Inches(3.911)
            table5.columns[2].width = Inches(3.911)

            headers5 = ["Days 1–30: Audit & Quick Wins", "Days 31–60: Scale & Automation", "Days 61–90: Compounding Authority"]
            for col_idx, text in enumerate(headers5):
                cell = table5.cell(0, col_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_NAVY
                p = cell.text_frame.paragraphs[0]
                p.text = text
                p.font.size = Pt(12)
                p.font.bold = True
                p.font.color.rgb = COLOR_WHITE
                p.alignment = PP_ALIGN.CENTER

            roadmap_matrix = [
                ("• Audit marketing stack, assets & pipeline\n• Deploy 1st wave AI content workflows\n• Establish unified weekly KPI cadence",
                 "• Launch high-intent GCC acquisition funnels\n• Scale automated editorial & social calendar\n• Implement lead-scoring & CRM handoffs",
                 "• Drive category-leading thought leadership\n• Expand compounding organic inbound SEO\n• Present full Q1 ROI & attribution report"),
                ("Key Deliverable:\nWorkflow Diagnostic & Initial 30% Turnaround Gain",
                 "Key Deliverable:\nMulti-Channel Pipeline Engine Fully Operational",
                 "Key Deliverable:\nCompounding Brand Leadership & Multiplied Inbound"),
                ("Target Milestone:\nImmediate Zero-Lag Integration",
                 "Target Milestone:\nMeasurable Inbound Lead Surge",
                 "Target Milestone:\nSustained Scalable Dominance")
            ]

            for row_idx, row_vals in enumerate(roadmap_matrix, start=1):
                for col_idx, val in enumerate(row_vals):
                    cell = table5.cell(row_idx, col_idx)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = COLOR_CARD_BG if row_idx % 2 == 1 else COLOR_WHITE
                    p = cell.text_frame.paragraphs[0]
                    p.text = val
                    p.font.size = Pt(11)
                    if row_idx == 1:
                        p.font.color.rgb = COLOR_TEXT_DARK
                    elif row_idx == 2:
                        p.font.bold = True
                        p.font.color.rgb = COLOR_NAVY
                    else:
                        p.font.bold = True
                        p.font.color.rgb = COLOR_EMERALD

            # ── Slide 6: Summary & Executive Scorecard ────────────────────────
            s6 = prs.slides.add_slide(blank_layout)
            add_header(s6, "5. Executive Summary & Value Proposition", f"Why {candidate_name} is the optimal leadership choice for {company_name}", "FINAL SCORECARD")

            cards_data = [
                ("13+ Years", "Leadership Mastery", "Proven track record bridging high-level marketing strategy, editorial positioning, and modern AI automation."),
                ("4,415%", "Audience Expansion", "Documented growth across C-suite decision makers in UAE, Saudi Arabia, Qatar, and wider regional markets."),
                ("50%+", "Efficiency Gain", "Direct experience deploying proprietary AI prompt systems and workflows that eliminate production bottlenecks.")
            ]

            for idx, (metric, label, desc) in enumerate(cards_data):
                card_x = Inches(0.8 + idx * 4.0)
                card_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_x, Inches(1.8), Inches(3.733), Inches(4.8))
                card_box.fill.solid()
                card_box.fill.fore_color.rgb = COLOR_WHITE
                card_box.line.color.rgb = COLOR_BORDER
                card_box.line.width = Pt(1.5)

                tf6 = card_box.text_frame
                tf6.word_wrap = True
                p = tf6.paragraphs[0]
                p.text = metric
                p.font.size = Pt(32)
                p.font.bold = True
                p.font.color.rgb = COLOR_NAVY
                p.alignment = PP_ALIGN.CENTER

                p_lbl = tf6.add_paragraph()
                p_lbl.text = label
                p_lbl.font.size = Pt(14)
                p_lbl.font.bold = True
                p_lbl.font.color.rgb = COLOR_RED
                p_lbl.alignment = PP_ALIGN.CENTER

                p_desc = tf6.add_paragraph()
                p_desc.text = f"\n{desc}"
                p_desc.font.size = Pt(11.5)
                p_desc.font.color.rgb = COLOR_TEXT_DARK
                p_desc.alignment = PP_ALIGN.LEFT

            prs.save(output_path)
            return output_path

        except ImportError:
            fallback_path = output_path.replace(".pptx", ".md")
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(f"# Strategic Value Proposition for {company_name}\n\nRole: {job_title}\nAuthor: {candidate_name}\n")
            return fallback_path

presentation_engine = PresentationGenerator()
