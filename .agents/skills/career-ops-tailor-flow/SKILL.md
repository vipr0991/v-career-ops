---
name: career-ops-tailor-flow
description: Architecture guide for the Career-Ops Tailor button, resume persistence, and optimize endpoint. Use whenever modifying resume upload, tailoring, the /api/optimize endpoint, or the LaTeX tailoring engine.
---

# Career-Ops Tailor Flow Architecture

## Endpoint Map
| Action | Frontend | Backend |
|--------|----------|---------|
| Click "Tailor" on job card | `JobsPage.jsx` → `handleOptimizeResume()` | `POST /api/optimize` |
| Set active resume base | `ResumeHubPage.jsx` → "Use for Tailor" btn | `POST /api/resumes/active` |
| Get active resume | `ResumeHubPage.jsx` on mount | `GET /api/resumes/active` |

## Active Resume Pattern
- The user picks which uploaded file is the "base" for tailoring by clicking **"Use for Tailor"** in the Resume Library.
- The selection is persisted server-side in `data/active_resume.json`.
- The `/api/optimize` endpoint reads this file automatically; no need to pass it from the frontend.
- Active resume card gets a green `ACTIVE BASE` badge and green border in the UI.

## Tailoring Source Priority
The `generate_tailored_resume()` function in `latex_tailoring_engine.py` uses this hierarchy:

1. **`uploaded_resume_content`** (user's actual `.tex` file) — **PRIMARY**
   - Full LaTeX content (up to 6000 chars) is passed directly to Gemini.
   - For `.pdf`/`.docx`: a descriptive note is passed; cv-template is used as the content source.
2. **`cv-template.tex`** — **STRUCTURAL FALLBACK**
   - Used when no upload is present, or as a secondary structural reference.

## Tailoring Quality Rules (enforced in every Gemini prompt)
Every tailored resume MUST comply with all of these — if not, the output is rejected and the fallback (original source) is saved instead:

### PRESERVATION (never alter)
- ALL personal facts: name, email, phone, LinkedIn, location.
- ALL authentic experience entries: company names, job titles, employment dates — 100% accurate.
- ALL authentic metrics and achievements (no invented numbers).
- ALL education, certifications, and language proficiencies.

### TAILORING (allowed changes)
- Reorder/rephrase bullets to lead with most relevant achievements for the target role.
- Embed ATS keywords naturally into the Professional Summary and two most recent roles.
- Promote the most relevant skills to the top of the Skills section.
- Tighten language for clarity and impact.
- Add a 2-3 sentence Professional Summary synthesized ONLY from real content.

### Quality Checklist (reviewed before output)
- Accuracy: every company, date, title, and metric matches the source.
- Clarity: every bullet is action-verb led and outcome-focused.
- Consistency: tense, capitalisation, and punctuation are uniform.
- Formatting: LaTeX compiles without errors; all environments properly closed.
- Keyword alignment: at least 5 target keywords appear naturally.
- Relevance: top 3 bullets in the most recent role speak directly to the target role.

## Critical Rules
1. **Never remove `/api/optimize`** — the Tailor button in `JobsPage.jsx` depends on it.
2. **Uploaded resumes in `/resumes/` are ephemeral on Railway** — files are lost on redeploy.
   - **Fix**: Attach a Railway Volume mounted at `/app/resumes` to persist files across deployments.
   - Until a Volume is attached, warn users that uploaded files reset on redeploy.
3. **Both sources are always used**: uploaded resume as primary content, cv-template as structural reference.
4. Gemini temperature is set to `0.15` (low) to ensure factual accuracy and minimal hallucination.
5. `maxOutputTokens: 8192` ensures long resumes are not truncated mid-document.

## Railway Volume Setup (for persistent uploads)
1. Railway dashboard → **career-ops** service → **Storage** tab.
2. **Add Volume** → Mount path: `/app/resumes`.
3. The `resumes/` StaticFiles mount and `RESUMES_DIR` will then persist across deploys.
