# Rule: Multi-Model AI Routing & Fallback Matrix

## Core Architecture
Career-Ops uses a tiered multi-model orchestration hierarchy to ensure high throughput, zero downtime, and strict factual fidelity.

## Tiered Routing
1. **Tier 1 (Primary AI Engine):**
   - **Moonshot Kimi AI** (`moonshot-v1-32k`, `moonshot-v1-8k`, `kimi-k2.5`) via `https://api.moonshot.ai/v1/chat/completions`.
   - Used for: LaTeX resume tailoring, 10-dimension scoring, company deep intelligence, decision-maker discovery, and 200-character LinkedIn notes.
   - Temperature: Low (`0.2` - `0.3`) for deterministic precision.
2. **Tier 2 (AI Fallback Engine):**
   - **Google Gemini** (`gemini-3.7-flash`, `gemini-flash-latest`, `gemini-3.5-flash`) via `https://generativelanguage.googleapis.com/v1beta`.
   - Automatically engaged upon any HTTP timeout, rate limit (429), or model outage on Tier 1.
3. **Tier 3 (Deterministic Engine):**
   - Heuristic scoring, rule-based company defaults, and ReportLab ATS PDF generation anchored directly to local master resume data.

## Invariant
Every AI tool or module must implement the Tier 1 -> Tier 2 -> Tier 3 failover pipeline with comprehensive logging and zero crashing.
