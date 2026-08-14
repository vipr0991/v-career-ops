import ScoreRing from './ScoreRing'

const CATEGORY_LABELS = {
  skills_match: 'Skills',
  experience_match: 'Experience',
  industry_fit: 'Industry',
  location_fit: 'Location',
  seniority_match: 'Seniority',
}

export default function ScoreDetail({ scoreData, job, onOptimize, onApply, loading }) {
  if (!scoreData) return null

  const cats = scoreData.category_scores || {}
  const level = (v) => v >= 70 ? 'high' : v >= 45 ? 'medium' : 'low'

  return (
    <div className="score-detail" id="score-detail-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>
            📊 Match Analysis — {job.company}
          </h2>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>{job.title}</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <ScoreRing score={scoreData.overall_score} size={72} />
          <span className={`rec-badge ${scoreData.recommendation || 'consider'}`}>
            {scoreData.recommendation || 'Consider'}
          </span>
        </div>
      </div>

      <div className="score-categories">
        {Object.entries(CATEGORY_LABELS).map(([key, label]) => {
          const val = cats[key] ?? 0
          return (
            <div className="score-cat" key={key}>
              <div className="score-cat-label">{label}</div>
              <div className="score-bar">
                <div
                  className={`score-bar-fill ${level(val)}`}
                  style={{ width: `${val}%` }}
                />
              </div>
              <div className={`score-cat-value`} style={{ color: `var(--accent-${level(val) === 'high' ? 'success' : level(val) === 'medium' ? 'warning' : 'danger'})` }}>
                {val}%
              </div>
            </div>
          )
        })}
      </div>

      <div className="score-insights">
        <div className="insight-col strengths">
          <h4>✅ Strengths</h4>
          {(scoreData.strengths || []).map((s, i) => (
            <div className="insight-item" key={i}>
              <span className="dot"></span>
              <span>{s}</span>
            </div>
          ))}
        </div>
        <div className="insight-col gaps">
          <h4>⚠️ Gaps</h4>
          {(scoreData.gaps || []).map((g, i) => (
            <div className="insight-item" key={i}>
              <span className="dot"></span>
              <span>{g}</span>
            </div>
          ))}
        </div>
      </div>

      {scoreData.summary && (
        <p style={{ marginTop: 16, fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          💡 {scoreData.summary}
        </p>
      )}

      <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
        <button
          className="btn btn-primary"
          onClick={onOptimize}
          disabled={loading.optimize}
          id="optimize-from-score"
        >
          {loading.optimize ? <><span className="spinner"></span> Optimizing...</> : <>✨ Optimize Resume</>}
        </button>
        <button
          className="btn btn-success"
          onClick={onApply}
          disabled={loading.apply}
          id="apply-from-score"
        >
          {loading.apply ? <><span className="spinner"></span> Applying...</> : <>🚀 Apply Now</>}
        </button>
      </div>
    </div>
  )
}
