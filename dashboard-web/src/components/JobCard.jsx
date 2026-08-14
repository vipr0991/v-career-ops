import ScoreRing from './ScoreRing'

export default function JobCard({ job, isSelected, onScore, onOptimize, onApply, loadingScore }) {
  return (
    <div className={`job-card ${isSelected ? 'selected' : ''}`}>
      <div className="job-card-header">
        <div>
          <div className="job-card-title">{job.title}</div>
          <div className="job-card-company">{job.company}</div>
        </div>
        {job.score != null && (
          <ScoreRing score={job.score} />
        )}
      </div>

      <div className="job-card-meta">
        {job.location && (
          <span className="meta-tag location">📍 {job.location}</span>
        )}
        {job.salary_range && (
          <span className="meta-tag salary">💰 {job.salary_range}</span>
        )}
        {job.source && (
          <span className="meta-tag source">🔗 {job.source}</span>
        )}
        {job.posted && (
          <span className="meta-tag posted">🕐 {job.posted}</span>
        )}
      </div>

      {job.description && (
        <div className="job-card-desc">{job.description}</div>
      )}

      <div className="job-card-actions">
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => onScore(job)}
          disabled={loadingScore}
          id={`score-btn-${job.id}`}
        >
          {loadingScore && isSelected ? (
            <><span className="spinner"></span> Scoring...</>
          ) : (
            <>📊 Score</>
          )}
        </button>
        <button
          className="btn btn-primary btn-sm"
          onClick={() => onOptimize(job)}
          id={`optimize-btn-${job.id}`}
        >
          ✨ Optimize
        </button>
        <button
          className="btn btn-success btn-sm"
          onClick={() => onApply(job)}
          id={`apply-btn-${job.id}`}
        >
          🚀 Apply
        </button>
      </div>
    </div>
  )
}
