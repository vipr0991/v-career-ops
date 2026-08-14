const PIPELINE_STEPS = [
  {
    name: 'ag-tailor',
    desc: 'Tailoring resume content to match JD keywords & requirements',
    icon: '✏️',
  },
  {
    name: 'ag-latex',
    desc: 'Generating tailored LaTeX code from template',
    icon: '📝',
  },
  {
    name: 'PDF Compile',
    desc: 'Compiling LaTeX → PDF via generate-latex.mjs',
    icon: '📄',
  },
]

export default function OptimizePanel({ data, loading }) {
  const getStatus = (idx) => {
    if (loading) {
      if (idx === 0) return 'running'
      return 'pending'
    }
    if (data) {
      if (data.pipeline) {
        const step = data.pipeline[idx] || ''
        if (step.includes('✓')) return 'done'
        if (step.includes('pending')) return 'pending'
      }
      return 'done'
    }
    return 'pending'
  }

  return (
    <div className="optimize-panel" id="optimize-panel">
      <h2 style={{ fontSize: 18, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
        ✨ Resume Optimization Pipeline
      </h2>

      <div className="optimize-steps">
        {PIPELINE_STEPS.map((step, idx) => {
          const status = getStatus(idx)
          return (
            <div className={`opt-step ${status}`} key={step.name}>
              <div className="opt-step-icon">
                {status === 'running' ? <span className="spinner"></span> :
                 status === 'done' ? '✅' : step.icon}
              </div>
              <div className="opt-step-text">
                <div className="opt-step-name">{step.name}</div>
                <div className="opt-step-desc">{step.desc}</div>
              </div>
              <div className="opt-step-status">
                {status === 'running' ? 'PROCESSING' :
                 status === 'done' ? 'COMPLETE' : 'WAITING'}
              </div>
            </div>
          )
        })}
      </div>

      {data?.tailored_text && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 8, color: 'var(--accent-success)' }}>
            ✅ Tailored Resume Preview
          </h3>
          <div style={{
            background: 'var(--bg-input)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: 16,
            fontSize: 13,
            fontFamily: 'var(--font-mono)',
            color: 'var(--text-secondary)',
            maxHeight: 300,
            overflowY: 'auto',
            lineHeight: 1.6,
            whiteSpace: 'pre-wrap',
          }}>
            {data.tailored_text.substring(0, 2000)}
            {data.tailored_text.length > 2000 && '\n\n... [truncated]'}
          </div>
        </div>
      )}

      {data?.latex?.tex_path && (
        <div style={{ marginTop: 12, fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
          📁 LaTeX saved to: {data.latex.tex_path}
        </div>
      )}
    </div>
  )
}
