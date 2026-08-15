/**
 * Resilient API Client with Dynamic Connection Strategy
 * Handles network failures, connection resets, and auto-reconnection
 */

// Multi-strategy API endpoint discovery
const API_ENDPOINTS = [
  import.meta.env.VITE_API_BASE ?? '',
  'http://localhost:5000',
  'http://127.0.0.1:5000',
];

let currentEndpointIndex = 0;
let connectionState = {
  isOnline: navigator.onLine,
  isRetrying: false,
  lastAttemptTime: 0,
  failureCount: 0,
  successCount: 0,
  currentEndpoint: API_ENDPOINTS[0],
};

// Listen for network changes
window.addEventListener('online', handleOnline);
window.addEventListener('offline', handleOffline);

function handleOnline() {
  console.log('[API] Network is online');
  connectionState.isOnline = true;
  connectionState.failureCount = 0;
  currentEndpointIndex = 0;
  connectionState.currentEndpoint = API_ENDPOINTS[0];
}

function handleOffline() {
  console.log('[API] Network is offline');
  connectionState.isOnline = false;
}

/**
 * Get next API endpoint (round-robin failover)
 */
function getNextEndpoint() {
  currentEndpointIndex = (currentEndpointIndex + 1) % API_ENDPOINTS.length;
  connectionState.currentEndpoint = API_ENDPOINTS[currentEndpointIndex];
  console.log(`[API] Switching to endpoint: ${connectionState.currentEndpoint}`);
  return connectionState.currentEndpoint;
}

/**
 * Check if we should retry based on connection state
 */
function shouldRetry(retryCount, error) {
  if (retryCount > 5) return false; // Max 5 retries
  if (!connectionState.isOnline && retryCount > 2) return false; // Offline - limit retries
  
  const isNetworkError = error instanceof TypeError ||
                        error?.message?.includes('fetch') ||
                        error?.message?.includes('network') ||
                        error?.message?.includes('ECONNREFUSED') ||
                        error?.message?.includes('timeout');
  
  return isNetworkError;
}

/**
 * Calculate exponential backoff with jitter
 */
function getBackoffDelay(retryCount) {
  const baseDelay = Math.pow(2, retryCount) * 1000; // 1s, 2s, 4s, 8s, 16s...
  const jitter = Math.random() * 1000; // Up to 1s random jitter
  const maxDelay = 32000; // Cap at 32 seconds
  return Math.min(baseDelay + jitter, maxDelay);
}

/**
 * Core fetch with retry logic and connection strategy
 */
async function fetchWithDynamicStrategy(url, options = {}, retryCount = 0) {
  const maxRetries = 5;
  const timeout = options.timeout || 30000;

  try {
    // Check if network is available
    if (!connectionState.isOnline) {
      console.warn('[API] Network offline - attempting request anyway');
    }

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    // Try current endpoint
    let response;
    try {
      response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {}),
        },
      });
      clearTimeout(timeoutId);
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }

    // Handle 503 (service unavailable) with retry
    if (response.status === 503 && retryCount < maxRetries) {
      console.warn(`[API] Service unavailable (503), retry ${retryCount + 1}/${maxRetries}`);
      const delay = getBackoffDelay(retryCount);
      await new Promise(res => setTimeout(res, delay));
      return fetchWithDynamicStrategy(url, options, retryCount + 1);
    }

    // Handle connection refused - switch endpoint
    if (!response.ok && retryCount < maxRetries) {
      const isConnectionError = response.status === 0 || 
                               response.type === 'error' ||
                               !response.headers;
      
      if (isConnectionError && currentEndpointIndex < API_ENDPOINTS.length - 1) {
        console.warn(`[API] Connection failed, trying next endpoint`);
        const nextEndpoint = getNextEndpoint();
        const newUrl = url.replace(connectionState.currentEndpoint, nextEndpoint);
        const delay = getBackoffDelay(retryCount);
        await new Promise(res => setTimeout(res, delay));
        return fetchWithDynamicStrategy(newUrl, options, retryCount + 1);
      }
    }

    connectionState.successCount++;
    connectionState.failureCount = 0;
    return response;

  } catch (error) {
    console.error(`[API] Request failed (attempt ${retryCount + 1}):`, error.message);
    connectionState.failureCount++;

    if (shouldRetry(retryCount, error)) {
      const delay = getBackoffDelay(retryCount);
      console.log(`[API] Retrying in ${Math.round(delay)}ms...`);
      await new Promise(res => setTimeout(res, delay));

      // Try next endpoint if available
      if (error.message?.includes('ECONNREFUSED') || error instanceof TypeError) {
        if (currentEndpointIndex < API_ENDPOINTS.length - 1) {
          getNextEndpoint();
          const newUrl = url.replace(
            API_ENDPOINTS[(currentEndpointIndex - 1 + API_ENDPOINTS.length) % API_ENDPOINTS.length],
            connectionState.currentEndpoint
          );
          return fetchWithDynamicStrategy(newUrl, options, retryCount + 1);
        }
      }

      return fetchWithDynamicStrategy(url, options, retryCount + 1);
    }

    throw error;
  }
}

/**
 * Health check endpoint
 */
export async function checkBackendHealth() {
  try {
    const response = await fetchWithDynamicStrategy(
      `${connectionState.currentEndpoint}/api/stats`,
      { timeout: 5000 }
    );
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Get current API endpoint
 */
export function getCurrentEndpoint() {
  return connectionState.currentEndpoint;
}

/**
 * Get connection state
 */
export function getConnectionState() {
  return {
    ...connectionState,
    isNetworkOnline: navigator.onLine,
  };
}

// Export wrapped fetch for use throughout app
export { fetchWithDynamicStrategy as fetchWithRetry };

// Export individual API functions
const API_BASE = connectionState.currentEndpoint;

export async function fetchProfile() {
  const res = await fetchWithDynamicStrategy(`${connectionState.currentEndpoint}/api/profile`);
  if (!res.ok) throw new Error('Failed to fetch profile');
  return res.json();
}

export async function fetchJobs() {
  const res = await fetchWithDynamicStrategy(`${connectionState.currentEndpoint}/api/jobs`);
  if (!res.ok) throw new Error('Failed to fetch jobs');
  return res.json();
}

export async function fetchStats() {
  const res = await fetchWithDynamicStrategy(`${connectionState.currentEndpoint}/api/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function searchJobs(filters) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/search`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filters),
    }
  );
  if (!res.ok) throw new Error('Search failed');
  return res.json();
}

export async function scoreJob(data) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/score`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }
  );
  if (!res.ok) throw new Error('Scoring failed');
  return res.json();
}

export async function optimizeResume(data) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/optimize`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }
  );
  if (!res.ok) throw new Error('Optimization failed');
  return res.json();
}

export async function searchLiveJobs(filters) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/search-live`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filters),
    }
  );
  if (!res.ok) throw new Error('Live search failed');
  return res.json();
}

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/upload-resume`,
    {
      method: 'POST',
      body: formData,
    }
  );
  if (!res.ok) throw new Error('Upload failed');
  return res.json();
}

export async function listResumes() {
  const res = await fetchWithDynamicStrategy(`${connectionState.currentEndpoint}/api/resumes`);
  if (!res.ok) throw new Error('Failed to list resumes');
  return res.json();
}

export async function fetchPipeline() {
  const res = await fetchWithDynamicStrategy(`${connectionState.currentEndpoint}/api/pipeline`);
  if (!res.ok) throw new Error('Failed to fetch pipeline');
  return res.json();
}

export async function updatePipelineStatus(id, status) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/pipeline/${id}`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    }
  );
  if (!res.ok) throw new Error('Pipeline update failed');
  return res.json();
}

export async function generateInterviewPrep(data) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/interview`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }
  );
  if (!res.ok) throw new Error('Interview prep failed');
  return res.json();
}

export async function deleteJob(jobId) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/jobs?job_id=${encodeURIComponent(jobId)}`,
    { method: 'DELETE', headers: { 'Content-Type': 'application/json' } }
  );
  if (!res.ok) throw new Error('Failed to delete job');
  return res.json();
}

export async function deletePipelineItem(itemId) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/pipeline?item_id=${encodeURIComponent(itemId)}`,
    { method: 'DELETE', headers: { 'Content-Type': 'application/json' } }
  );
  if (!res.ok) throw new Error('Failed to delete pipeline item');
  return res.json();
}

export async function deleteResume(filename) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/resumes?filename=${encodeURIComponent(filename)}`,
    { method: 'DELETE', headers: { 'Content-Type': 'application/json' } }
  );
  if (!res.ok) throw new Error('Failed to delete resume');
  return res.json();
}

export async function searchCompanyCareers(filters) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/search-company-careers`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filters),
    }
  );
  if (!res.ok) throw new Error('Company career page search failed');
  return res.json();
}

export async function chatWithKimi(message, context = '') {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/chat`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, context }),
    }
  );
  if (!res.ok) throw new Error('Chat failed');
  return res.json();
}

export async function runScan(dryRun = true, company = null) {
  const res = await fetchWithDynamicStrategy(
    `${connectionState.currentEndpoint}/api/scan`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dry_run: dryRun, company }),
    }
  );
  if (!res.ok) throw new Error('Scan failed');
  return res.json();
}
