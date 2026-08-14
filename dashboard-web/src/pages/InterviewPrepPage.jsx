import React, { useState } from 'react'

const API_BASE = 'http://localhost:5000'

export default function InterviewPrepPage({ jobs, addToast }) {
  const [selectedJobId, setSelectedJobId] = useState('')
  const [prepData, setPrepData] = useState(null)
  const [loading, setLoading] = useState(false)

  const scoredJobs = (jobs || []).filter((j) => j.score != null)

  const handleGenerate = async () => {
    if (!selectedJobId) {
      addToast('Select a scored job first', 'warning')
      return
    }

    const job = scoredJobs.find((j) => j.id === selectedJobId)
    if (!job) return

    setLoading(true)
    setPrepData(null)
    addToast(`Generating interview prep for ${job.role || job.title}...`, 'info')

    try {
      const res = await fetch(`${API_BASE}/api/interview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_title: job.role || job.title,
          company: job.company,
          job_description: job.jd_content || '',
        }),
      })

      if (res.ok) {
        const data = await res.json()
        setPrepData(data)
        addToast('Interview prep generated!', 'success')
      } else {
        addToast('Failed to generate prep — LiteLLM may be offline', 'error')
        // Use fallback data
        setPrepData(getFallbackPrep(job))
      }
    } catch {
      addToast('Backend offline — showing sample prep', 'warning')
      setPrepData(getFallbackPrep(job))
    } finally {
      setLoading(false)
    }
  }

  const getFallbackPrep = (job) => ({
    company: job.company,
    role: job.role || job.title,
    questions: [
      {
        question: `Tell us about your experience with ${job.role || 'this type of role'}.`,
        star: {
          situation: 'At Business Tabloid, the editorial team needed AI-powered workflow automation to scale content output.',
          task: 'I was tasked with redesigning the entire editorial and marketing workflow using AI tools.',
          action: 'I built multi-model AI pipelines using Antigravity 2.0, Gemini, Claude, and GPT-OSS, creating repeatable web-app workflows for awards curation, copywriting, and outreach.',
          result: 'Reduced manual revision cycles by 50%+, editing effort by 60%+, and improved team AI adoption by 3x.',
        },
      },
      {
        question: 'How do you measure ROI on marketing campaigns?',
        star: {
          situation: 'At Green Earth Action Foundation, we had a $130K marketing budget with pressure to demonstrate clear ROI.',
          task: 'I needed to revamp the LinkedIn and content strategy while reducing long-term costs.',
          action: 'Implemented data-driven LinkedIn campaigns, newsletter optimization, and cross-regional engagement strategies targeting UAE-Switzerland brand alignment.',
          result: 'Increased reach by 90,000+, newsletter subscribers by 1000%, reduced long-term marketing costs by 15%, and improved cross-regional engagement by 26%.',
        },
      },
      {
        question: 'How would you train a non-technical team on AI tools?',
        star: {
          situation: 'At Business Tabloid, the team had limited exposure to AI tools and resisted adoption.',
          task: 'I needed to create accessible AI training and integrate it into daily workflows.',
          action: 'Created AI training programs and multi-model pipelines with clear documentation, making tools accessible through web-app-based workflows rather than complex CLI interfaces.',
          result: 'Improved team adoption by 3x, reduced back-and-forth edits by 70%, and lowered hands-on operational involvement to roughly 10%.',
        },
      },
    ],
  })

  return (
    <div className="page-content" id="interview-prep-page">
      {/* Job Selector */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <span className="material-symbols-outlined" style={{ color: 'var(--accent-warning)' }}>school</span>
            Interview Preparation
          </div>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
          Select a scored job to generate STAR-format interview answers powered by Kimi AI.
        </p>
        <div style={{ display: 'flex', gap: 12, alignItems: 'end' }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Select Job to Prepare For</label>
            <select
              className="form-select"
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
            >
              <option value="">— Choose a scored job —</option>
              {scoredJobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.role || job.title} at {job.company} ({Math.round(job.score)}%)
                </option>
              ))}
            </select>
          </div>
          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={!selectedJobId || loading}
          >
            {loading ? (
              <><span className="spinner" /> Generating...</>
            ) : (
              <><span className="material-symbols-outlined" style={{ fontSize: 18 }}>auto_awesome</span> Generate Prep</>
            )}
          </button>
        </div>
      </div>

      {/* Prep Results */}
      {prepData && (
        <div className="animate-fade-in">
          <div className="panel">
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>
              {prepData.role} at {prepData.company}
            </h3>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 20 }}>
              {prepData.questions?.length || 0} practice questions with STAR framework answers
            </p>

            {(prepData.questions || []).map((q, i) => (
              <div className="interview-question" key={i}>
                <h4>
                  <span style={{ color: 'var(--accent-primary-light)', marginRight: 8 }}>Q{i + 1}.</span>
                  {q.question}
                </h4>
                {q.star && (
                  <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div>
                      <div className="star-label">Situation</div>
                      <p>{q.star.situation}</p>
                    </div>
                    <div>
                      <div className="star-label">Task</div>
                      <p>{q.star.task}</p>
                    </div>
                    <div>
                      <div className="star-label">Action</div>
                      <p>{q.star.action}</p>
                    </div>
                    <div>
                      <div className="star-label">Result</div>
                      <p>{q.star.result}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!prepData && !loading && (
        <div className="empty-state" style={{ border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-lg)', marginTop: 24 }}>
          <span className="material-symbols-outlined icon">quiz</span>
          <h3>Ready to Prepare</h3>
          <p>Select a scored job above and generate AI-powered STAR format interview answers tailored to your experience.</p>
        </div>
      )}
    </div>
  )
}
