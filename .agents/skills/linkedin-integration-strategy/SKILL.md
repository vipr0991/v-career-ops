---
name: linkedin-integration-strategy
description: Strategy and compliance rules for integrating LinkedIn with Career-Ops
---

# LinkedIn Integration Architecture & Compliance

## Identification
- **Type**: Skill
- **Name**: `linkedin-integration-strategy`
- **Trigger**: When the user requests to integrate LinkedIn, fetch LinkedIn jobs, build browser extensions for LinkedIn, or handle LinkedIn OAuth.

## Rationale
The user provided a comprehensive architectural and compliance strategy for integrating with LinkedIn, explicitly avoiding scraping or violating the LinkedIn User Agreement (Section 8.2). Because this involves strict legal/compliance boundaries, OAuth 2.0 implementation specifics, and a multi-prong strategy (OAuth, alternative job boards, and a user-initiated browser extension), this information must be preserved as a skill so that the agent never attempts to scrape LinkedIn directly and properly follows the approved integration paths.

## Proposed Skill Content
The skill will instruct the agent on the three approved prongs for LinkedIn integration:

### Prong 1: Sign In With LinkedIn (OAuth 2.0)
- Use standard OIDC flow (`openid`, `profile`, `email`).
- Exchange code for token on the backend only.
- Encrypt tokens at rest and enforce CSRF state checking.
- Do not request "Talent Solutions" or "Marketing" API products.

### Prong 2: Reading Job Listings (Compliant)
- **Route A (Default):** Do not fetch from LinkedIn. Use public job APIs (Greenhouse, Lever, Adzuna, TheMuse, USAJOBS) and normalize the schema.
- **Route C (Manual):** Allow the user to paste a LinkedIn URL and process the pasted text. Do not have the server fetch the LinkedIn HTML.

### Prong 3: Browser Extension (User-Initiated)
- Extension must only observe and assist, never act without a click.
- Extract visible fields (title, company, description) via DOM when the user clicks a "Send to Career Ops" button.
- Use `activeTab` permission on `https://www.linkedin.com/jobs/*`.
- Post to Career Ops API using a Career Ops-issued token, not the LinkedIn token.

### Compliance Checklist
- No server-side fetching of `linkedin.com` (except OAuth).
- Extension requires explicit user click for every network call.
- Provide a disconnect flow to delete all captured data.
