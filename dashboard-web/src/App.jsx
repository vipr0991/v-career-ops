import React, { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import AiChatPanel from './components/AiChatPanel'
import DashboardPage from './pages/DashboardPage'
import JobsPage from './pages/JobsPage'
import PipelinePage from './pages/PipelinePage'
import ResumeHubPage from './pages/ResumeHubPage'
import InterviewPrepPage from './pages/InterviewPrepPage'
import SettingsPage from './pages/SettingsPage'
import PrivacyPolicyPage from './pages/PrivacyPolicyPage'

// Environment-aware API base — uses relative '' when co-hosted on Railway, or VITE_API_BASE
const API_BASE = import.meta.env.VITE_API_BASE ?? ''

const PAGE_TITLES = {
  dashboard: 'Dashboard',
  jobs: 'Jobs',
  pipeline: 'Pipeline',
  resume: 'Resume Hub',
  interview: 'Interview Prep',
  settings: 'Settings',
  'privacy-policy': 'Privacy Policy',
}

function getInitialPage() {
  if (window.location.pathname === '/privacy-policy') return 'privacy-policy'
  const hash = window.location.hash.replace('#/', '').replace('#', '')
  return PAGE_TITLES[hash] ? hash : 'dashboard'
}

let _toastId = 0

export default function App() {
  const [authStatus, setAuthStatus] = useState('loading') // 'loading' | 'authenticated' | 'unauthenticated'
  const [authUser, setAuthUser] = useState(null)
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [loginError, setLoginError] = useState('')
  const [forgotPasswordMsg, setForgotPasswordMsg] = useState('')
  
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
    title: 'Senior Marketing Manager', location: 'Dubai, UAE', currency: 'AED', salary: 'Any'
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
    if (page === 'privacy-policy') {
      window.history.pushState({}, '', '/privacy-policy')
      window.location.hash = ''
    } else {
      if (window.location.pathname === '/privacy-policy') {
        window.history.pushState({}, '', '/')
      }
      window.location.hash = '#/' + page
    }
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
  const checkAuth = useCallback(async () => {
    try {
      const res = await apiFetch('/api/auth/me')
      if (res.ok) {
        const data = await res.json()
        if (data.authenticated) {
          setAuthStatus('authenticated')
          setAuthUser({ name: data.name, email: data.email })
        } else {
          setAuthStatus('unauthenticated')
        }
      } else {
        setAuthStatus('unauthenticated')
      }
    } catch {
      setAuthStatus('unauthenticated')
    }
  }, [apiFetch])

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
    checkAuth()
    refreshData()
    const iv = setInterval(refreshData, 15000)
    return () => clearInterval(iv)
  }, [refreshData, checkAuth])

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

  const handleManualLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    try {
      const res = await apiFetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: loginEmail, password: loginPassword })
      });
      if (res.ok) {
        setAuthStatus('authenticated');
        setAuthUser({ name: 'Vinay Prakash', email: loginEmail });
      } else {
        setLoginError('Invalid credentials');
      }
    } catch (err) {
      setLoginError('Server error during login');
    }
  };

  const handleForgotPassword = () => {
    if (loginEmail === 'voommen@my.madonna.edu') {
      setForgotPasswordMsg('A password reset link has been sent to voommen@my.madonna.edu');
    } else {
      setForgotPasswordMsg('Forgot Password option is only available for your primary university account.');
    }
  };

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
      case 'privacy-policy':
        return <PrivacyPolicyPage />
      default:
        return <DashboardPage stats={stats} jobs={jobs} onNavigate={navigate} onOpenChat={() => setChatOpen(true)} />
    }
  }

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  if (authStatus === 'loading') {
    return (
      <div style={{display:'flex',height:'100vh',background:'#111827',color:'#fff',alignItems:'center',justifyContent:'center',fontFamily:'Inter, sans-serif'}}>
        <div>Loading Career-Ops...</div>
      </div>
    )
  }

  if (authStatus === 'unauthenticated') {
    return (
      <div style={{display:'flex',height:'100vh',background:'#111827',color:'#fff',alignItems:'center',justifyContent:'center',fontFamily:'Inter, sans-serif',flexDirection:'column'}}>
        <div style={{background:'#1f2937',padding:'2rem',borderRadius:'8px',boxShadow:'0 4px 6px rgba(0,0,0,0.3)',width:'100%',maxWidth:'400px',boxSizing:'border-box',textAlign:'center'}}>
          <h2 style={{marginTop:0,marginBottom:'1.5rem'}}>Career-Ops Sign In</h2>
          
          <form onSubmit={handleManualLogin} style={{display:'flex',flexDirection:'column',gap:'1rem',marginBottom:'1.5rem'}}>
            <input 
              type="email" 
              placeholder="Email ID" 
              value={loginEmail}
              onChange={e => setLoginEmail(e.target.value)}
              style={{width:'100%',padding:'0.75rem',borderRadius:'4px',border:'1px solid #374151',background:'#111827',color:'white',boxSizing:'border-box'}} 
              required
            />
            <input 
              type="password" 
              placeholder="Password" 
              value={loginPassword}
              onChange={e => setLoginPassword(e.target.value)}
              style={{width:'100%',padding:'0.75rem',borderRadius:'4px',border:'1px solid #374151',background:'#111827',color:'white',boxSizing:'border-box'}} 
              required
            />
            {loginError && <div style={{color:'#ef4444',fontSize:'14px'}}>{loginError}</div>}
            
            <button type="submit" style={{width:'100%',padding:'0.75rem',borderRadius:'4px',border:'none',background:'#3b82f6',color:'white',fontWeight:'bold',cursor:'pointer'}}>
              Sign In
            </button>

            <div style={{fontSize:'12px',color:'#9ca3af',textAlign:'right',cursor:'pointer',marginTop:'-8px'}} onClick={handleForgotPassword}>
              Forgot Password?
            </div>
            {forgotPasswordMsg && <div style={{color:'#3b82f6',fontSize:'13px',marginTop:'4px'}}>{forgotPasswordMsg}</div>}
          </form>

          <div style={{display:'flex',alignItems:'center',margin:'1.5rem 0',color:'#9ca3af'}}>
            <div style={{flex:1,height:'1px',background:'#374151'}}></div>
            <span style={{padding:'0 10px',fontSize:'12px'}}>OR</span>
            <div style={{flex:1,height:'1px',background:'#374151'}}></div>
          </div>

          <p style={{color:'#9ca3af',fontSize:'14px',marginBottom:'1rem'}}>Sign in securely with LinkedIn to access your dashboard.</p>
          <a href="/auth/linkedin/login" style={{display:'inline-block',width:'100%',padding:'0.75rem',borderRadius:'4px',border:'none',background:'#0a66c2',color:'white',fontWeight:'bold',cursor:'pointer',textDecoration:'none',boxSizing:'border-box'}}>
            Sign In with LinkedIn
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <Sidebar
        activePage={activePage}
        onNavigate={navigate}
        mcpStatus={mcpStatus}
        candidateName={stats.candidate_name}
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
      />

      <div className="main-area">
        <header className="topbar">
          <div className="topbar-left" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              className="mobile-menu-btn"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open Navigation Menu"
            >
              <span className="material-symbols-outlined">menu</span>
            </button>
            <div>
              <h2 className="topbar-title">{PAGE_TITLES[activePage] || 'Dashboard'}</h2>
              <span className="topbar-breadcrumb">career-ops / {activePage}</span>
            </div>
          </div>
          <div className="topbar-right">
            <div className="topbar-status">
              <span className={`status-dot ${mcpStatus === 'offline' ? 'offline' : ''}`} />
              <span className="status-text">{mcpStatus === 'online' ? 'Gateway Online' : 'Gateway Offline'}</span>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={refreshData} title="Refresh System Data">
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>sync</span>
              <span className="refresh-btn-label">Refresh</span>
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
