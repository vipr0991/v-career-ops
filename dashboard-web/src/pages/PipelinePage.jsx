import React, { useState, useEffect, useCallback } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

const STAGES = [
  { key: 'all', label: 'All Jobs', color: '#3b82f6', icon: 'list' },
  { key: 'pipeline_saved', label: 'Saved / Qualified', color: '#06b6d4', icon: 'bookmark' },
  { key: 'assets_generated', label: 'Kit Ready (PPTX/LaTeX)', color: '#8b5cf6', icon: 'inventory' },
  { key: 'outreach_active', label: 'Outreach Active', color: '#f59e0b', icon: 'send' },
  { key: 'interviewing', label: 'Interviewing', color: '#10b981', icon: 'groups' },
]

export default function PipelinePage({ addToast, onRefresh }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeStage, setActiveStage] = useState('all')
  const [locationFilter, setLocationFilter] = useState('All')
  const [generatingKitId, setGeneratingKitId] = useState(null)
  const [selectedItemModal, setSelectedItemModal] = useState(null)

  const fetchPipeline = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/pipeline`)
      if (res.ok) {
        const data = await res.json()
        setItems(data.items || [])
      }
    } catch {
      addToast('Could not load pipeline data', 'error')
    } finally {
      setLoading(false)
    }
  }, [addToast])

  useEffect(() => {
    fetchPipeline()
  }, [fetchPipeline])

  const updateStage = async (id, newStage) => {
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStage }),
      })
      if (res.ok) {
        setItems(prev => prev.map(it => it.id === id ? { ...it, stage: newStage } : it))
        addToast(`Stage updated to ${newStage}`, 'success')
      }
    } catch {
      addToast('Failed to update stage', 'error')
    }
  }

  const deleteItem = async (id) => {
    if (!window.confirm('Remove this opportunity from your active pipeline?')) return
    try {
      const res = await fetch(`${API_BASE}/api/pipeline?item_id=${id}`, {
        method: 'DELETE',
      })
      if (res.ok) {
        setItems(prev => prev.filter(it => it.id !== id))
        addToast('Removed from pipeline', 'success')
      }
    } catch {
      addToast('Failed to delete item', 'error')
    }
  }

  const generateKit = async (id) => {
    setGeneratingKitId(id)
    addToast('Generating Company Intelligence, LaTeX Resume & 6-Slide PPTX Deck...', 'info')
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/generate-kit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: id }),
      })
      if (res.ok) {
        const result = await res.json()
        setItems(prev => prev.map(it => it.id === id ? result.pipeline_item : it))
        setSelectedItemModal(result.pipeline_item)
        addToast('Application Kit (LaTeX + PPTX + Research) Ready!', 'success')
      } else {
        addToast('Kit generation failed', 'error')
      }
    } catch {
      addToast('Network error during kit generation', 'error')
    } finally {
      setGeneratingKitId(null)
    }
  }

  const filteredItems = items.filter(it => {
    const stageMatch = activeStage === 'all' || it.stage === activeStage
    const locMatch = locationFilter === 'All' || (it.location || '').toLowerCase().includes(locationFilter.toLowerCase())
    return stageMatch && locMatch
  })

  return (
    <div className="page-container" style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: '0 0 6px 0', color: 'var(--text-primary)' }}>
            Job Pipeline & Application Command Center
          </h1>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', margin: 0 }}>
            Track opportunities, generate company research briefs, customized LaTeX resumes, and executive PowerPoint decks.
          </p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={fetchPipeline} disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>sync</span>
          {loading ? 'Refreshing...' : 'Refresh Pipeline'}
        </button>
      </div>

      {/* Filter Tabs & Location Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
        {/* Stage Filter */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {STAGES.map(s => {
            const count = s.key === 'all' ? items.length : items.filter(x => x.stage === s.key).length
            const isActive = activeStage === s.key
            return (
              <button
                key={s.key}
                onClick={() => setActiveStage(s.key)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '8px 14px',
                  borderRadius: '20px',
                  border: isActive ? `1px solid ${s.color}` : '1px solid rgba(255,255,255,0.08)',
                  background: isActive ? `${s.color}22` : 'rgba(255,255,255,0.03)',
                  color: isActive ? '#fff' : 'var(--text-secondary)',
                  fontSize: '13px',
                  cursor: 'pointer',
                  fontWeight: isActive ? '600' : 'normal'
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16, color: s.color }}>{s.icon}</span>
                {s.label}
                <span style={{ fontSize: 11, background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: 10 }}>
                  {count}
                </span>
              </button>
            )
          })}
        </div>

        {/* Location Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 18, color: 'var(--text-secondary)' }}>travel_explore</span>
          <select
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.1)',
              background: '#1e293b',
              color: '#fff',
              fontSize: '13px',
              cursor: 'pointer'
            }}
          >
            <option value="All">All Locations</option>
            <option value="UAE">UAE (Dubai / Abu Dhabi)</option>
            <option value="Saudi">Saudi Arabia (Riyadh / NEOM)</option>
            <option value="Qatar">Qatar (Doha)</option>
            <option value="Bahrain">Bahrain</option>
            <option value="Oman">Oman</option>
            <option value="Kuwait">Kuwait</option>
            <option value="Bangalore">Bangalore (India)</option>
          </select>
        </div>
      </div>

      {/* Grid of Pipeline Cards */}
      {filteredItems.length === 0 ? (
        <div style={{ padding: '60px 20px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: 12, border: '1px dashed rgba(255,255,255,0.1)' }}>
          <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--text-secondary)', marginBottom: 12 }}>inbox</span>
          <h3 style={{ margin: '0 0 8px', fontSize: 16, color: 'var(--text-primary)' }}>No opportunities found in this view</h3>
          <p style={{ margin: 0, fontSize: 13, color: 'var(--text-secondary)' }}>
            Search jobs in the <strong>Jobs</strong> tab or adjust your location and stage filters.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))', gap: '16px' }}>
          {filteredItems.map(item => {
            const scoreVal = typeof item.score === 'object' ? item.score?.overall_score : item.score
            const isKitGenerating = generatingKitId === item.id
            const hasKit = item.presentation_deck || item.tailored_resume_tex || item.company_research

            return (
              <div
                key={item.id}
                style={{
                  background: 'rgba(30, 41, 59, 0.7)',
                  backdropFilter: 'blur(12px)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '12px',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '14px',
                  position: 'relative'
                }}
              >
                {/* Header: Title & Score Badge */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
                  <div>
                    <h3 style={{ margin: '0 0 4px', fontSize: '16px', fontWeight: 'bold', color: '#fff' }}>
                      {item.title}
                    </h3>
                    <div style={{ fontSize: '14px', color: '#38bdf8', fontWeight: '500' }}>
                      {item.company}
                    </div>
                  </div>
                  {scoreVal != null && (
                    <div style={{
                      padding: '4px 10px',
                      borderRadius: '8px',
                      background: scoreVal >= 85 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(59, 130, 246, 0.15)',
                      border: scoreVal >= 85 ? '1px solid #10b981' : '1px solid #3b82f6',
                      color: scoreVal >= 85 ? '#10b981' : '#3b82f6',
                      fontWeight: 'bold',
                      fontSize: '13px'
                    }}>
                      {scoreVal}% Match
                    </div>
                  )}
                </div>

                {/* Location & Salary Chips */}
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(255,255,255,0.04)', padding: '3px 8px', borderRadius: 4 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 14 }}>location_on</span>
                    {item.location}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(255,255,255,0.04)', padding: '3px 8px', borderRadius: 4 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 14 }}>payments</span>
                    {item.salary_range}
                  </span>
                </div>

                {/* Stage Selector Dropdown */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: 12 }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Stage:</span>
                  <select
                    value={item.stage}
                    onChange={(e) => updateStage(item.id, e.target.value)}
                    style={{
                      padding: '4px 8px',
                      borderRadius: '6px',
                      border: '1px solid rgba(255,255,255,0.1)',
                      background: '#0f172a',
                      color: '#38bdf8',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    <option value="pipeline_saved">Saved / Qualified</option>
                    <option value="assets_generated">Kit Ready</option>
                    <option value="outreach_active">Outreach Active</option>
                    <option value="interviewing">Interviewing</option>
                    <option value="archived">Archived</option>
                  </select>
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: 8, marginTop: 'auto', flexWrap: 'wrap' }}>
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => generateKit(item.id)}
                    disabled={isKitGenerating}
                    style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, fontSize: '12px' }}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                      {hasKit ? 'auto_fix_high' : 'bolt'}
                    </span>
                    {isKitGenerating ? 'Synthesizing Kit...' : hasKit ? 'Regenerate Kit' : '1-Click App Kit'}
                  </button>

                  {hasKit && (
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => setSelectedItemModal(item)}
                      style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '12px' }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 16 }}>visibility</span>
                      View Assets
                    </button>
                  )}

                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => deleteItem(item.id)}
                    title="Remove from pipeline"
                    style={{ color: '#ef4444' }}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 16 }}>delete</span>
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Asset Inspection Modal */}
      {selectedItemModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0,0,0,0.75)',
            backdropFilter: 'blur(8px)',
            zIndex: 9999,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            padding: '20px'
          }}
          onClick={() => setSelectedItemModal(null)}
        >
          <div
            style={{
              background: '#0f172a',
              border: '1px solid rgba(255,255,255,0.15)',
              borderRadius: '16px',
              width: '100%',
              maxWidth: '850px',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: '28px',
              color: '#fff'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 16 }}>
              <div>
                <h2 style={{ margin: '0 0 4px', fontSize: '20px', color: '#38bdf8' }}>
                  Application Kit: {selectedItemModal.title}
                </h2>
                <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                  {selectedItemModal.company} • {selectedItemModal.location}
                </div>
              </div>
              <button
                onClick={() => setSelectedItemModal(null)}
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: 24 }}
              >
                ✕
              </button>
            </div>

            {/* Generated Downloads Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12, marginBottom: 24 }}>
              {selectedItemModal.presentation_deck && (
                <a
                  href={`${API_BASE}/api/downloads/output/${selectedItemModal.presentation_deck}`}
                  download
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '12px 16px',
                    borderRadius: 8,
                    background: 'rgba(59, 130, 246, 0.15)',
                    border: '1px solid #3b82f6',
                    color: '#60a5fa',
                    textDecoration: 'none',
                    fontSize: '13px',
                    fontWeight: 'bold'
                  }}
                >
                  <span className="material-symbols-outlined">slideshow</span>
                  Download 6-Slide PPTX Deck
                </a>
              )}

              {selectedItemModal.tailored_resume_tex && (
                <a
                  href={`${API_BASE}/api/downloads/latex/${selectedItemModal.tailored_resume_tex}`}
                  download
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '12px 16px',
                    borderRadius: 8,
                    background: 'rgba(16, 185, 129, 0.15)',
                    border: '1px solid #10b981',
                    color: '#34d399',
                    textDecoration: 'none',
                    fontSize: '13px',
                    fontWeight: 'bold'
                  }}
                >
                  <span className="material-symbols-outlined">description</span>
                  Download Tailored LaTeX (.tex)
                </a>
              )}
            </div>

            {/* Decision Makers & LinkedIn Notes */}
            {selectedItemModal.decision_makers && selectedItemModal.decision_makers.length > 0 && (
              <div style={{ marginBottom: 24 }}>
                <h3 style={{ fontSize: 16, color: '#38bdf8', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span className="material-symbols-outlined">group</span>
                  Decision Makers & LinkedIn Invites (200-char max)
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {selectedItemModal.decision_makers.map((dm, idx) => (
                    <div key={idx} style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.06)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                        <span style={{ fontWeight: 'bold', fontSize: '14px', color: '#fff' }}>{dm.target_title}</span>
                        <a href={dm.linkedin_search_url} target="_blank" rel="noreferrer" style={{ fontSize: '12px', color: '#38bdf8', textDecoration: 'none' }}>
                          Search on LinkedIn ↗
                        </a>
                      </div>
                      <p style={{ margin: '0 0 6px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                        <strong>Relevance:</strong> {dm.relevance}
                      </p>
                      <div style={{ background: 'rgba(0,0,0,0.3)', padding: '8px', borderRadius: 6, fontSize: '12px', color: '#e2e8f0', border: '1px solid rgba(255,255,255,0.05)' }}>
                        "{dm.outreach_note_200_char}"
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Company Intelligence Summary */}
            {selectedItemModal.company_research && (
              <div>
                <h3 style={{ fontSize: 16, color: '#38bdf8', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span className="material-symbols-outlined">insights</span>
                  Strategic Intelligence & Pitch Solutions
                </h3>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: 8, fontSize: '13px', lineHeight: '1.6', color: '#cbd5e1' }}>
                  <p><strong>Business Model:</strong> {selectedItemModal.company_research.business_model}</p>
                  <p><strong>Identified Pain Points:</strong> {(selectedItemModal.company_research.strategic_pain_points || []).join(' ')}</p>
                  <p><strong>Solutions to Pitch:</strong></p>
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    {(selectedItemModal.company_research.candidate_solutions_to_pitch || []).map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
