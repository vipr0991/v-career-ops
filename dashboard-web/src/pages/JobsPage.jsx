import React, { useState, useEffect } from 'react'
import ScoreRing from '../components/ScoreRing'
import * as api from '../api-resilient'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

const ROLE_PRESETS = [
  'Senior Marketing Manager',
  'AI Content & Automation Specialist',
  'AI Strategy & Enablement Lead',
  'Marketing Operations Manager',
  'Senior Marketing Manager – MarTech',
  'Head of Digital Marketing',
  'Director / Head of Content Marketing',
  'MENA / Regional Marketing Lead',
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
      title: newJdTitle,
      company: newJdCompany,
      location: newJdLocation || 'Dubai, UAE',
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
          title: job.title || job.role || 'Target Role',
          company: job.company || 'Enterprise',
          location: job.location || searchFilters.location || 'Dubai, UAE',
          salary_range: job.salary_range || 'Not Disclosed',
          url: job.url || '',
          source: job.source || 'SERP Search Discovery',
          description: job.description || job.jd_content || '',
          score: scoreVal,
          stage: 'pipeline_saved'
        })
      })
      if (res.ok) {
        addToast(`Saved ${job.company} to Pipeline!`, 'success')
      } else {
        addToast('Could not save to pipeline', 'error')
      }
    } catch {
      addToast('Network error while saving to pipeline', 'error')
    }
  }

  const filteredEvaluatedJobs = (jobs || []).filter(j => {
    if (evaluatedFilter === 'top') {
      const s = typeof j.score === 'object' ? (j.score?.overall_score || 0) : (j.score || 0)
      return s >= 85
    }
    return true
  })

  return (
    <div className="page-content" id="jobs-page" style={{ maxWidth: 1400, margin: '0 auto', padding: '24px 16px' }}>
      
      {/* ── Search & Location Control Panel ────────────────────────────────── */}
      <div className="search-panel" style={{ background: 'rgba(30, 41, 59, 0.75)', backdropFilter: 'blur(12px)', padding: 24, borderRadius: 14, border: '1px solid rgba(255,255,255,0.08)', marginBottom: 28, boxShadow: '0 8px 32px rgba(0,0,0,0.2)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 20, margin: 0, color: '#fff', fontWeight: 700 }}>
            <span className="material-symbols-outlined" style={{ color: '#38bdf8' }}>travel_explore</span>
            Multi-Location Job Discovery & Live SERP Scanner
          </h2>
          <span style={{ fontSize: 12, color: '#38bdf8', background: 'rgba(56, 189, 248, 0.12)', padding: '4px 12px', borderRadius: 20, border: '1px solid rgba(56, 189, 248, 0.25)', fontWeight: 600 }}>
            Middle East (GCC) & Bangalore
          </span>
        </div>

        {/* Role Presets */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
          {ROLE_PRESETS.map((role) => (
            <button
              key={role}
              style={{
                padding: '6px 14px',
                borderRadius: 20,
                border: searchFilters.title === role ? '1px solid #38bdf8' : '1px solid rgba(255,255,255,0.08)',
                background: searchFilters.title === role ? 'rgba(56, 189, 248, 0.18)' : 'rgba(255,255,255,0.03)',
                color: searchFilters.title === role ? '#fff' : 'var(--text-secondary)',
                fontSize: 12,
                fontWeight: searchFilters.title === role ? 600 : 400,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onClick={() => setSearchFilters({ ...searchFilters, title: role })}
            >
              {role}
            </button>
          ))}
        </div>

        {/* Location Presets */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20 }}>
          {LOCATION_PRESETS.map((loc) => {
            const isMatch = searchFilters.location === loc.value
            return (
              <button
                key={loc.value}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  padding: '6px 12px',
                  borderRadius: 20,
                  border: isMatch ? '1px solid #10b981' : '1px solid rgba(255,255,255,0.08)',
                  background: isMatch ? 'rgba(16, 185, 129, 0.18)' : 'rgba(255,255,255,0.03)',
                  color: isMatch ? '#fff' : 'var(--text-secondary)',
                  fontSize: 12,
                  fontWeight: isMatch ? 600 : 400,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onClick={() => setSearchFilters({ ...searchFilters, location: loc.value })}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 14, color: isMatch ? '#10b981' : 'var(--text-secondary)' }}>location_on</span>
                {loc.label}
              </button>
            )
          })}
        </div>

        {/* Search Form Inputs */}
        <form onSubmit={(e) => { e.preventDefault(); onSearch(searchFilters) }} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, alignItems: 'flex-end' }}>
          <div>
            <label style={{ display: 'block', fontSize: 12, marginBottom: 6, color: 'var(--text-secondary)', fontWeight: 500 }}>Target Role Title</label>
            <input
              type="text"
              value={searchFilters.title}
              onChange={(e) => setSearchFilters({ ...searchFilters, title: e.target.value })}
              placeholder="e.g. Senior Marketing Manager"
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#0f172a', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', fontSize: 13, boxSizing: 'border-box' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, marginBottom: 6, color: 'var(--text-secondary)', fontWeight: 500 }}>Location (Drop-down)</label>
            <select
              value={searchFilters.location || 'Dubai, UAE'}
              onChange={(e) => setSearchFilters({ ...searchFilters, location: e.target.value })}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#0f172a', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', fontSize: 13, boxSizing: 'border-box', appearance: 'none' }}
            >
              {LOCATION_PRESETS.map(loc => <option key={loc.value} value={loc.value}>{loc.label}</option>)}
            </select>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', fontSize: 12, marginBottom: 6, color: 'var(--text-secondary)', fontWeight: 500 }}>Currency</label>
              <select
                value={searchFilters.currency || 'AED'}
                onChange={(e) => setSearchFilters({ ...searchFilters, currency: e.target.value })}
                style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#0f172a', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', fontSize: 13, boxSizing: 'border-box', appearance: 'none' }}
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
            <div style={{ flex: 1.5 }}>
              <label style={{ display: 'block', fontSize: 12, marginBottom: 6, color: 'var(--text-secondary)', fontWeight: 500 }}>Salary Range</label>
              <select
                value={searchFilters.salary || 'Any'}
                onChange={(e) => setSearchFilters({ ...searchFilters, salary: e.target.value })}
                style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#0f172a', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', fontSize: 13, boxSizing: 'border-box', appearance: 'none' }}
              >
                <option value="Any">Any Salary</option>
                <option value="20k-30k">20k - 30k</option>
                <option value="30k-40k">30k - 40k</option>
                <option value="40k-50k">40k - 50k</option>
                <option value="50k+">50k+</option>
              </select>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button type="submit" className="btn btn-primary" style={{ flex: 1, padding: '10px 16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, fontWeight: 600 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>search</span>
              Scan Jobs
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => setShowAddJdModal(true)} style={{ padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 6 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>post_add</span>
              Paste JD
            </button>
          </div>
        </form>
      </div>

      {/* ── SECTION 1: Newly Discovered Job Listings (SERP & Multi-API) ────── */}
      <section style={{ marginBottom: 36 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18, flexWrap: 'wrap', gap: 10 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="material-symbols-outlined" style={{ color: '#38bdf8', fontSize: 22 }}>radar</span>
              <h3 style={{ margin: 0, fontSize: 18, color: '#fff', fontWeight: 700 }}>
                Newly Discovered Job Listings (SERP & Multi-API)
              </h3>
              <span style={{ fontSize: 12, background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', padding: '2px 8px', borderRadius: 12, fontWeight: 700 }}>
                {searchResults.length} Live Results
              </span>
            </div>
            <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--text-secondary)' }}>
              Real-time vacancies retrieved via Google Jobs SERP, JSearch, and Adzuna APIs with direct sendable links.
            </p>
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            Active Query: <strong style={{ color: '#fff' }}>{searchFilters.title}</strong> · <strong style={{ color: '#fff' }}>{searchFilters.location}</strong>
          </div>
        </div>

        {searchResults.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', background: 'rgba(30, 41, 59, 0.4)', borderRadius: 12, border: '1px dashed rgba(255,255,255,0.1)' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 36, color: 'var(--text-secondary)' }}>manage_search</span>
            <p style={{ margin: '8px 0 0', color: 'var(--text-secondary)', fontSize: 13 }}>No search results loaded yet. Click <strong>"Scan Jobs"</strong> above to discover live postings.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 16 }}>
            {searchResults.map((job) => (
              <div
                key={job.id}
                style={{
                  background: 'rgba(30, 41, 59, 0.7)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: 12,
                  padding: 18,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 12,
                  transition: 'transform 0.2s, border-color 0.2s',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                  <div>
                    <h4 style={{ margin: '0 0 4px', fontSize: 15, fontWeight: 700, color: '#fff', lineHeight: 1.3 }}>{job.title}</h4>
                    <div style={{ fontSize: 13, color: '#38bdf8', fontWeight: 600 }}>{job.company}</div>
                  </div>
                  <span style={{ fontSize: 10.5, background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', padding: '3px 8px', borderRadius: 6, whiteSpace: 'nowrap', border: '1px solid rgba(255,255,255,0.05)' }}>
                    {job.source || 'Live Search'}
                  </span>
                </div>

                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', fontSize: 12, color: 'var(--text-secondary)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(255,255,255,0.04)', padding: '3px 8px', borderRadius: 6, border: '1px solid rgba(255,255,255,0.04)' }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 13, color: '#38bdf8' }}>location_on</span>
                    {job.location}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(255,255,255,0.04)', padding: '3px 8px', borderRadius: 6, border: '1px solid rgba(255,255,255,0.04)' }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 13, color: '#10b981' }}>payments</span>
                    {job.salary_range}
                  </span>
                </div>

                <p style={{ margin: 0, fontSize: 12, color: '#94a3b8', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {job.description || 'No snapshot description stored. Direct application and evaluation available.'}
                </p>

                <div style={{ display: 'flex', gap: 8, marginTop: 'auto', paddingTop: 10, borderTop: '1px solid rgba(255,255,255,0.06)', alignItems: 'center' }}>
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => onScoreJob(job)}
                    disabled={scoringJobId === job.id}
                    style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5, fontSize: 12, fontWeight: 600 }}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 15 }}>analytics</span>
                    {scoringJobId === job.id ? 'Evaluating...' : 'Score 10-D'}
                  </button>

                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => saveJobToPipeline(job)}
                    style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12 }}
                    title="Save to Pipeline"
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 15 }}>bookmark_add</span>
                    Save
                  </button>

                  {job.url && job.url.startsWith('http') && (
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-secondary btn-sm"
                      style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, padding: '6px 10px' }}
                      title="Open Direct Apply Link"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>open_in_new</span>
                      Apply
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* ── SECTION 2: Deep 10-Dimension Line-by-Line AI Evaluation Drawer ── */}
      {selectedJob && (
        <section style={{ background: '#0f172a', border: '1px solid rgba(56, 189, 248, 0.35)', borderRadius: 16, padding: 24, marginBottom: 36, boxShadow: '0 8px 32px rgba(56, 189, 248, 0.08)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 20 }}>
            <div>
              <span style={{ fontSize: 11, color: '#38bdf8', textTransform: 'uppercase', letterSpacing: 1.2, fontWeight: 700 }}>
                10-Dimension Line-by-Line AI Evaluation
              </span>
              <h3 style={{ margin: '4px 0', fontSize: 20, color: '#fff', fontWeight: 700 }}>
                {selectedJob.job_meta?.title || selectedJob.title || 'Evaluated Job'}
              </h3>
              <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: 13 }}>
                {selectedJob.job_meta?.company || selectedJob.company} • {selectedJob.source_agent || 'Career-Ops Evaluator'}
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 28, fontWeight: 'bold', color: '#10b981' }}>
                  {selectedJob.score?.overall_score || 85}%
                </div>
                <div style={{ fontSize: 12, color: '#38bdf8', fontWeight: 600 }}>
                  {selectedJob.score?.verdict || 'Strong Match'}
                </div>
              </div>
              <button className="btn btn-primary" onClick={() => saveJobToPipeline(selectedJob)}>
                Save to Pipeline
              </button>
            </div>
          </div>

          {/* Category Scores Grid */}
          {selectedJob.score?.category_scores && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 10, marginBottom: 20 }}>
              {Object.entries(selectedJob.score.category_scores).map(([k, v]) => (
                <div key={k} style={{ background: 'rgba(255,255,255,0.03)', padding: 10, borderRadius: 8, border: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                    {k.replace(/_/g, ' ')}
                  </div>
                  <div style={{ fontSize: 16, fontWeight: 'bold', color: v >= 85 ? '#10b981' : '#38bdf8' }}>
                    {v}%
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Strengths & Missing Gaps */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 16, marginBottom: 16 }}>
            <div style={{ background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: 16, borderRadius: 10 }}>
              <h4 style={{ margin: '0 0 8px', fontSize: 14, color: '#34d399', display: 'flex', alignItems: 'center', gap: 6 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>check_circle</span>
                Matched Profile Strengths
              </h4>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: '#e2e8f0', lineHeight: 1.6 }}>
                {(selectedJob.score?.strengths || ['Direct match for AI automation workflows', 'Multi-market GCC campaign experience']).map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>

            <div style={{ background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.2)', padding: 16, borderRadius: 10 }}>
              <h4 style={{ margin: '0 0 8px', fontSize: 14, color: '#fbbf24', display: 'flex', alignItems: 'center', gap: 6 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>warning</span>
                Identified Missing Gaps & Bridge Talking Points
              </h4>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: '#e2e8f0', lineHeight: 1.6 }}>
                {(selectedJob.score?.missing_gaps || ['Verify niche CRM integration vendor requirements']).map((g, i) => (
                  <li key={i}>{g}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}

      {/* ── SECTION 3: Evaluated & Saved Opportunities Area ────────────────── */}
      <section style={{ marginBottom: 36 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="material-symbols-outlined" style={{ color: '#10b981', fontSize: 22 }}>verified</span>
              <h3 style={{ margin: 0, fontSize: 18, color: '#fff', fontWeight: 700 }}>
                Evaluated & Saved Opportunities
              </h3>
              <span style={{ fontSize: 12, background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', padding: '2px 8px', borderRadius: 12, fontWeight: 700 }}>
                {filteredEvaluatedJobs.length} Saved Roles
              </span>
            </div>
            <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--text-secondary)' }}>
              Completed AI evaluations, STAR metric reports, and application kits stored in your Career-Ops system.
            </p>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={() => setEvaluatedFilter('all')}
              style={{
                padding: '6px 12px',
                borderRadius: 16,
                border: evaluatedFilter === 'all' ? '1px solid #10b981' : '1px solid rgba(255,255,255,0.08)',
                background: evaluatedFilter === 'all' ? 'rgba(16, 185, 129, 0.15)' : 'transparent',
                color: evaluatedFilter === 'all' ? '#fff' : 'var(--text-secondary)',
                fontSize: 12,
                cursor: 'pointer'
              }}
            >
              All Saved ({jobs?.length || 0})
            </button>
            <button
              onClick={() => setEvaluatedFilter('top')}
              style={{
                padding: '6px 12px',
                borderRadius: 16,
                border: evaluatedFilter === 'top' ? '1px solid #38bdf8' : '1px solid rgba(255,255,255,0.08)',
                background: evaluatedFilter === 'top' ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                color: evaluatedFilter === 'top' ? '#fff' : 'var(--text-secondary)',
                fontSize: 12,
                cursor: 'pointer'
              }}
            >
              Top Matches (≥85%)
            </button>
          </div>
        </div>

        {filteredEvaluatedJobs.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', background: 'rgba(30, 41, 59, 0.4)', borderRadius: 12, border: '1px dashed rgba(255,255,255,0.1)' }}>
            <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: 13 }}>No evaluated jobs match the selected filter.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 16 }}>
            {filteredEvaluatedJobs.map((job) => {
              const scoreNum = typeof job.score === 'object' ? (job.score?.overall_score || 0) : (job.score || 0)
              const isHigh = scoreNum >= 85
              return (
                <div
                  key={job.id}
                  style={{
                    background: 'rgba(30, 41, 59, 0.7)',
                    backdropFilter: 'blur(10px)',
                    border: isHigh ? '1px solid rgba(16, 185, 129, 0.25)' : '1px solid rgba(255,255,255,0.08)',
                    borderRadius: 12,
                    padding: 18,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 12,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                    <div>
                      <h4 style={{ margin: '0 0 4px', fontSize: 15, fontWeight: 700, color: '#fff', lineHeight: 1.3 }}>
                        {job.title || job.role}
                      </h4>
                      <div style={{ fontSize: 13, color: '#38bdf8', fontWeight: 600 }}>{job.company}</div>
                    </div>
                    {scoreNum > 0 && (
                      <div style={{
                        fontSize: 13,
                        fontWeight: 700,
                        color: isHigh ? '#10b981' : '#38bdf8',
                        background: isHigh ? 'rgba(16, 185, 129, 0.15)' : 'rgba(56, 189, 248, 0.15)',
                        border: isHigh ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(56, 189, 248, 0.3)',
                        padding: '3px 8px',
                        borderRadius: 8,
                        whiteSpace: 'nowrap'
                      }}>
                        {Math.round(scoreNum)}% Match
                      </div>
                    )}
                  </div>

                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', fontSize: 12, color: 'var(--text-secondary)' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(255,255,255,0.04)', padding: '3px 8px', borderRadius: 6, border: '1px solid rgba(255,255,255,0.04)' }}>
                      <span className="material-symbols-outlined" style={{ fontSize: 13, color: '#38bdf8' }}>location_on</span>
                      {job.location || 'Dubai, UAE'}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(255,255,255,0.04)', padding: '3px 8px', borderRadius: 6, border: '1px solid rgba(255,255,255,0.04)' }}>
                      <span className="material-symbols-outlined" style={{ fontSize: 13, color: '#10b981' }}>payments</span>
                      {job.salary_range || 'AED 25,000 - 45,000 / month'}
                    </span>
                  </div>

                  <p style={{ margin: 0, fontSize: 12, color: '#94a3b8', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {job.description || 'Full STAR metrics report available in system records.'}
                  </p>

                  <div style={{ display: 'flex', gap: 8, marginTop: 'auto', paddingTop: 10, borderTop: '1px solid rgba(255,255,255,0.06)', alignItems: 'center' }}>
                    {job.report_file ? (
                      <a
                        href={`${API_BASE}/reports/${job.report_file}`}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-secondary btn-sm"
                        style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4, fontSize: 12, textDecoration: 'none' }}
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 15, color: '#38bdf8' }}>description</span>
                        View Report
                      </a>
                    ) : (
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => onScoreJob(job)}
                        disabled={scoringJobId === job.id}
                        style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4, fontSize: 12 }}
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 15 }}>analytics</span>
                        {scoringJobId === job.id ? 'Scoring...' : 'Score'}
                      </button>
                    )}

                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => onOptimizeResume(job)}
                      style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12 }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>edit_document</span>
                      Tailor
                    </button>

                    {job.url && job.url.startsWith('http') && (
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-secondary btn-sm"
                        style={{ display: 'flex', alignItems: 'center', padding: '6px 10px' }}
                        title="Open Direct Apply Link"
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 15 }}>open_in_new</span>
                      </a>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>

      {/* ── Paste Custom JD Modal ──────────────────────────────────────────── */}
      {showAddJdModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.8)', zIndex: 9999, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: 20 }}>
          <div style={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 14, width: '100%', maxWidth: 550, padding: 24, color: '#fff', boxShadow: '0 12px 48px rgba(0,0,0,0.5)' }}>
            <h3 style={{ margin: '0 0 16px', fontSize: 18, color: '#38bdf8', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="material-symbols-outlined">post_add</span>
              Paste Custom Job Description
            </h3>
            <form onSubmit={handleCustomJdSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <input
                type="text"
                placeholder="Job Title (e.g. Senior Marketing Manager)"
                value={newJdTitle}
                onChange={(e) => setNewJdTitle(e.target.value)}
                style={{ padding: '10px 12px', borderRadius: 8, background: '#1e293b', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', fontSize: 13 }}
              />
              <input
                type="text"
                placeholder="Company Name (e.g. Clifford Chance, DEAL Holdings)"
                value={newJdCompany}
                onChange={(e) => setNewJdCompany(e.target.value)}
                style={{ padding: '10px 12px', borderRadius: 8, background: '#1e293b', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', fontSize: 13 }}
              />
              <input
                type="text"
                placeholder="Location (e.g. Dubai, UAE / Riyadh, Saudi Arabia)"
                value={newJdLocation}
                onChange={(e) => setNewJdLocation(e.target.value)}
                style={{ padding: '10px 12px', borderRadius: 8, background: '#1e293b', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', fontSize: 13 }}
              />
              <textarea
                placeholder="Paste Full Job Description Text..."
                rows={8}
                value={newJdText}
                onChange={(e) => setNewJdText(e.target.value)}
                style={{ padding: '10px 12px', borderRadius: 8, background: '#1e293b', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', resize: 'vertical', fontSize: 13, lineHeight: 1.5 }}
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 8 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddJdModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ fontWeight: 600 }}>Score & Evaluate</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
