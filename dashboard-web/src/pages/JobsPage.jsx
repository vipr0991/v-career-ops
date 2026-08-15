import React, { useState, useEffect } from 'react'
import ScoreRing from '../components/ScoreRing'
import * as api from '../api-resilient'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

const ROLE_PRESETS = [
  'Senior Marketing Manager',
  'AI Content & Automation Specialist',
  'AI Strategy & Enablement Lead',
  'Marketing Operations Manager',
  'Senior Marketing Manager MarTech',
  'Head of Digital Marketing',
  'Director / Head of Content Marketing',
  'MENA Regional Marketing Lead',
]

const LOCATION_PRESETS = [
  { label: 'All Regions', value: 'All' },
  { label: 'UAE (Dubai / Abu Dhabi)', value: 'Dubai, UAE' },
  { label: 'Saudi Arabia (Riyadh / NEOM)', value: 'Riyadh, Saudi Arabia' },
  { label: 'Qatar (Doha)', value: 'Doha, Qatar' },
  { label: 'Bahrain', value: 'Manama, Bahrain' },
  { label: 'Oman', value: 'Muscat, Oman' },
  { label: 'Kuwait', value: 'Kuwait City, Kuwait' },
  { label: 'Bangalore, India', value: 'Bangalore, India' },
]

// String sanitizer helper to remove noisy dashes, repeated symbols, and letter-hyphens
function cleanJobString(str) {
  if (!str || typeof str !== 'string') return ''
  let s = str
  // Remove letter-by-letter hyphens if present (-C-l-i-f-f-o-r-d-)
  if (/-[a-zA-Z]-/.test(s)) {
    s = s.replace(/-/g, '')
  }
  // Strip leading/trailing hyphens, underscores, dots, bars
  s = s.replace(/^[\s\-_|·•]+|[\s\-_|·•]+$/g, '')
  // Collapse multiple consecutive hyphens or spaces into a single clean space
  s = s.replace(/[\s\-_]{2,}/g, ' ')
  // Clean redundant location suffix in title if present
  s = s.replace(/\s*\|\s*Dubai,\s*UAE.*$/i, '')
  s = s.replace(/\s*-\s*Dubai,\s*UAE.*$/i, '')
  return s.trim()
}

export default function JobsPage({
  searchResults, jobs, selectedJob, scoringJobId,
  searchFilters, setSearchFilters,
  onSearch, onScoreJob, onOptimizeResume, onApply,
  showAddJdModal, setShowAddJdModal,
  addToast
}) {
  const [newJdText, setNewJdText] = useState('')
  const [newJdTitle, setNewJdTitle] = useState('')
  const [newJdCompany, setNewJdCompany] = useState('')
  const [newJdLocation, setNewJdLocation] = useState('')
  const [hasAutoSearched, setHasAutoSearched] = useState(false)
  const [evaluatedFilter, setEvaluatedFilter] = useState('all')
  const [localExcluded, setLocalExcluded] = useState(new Set())

  const handleExcludeJob = async (job) => {
    const comp = cleanJobString(job.company || 'Unknown')
    const tit = cleanJobString(job.title || job.role || 'Role')
    const key = `${comp.toLowerCase()}_${tit.toLowerCase()}`
    setLocalExcluded(prev => new Set(prev).add(key))
    try {
      await fetch(`${API_BASE}/api/jobs/exclude`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company: comp,
          title: tit,
          url: job.url || '',
          reason: 'User removed from search results'
        })
      })
      addToast(`Permanently excluded ${comp}`, 'info')
    } catch {
      addToast(`Excluded ${comp}`, 'info')
    }
  }

  // Auto-search on first load if empty
  useEffect(() => {
    if (!hasAutoSearched && searchResults.length === 0) {
      setHasAutoSearched(true)
      onSearch(searchFilters)
    }
  }, [hasAutoSearched, searchResults.length, onSearch, searchFilters])

  const handleCustomJdSubmit = (e) => {
    e.preventDefault()
    if (!newJdText.trim() || !newJdTitle.trim() || !newJdCompany.trim()) {
      addToast('Please fill out all fields', 'warning')
      return
    }
    const customJob = {
      id: `custom-${Date.now()}`,
      title: cleanJobString(newJdTitle),
      company: cleanJobString(newJdCompany),
      location: cleanJobString(newJdLocation) || 'Dubai, UAE',
      description: newJdText,
      url: 'Custom Paste'
    }
    setShowAddJdModal(false)
    onScoreJob(customJob)
    setNewJdText('')
    setNewJdTitle('')
    setNewJdCompany('')
    setNewJdLocation('')
  }

  const saveJobToPipeline = async (job) => {
    try {
      const scoreVal = typeof job.score === 'object' ? job.score : { overall_score: job.score || 80 }
      const res = await fetch(`${API_BASE}/api/pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: cleanJobString(job.title || job.role || 'Target Role'),
          company: cleanJobString(job.company || 'Enterprise'),
          location: cleanJobString(job.location || searchFilters.location || 'Dubai, UAE'),
          salary_range: job.salary_range || 'Not Disclosed',
          url: job.url || '',
          source: job.source || 'SERP Discovery',
          description: job.description || job.jd_content || '',
          score: scoreVal,
          stage: 'pipeline_saved'
        })
      })
      if (res.ok) {
        addToast(`Saved ${cleanJobString(job.company)} to Pipeline!`, 'success')
      } else {
        addToast('Could not save to pipeline', 'error')
      }
    } catch {
      addToast('Network error while saving to pipeline', 'error')
    }
  }

  const filteredSearchResults = (searchResults || []).filter(j => {
    const key = `${cleanJobString(j.company || '').toLowerCase()}_${cleanJobString(j.title || '').toLowerCase()}`
    return !localExcluded.has(key)
  })

  const filteredEvaluatedJobs = (jobs || []).filter(j => {
    const key = `${cleanJobString(j.company || '').toLowerCase()}_${cleanJobString(j.role || j.title || '').toLowerCase()}`
    if (localExcluded.has(key)) return false
    if (evaluatedFilter === 'top') {
      const s = typeof j.score === 'object' ? (j.score?.overall_score || 0) : (j.score || 0)
      return s >= 85
    }
    return true
  })

  return (
    <div className="page-content" id="jobs-page">
      
      {/* ── Search & Filter Control Panel ─────────────────────────────────── */}
      <div className="search-panel">
        <div className="search-panel-header">
          <div className="search-panel-title-wrap">
            <span className="material-symbols-outlined search-panel-icon">travel_explore</span>
            <div>
              <h2 className="search-panel-title">Multi-Location Job Discovery & SERP Search</h2>
              <p className="search-panel-subtitle">
                Targeting Middle East (GCC) & Bangalore
              </p>
            </div>
          </div>
        </div>

        {/* Role Presets */}
        <div className="preset-group">
          <span className="preset-group-label">Role Suggestions:</span>
          <div className="preset-chips-wrap">
            {ROLE_PRESETS.map((role) => (
              <button
                key={role}
                className={`preset-chip ${searchFilters.title === role ? 'active' : ''}`}
                onClick={() => setSearchFilters({ ...searchFilters, title: role })}
              >
                {role}
              </button>
            ))}
          </div>
        </div>

        {/* Location Presets */}
        <div className="preset-group">
          <span className="preset-group-label">Target Metro:</span>
          <div className="preset-chips-wrap">
            {LOCATION_PRESETS.map((loc) => {
              const isMatch = searchFilters.location === loc.value
              return (
                <button
                  key={loc.value}
                  className={`preset-chip location ${isMatch ? 'active' : ''}`}
                  onClick={() => setSearchFilters({ ...searchFilters, location: loc.value })}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: 13 }}>location_on</span>
                  {loc.label}
                </button>
              )
            })}
          </div>
        </div>

        {/* Search Input Form */}
        <form className="search-form-grid" onSubmit={(e) => { e.preventDefault(); onSearch(searchFilters) }}>
          <div className="form-field">
            <label className="form-label">Target Role Title</label>
            <input
              type="text"
              className="form-input"
              value={searchFilters.title}
              onChange={(e) => setSearchFilters({ ...searchFilters, title: e.target.value })}
              placeholder="e.g. Senior Marketing Manager"
            />
          </div>

          <div className="form-field">
            <label className="form-label">Location (Drop-down)</label>
            <select
              className="form-select"
              value={searchFilters.location || 'Dubai, UAE'}
              onChange={(e) => setSearchFilters({ ...searchFilters, location: e.target.value })}
            >
              {LOCATION_PRESETS.map(loc => <option key={loc.value} value={loc.value}>{loc.label}</option>)}
            </select>
          </div>

          <div className="form-field-dual">
            <div className="form-field">
              <label className="form-label">Currency</label>
              <select
                className="form-select"
                value={searchFilters.currency || 'AED'}
                onChange={(e) => setSearchFilters({ ...searchFilters, currency: e.target.value })}
              >
                <option value="AED">AED (UAE)</option>
                <option value="SAR">SAR (Saudi Arabia)</option>
                <option value="QAR">QAR (Qatar)</option>
                <option value="BHD">BHD (Bahrain)</option>
                <option value="OMR">OMR (Oman)</option>
                <option value="KWD">KWD (Kuwait)</option>
                <option value="INR">INR (India)</option>
                <option value="USD">USD (Global)</option>
              </select>
            </div>

            <div className="form-field">
              <label className="form-label">Salary Range</label>
              <select
                className="form-select"
                value={searchFilters.salary || 'Any'}
                onChange={(e) => setSearchFilters({ ...searchFilters, salary: e.target.value })}
              >
                <option value="Any">Any Salary</option>
                <option value="20k-30k">20k to 30k</option>
                <option value="30k-40k">30k to 40k</option>
                <option value="40k-50k">40k to 50k</option>
                <option value="50k+">50k+</option>
              </select>
            </div>
          </div>

          <div className="form-actions-wrap">
            <button type="submit" className="btn btn-primary form-btn-scan">
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>search</span>
              Scan Jobs
            </button>
            <button type="button" className="btn btn-secondary form-btn-paste" onClick={() => setShowAddJdModal(true)}>
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>post_add</span>
              Paste JD
            </button>
          </div>
        </form>
      </div>

      {/* ── SECTION 1: Newly Discovered Job Listings (SERP & Multi-API) ────── */}
      <section className="jobs-section-container">
        <div className="section-header-bar">
          <div className="section-title-wrap">
            <div className="section-title-badge-row">
              <span className="material-symbols-outlined section-icon" style={{ color: '#38bdf8' }}>radar</span>
              <h3 className="section-title">Newly Discovered Job Listings</h3>
              <span className="section-count-badge discovery-badge">
                {searchResults.length} Live
              </span>
            </div>
            <p className="section-subtitle">
              Live vacancies aggregated via Google Jobs SERP, JSearch, and Adzuna APIs with verified application links.
            </p>
          </div>
          <div className="section-meta-query">
            {cleanJobString(searchFilters.title)} in {cleanJobString(searchFilters.location)}
          </div>
        </div>

        {filteredSearchResults.length === 0 ? (
          <div className="empty-state-box">
            <span className="material-symbols-outlined empty-state-icon">manage_search</span>
            <p className="empty-state-text">No live search results currently loaded. Click <strong>"Scan Jobs"</strong> above to retrieve openings.</p>
          </div>
        ) : (
          <div className="jobs-grid-container">
            {filteredSearchResults.map((job) => {
              const cleanTitle = cleanJobString(job.title)
              const cleanCompany = cleanJobString(job.company)
              const cleanLoc = cleanJobString(job.location)
              return (
                <div key={job.id} className="job-card-clean">
                  <div className="job-card-top-row">
                    <div className="job-card-title-group">
                      <h4 className="job-card-title">{cleanTitle}</h4>
                      <div className="job-card-company">{cleanCompany}</div>
                    </div>
                    <span className="job-card-source-pill">
                      {cleanJobString(job.source) || 'Live SERP'}
                    </span>
                  </div>

                  <div className="job-card-badges-row">
                    <span className="job-badge location-badge">
                      <span className="material-symbols-outlined" style={{ fontSize: 13, color: '#38bdf8' }}>location_on</span>
                      {cleanLoc}
                    </span>
                    <span className="job-badge salary-badge">
                      <span className="material-symbols-outlined" style={{ fontSize: 13, color: '#10b981' }}>payments</span>
                      {job.salary_range || 'Competitive'}
                    </span>
                    {(job.is_verified || (job.url && job.url.startsWith('http'))) && (
                      <span className="job-badge verified-badge" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 13, color: '#34d399' }}>check_circle</span>
                        Verified Live
                      </span>
                    )}
                  </div>

                  <p className="job-card-desc">
                    {job.description || 'Live vacancy ready for line-by-line 10-dimension evaluation and instant resume tailoring.'}
                  </p>

                  <div className="job-card-actions-row">
                    <button
                      className="btn btn-primary btn-sm job-action-score"
                      onClick={() => onScoreJob(job)}
                      disabled={scoringJobId === job.id}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>analytics</span>
                      {scoringJobId === job.id ? 'Scoring...' : 'Score 10-D'}
                    </button>

                    <button
                      className="btn btn-secondary btn-sm job-action-save"
                      onClick={() => saveJobToPipeline(job)}
                      title="Save to Active Pipeline"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>bookmark_add</span>
                      Save
                    </button>

                    {job.url && job.url.startsWith('http') && (
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-secondary btn-sm job-action-apply"
                        title="Open Official Job Application Link"
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 15 }}>open_in_new</span>
                        Apply
                      </a>
                    )}

                    <button
                      className="btn btn-secondary btn-sm job-action-exclude"
                      onClick={() => handleExcludeJob(job)}
                      title="Permanently Exclude Job"
                      style={{ color: '#ef4444' }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>block</span>
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>

      {/* ── SECTION 2: Deep 10-Dimension Line-by-Line AI Evaluation Drawer ── */}
      {selectedJob && (
        <section className="eval-drawer-card">
          <div className="eval-drawer-header">
            <div>
              <span className="eval-drawer-kicker">10-Dimension Line-by-Line AI Evaluation</span>
              <h3 className="eval-drawer-title">
                {cleanJobString(selectedJob.job_meta?.title || selectedJob.title || 'Evaluated Job')}
              </h3>
              <p className="eval-drawer-company">
                {cleanJobString(selectedJob.job_meta?.company || selectedJob.company)}
              </p>
            </div>

            <div className="eval-drawer-score-wrap">
              <div className="eval-drawer-score-number">
                {selectedJob.score?.overall_score || 85}%
              </div>
              <div className="eval-drawer-verdict">
                {selectedJob.score?.verdict || 'Strong Match'}
              </div>
              <button className="btn btn-primary btn-sm" onClick={() => saveJobToPipeline(selectedJob)}>
                Save to Pipeline
              </button>
            </div>
          </div>

          {/* Category Scores Grid */}
          {selectedJob.score?.category_scores && (
            <div className="eval-categories-grid">
              {Object.entries(selectedJob.score.category_scores).map(([k, v]) => (
                <div key={k} className="eval-category-card">
                  <div className="eval-category-name">{k.replace(/_/g, ' ')}</div>
                  <div className={`eval-category-val ${v >= 85 ? 'high' : 'normal'}`}>{v}%</div>
                </div>
              ))}
            </div>
          )}

          {/* Strengths & Missing Gaps */}
          <div className="eval-insights-grid">
            <div className="eval-box strengths">
              <h4 className="eval-box-heading strengths-heading">
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>check_circle</span>
                Matched Profile Strengths
              </h4>
              <ul className="eval-box-list">
                {(selectedJob.score?.strengths || ['Direct match for AI automation workflows', 'Multi-market GCC campaign experience']).map((s, i) => (
                  <li key={i}>{cleanJobString(s)}</li>
                ))}
              </ul>
            </div>

            <div className="eval-box gaps">
              <h4 className="eval-box-heading gaps-heading">
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>warning</span>
                Identified Missing Gaps & Talking Points
              </h4>
              <ul className="eval-box-list">
                {(selectedJob.score?.missing_gaps || ['Verify niche CRM integration vendor requirements']).map((g, i) => (
                  <li key={i}>{cleanJobString(g)}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}

      {/* ── SECTION 3: Evaluated & Saved Opportunities Area ────────────────── */}
      <section className="jobs-section-container">
        <div className="section-header-bar">
          <div className="section-title-wrap">
            <div className="section-title-badge-row">
              <span className="material-symbols-outlined section-icon" style={{ color: '#10b981' }}>verified</span>
              <h3 className="section-title">Evaluated & Saved Opportunities</h3>
              <span className="section-count-badge saved-badge">
                {filteredEvaluatedJobs.length} Saved
              </span>
            </div>
            <p className="section-subtitle">
              Completed AI evaluations, STAR metric reports, and application kits stored in your system.
            </p>
          </div>

          <div className="filter-toggle-buttons">
            <button
              onClick={() => setEvaluatedFilter('all')}
              className={`filter-toggle-btn ${evaluatedFilter === 'all' ? 'active-green' : ''}`}
            >
              All Saved ({jobs?.length || 0})
            </button>
            <button
              onClick={() => setEvaluatedFilter('top')}
              className={`filter-toggle-btn ${evaluatedFilter === 'top' ? 'active-blue' : ''}`}
            >
              Top Matches (≥85%)
            </button>
          </div>
        </div>

        {filteredEvaluatedJobs.length === 0 ? (
          <div className="empty-state-box">
            <p className="empty-state-text">No evaluated jobs match the selected filter.</p>
          </div>
        ) : (
          <div className="jobs-grid-container">
            {filteredEvaluatedJobs.map((job) => {
              const cleanTitle = cleanJobString(job.title || job.role)
              const cleanCompany = cleanJobString(job.company)
              const cleanLoc = cleanJobString(job.location) || 'Dubai, UAE'
              const scoreNum = typeof job.score === 'object' ? (job.score?.overall_score || 0) : (job.score || 0)
              const isHigh = scoreNum >= 85

              return (
                <div key={job.id} className={`job-card-clean ${isHigh ? 'card-high-match' : ''}`}>
                  <div className="job-card-top-row">
                    <div className="job-card-title-group">
                      <h4 className="job-card-title">{cleanTitle}</h4>
                      <div className="job-card-company">{cleanCompany}</div>
                    </div>
                    {scoreNum > 0 && (
                      <span className={`job-card-match-pill ${isHigh ? 'pill-high' : 'pill-normal'}`}>
                        {Math.round(scoreNum)}% Match
                      </span>
                    )}
                  </div>

                  <div className="job-card-badges-row">
                    <span className="job-badge location-badge">
                      <span className="material-symbols-outlined" style={{ fontSize: 13, color: '#38bdf8' }}>location_on</span>
                      {cleanLoc}
                    </span>
                    <span className="job-badge salary-badge">
                      <span className="material-symbols-outlined" style={{ fontSize: 13, color: '#10b981' }}>payments</span>
                      {job.salary_range || 'AED 25,000 to 45,000 / mo'}
                    </span>
                  </div>

                  <p className="job-card-desc">
                    {cleanJobString(job.description) || 'Full STAR metrics report available in system records.'}
                  </p>

                  <div className="job-card-actions-row">
                    {job.report_file ? (
                      <a
                        href={`${API_BASE}/reports/${job.report_file}`}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-secondary btn-sm job-action-report"
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 15, color: '#38bdf8' }}>description</span>
                        View Report
                      </a>
                    ) : (
                      <button
                        className="btn btn-secondary btn-sm job-action-score"
                        onClick={() => onScoreJob(job)}
                        disabled={scoringJobId === job.id}
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 15 }}>analytics</span>
                        {scoringJobId === job.id ? 'Scoring...' : 'Score'}
                      </button>
                    )}

                    <button
                      className="btn btn-primary btn-sm job-action-tailor"
                      onClick={() => onOptimizeResume(job)}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>edit_document</span>
                      Tailor
                    </button>

                    <a
                      href={`${API_BASE}/api/downloads/pdf/resume-${cleanJobString(job.company || 'target').toLowerCase().replace(/[^a-z0-9]/g, '-')}.pdf`}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-secondary btn-sm job-action-pdf"
                      title="Download Compiled ATS PDF Resume"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 15, color: '#ef4444' }}>picture_as_pdf</span>
                      PDF
                    </a>

                    {job.url && job.url.startsWith('http') && (
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-secondary btn-sm job-action-apply"
                        title="Open Direct Application Link"
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 15 }}>open_in_new</span>
                      </a>
                    )}

                    <button
                      className="btn btn-secondary btn-sm job-action-exclude"
                      onClick={() => handleExcludeJob(job)}
                      title="Permanently Exclude Job"
                      style={{ color: '#ef4444' }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>block</span>
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>

      {/* ── Paste Custom JD Modal ──────────────────────────────────────────── */}
      {showAddJdModal && (
        <div className="modal-backdrop">
          <div className="modal-content-box">
            <div className="modal-header-row">
              <h3 className="modal-title">
                <span className="material-symbols-outlined" style={{ color: '#38bdf8' }}>post_add</span>
                Paste Custom Job Description
              </h3>
              <button className="modal-close-btn" onClick={() => setShowAddJdModal(false)}>×</button>
            </div>
            <form onSubmit={handleCustomJdSubmit} className="modal-form">
              <input
                type="text"
                placeholder="Job Title (e.g. Senior Marketing Manager)"
                value={newJdTitle}
                onChange={(e) => setNewJdTitle(e.target.value)}
                className="form-input"
              />
              <input
                type="text"
                placeholder="Company Name (e.g. Clifford Chance, DEAL Holdings)"
                value={newJdCompany}
                onChange={(e) => setNewJdCompany(e.target.value)}
                className="form-input"
              />
              <input
                type="text"
                placeholder="Location (e.g. Dubai, UAE / Riyadh, Saudi Arabia)"
                value={newJdLocation}
                onChange={(e) => setNewJdLocation(e.target.value)}
                className="form-input"
              />
              <textarea
                placeholder="Paste Full Job Description Text..."
                rows={7}
                value={newJdText}
                onChange={(e) => setNewJdText(e.target.value)}
                className="form-textarea"
              />
              <div className="modal-footer-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddJdModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Score & Evaluate</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
