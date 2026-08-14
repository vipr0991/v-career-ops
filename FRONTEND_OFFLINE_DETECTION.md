# Frontend Update: Better Offline Detection & Messages

When LiteLLM is offline, show helpful message instead of generic error.

## File: `dashboard-web/src/App.jsx`

Update the `handleScoreJob` function to show which fallback agent is being used:

```javascript
const handleScoreJob = async (job) => {
  setScoringJobId(job.id)
  setSelectedJob(null)
  addToast(`Evaluating ${job.title} at ${job.company}...`, 'info')

  try {
    const res = await fetch(`${API_BASE}/api/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_description: job.description,
        job_title: job.title,
        company: job.company,
        location: job.location,
        url: job.url,
      }),
    })
    
    if (res.ok) {
      const data = await res.json()
      
      // ✅ NEW: Show which agent was used
      const agent = data.source_agent || 'Unknown agent'
      const agentEmoji = agent.includes('LiteLLM') ? '⚡' : 
                        agent.includes('Gemini') ? '🔷' :
                        agent.includes('Kimi') ? '🌙' :
                        agent.includes('Ollama') ? '🦙' : '📊'
      
      addToast(`✅ Scored via ${agentEmoji} ${agent}`, 'success')
      setSelectedJob(data)
      refreshData()
    } else if (res.status === 503) {
      // ✅ NEW: 503 means all services down, but fallback will score
      addToast('LiteLLM offline. Using local fallback scoring (score: neutral)', 'warning')
      const data = await res.json()
      setSelectedJob(data)
      refreshData()
    } else {
      const err = await res.json().catch(() => ({}))
      addToast(err.detail || `Error ${res.status}: ${res.statusText}`, 'error')
    }
  } catch (error) {
    const msg = error.message || String(error)
    if (msg.includes('Failed to fetch')) {
      addToast('Cannot reach backend on :5000. Is FastAPI running?', 'error')
    } else {
      addToast(`Error: ${msg}`, 'error')
    }
  } finally {
    setScoringJobId(null)
  }
}
```

This shows users:
- ⚡ When using LiteLLM
- 🔷 When using Gemini
- 🌙 When using Kimi
- 🦙 When using Ollama
- 📊 When using fallback
