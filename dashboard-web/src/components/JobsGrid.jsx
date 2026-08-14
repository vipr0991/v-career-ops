import JobCard from './JobCard'

export default function JobsGrid({ jobs, selectedJob, onScore, onOptimize, onApply, loadingScore }) {
  if (!jobs.length) return null

  return (
    <div className="jobs-section">
      <div className="section-header">
        <div className="section-title">
          📋 Job Listings
        </div>
        <span className="section-count">{jobs.length} results</span>
      </div>

      <div className="jobs-grid">
        {jobs.map(job => (
          <JobCard
            key={job.id}
            job={job}
            isSelected={selectedJob?.id === job.id}
            onScore={onScore}
            onOptimize={onOptimize}
            onApply={onApply}
            loadingScore={loadingScore && selectedJob?.id === job.id}
          />
        ))}
      </div>
    </div>
  )
}
