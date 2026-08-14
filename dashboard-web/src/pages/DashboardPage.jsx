import React from 'react'

const TARGET_ROLES = [
  { name: 'AI Content & Automation Specialist', match: 90, cities: 'Dubai, Abu Dhabi, Riyadh' },
  { name: 'AI Strategy & Enablement Lead', match: 80, cities: 'Dubai, Abu Dhabi, Riyadh' },
  { name: 'Marketing Operations Manager', match: 80, cities: 'Abu Dhabi, Dubai, Riyadh' },
  { name: 'Senior Marketing Manager – MarTech', match: 85, cities: 'Abu Dhabi, Dubai' },
  { name: 'Head of Digital Communications', match: 75, cities: 'Dubai, Riyadh, Jeddah' },
  { name: 'Director / Head of Content Marketing', match: 75, cities: 'Dubai, Abu Dhabi, Riyadh' },
]

export default function DashboardPage({ stats, jobs, onNavigate, onOpenChat }) {
  const recentJobs = (jobs || []).slice(-5).reverse()

  return (
    <div className="page-content" id="dashboard-page">
      {/* Hero Stats */}
      <section className="stats-row">
        <div className="stat-card">
          <span className="material-symbols-outlined stat-icon" style={{ color: 'var(--accent-primary-light)' }}>assessment</span>
          <div className="stat-value">{stats.total_scored || 0}</div>
          <div className="stat-label">Evaluated Roles</div>
        </div>
        <div className="stat-card">
          <span className="material-symbols-outlined stat-icon" style={{ color: 'var(--accent-secondary)' }}>pending_actions</span>
          <div className="stat-value">{stats.total_jds || 0}</div>
          <div className="stat-label">Pending JDs</div>
        </div>
        <div className="stat-card">
          <span className="material-symbols-outlined stat-icon" style={{ color: 'var(--accent-success)' }}>task_alt</span>
          <div className="stat-value">{stats.total_outputs || 0}</div>
          <div className="stat-label">Optimized CVs</div>
        </div>
        <div className="stat-card">
          <span className="material-symbols-outlined stat-icon" style={{ color: 'var(--accent-warning)' }}>location_on</span>
          <div className="stat-value">{stats.location || 'Dubai'}</div>
          <div className="stat-label">Target Metro</div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="quick-actions">
        <div className="quick-action-card" onClick={() => onNavigate('jobs')}>
          <div className="quick-action-icon search">
            <span className="material-symbols-outlined">search</span>
          </div>
          <div className="quick-action-label">Search Jobs</div>
          <div className="quick-action-desc">Find roles on portals</div>
        </div>
        <div className="quick-action-card" onClick={() => onNavigate('jobs')}>
          <div className="quick-action-icon paste">
            <span className="material-symbols-outlined">content_paste</span>
          </div>
          <div className="quick-action-label">Paste JD</div>
          <div className="quick-action-desc">Evaluate any job listing</div>
        </div>
        <div className="quick-action-card" onClick={() => onNavigate('resume')}>
          <div className="quick-action-icon resume">
            <span className="material-symbols-outlined">description</span>
          </div>
          <div className="quick-action-label">Resume Hub</div>
          <div className="quick-action-desc">Tailor & download CVs</div>
        </div>
        <div className="quick-action-card" onClick={onOpenChat}>
          <div className="quick-action-icon chat">
            <span className="material-symbols-outlined">smart_toy</span>
          </div>
          <div className="quick-action-label">AI Assistant</div>
          <div className="quick-action-desc">Chat with Kimi</div>
        </div>
      </section>

      {/* Two Column: Activity + Target Roles */}
      <div className="grid-2">
        {/* Recent Activity */}
        <div className="activity-feed">
          <h3>
            <span className="material-symbols-outlined" style={{ color: 'var(--accent-primary-light)' }}>history</span>
            Recent Activity
          </h3>
          {recentJobs.length === 0 ? (
            <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
              No recent activity. Start by searching for jobs!
            </div>
          ) : (
            recentJobs.map((job, i) => (
              <div className="activity-item" key={job.id || i}>
                <span className={`activity-dot ${job.status === 'scored' ? 'scored' : 'applied'}`} />
                <div className="activity-text">
                  <strong>{job.role || job.title || 'Role'}</strong> at {job.company || 'Unknown'}
                </div>
                <span className="activity-time">
                  {job.score != null ? `${Math.round(job.score)}%` : job.status || 'pending'}
                </span>
              </div>
            ))
          )}
        </div>

        {/* Target Roles */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <span className="material-symbols-outlined" style={{ color: 'var(--accent-warning)' }}>target</span>
              Target Roles
            </div>
          </div>
          <div className="target-roles-grid">
            {TARGET_ROLES.map((role) => (
              <div className="target-role-card" key={role.name}>
                <div className="target-role-title">{role.name}</div>
                <div className={`target-role-match ${role.match >= 80 ? 'high' : 'medium'}`}>
                  {role.match}% Match
                </div>
                <div className="target-role-cities">{role.cities}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
