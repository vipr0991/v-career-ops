import React, { useState, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

export default function SettingsPage({ profile, mcpStatus, addToast }) {
  const [models, setModels] = useState([])
  const [loadingModels, setLoadingModels] = useState(false)

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    setLoadingModels(true)
    try {
      const res = await fetch(`${API_BASE}/api/models`)
      if (res.ok) {
        const data = await res.json()
        setModels(data.models || [])
      }
    } catch {
      // Fallback
      setModels([
        { id: 'ag-scoring', status: 'configured' },
        { id: 'ag-tailor', status: 'configured' },
        { id: 'ag-latex', status: 'configured' },
        { id: 'ag-chat', status: 'configured' },
        { id: 'ag-interview', status: 'configured' },
      ])
    } finally {
      setLoadingModels(false)
    }
  }

  const profileData = profile?.profile || {}
  const candidate = profileData.candidate || {}
  const narrative = profileData.narrative || {}
  const compensation = profileData.compensation || {}
  const location = profileData.location || {}
  const targetRoles = profileData.target_roles || {}

  return (
    <div className="page-content" id="settings-page">
      {/* Profile Section */}
      <div className="settings-section">
        <h3>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-primary-light)' }}>person</span>
          Candidate Profile
        </h3>
        <div className="settings-row">
          <div className="settings-row-label">Full Name</div>
          <div className="settings-row-value">{candidate.full_name || 'Vinay Prakash'}</div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">Email</div>
          <div className="settings-row-value">{candidate.email || 'voommen@my.madonna.edu'}</div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">Phone</div>
          <div className="settings-row-value">{candidate.phone || '+971585951173'}</div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">Location</div>
          <div className="settings-row-value">{candidate.location || 'Dubai, UAE'}</div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">LinkedIn</div>
          <div className="settings-row-value">
            <a href={`https://${candidate.linkedin || 'linkedin.com/in/vipr0'}`}
              target="_blank" rel="noopener noreferrer"
              style={{ color: 'var(--accent-primary-light)', textDecoration: 'none' }}>
              {candidate.linkedin || 'linkedin.com/in/vipr0'}
            </a>
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">Portfolio</div>
          <div className="settings-row-value">
            <a href={candidate.portfolio_url || 'https://behance.net/vinaypoommen'}
              target="_blank" rel="noopener noreferrer"
              style={{ color: 'var(--accent-primary-light)', textDecoration: 'none' }}>
              {candidate.portfolio_url || 'behance.net/vinaypoommen'}
            </a>
          </div>
        </div>
      </div>

      {/* Narrative */}
      <div className="settings-section">
        <h3>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-secondary)' }}>auto_awesome</span>
          Professional Narrative
        </h3>
        <div className="settings-row">
          <div className="settings-row-label">Headline</div>
          <div className="settings-row-value" style={{ fontFamily: 'var(--font-sans)', maxWidth: 500 }}>
            {narrative.headline || 'Strategic Marketing & Editorial Leader specializing in AI Workflows & Brand Strategy'}
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">Superpowers</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {(narrative.superpowers || ['AI workflow automation', 'Content marketing', 'Demand generation']).map((sp, i) => (
              <span key={i} className="model-tag">{sp}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Target Roles */}
      <div className="settings-section">
        <h3>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-warning)' }}>target</span>
          Target Roles ({(targetRoles.archetypes || []).length})
        </h3>
        {(targetRoles.archetypes || []).map((role, i) => (
          <div className="settings-row" key={i}>
            <div className="settings-row-label">{role.name}</div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <span className="model-tag">{role.level}</span>
              <span className={`rec-badge ${role.fit === 'primary' ? 'apply' : role.fit === 'secondary' ? 'consider' : 'skip'}`}>
                {role.fit}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Compensation */}
      <div className="settings-section">
        <h3>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-success)' }}>payments</span>
          Compensation Targets
        </h3>
        <div className="settings-row">
          <div className="settings-row-label">Target Range</div>
          <div className="settings-row-value">{compensation.target_range || '$120K-160K'}</div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">Currency</div>
          <div className="settings-row-value">{compensation.currency || 'USD'}</div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">Minimum</div>
          <div className="settings-row-value">{compensation.minimum || '$100K'}</div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">Flexibility</div>
          <div className="settings-row-value" style={{ fontFamily: 'var(--font-sans)' }}>
            {compensation.location_flexibility || 'Local UAE on-site/hybrid, or GCC/Remote'}
          </div>
        </div>
      </div>

      {/* API Status */}
      <div className="settings-section">
        <h3>
          <span className="material-symbols-outlined" style={{ color: mcpStatus === 'online' ? 'var(--accent-success)' : 'var(--accent-danger)' }}>dns</span>
          System Status
        </h3>
        <div className="settings-row">
          <div className="settings-row-label">FastAPI Backend (Port 5000)</div>
          <div className="settings-row-value" style={{ color: mcpStatus === 'online' ? 'var(--accent-success)' : 'var(--accent-danger)' }}>
            {mcpStatus === 'online' ? '● Online' : '● Offline'}
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">LiteLLM Proxy (Port 4000)</div>
          <div className="settings-row-value" style={{ color: models.length > 0 ? 'var(--accent-success)' : 'var(--text-muted)' }}>
            {models.length > 0 ? '● Connected' : '○ Unknown'}
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-label">Available Models</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {loadingModels ? (
              <span className="spinner" />
            ) : models.length > 0 ? (
              models.map((m, i) => (
                <span key={i} className="model-tag active">{m.id || m}</span>
              ))
            ) : (
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>No models detected — start LiteLLM</span>
            )}
          </div>
        </div>
      </div>

      {/* Refresh Button */}
      <div style={{ display: 'flex', gap: 12 }}>
        <button className="btn btn-secondary" onClick={() => { fetchModels(); addToast('Refreshing system status...', 'info') }}>
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>sync</span>
          Refresh Status
        </button>
      </div>
    </div>
  )
}
