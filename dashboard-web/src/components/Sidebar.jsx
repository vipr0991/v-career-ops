import React from 'react'

const NAV_ITEMS = [
  { id: 'dashboard', icon: 'dashboard', label: 'Dashboard' },
  { id: 'jobs', icon: 'work', label: 'Jobs' },
  { id: 'pipeline', icon: 'view_kanban', label: 'Pipeline' },
  { id: 'resume', icon: 'folder', label: 'Resume Hub' },
  { id: 'interview', icon: 'school', label: 'Interview Prep' },
]

const NAV_BOTTOM = [
  { id: 'settings', icon: 'settings', label: 'Settings' },
]

export default function Sidebar({ activePage, onNavigate, mcpStatus, candidateName, isOpen, onClose }) {
  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.reload();
    } catch (err) {
      console.error('Logout failed', err);
    }
  }

  const handleNav = (id) => {
    onNavigate(id)
    if (onClose) onClose()
  }

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="sidebar-backdrop"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <nav className={`sidebar ${isOpen ? 'open' : ''}`} id="main-sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-logo">
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>rocket_launch</span>
          </div>
          <div className="sidebar-brand-text">
            <h1>Career-Ops</h1>
            <p>AI Job Search</p>
          </div>
          {isOpen && (
            <button
              className="sidebar-close-btn"
              onClick={onClose}
              aria-label="Close Menu"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          )}
        </div>

        <div className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`sidebar-nav-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => handleNav(item.id)}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
          <div className="sidebar-divider" />
          {NAV_BOTTOM.map((item) => (
            <button
              key={item.id}
              className={`sidebar-nav-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => handleNav(item.id)}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <div style={{display:'flex', width:'100%', alignItems:'center', gap:'12px', paddingBottom:'12px', borderBottom:'1px solid var(--border-color)', marginBottom:'12px'}}>
            <div className="sidebar-avatar">VP</div>
            <div className="sidebar-user-info">
              <div className="sidebar-user-name">{candidateName || 'Vinay Prakash'}</div>
              <div className="sidebar-user-role">Candidate</div>
            </div>
            <div
              className={`sidebar-status-dot ${mcpStatus === 'offline' ? 'offline' : ''}`}
              title={mcpStatus === 'online' ? 'Gateway Online' : 'Gateway Offline'}
              style={{ marginLeft: 'auto' }}
            />
          </div>
          <button onClick={handleLogout} className="sidebar-nav-item" style={{color: 'var(--text-secondary)', padding: '8px', fontSize: '14px', width: '100%'}}>
            <span className="material-symbols-outlined" style={{fontSize: '18px'}}>logout</span>
            <span>Disconnect LinkedIn</span>
          </button>
        </div>
      </nav>
    </>
  )
}
