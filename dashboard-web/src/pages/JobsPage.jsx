import React, { useState, useEffect } from 'react'
import ScoreRing from '../components/ScoreRing'
import * as api from '../api-resilient'

const API_BASE = 'http://localhost:5000'

const ROLE_PRESETS = [
  'AI Content & Automation Specialist',
  'AI Strategy & Enablement Lead',
  'Marketing Operations Manager',
  'Senior Marketing Manager – MarTech',
  'Head of Digital Communications',
  'Director / Head of Content Marketing',
  'MENA / Regional Marketing Lead',
  'Digital Marketing Manager',
]

const SORT_OPTIONS = [
  { value: 'score-desc', label: 'Score ↓' },
  { value: 'score-asc', label: 'Score ↑' },
  { value: 'company', label: 'Company A-Z' },
]

// Salary ranges in AED (typical GCC market)
const SALARY_RANGES = [
  { value: 'all', label: 'Any Salary', min: 0, max: 999999 },
  { value: 'entry', label: 'Entry (AED 8k-15k)', min: 8000, max: 15000 },
  { value: 'mid', label: 'Mid-level (AED 15k-30k)', min: 15000, max: 30000 },
  { value: 'senior', label: 'Senior (AED 30k-60k)', min: 30000, max: 60000 },
  { value: 'executive', label: 'Executive (AED 60k+)', min: 60000, max: 999999 },
  { value: 'custom', label: 'Custom Range', min: null, max: null },
]

export default function JobsPage({
  searchResults, jobs, selectedJob, scoringJobId,
  searchFilters, setSearchFilters,
  onSearch, onScoreJob, onOptimizeResume, onApply,
  optimizingJob, optimizeStep, optimizeResult,
  showAddJdModal, setShowAddJdModal,
  addToast
}) {
  const [sortBy, setSortBy] = useState('score-desc')
  const [newJdText, setNewJdText] = useState('')
  const [newJdTitle, setNewJdTitle] = useState('')
  const [newJdCompany, setNewJdCompany] = useState('')
  const [newJdLocation, setNewJdLocation] = useState('')
  const [hasAutoSearched, setHasAutoSearched] = useState(false)
  const [salaryRange, setSalaryRange] = useState('all')
  const [customSalaryMin, setCustomSalaryMin] = useState('')
  const [customSalaryMax, setCustomSalaryMax] = useState('')
  const [displayedSearchResults, setDisplayedSearchResults] = useState([])
  const [displayedJobs, setDisplayedJobs] = useState([])

  // Auto-search on first load to surface profile-matched listings
  useEffect(() => {
    if (!hasAutoSearched && searchResults.length === 0) {
      setHasAutoSearched(true)
      onSearch(searchFilters)
    }
  }, [hasAutoSearched, searchResults.length, onSearch, searchFilters])

  // Sync displayed results with parent
  useEffect(() => {
    setDisplayedSearchResults(searchResults || [])
  }, [searchResults])

  useEffect(() => {
    setDisplayedJobs(jobs || [])
  }, [jobs])

  const getScoreColorClass = (score) => {
    if (score >= 70) return 'high'
    if (score >= 45) return 'medium'
    return 'low'
  }

  const handleAddCustomJd = (e) => {
    e.preventDefault()
    if (!newJdText || !newJdTitle || !newJdCompany) {
      addToast('Please fill out all fields', 'warning')
      return
    }
    const mockJob = {
      id: `custom-${Date.now()}`,
      title: newJdTitle,
      company: newJdCompany,
      location: newJdLocation || 'Remote',
      description: newJdText,
      url: 'Custom Paste'
    }
    setShowAddJdModal(false)
    onScoreJob(mockJob)
    setNewJdText('')
    setNewJdTitle('')
    setNewJdCompany('')
    setNewJdLocation('')
  }

  const handleSearch = (e) => {
    if (e) e.preventDefault()
    
    // Build salary filter based on selected range
    let filters = { ...searchFilters }
    const selectedRange = SALARY_RANGES.find(r => r.value === salaryRange)
    
    if (salaryRange === 'custom') {
      filters.salary_min = customSalaryMin ? parseInt(customSalaryMin) : null
      filters.salary_max = customSalaryMax ? parseInt(customSalaryMax) : null
    } else if (selectedRange) {
      filters.salary_min = selectedRange.min
      filters.salary_max = selectedRange.max
    }
    
    onSearch(filters)
  }

  const handleDeleteSearchResult = async (jobId) => {
    if (!window.confirm('Remove this listing from search results?')) return
    try {
      await api.deleteJob(jobId)
      setDisplayedSearchResults((prev) => prev.filter((j) => j.id !== jobId))
      addToast('Listing removed', 'success')
    } catch (err) {
      addToast('Failed to remove listing', 'error')
    }
  }

  const handleDeleteScoredJob = async (jobId) => {
    if (!window.confirm('Remove this evaluation and report?')) return
    try {
      await api.deleteJob(jobId)
      setDisplayedJobs((prev) => prev.filter((j) => j.id !== jobId))
      addToast('Evaluation removed', 'success')
    } catch (err) {
      addToast('Failed to remove evaluation', 'error')
    }
  }

  const sortedJobs = [...displayedJobs].sort((a, b) => {
    if (sortBy === 'score-desc') return (b.score || 0) - (a.score || 0)
    if (sortBy === 'score-asc') return (a.score || 0) - (b.score || 0)
    return (a.company || '').localeCompare(b.company || '')
  })

  return (
    <div className="page-content" id="jobs-page">
      {/* Search Panel */}
      <div className="search-panel">
        <h2>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-primary-light)' }}>search</span>
          Scan Portals & Find Jobs
        </h2>

        {/* Role Presets */}
        <div className="role-presets">
          {ROLE_PRESETS.map((role) => (
            <button
              key={role}
              className={`role-preset-chip ${searchFilters.title === role ? 'active' : ''}`}
              onClick={() => setSearchFilters({ ...searchFilters, title: role })}
            >
              {role}
            </button>
          ))}
        </div>

        <form onSubmit={handleSearch} className="search-grid">
          <div className="form-group">
            <label className="form-label">Target Role Title</label>
            <input
              type="text"
              className="form-input"
              value={searchFilters.title}
              onChange={(e) => setSearchFilters({ ...searchFilters, title: e.target.value })}
              placeholder="e.g. Marketing Manager"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Location</label>
            <input
              type="text"
              className="form-input"
              value={searchFilters.location}
              onChange={(e) => setSearchFilters({ ...searchFilters, location: e.target.value })}
              placeholder="e.g. Dubai, UAE"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Monthly Salary Range</label>
            <select
              className="form-select"
              value={salaryRange}
              onChange={(e) => setSalaryRange(e.target.value)}
            >
              {SALARY_RANGES.map((range) => (
                <option key={range.value} value={range.value}>{range.label}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Currency</label>
            <select
              className="form-select"
              value={searchFilters.currency}
              onChange={(e) => setSearchFilters({ ...searchFilters, currency: e.target.value })}
            >
              <option value="AED">AED (Dirham)</option>
              <option value="USD">USD (Dollar)</option>
              <option value="QAR">QAR (Riyal)</option>
              <option value="SAR">SAR (Riyal)</option>
              <option value="INR">INR (Rupee)</option>
            </select>
          </div>
          {salaryRange === 'custom' && (
            <>
              <div className="form-group">
                <label className="form-label">Min Monthly Salary</label>
                <input
                  type="number"
                  className="form-input"
                  value={customSalaryMin}
                  onChange={(e) => setCustomSalaryMin(e.target.value)}
                  placeholder="e.g. 15000"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Max Monthly Salary</label>
                <input
                  type="number"
                  className="form-input"
                  value={customSalaryMax}
                  onChange={(e) => setCustomSalaryMax(e.target.value)}
                  placeholder="e.g. 50000"
                />
              </div>
            </>
          )}
          <button type="submit" className="btn btn-primary" style={{ alignSelf: 'end' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>search</span>
            Search
          </button>
        </form>
      </div>

      {/* Search Results */}
      <div className="jobs-section">
        <div className="section-header">
          <h3 className="section-title">
            <span className="material-symbols-outlined" style={{ color: 'var(--accent-secondary)' }}>explore</span>
            Search Results & Recommendations
          </h3>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            {displayedSearchResults.length > 0 && (
              <span className="section-count">{displayedSearchResults.length} Listings</span>
            )}
            <button className="btn btn-secondary btn-sm" onClick={() => setShowAddJdModal(true)}>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>add</span>
              Paste JD
            </button>
          </div>
        </div>

        {displayedSearchResults.length === 0 ? (
          <div className="empty-state" style={{ border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-lg)' }}>
            <span className="material-symbols-outlined icon">travel_explore</span>
            <h3>No active search results</h3>
            <p>Enter your target keywords above and click search, or paste a custom job description.</p>
          </div>
        ) : (
          <div className="jobs-grid">
            {displayedSearchResults.map((job) => (
              <div key={job.id} className="job-card">
                <div className="job-card-header">
                  <div style={{ flex: 1 }}>
                    <div className="job-card-title">{job.title}</div>
                    <div className="job-card-company">{job.company}</div>
                  </div>
                  <button
                    className="btn btn-icon"
                    onClick={() => handleDeleteSearchResult(job.id)}
                    title="Remove this listing"
                    style={{ padding: 6, minWidth: 'auto', background: 'var(--bg-hover)', border: 'none', cursor: 'pointer' }}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 18, color: 'var(--text-muted)' }}>remove</span>
                  </button>
                </div>
                <div className="job-card-meta">
                  <span className="meta-tag location">
                    <span className="material-symbols-outlined" style={{ fontSize: 12 }}>location_on</span>
                    {job.location}
                  </span>
                  <span className="meta-tag salary">
                    <span className="material-symbols-outlined" style={{ fontSize: 12 }}>payments</span>
                    {job.salary_range}
                  </span>
                  <span className="meta-tag source">
                    <span className="material-symbols-outlined" style={{ fontSize: 12 }}>link</span>
                    {job.source}
                  </span>
                  {job.posted && (
                    <span className="meta-tag posted">
                      <span className="material-symbols-outlined" style={{ fontSize: 12 }}>schedule</span>
                      {job.posted}
                    </span>
                  )}
                </div>
                <div className="job-card-desc">{job.description}</div>
                <div className="job-card-actions">
                  <button
                    className="btn btn-primary btn-sm"
                    disabled={scoringJobId !== null}
                    onClick={() => onScoreJob(job)}
                  >
                    {scoringJobId === job.id ? (
                      <><span className="spinner" /> Scoring...</>
                    ) : (
                      <><span className="material-symbols-outlined" style={{ fontSize: 16 }}>insights</span> Score Match</>
                    )}
                  </button>
                  <button className="btn btn-secondary btn-sm" onClick={() => onApply(job.url)}>
                    <span className="material-symbols-outlined" style={{ fontSize: 16 }}>open_in_new</span> Apply
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Scored Reports & Pipeline History */}
      <div className="jobs-section">
        <div className="section-header">
          <h3 className="section-title">
            <span className="material-symbols-outlined" style={{ color: 'var(--accent-primary-light)' }}>history</span>
            Scored Reports & History
          </h3>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span className="section-count">{sortedJobs.length} Items</span>
            <select
              className="form-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={{ padding: '6px 28px 6px 10px', fontSize: 11 }}
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>

        {sortedJobs.length === 0 ? (
          <div className="empty-state" style={{ border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-lg)' }}>
            <span className="material-symbols-outlined icon">assessment</span>
            <h3>No records found</h3>
            <p>Start by scoring a job listing to compile your target dashboard data.</p>
          </div>
        ) : (
          <div className="jobs-grid">
            {sortedJobs.map((job) => (
              <div key={job.id} className="job-card">
                <div className="job-card-header">
                  <div style={{ flex: 1 }}>
                    <div className="job-card-title">{job.role || job.title}</div>
                    <div className="job-card-company">{job.company}</div>
                  </div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    {job.score != null && <ScoreRing score={job.score} />}
                    <button
                      className="btn btn-icon"
                      onClick={() => handleDeleteScoredJob(job.id)}
                      title="Remove this evaluation"
                      style={{ padding: 6, minWidth: 'auto', background: 'var(--bg-hover)', border: 'none', cursor: 'pointer' }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 18, color: 'var(--text-muted)' }}>close</span>
                    </button>
                  </div>
                </div>
                <div className="job-card-meta">
                  <span className="meta-tag location">
                    <span className="material-symbols-outlined" style={{ fontSize: 12 }}>check_circle</span>
                    Scored
                  </span>
                  <span className="meta-tag source">
                    <span className="material-symbols-outlined" style={{ fontSize: 12 }}>description</span>
                    {job.report_file || job.jd_file}
                  </span>
                </div>
                <div className="job-card-desc">
                  {job.jd_content || 'No snapshot description stored. View full report for complete STAR metrics.'}
                </div>
                <div className="job-card-actions">
                  <button className="btn btn-success btn-sm" onClick={() => onOptimizeResume(job)}>
                    <span className="material-symbols-outlined" style={{ fontSize: 16 }}>description</span> Tailor Resume
                  </button>
                  {job.report_file && (
                    <a
                      href={`${API_BASE}/reports/${job.report_file}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary btn-sm"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 16 }}>visibility</span> Report
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected Job Score Detail */}
      {selectedJob && (
        <div className="score-detail" id="score-detail-panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
            <div>
              <h3 style={{ fontSize: 18, fontWeight: 700 }}>{selectedJob.job_meta?.title || 'Job Score Breakdown'}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{selectedJob.job_meta?.company}</p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <ScoreRing score={selectedJob.score?.overall_score} size={72} />
              <span className={`rec-badge ${selectedJob.score?.recommendation}`}>
                {selectedJob.score?.recommendation}
              </span>
            </div>
          </div>

          <div className="score-categories">
            {selectedJob.score?.category_scores && Object.entries(selectedJob.score.category_scores).map(([key, val]) => (
              <div key={key} className="score-cat">
                <div className="score-cat-label">{key.replace(/_/g, ' ')}</div>
                <div className="score-bar">
                  <div className={`score-bar-fill ${getScoreColorClass(val)}`} style={{ width: `${val}%` }} />
                </div>
                <div className="score-cat-value" style={{ color: `var(--accent-${getScoreColorClass(val) === 'high' ? 'success' : getScoreColorClass(val) === 'medium' ? 'warning' : 'danger'})` }}>
                  {val}%
                </div>
              </div>
            ))}
          </div>

          <div className="score-insights" style={{ marginTop: 20 }}>
            <div className="insight-col strengths">
              <h4>Key Strengths</h4>
              {selectedJob.score?.strengths?.map((str, idx) => (
                <div key={idx} className="insight-item">
                  <span className="dot" />
                  <span>{str}</span>
                </div>
              ))}
            </div>
            <div className="insight-col gaps">
              <h4>Identified Gaps</h4>
              {selectedJob.score?.gaps?.map((gap, idx) => (
                <div key={idx} className="insight-item">
                  <span className="dot" />
                  <span>{gap}</span>
                </div>
              ))}
            </div>
          </div>

          {selectedJob.score?.summary && (
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 16, marginTop: 20 }}>
              <h4 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>Match Executive Summary</h4>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{selectedJob.score.summary}</p>
            </div>
          )}
        </div>
      )}

      {/* Optimization Panel */}
      {optimizingJob && (
        <div className="optimize-panel">
          <h3 style={{ fontSize: 16, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="material-symbols-outlined" style={{ color: 'var(--accent-secondary)' }}>settings_suggest</span>
            Optimization Pipeline
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>
            Tailoring resume for {optimizingJob.role || optimizingJob.title} at {optimizingJob.company}
          </p>
          <div className="optimize-steps">
            {[
              { step: 1, name: 'ag-tailor (Kimi AI Engine)', desc: 'Rewriting bullet points and skills alignment', icon: 'edit_note' },
              { step: 2, name: 'ag-latex (Qwen Max LaTeX Engine)', desc: 'Generating customized LaTeX template', icon: 'code' },
              { step: 3, name: 'PDF Engine Compiler', desc: 'Compiling customized resume to outputs', icon: 'picture_as_pdf' },
            ].map(({ step, name, desc, icon }) => (
              <div key={step} className={`opt-step ${optimizeStep === step ? 'running' : optimizeStep > step ? 'done' : 'pending'}`}>
                <div className="opt-step-icon">
                  {optimizeStep === step ? <span className="spinner" /> : <span className="material-symbols-outlined">{icon}</span>}
                </div>
                <div className="opt-step-text">
                  <div className="opt-step-name">{name}</div>
                  <div className="opt-step-desc">{desc}</div>
                </div>
                <div className="opt-step-status">
                  {optimizeStep === step ? 'RUNNING' : optimizeStep > step ? 'DONE' : 'PENDING'}
                </div>
              </div>
            ))}
          </div>
          {optimizeResult && (
            <div style={{ marginTop: 20, borderTop: '1px solid var(--border-subtle)', paddingTop: 16 }} className="animate-fade-in">
              <h4 style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Generated Output PDF</h4>
              <p style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{optimizeResult.latex?.pdf_path}</p>
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <a href={`${API_BASE}/output/tailored_resume.tex`} download className="btn btn-secondary btn-sm" style={{ flex: 1 }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>download</span> Download LaTeX
                </a>
                <button className="btn btn-primary btn-sm" style={{ flex: 1 }} onClick={() => addToast('Opening PDF preview', 'info')}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>visibility</span> Preview
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Add JD Modal */}
      {showAddJdModal && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ position: 'relative' }}>
            <button className="modal-close" onClick={() => setShowAddJdModal(false)}>×</button>
            <h3 className="modal-title">Evaluate Job Description</h3>
            <form onSubmit={handleAddCustomJd} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div className="form-group">
                  <label className="form-label">Role Title</label>
                  <input type="text" className="form-input" value={newJdTitle} onChange={(e) => setNewJdTitle(e.target.value)} placeholder="e.g. Marketing Manager" required />
                </div>
                <div className="form-group">
                  <label className="form-label">Company</label>
                  <input type="text" className="form-input" value={newJdCompany} onChange={(e) => setNewJdCompany(e.target.value)} placeholder="e.g. Careem" required />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Location</label>
                <input type="text" className="form-input" value={newJdLocation} onChange={(e) => setNewJdLocation(e.target.value)} placeholder="e.g. Dubai, UAE (or Remote)" />
              </div>
              <div className="form-group">
                <label className="form-label">Paste Job Description Text</label>
                <textarea className="form-input" style={{ minHeight: 200 }} value={newJdText} onChange={(e) => setNewJdText(e.target.value)} placeholder="Paste the full job requirements, description, and compensation details here..." required />
              </div>
              <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', paddingTop: 8 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddJdModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Score Listing</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
