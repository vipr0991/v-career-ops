import React from 'react'

export default function PrivacyPolicyPage() {
  return (
    <div className="page-content" style={{ maxWidth: 800, margin: '0 auto', padding: '40px 20px', lineHeight: 1.6 }}>
      <h1 style={{ marginBottom: 8 }}>Privacy Policy</h1>
      <p style={{ color: 'var(--text-muted)' }}>
        <strong>Effective Date:</strong> August 15, 2026 <br />
        <strong>Last Updated:</strong> August 15, 2026
      </p>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>1. Overview & Nature of the Platform</h3>
      <p>Career-Ops ("we", "us", or "the Platform") is a private, personal-use web application designed exclusively to assist the owner in organizing, analyzing, and conducting their personal job search.</p>
      
      <p><strong>Career-Ops is strictly non-commercial:</strong></p>
      <ul>
        <li>It is <strong>not</strong> intended for commercial advertising, marketing campaigns, lead generation, selling products or services, or promotional activities.</li>
        <li>It is configured with strict search engine non-indexation directives (<code>noindex, nofollow, noarchive</code>) and is not intended for public indexing or discovery on search engines.</li>
      </ul>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>2. Purpose of Career-Ops</h3>
      <p>The platform exists solely to streamline personal career development and job search operations by:</p>
      <ol>
        <li><strong>Curating High-Quality Opportunities:</strong> Discovering relevant career openings across target markets (including the UAE, Saudi Arabia, Qatar, Bahrain, Oman, Kuwait, and Bangalore, India) without the clutter of irrelevant, duplicate, or expired job postings.</li>
        <li><strong>Tailoring Application Materials:</strong> Customizing résumé versions (in LaTeX and ATS-optimized PDF formats) and strategic presentations for specific target opportunities.</li>
        <li><strong>Evaluating Role & Company Credibility:</strong> Analyzing company business models, growth trajectories, and job requirements to assess role fit before deciding to submit an application.</li>
      </ol>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>3. Information We Collect</h3>
      <p>Because Career-Ops is a personal career management utility, data collection is limited to operational inputs necessary for the tool's functionality:</p>
      <ul>
        <li><strong>Application Documents & Profile Data:</strong> Résumés, CV files, work history, portfolio links, and contact details uploaded or configured by the user.</li>
        <li><strong>Job Search & Evaluation Inputs:</strong> Job descriptions, job titles, target companies, notes, and geographic preferences entered or imported for analysis.</li>
        <li><strong>System & Activity Records:</strong> Generated evaluation scores, customized document archives, exclusion lists, and temporary system operational logs.</li>
      </ul>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>4. How Information Is Used</h3>
      <p>Information processed by Career-Ops is used exclusively to:</p>
      <ul>
        <li>Score and match job descriptions against the user's qualifications and career goals.</li>
        <li>Generate tailored LaTeX source files, PDF résumé downloads, and strategic PowerPoint decks.</li>
        <li>Maintain a persistent exclusion registry so irrelevant or dismissed jobs are not repeatedly surfaced.</li>
        <li>Track application stages within the user's private pipeline command center.</li>
      </ul>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>5. Third-Party Services & API Processing</h3>
      <p>To perform search and reasoning tasks requested by the user, Career-Ops interacts with selected third-party API providers:</p>
      <ul>
        <li><strong>Artificial Intelligence Engines:</strong> (e.g., Google Gemini / Vertex AI) used strictly to evaluate job criteria, research company context, and tailor resume bullet points.</li>
        <li><strong>Job Aggregation Providers:</strong> (e.g., JSearch, Adzuna, SerpAPI) used solely to query public job listings based on user-defined keywords and locations.</li>
      </ul>
      <p><em>We do not sell, rent, monetize, or trade any user data, uploaded resumes, or job search activity with any third-party marketing network or data broker.</em></p>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>6. Cookies, Tracking & Analytics</h3>
      <ul>
        <li>Career-Ops <strong>does not</strong> utilize advertising cookies, behavioral tracking pixels, third-party analytics trackers, or commercial marketing SDKs.</li>
        <li>Local browser storage (e.g., <code>localStorage</code>) is used strictly for essential user preferences, UI drawer states, and application session performance.</li>
      </ul>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>7. Data Retention & Deletion Controls</h3>
      <ul>
        <li>All resume files, pipeline records, research notes, and exclusion memories remain under the direct control of the user.</li>
        <li>The user may delete uploaded files, clear evaluation reports, or purge excluded records directly through the platform interface at any time.</li>
      </ul>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>8. Data Security</h3>
      <p>We implement reasonable technical and architectural safeguards to protect stored data, including HTTPS/TLS encryption in transit, strict environment-level API key management, and isolated application hosting environments.</p>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>9. Search Engine Non-Indexation (<code>noindex</code>)</h3>
      <p>Career-Ops enforces search engine exclusion directives via HTTP headers (<code>X-Robots-Tag: noindex, nofollow, noarchive</code>) and <code>robots.txt</code> configuration to prevent search engine crawlers from indexing site content or user materials.</p>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>10. User Rights & Data Management</h3>
      <p>As the sole operator and user of this personal platform, you maintain complete control over all data:</p>
      <ul>
        <li><strong>Right to Access & Export:</strong> You may export or download all tailored resumes (PDF/LaTeX), decks, and evaluations at any time.</li>
        <li><strong>Right to Modify & Purge:</strong> You may modify profile settings or permanently delete individual pipeline records, uploaded CVs, or exclusion entries.</li>
      </ul>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>11. Contact Information</h3>
      <p>If you have questions regarding this Privacy Policy or the operational handling of data on Career-Ops, please contact:</p>
      <ul>
        <li><strong>Site Owner / Administrator:</strong> Vinay Prakash</li>
        <li><strong>Email:</strong> vinay@example.com</li>
        <li><strong>Location:</strong> Dubai, United Arab Emirates</li>
      </ul>

      <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)', opacity: 0.5 }} />

      <h3>12. Informational Notice</h3>
      <p><em>This Privacy Policy is provided for informational transparency regarding the private, non-commercial operation of the Career-Ops platform. If this application is ever modified, expanded, or made publicly accessible for multi-user commercial use, a formal legal review may be required to ensure compliance with applicable regional privacy regulations (such as GDPR, UAE Data Protection Law, or CCPA).</em></p>
    </div>
  )
}
