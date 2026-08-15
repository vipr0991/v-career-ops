---
name: career-ops-tailor-flow
description: Architecture guide for Career-Ops Tailoring, 1-Click App Kit on Pipeline, PDF compilation, and Moonshot Kimi / Gemini API routing.
---

# Career-Ops Tailor & 1-Click Kit Flow Architecture

## Master Source of Truth
**File:** `Vinay_Prakash_Resume_Optimized_6.8` (available as `.docx`, `.pdf`, and compiled master `cv-template.tex`).
All resume generators (LaTeX and ReportLab PDF) must strictly maintain 100% factual accuracy with this document:
- 8 Verified Roles (Jan 2025 Present, May 2024 Jan 2025, Aug 2022 May 2024, Apr 2020 Aug 2022, Jan 2018 Mar 2020, Dec 2016 Dec 2017, Jun 2015 Sep 2015, Jun 2008 Aug 2012)
- Real Degrees (MBA 2016, B.Sc. 2012 from Madonna University, Livonia)
- Real Metrics (4415% follower growth, 3M+ reach, $130K+ budget, 90,000+ reach, 1000% newsletter, 5,166+ article views, 1,100+ webinar attendance, 645% social growth, 428% organic growth, AED 250,000+ ROI).

## Endpoint & Trigger Map
| Action | Trigger UI | Backend Endpoint | AI Engine |
|---|---|---|---|
| Click "Tailor" | `JobsPage.jsx` | `POST /api/optimize` | Moonshot Kimi (`moonshot-v1-32k` / `kimi-k2.5`) + Gemini fallback |
| Click "1-Click App Kit" / "Regenerate Kit" | `PipelinePage.jsx` | `POST /api/pipeline/generate-kit` | Moonshot Kimi + Gemini fallback |
| Download PDF Resume | Pipeline Asset Modal / Hub | `GET /api/downloads/pdf/{filename}` | ReportLab ATS Compiler (anchored to Master Resume) |
| Download LaTeX Resume | Pipeline Asset Modal / Hub | `GET /api/downloads/latex/{filename}` | LaTeX Tailoring Engine |

## Multi-Model AI Routing Hierarchy
1. **Primary AI Engine:** Moonshot Kimi (`moonshot-v1-32k`, `moonshot-v1-8k`, `kimi-k2.5`) via `https://api.moonshot.ai/v1`.
2. **Secondary Fallback:** Google Gemini (`gemini-3.7-flash`, `gemini-flash-latest`, `gemini-3.5-flash`, `gemini-pro-latest`).
3. **Deterministic Fallback:** Master `cv-template.tex` compiled directly.

## PDF Compiler Guardrails (`pdf_compiler.py`)
- The ReportLab engine extracts the tailored summary and core skills from the generated LaTeX file.
- It renders all 8 authentic career roles and real education entries with zero hardcoded mocks or hallucinated companies/dates.
