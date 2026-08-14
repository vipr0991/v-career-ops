const API_BASE = 'http://localhost:5000'

async function fetchWithRetry(url, options = {}, retries = 3) {
  const response = await fetch(url, options);
  if (response.status === 503 && retries > 0) {
    const delay = Math.pow(2, 4 - retries) * 1000; // Exponential backoff: 2s, 4s, 8s
    await new Promise(res => setTimeout(res, delay));
    return fetchWithRetry(url, options, retries - 1);
  }
  return response;
}

export async function fetchProfile() {
  const res = await fetchWithRetry(`${API_BASE}/api/profile`)
  if (!res.ok) throw new Error('Failed to fetch profile')
  return res.json()
}

export async function fetchJobs() {
  const res = await fetchWithRetry(`${API_BASE}/api/jobs`)
  if (!res.ok) throw new Error('Failed to fetch jobs')
  return res.json()
}

export async function fetchStats() {
  const res = await fetchWithRetry(`${API_BASE}/api/stats`)
  if (!res.ok) throw new Error('Failed to fetch stats')
  return res.json()
}

export async function searchJobs(filters) {
  const res = await fetchWithRetry(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(filters),
  })
  if (!res.ok) throw new Error('Search failed')
  return res.json()
}

export async function scoreJob(data) {
  const res = await fetchWithRetry(`${API_BASE}/api/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Scoring failed')
  return res.json()
}

export async function optimizeResume(data) {
  const res = await fetchWithRetry(`${API_BASE}/api/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Optimization failed')
  return res.json()
}

export async function applyToJob(data) {
  const res = await fetchWithRetry(`${API_BASE}/api/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Apply failed')
  return res.json()
}

export async function convertCurrency(amount, fromCurrency) {
  const res = await fetchWithRetry(`${API_BASE}/api/currency`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount, from_currency: fromCurrency }),
  })
  if (!res.ok) throw new Error('Currency conversion failed')
  return res.json()
}

// ─── NEW API FUNCTIONS ──────────────────────────────────

export async function chatWithKimi(message, context = '') {
  const res = await fetchWithRetry(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, context }),
  })
  if (!res.ok) throw new Error('Chat failed')
  return res.json()
}

export async function fetchPipeline() {
  const res = await fetchWithRetry(`${API_BASE}/api/pipeline`)
  if (!res.ok) throw new Error('Failed to fetch pipeline')
  return res.json()
}

export async function updatePipelineStatus(id, status) {
  const res = await fetchWithRetry(`${API_BASE}/api/pipeline/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
  if (!res.ok) throw new Error('Pipeline update failed')
  return res.json()
}

export async function generateInterviewPrep(data) {
  const res = await fetchWithRetry(`${API_BASE}/api/interview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Interview prep failed')
  return res.json()
}

export async function uploadResume(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetchWithRetry(`${API_BASE}/api/upload-resume`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error('Upload failed')
  return res.json()
}

export async function listResumes() {
  const res = await fetchWithRetry(`${API_BASE}/api/resumes`)
  if (!res.ok) throw new Error('Failed to list resumes')
  return res.json()
}

export async function fetchModels() {
  const res = await fetchWithRetry(`${API_BASE}/api/models`)
  if (!res.ok) throw new Error('Failed to fetch models')
  return res.json()
}

// ─── SerpAPI Real Job Search ─────────────────────────────

export async function searchLiveJobs(filters) {
  const res = await fetchWithRetry(`${API_BASE}/api/search-live`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(filters),
  })
  if (!res.ok) throw new Error('Live search failed')
  return res.json()
}

// ─── Portal Scanner ──────────────────────────────────────

export async function runScan(dryRun = true, company = null) {
  const res = await fetchWithRetry(`${API_BASE}/api/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dry_run: dryRun, company }),
  })
  if (!res.ok) throw new Error('Scan failed')
  return res.json()
}

// ─── Health Check ────────────────────────────────────────

export async function fetchDoctor() {
  const res = await fetchWithRetry(`${API_BASE}/api/doctor`)
  if (!res.ok) throw new Error('Doctor check failed')
  return res.json()
}

// ─── Company Career Pages Search ──────────────────────────────────────

export async function searchCompanyCareers(filters) {
  const res = await fetchWithRetry(`${API_BASE}/api/search-company-careers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(filters),
  })
  if (!res.ok) throw new Error('Company career page search failed')
  return res.json()
}

// ─── Delete Functions ─────────────────────────────────────────────────────

export async function deleteJob(jobId) {
  const res = await fetchWithRetry(`${API_BASE}/api/jobs?job_id=${encodeURIComponent(jobId)}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
  })
  if (!res.ok) throw new Error('Failed to delete job')
  return res.json()
}

export async function deletePipelineItem(itemId) {
  const res = await fetchWithRetry(`${API_BASE}/api/pipeline?item_id=${encodeURIComponent(itemId)}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
  })
  if (!res.ok) throw new Error('Failed to delete pipeline item')
  return res.json()
}

export async function deleteResume(filename) {
  const res = await fetchWithRetry(`${API_BASE}/api/resumes?filename=${encodeURIComponent(filename)}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
  })
  if (!res.ok) throw new Error('Failed to delete resume')
  return res.json()
}
