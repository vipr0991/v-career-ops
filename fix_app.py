import re

with open(r'C:\Users\ASUS\Downloads\Career-Ops\career-ops\dashboard-web\src\App.jsx', 'r') as f:
    content = f.read()

# Replace handleOptimizeResume function
old_fn = r'''// ─── Optimize Resume ──────────────────────────────
  const handleOptimizeResume = async \(job\) => \{
    setOptimizingJob\(job\)
    setOptimizeStep\(1\)
    setOptimizeResult\(null\)
    addToast\('Initiating optimization pipeline\.\.\.', 'info'\)

    try \{
      const res = await fetchWithRetry\(`\$\{API_BASE\}/api/optimize`, \{
        method: 'POST',
        headers: \{ 'Content-Type': 'application/json' \},
        body: JSON\.stringify\(\{ job_description: job\.description \|\| job\.jd_content \}\),
      \}\)
      if \(res\.ok\) \{
        const data = await res\.json\(\)
        setOptimizeResult\(data\)
        setOptimizeStep\(4\)
        addToast\('Resume tailored & compiled successfully!', 'success'\)
        refreshData\(\)
      \} else \{
        const err = await res\.json\(\)\.catch\(\(\) => \(\{\}\)\)
        addToast\(err\.detail \|\| 'Optimization failed', 'error'\)
        setOptimizeStep\(0\)
      \}
    \} catch \{
      addToast\('Optimization failed: backend offline', 'error'\)
      setOptimizeStep\(0\)
    \}
  \}'''

new_fn = '''// ─── Optimize Resume ──────────────────────────────
  const handleOptimizeResume = async (job) => {
    setOptimizingJob(job)
    setOptimizeStep(1)
    setOptimizeResult(null)
    addToast('Initiating optimization pipeline...', 'info')

    try {
      const res = await fetchWithRetry(`${API_BASE}/api/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
        addToast('Resume tailored & compiled successfully!', 'success')
        refreshData()
      } else {
        const err = await res.json().catch(() => ({}))
        addToast(err.detail || 'Optimization failed', 'error')
        setOptimizeStep(0)
      }
    } catch (error) {
      addToast(`Tailor Resume failed: ${error.message || 'backend offline'}`, 'error')
      setOptimizeStep(0)
    }
  }'''

# Find and replace
start = content.find('// ─── Optimize Resume')
if start > -1:
    end = content.find('// ─── Apply', start)
    if end > -1:
        content = content[:start] + new_fn + '\n\n  ' + content[end:]

with open(r'C:\Users\ASUS\Downloads\Career-Ops\career-ops\dashboard-web\src\App.jsx', 'w') as f:
    f.write(content)

print("Fixed handleOptimizeResume function")
