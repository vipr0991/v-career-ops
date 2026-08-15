import React, { useState, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

const STAGES = [
  { key: 'new',        label: 'New',        color: '#64748b', icon: 'fiber_new' },
  { key: 'evaluating', label: 'Evaluating', color: '#6366f1', icon: 'manage_search' },
  { key: 'scored',     label: 'Scored',     color: '#06b6d4', icon: 'insights' },
  { key: 'applied',    label: 'Applied',    color: '#f59e0b', icon: 'send' },
  { key: 'interview',  label: 'Interview',  color: '#8b5cf6', icon: 'groups' },
  { key: 'offer',      label: 'Offer',      color: '#10b981', icon: 'workspace_premium' },
]

const STAGE_KEYS = STAGES.map(s => s.key)

// Persist pipeline state in localStorage so status changes survive reload
function loadPipelineOverrides() {
  try { return JSON.parse(localStorage.getItem('pipeline_overrides') || '{}') } catch { return {} }
}
function savePipelineOverrides(overrides) {
  try { localStorage.setItem('pipeline_overrides', JSON.stringify(overrides)) } catch {}
}

export default function PipelinePage({ jobs, addToast, onRefresh }) {
  const [items, setItems] = useState([])
  const [overrides, setOverrides] = useState(loadPipelineOverrides)
  const [filterStage, setFilterStage] = useState('all')
  const [dragId, setDragId] = useState(null)

  // Build items from scored jobs + apply any status overrides
  useEffect(() => {
    const built = (jobs || []).map(job => {
      const base = overrides[job.id]?.status
      return {
        id: job.id,
        role: job.role || job.title || 'Untitled',
        company: job.company || 'Unknown',
        score: job.score,
        status: base || (job.score != null ? 'scored' : 'new'),
        date: job.report_file ? job.report_file.split('-').slice(1, 4).join('-') : '',
        report_file: job.report_file,
      }
    })
    setItems(built)
  }, [jobs, overrides])

  const updateStatus = (id, newStatus) => {
    const next = { ...overrides, [id]: { ...(overrides[id] || {}), status: newStatus } }
    setOverrides(next)
    savePipelineOverrides(next)
    setItems(prev => prev.map(it => it.id === id ? { ...it, status: newStatus } : it))
    // best-effort backend sync
    fetch(`${API_BASE}/api/pipeline/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    }).catch(() => {})
    addToast(`Moved to ${newStatus}`, 'success')
  }

  const deleteItem = (id) => {
    if (!window.confirm('Remove from pipeline?')) return
    const next = { ...overrides }
    delete next[id]
    setOverrides(next)
    savePipelineOverrides(next)
    setItems(prev => prev.filter(it => it.id !== id))
    addToast('Removed from pipeline', 'info')
  }

  // Drag-and-drop between columns
  const onDragStart = (id) => setDragId(id)
  const onDrop = (stageKey) => {
    if (dragId) { updateStatus(dragId, stageKey); setDragId(null) }
  }

  const counts = STAGE_KEYS.reduce((acc, k) => ({ ...acc, [k]: items.filter(i => i.status === k).length }), {})
  const total = items.length || 1

  const filtered = filterStage === 'all' ? items : items.filter(i => i.status === filterStage)

  return (
    <div className="page-content" id="pipeline-page">
      {/* Header */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <span className="material-symbols-outlined" style={{ color: 'var(--accent-primary-light)' }}>view_kanban</span>
            Application Pipeline
          </div>
          <span className="section-count">{items.length} Total</span>
        </div>

        {/* Progress bar */}
        <div style={{ display: 'flex', height: 8, borderRadius: 4, overflow: 'hidden', gap: 2, margin: '12px 0' }}>
          {STAGES.map(s => (
            <div key={s.key} style={{ width: `${(counts[s.key] / total) * 100}%`, background: s.color, transition: 'width 0.3s' }} title={`${s.label}: ${counts[s.key]}`} />
          ))}
        </div>

        {/* Stage filter chips */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <button className={`filter-chip ${filterStage === 'all' ? 'active' : ''}`} onClick={() => setFilterStage('all')}>
            All <strong style={{ marginLeft: 4 }}>{items.length}</strong>
          </button>
          {STAGES.map(s => (
            <button key={s.key} className={`filter-chip ${filterStage === s.key ? 'active' : ''}`} onClick={() => setFilterStage(s.key)}>
              <span className="material-symbols-outlined" style={{ fontSize: 13, color: s.color }}>{s.icon}</span>
              {s.label} <strong style={{ marginLeft: 4 }}>{counts[s.key]}</strong>
            </button>
          ))}
        </div>
      </div>

      {/* Kanban columns */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 12, marginTop: 16, overflowX: 'auto' }}>
        {STAGES.map(stage => (
          <div
            key={stage.key}
            onDragOver={e => e.preventDefault()}
            onDrop={() => onDrop(stage.key)}
            style={{
              background: 'var(--bg-card)',
              border: `1px solid ${dragId ? stage.color + '55' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-lg)',
              padding: 12,
              minHeight: 200,
              transition: 'border-color 0.2s',
            }}
          >
            {/* Column header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 16, color: stage.color }}>{stage.icon}</span>
              <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: stage.color }}>{stage.label}</span>
              <span style={{ marginLeft: 'auto', background: stage.color + '22', color: stage.color, fontSize: 11, fontWeight: 700, padding: '1px 7px', borderRadius: 12 }}>
                {counts[stage.key]}
              </span>
            </div>

            {/* Cards */}
            {items.filter(it => it.status === stage.key).map(item => (
              <div
                key={item.id}
                draggable
                onDragStart={() => onDragStart(item.id)}
                style={{
                  background: 'var(--bg-glass)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '10px 12px',
                  marginBottom: 8,
                  cursor: 'grab',
                  transition: 'transform 0.15s, box-shadow 0.15s',
                }}
                onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)' }}
                onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '' }}
              >
                <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 2 }}>{item.role}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>{item.company}</div>
                {item.score != null && (
                  <div style={{ fontSize: 11, fontWeight: 600, color: item.score >= 70 ? 'var(--accent-success)' : item.score >= 45 ? 'var(--accent-warning)' : 'var(--accent-danger)', marginBottom: 6 }}>
                    {Math.round(item.score)}% match
                  </div>
                )}

                {/* Move to next stage */}
                <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 4 }}>
                  {STAGE_KEYS.filter(k => k !== stage.key).map(k => {
                    const s = STAGES.find(x => x.key === k)
                    return (
                      <button
                        key={k}
                        onClick={() => updateStatus(item.id, k)}
                        title={`Move to ${s.label}`}
                        style={{
                          background: s.color + '18', color: s.color, border: `1px solid ${s.color}44`,
                          borderRadius: 4, padding: '2px 6px', fontSize: 10, cursor: 'pointer',
                        }}
                      >
                        {s.label}
                      </button>
                    )
                  })}
                  <button
                    onClick={() => deleteItem(item.id)}
                    style={{ background: 'transparent', color: 'var(--text-muted)', border: '1px solid var(--border-subtle)', borderRadius: 4, padding: '2px 6px', fontSize: 10, cursor: 'pointer', marginLeft: 'auto' }}
                  >✕</button>
                </div>
              </div>
            ))}

            {items.filter(it => it.status === stage.key).length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: 11, padding: '20px 0', borderRadius: 8, border: '1px dashed var(--border-subtle)' }}>
                Drop cards here
              </div>
            )}
          </div>
        ))}
      </div>

      {/* List view */}
      <div className="panel" style={{ marginTop: 24 }}>
        <div className="panel-header">
          <div className="panel-title">
            <span className="material-symbols-outlined" style={{ color: 'var(--accent-secondary)' }}>list</span>
            All Applications
          </div>
        </div>
        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 24, color: 'var(--text-muted)', fontSize: 13 }}>
            No items. Score jobs on the Jobs page to populate the pipeline.
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                {['Role', 'Company', 'Score', 'Stage', 'Date', 'Move To', ''].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '10px 12px', fontWeight: 600, fontSize: 11 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => {
                const stage = STAGES.find(s => s.key === item.status) || STAGES[0]
                const nextStageKey = STAGE_KEYS[STAGE_KEYS.indexOf(item.status) + 1]
                const nextStage = STAGES.find(s => s.key === nextStageKey)
                return (
                  <tr key={item.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '10px 12px', fontWeight: 600 }}>{item.role}</td>
                    <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>{item.company}</td>
                    <td style={{ padding: '10px 12px' }}>
                      {item.score != null
                        ? <span style={{ fontWeight: 700, color: item.score >= 70 ? 'var(--accent-success)' : item.score >= 45 ? 'var(--accent-warning)' : 'var(--accent-danger)' }}>{Math.round(item.score)}%</span>
                        : <span style={{ color: 'var(--text-muted)' }}>—</span>}
                    </td>
                    <td style={{ padding: '10px 12px' }}>
                      <span style={{ background: stage.color + '22', color: stage.color, padding: '3px 10px', borderRadius: 12, fontSize: 11, fontWeight: 600 }}>
                        {stage.label}
                      </span>
                    </td>
                    <td style={{ padding: '10px 12px', fontSize: 11, color: 'var(--text-muted)' }}>{item.date || '—'}</td>
                    <td style={{ padding: '10px 12px' }}>
                      <select
                        value={item.status}
                        onChange={e => updateStatus(item.id, e.target.value)}
                        style={{ background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-subtle)', borderRadius: 6, padding: '4px 8px', fontSize: 11, cursor: 'pointer' }}
                      >
                        {STAGES.map(s => <option key={s.key} value={s.key}>{s.label}</option>)}
                      </select>
                    </td>
                    <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                      <button onClick={() => deleteItem(item.id)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 16 }}>✕</button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
