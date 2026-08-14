export default function Navbar({ apiOnline, candidateName }) {
  const initials = (candidateName || 'VP')
    .split(' ')
    .map(w => w[0])
    .join('')
    .toUpperCase()

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div className="navbar-logo">C</div>
        <div>
          <div className="navbar-title">Career-Ops</div>
          <div className="navbar-subtitle">AI-Powered Job Pipeline</div>
        </div>
      </div>

      <div className="navbar-right">
        <div className="navbar-status">
          <span className={`status-dot ${apiOnline ? '' : 'offline'}`}></span>
          <span>{apiOnline ? 'API Online' : 'API Offline'}</span>
        </div>
        <div className="navbar-status">
          <span className={`status-dot ${apiOnline ? '' : 'offline'}`}></span>
          <span>LiteLLM :4000</span>
        </div>
        <div className="navbar-avatar" title={candidateName || 'User'}>
          {initials}
        </div>
      </div>
    </nav>
  )
}
