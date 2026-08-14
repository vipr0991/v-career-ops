import React, { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import AiChatPanel from './components/AiChatPanel'
import DashboardPage from './pages/DashboardPage'
import JobsPage from './pages/JobsPage'
import PipelinePage from './pages/PipelinePage'
import ResumeHubPage from './pages/ResumeHubPage'
import InterviewPrepPage from './pages/InterviewPrepPage'
import SettingsPage from './pages/SettingsPage'

// Environment-aware API base — uses import.meta.env.VITE_API_BASE from .env
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

const PAGE_TITLES = {
  dashboard: 'Dashboard',
  jobs: 'Jobs',
  pipeline: 'Pipeline',
  resume: 'Resume Hub',
  interview: 'Interview Prep',
  settings: 'Settings',
}

function getInitialPage() {
  const hash = window.location.hash.replace('#/', '').replace('#', '')
  return PAGE_TITLES[hash] ? hash : 'dashboard'
}

let _toastId = 0

export default function App() {
  const [activePage, setActivePage] = useState(getInitialPage)
  const [chatOpen, setChatOpen] = useState(false)
  const [mcpStatus, setMcpStatus] = useState('offline')
  const [stats, setStats] = useState({
    total_scored: 0, total_jds: 0, total_outputs: 0,
    location: 'Dubai', candidate_name: 'Candidate',
  })
  const [jobs, setJobs] = useState([])
  const [searchResults, setSearchResults] = useState([])
  const [searchFilters, setSearchFilters] = useState({
    title: 'Marketing Manager', location: 'Dubai', currency: 'AED',
  })
  const [selectedJob, setSelectedJob] = useState(null)
  const [scoringJobId, setScoringJobId] = useState(null)
  const [optimizingJob, setOptimizingJob] = useState(null)
  const [optimizeStep, setOptimizeStep] = useState(0)
  const [optimizeResult, setOptimizeResult] = useState(null)
  const [showAddJdModal, setShowAddJdModal] = useState(false)
  const [toasts, setToasts] = useState([])

  // ── Hash-based routing ────────────────────────────────────────
  const navigate = useCallback((page) => {
    setActivePage(page)
    window.location.hash = '#/' + page
  }, [])

  useEffect(() => {
    const onHash = () => {
      const h = window.location.hash.replace('#/', '').replace('#', '')
      if (PAGE_TITLES[h]) setActivePage(h)
    }
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  // ── Toast helper ──────────────────────────────────────────────
  const addToast = useCallback((text, type = 'info') => {
    const id = ++_toastId
    setToasts(prev => [...prev, { id, text, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000)
  }, [])

  // ── API helper — simple fetch, no retry library ───────────────
  const apiFetch = useCallback(async (path, opts = {}) => {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 20000)
    try {
      const res = await fetch(API_BASE + path, {
        ...opts,
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
      })
      clearTimeout(timer)
      return res
    } catch (err) {
      clearTimeout(timer)
      throw err
    }
  }, [])

  // ── Initial data load + health poll ──────────────────────────
  const refreshData = useCallback(async () => {
    try {
      const [sRes, jRes] = await Promise.all([
        apiFetch('/api/stats'),
        apiFetch('/api/jobs'),
      ])
      if (sRes.ok) setStats(await sRes.json())
      if (jRes.ok) { const d = await jRes.json(); setJobs(d.jobs || []) }
      setMcpStatus('online')
    } catch {
      setMcpStatus('offline')
    }
  }, [apiFetch])

  useEffect(() => {
    refreshData()
    const iv = setInterval(refreshData, 15000)
    return () => clearInterval(iv)
  }, [refreshData])

  // ── Search ────────────────────────────────────────────────────
  const handleSearch = async (filters) => {
    try {
      const res = await apiFetch('/api/search-live', {
        method: 'POST', body: JSON.stringify(filters || searchFilters),
      })
      if (res.ok) {
        const d = await res.json()
        setSearchResults(d.results || [])
        addToast(`Found ${d.total || 0} jobs`, 'success')
      } else { throw new Error('Search failed') }
    } catch {
      addToast('Search failed — backend may be offline', 'error')
    }
  }

  // ── Score job ─────────────────────────────────────────────────
  const handleScoreJob = async (job) => {
    setScoringJobId(job.id)
    setSelectedJob(null)
    try {
      const res = await apiFetch('/api/score', {
        method: 'POST',
        body: JSON.stringify({
          job_description: job.description || '',
          job_title: job.title,
          company: job.company,
          location: job.location,
        }),
      })
      if (res.ok) {
        const data = await res.json()
        setSelectedJob(data)
        addToast('Evaluation complete', 'success')
        refreshData()
      } else { throw new Error('Score failed') }
    } catch (err) {
      addToast(`Scoring error: ${err.message}`, 'error')
    } finally {
      setScoringJobId(null)
    }
  }

  // ── Tailor resume ─────────────────────────────────────────────
  const handleOptimizeResume = async (job) => {
    setOptimizingJob(job)
    setOptimizeStep(1)
    setOptimizeResult(null)
    try {
      const res = await apiFetch('/api/optimize', {
        method: 'POST',
        body: JSON.stringify({
          job_id: job.id || `job-${Date.now()}`,
          role: job.role || job.title || 'Role',
          company: job.company || 'Company',
          location: job.location || 'Dubai',
        }),
      })
      if (res.ok) {
        const data = await res.json()
        setOptimizeResult(data)
        setOptimizeStep(3)
        addToast('Resume tailored successfully!', 'success')
        refreshData()
      } else { throw new Error('Tailor failed') }
    } catch (err) {
      addToast(`Tailor error: ${err.message}`, 'error')
      setOptimizeStep(0)
    }
  }

  // ── Render ────────────────────────────────────────────────────
  const renderPage = () => {
    switch (activePage) {
      case 'jobs':
        return (
          <JobsPage
            searchResults={searchResults} jobs={jobs}
            selectedJob={selectedJob} scoringJobId={scoringJobId}
            searchFilters={searchFilters} setSearchFilters={setSearchFilters}
            onSearch={handleSearch} onScoreJob={handleScoreJob}
            onOptimizeResume={handleOptimizeResume} onApply={(url) => window.open(url, '_blank')}
            optimizingJob={optimizingJob} optimizeStep={optimizeStep} optimizeResult={optimizeResult}
            showAddJdModal={showAddJdModal} setShowAddJdModal={setShowAddJdModal}
            addToast={addToast}
          />
        )
      case 'pipeline':
        return <PipelinePage jobs={jobs} addToast={addToast} onRefresh={refreshData} />
      case 'resume':
        return <ResumeHubPage jobs={jobs} onOptimizeResume={handleOptimizeResume} addToast={addToast} />
      case 'interview':
        return <InterviewPrepPage jobs={jobs} addToast={addToast} />
      case 'settings':
        return <SettingsPage mcpStatus={mcpStatus} addToast={addToast} />
      default:
        return <DashboardPage stats={stats} jobs={jobs} onNavigate={navigate} onOpenChat={() => setChatOpen(true)} />
    }
  }

  return (
    <div className="app-shell">
      <Sidebar activePage={activePage} onNavigate={navigate} mcpStatus={mcpStatus} candidateName={stats.candidate_name} />

      <div className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <h2 className="topbar-title">{PAGE_TITLES[activePage] || 'Dashboard'}</h2>
            <span className="topbar-breadcrumb">career-ops / {activePage}</span>
          </div>
          <div className="topbar-right">
            <div className="topbar-status">
              <span className={`status-dot ${mcpStatus === 'offline' ? 'offline' : ''}`} />
              <span>{mcpStatus === 'online' ? 'Gateway Online' : 'Gateway Offline'}</span>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={refreshData}>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>sync</span>
              Refresh
            </button>
          </div>
        </header>

        {mcpStatus === 'offline' && (
          <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: 8, padding: '10px 16px', margin: '0 16px 12px', fontSize: 12, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 10 }}>
            <span className="material-symbols-outlined" style={{ color: '#ef4444', fontSize: 18 }}>warning</span>
            <span>Backend offline — run <code>python career_ops_api.py</code> in the project folder</span>
            <button className="btn btn-secondary btn-sm" onClick={refreshData} style={{ marginLeft: 'auto' }}>Retry</button>
          </div>
        )}

        <div key={activePage}>{renderPage()}</div>
      </div>

      <AiChatPanel isOpen={chatOpen} onClose={() => setChatOpen(false)} />

      {!chatOpen && (
        <button className="chat-fab" onClick={() => setChatOpen(true)} title="AI Assistant">
          <span className="material-symbols-outlined">smart_toy</span>
        </button>
      )}

      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast ${t.type}`}>
            <span className="material-symbols-outlined toast-icon">
              {t.type === 'success' ? 'check_circle' : t.type === 'error' ? 'error' : t.type === 'warning' ? 'warning' : 'info'}
            </span>
            <span className="toast-text">{t.text}</span>
            <button className="toast-close" onClick={() => setToasts(p => p.filter(x => x.id !== t.id))}>×</button>
          </div>
        ))}
      </div>
    </div>
  )
}
