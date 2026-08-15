import React, { useState, useEffect } from 'react'
import ScoreRing from '../components/ScoreRing'
import * as api from '../api-resilient'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

const ROLE_PRESETS = [
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

  // Auto-search on first load
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
      const scoreVal = typeof job.score === 'object' ? job.score : { overall_score: job.score }
      const res = await fetch(`${API_BASE}/api/pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: job.title || job.role || 'Target Role',
          company: job.company || 'Enterprise',
          location: job.location || searchFilters.location || 'Dubai, UAE',
          salary_range: job.salary_range || 'Not Disclosed',
          url: job.url || '',
          source: job.source || 'Search Discovery',
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

  return (
    <div className="page-content" id="jobs-page" style={{ maxWidth: 1400, margin: '0 auto', padding: 24 }}>
      {/* Search & Location Bar */}
      <div className="search-panel" style={{ background: 'rgba(30, 41, 59, 0.7)', backdropFilter: 'blur(12px)', padding: 24, borderRadius: 12, border: '1px solid rgba(255,255,255,0.08)', marginBottom: 24 }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 20, margin: '0 0 16px 0', color: '#fff' }}>
          <span className="material-symbols-outlined" style={{ color: '#38bdf8' }}>travel_explore</span>
          Multi-Location Job Discovery (Middle East & Bangalore)
        </h2>

        {/* Role Presets */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
          {ROLE_PRESETS.map((role) => (
            <button
              key={role}
              style={{
                padding: '6px 12px',
                borderRadius: 20,
                border: searchFilters.title === role ? '1px solid #38bdf8' : '1px solid rgba(255,255,255,0.1)',
                background: searchFilters.title === role ? 'rgba(56, 189, 248, 0.15)' : 'rgba(255,255,255,0.03)',
                color: searchFilters.title === role ? '#fff' : 'var(--text-secondary)',
                fontSize: 12,
                cursor: 'pointer'
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
                  border: isMatch ? '1px solid #10b981' : '1px solid rgba(255,255,255,0.1)',
                  background: isMatch ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255,255,255,0.03)',
                  color: isMatch ? '#fff' : 'var(--text-secondary)',
                  fontSize: 12,
                  cursor: 'pointer'
                }}
                onClick={() => setSearchFilters({ ...searchFilters, location: loc.value })}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 14, color: isMatch ? '#10b981' : 'var(--text-secondary)' }}>location_on</span>
                {loc.label}
              </button>
            )
          })}
        </div>

        {/* Search Input Grid */}
        <form onSubmit={(e) => { e.preventDefault(); onSearch(searchFilters) }} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12, alignItems: 'flex-end' }}>
          <div>
            <label style={{ display: 'block', fontSize: 12, marginBottom: 4, color: 'var(--text-secondary)' }}>Target Role</label>
            <input
              type="text"
              value={searchFilters.title}
              onChange={(e) => setSearchFilters({ ...searchFilters, title: e.target.value })}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', fontSize: 13 }}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, marginBottom: 4, color: 'var(--text-secondary)' }}>Target Region</label>
            <input
              type="text"
              value={searchFilters.location}
              onChange={(e) => setSearchFilters({ ...searchFilters, location: e.target.value })}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', fontSize: 13 }}
            />
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button type="submit" className="btn btn-primary" style={{ flex: 1, padding: '10px 16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
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

      {/* Discovered Opportunities Grid */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h3 style={{ margin: 0, fontSize: 18, color: '#fff' }}>
            Discovered Opportunities ({searchResults.length})
          </h3>
          <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            Region: <strong>{searchFilters.location}</strong>
          </span>
        </div>

        {searchResults.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: 12, border: '1px dashed rgba(255,255,255,0.1)' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 40, color: 'var(--text-secondary)' }}>search_off</span>
            <p style={{ margin: '8px 0 0', color: 'var(--text-secondary)', fontSize: 13 }}>No search results loaded. Click "Scan Jobs" above.</p>
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
                  gap: 12
                }}
              >
                <div>
                  <h4 style={{ margin: '0 0 4px', fontSize: 15, fontWeight: 'bold', color: '#fff' }}>{job.title}</h4>
                  <div style={{ fontSize: 13, color: '#38bdf8', fontWeight: 500 }}>{job.company}</div>
                </div>

                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', fontSize: 12, color: 'var(--text-secondary)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(255,255,255,0.04)', padding: '2px 6px', borderRadius: 4 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 13 }}>location_on</span>
                    {job.location}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(255,255,255,0.04)', padding: '2px 6px', borderRadius: 4 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 13 }}>payments</span>
                    {job.salary_range}
                  </span>
                </div>

                <p style={{ margin: 0, fontSize: 12, color: '#94a3b8', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {job.description}
                </p>

                <div style={{ display: 'flex', gap: 8, marginTop: 'auto', paddingTop: 8, borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => onScoreJob(job)}
                    disabled={scoringJobId === job.id}
                    style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4, fontSize: 12 }}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 15 }}>analytics</span>
                    {scoringJobId === job.id ? 'Evaluating...' : 'Score 10-D'}
                  </button>

                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => saveJobToPipeline(job)}
                    style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12 }}
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
                      style={{ display: 'flex', alignItems: 'center', padding: '0 8px' }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>open_in_new</span>
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected Job Deep 10-Dimension Evaluation Drawer/Card */}
      {selectedJob && (
        <div style={{ background: '#0f172a', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: 16, padding: 24, marginBottom: 32 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 20 }}>
            <div>
              <span style={{ fontSize: 12, color: '#38bdf8', textTransform: 'uppercase', letterSpacing: 1, fontWeight: 'bold' }}>
                10-Dimension Line-by-Line AI Evaluation
              </span>
              <h3 style={{ margin: '4px 0', fontSize: 20, color: '#fff' }}>
                {selectedJob.job_meta?.title || selectedJob.title || 'Evaluated Job'}
              </h3>
              <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: 13 }}>
                {selectedJob.job_meta?.company || selectedJob.company} • {selectedJob.source_agent || 'Gemini 2.5 Flash'}
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
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10, marginBottom: 20 }}>
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

          {/* Interview Pitch Points */}
          {selectedJob.score?.interview_talking_points && (
            <div style={{ background: 'rgba(59, 130, 246, 0.05)', border: '1px solid rgba(59, 130, 246, 0.2)', padding: 16, borderRadius: 10 }}>
              <h4 style={{ margin: '0 0 8px', fontSize: 14, color: '#60a5fa', display: 'flex', alignItems: 'center', gap: 6 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>lightbulb</span>
                Recommended Interview Talking Points
              </h4>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: '#cbd5e1', lineHeight: 1.6 }}>
                {selectedJob.score.interview_talking_points.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Paste JD Modal */}
      {showAddJdModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.8)', zIndex: 9999, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: 20 }}>
          <div style={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 12, width: '100%', maxWidth: 550, padding: 24, color: '#fff' }}>
            <h3 style={{ margin: '0 0 16px', fontSize: 18, color: '#38bdf8' }}>Paste Custom Job Description</h3>
            <form onSubmit={handleCustomJdSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <input
                type="text"
                placeholder="Job Title (e.g. Marketing Automation Lead)"
                value={newJdTitle}
                onChange={(e) => setNewJdTitle(e.target.value)}
                style={{ padding: 10, borderRadius: 6, background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#fff' }}
              />
              <input
                type="text"
                placeholder="Company Name (e.g. Careem, NEOM)"
                value={newJdCompany}
                onChange={(e) => setNewJdCompany(e.target.value)}
                style={{ padding: 10, borderRadius: 6, background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#fff' }}
              />
              <input
                type="text"
                placeholder="Location (e.g. Dubai / Riyadh / Bangalore)"
                value={newJdLocation}
                onChange={(e) => setNewJdLocation(e.target.value)}
                style={{ padding: 10, borderRadius: 6, background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#fff' }}
              />
              <textarea
                placeholder="Paste Full Job Description Text..."
                rows={8}
                value={newJdText}
                onChange={(e) => setNewJdText(e.target.value)}
                style={{ padding: 10, borderRadius: 6, background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', resize: 'vertical' }}
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 8 }}>
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
