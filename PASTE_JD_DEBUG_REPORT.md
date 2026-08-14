# 🔍 Paste JD Button - Root Cause Analysis & Fix

## Executive Summary

**The "Paste JD" button DOES work** — it opens the modal correctly. However, when you submit the form by clicking "Score Listing", the scoring fails with a **503 Service Unavailable** error.

**Root Cause**: LiteLLM proxy is not running on port 4000, so the scoring AI cannot be reached.

**Error 2** (Chrome Extension message) is unrelated — it's from DevTools analysis tools, not the button itself.

---

## Problem Breakdown

### What Works ✅
1. **Button click** → Modal opens ✅
2. **Form submission** → `handleAddCustomJd()` is called ✅
3. **Mock job created** → Job object built correctly ✅
4. **onScoreJob called** → Function triggered ✅

### What Fails ❌
5. **HTTP Request to /api/score** → Reaches FastAPI backend on :5000 ✅
6. **Backend calls LiteLLM** → Tries to reach `http://localhost:4000/v1/chat/completions` ❌
7. **LiteLLM response** → **PORT 4000 NOT LISTENING** → 503 error returned
8. **Frontend error handling** → Catch block executes but no user feedback ❌

---

## Error Flow

```
Click "Paste JD" button
  ↓
Modal opens (WORKS ✅)
  ↓
Fill form fields
  ↓
Click "Score Listing" button
  ↓
Form submits → handleAddCustomJd()
  ↓
Call onScoreJob(mockJob)
  ↓
Fetch to /api/score
  ↓
FastAPI receives request
  ↓
FastAPI calls: httpx.post('http://localhost:4000/v1/chat/completions')
  ↓
Connection refused OR timeout → 503 returned
  ↓
Frontend catch block: addToast('Evaluation failed: LiteLLM or backend unreachable', 'error')
  ↓
User sees generic error message (not specific enough)
```

---

## The Two Errors You Reported

### Error 1: 503 Service Unavailable ⚠️

**When**: Clicking "Score Listing" after pasting a JD
**Response**: `"the server responded with a status of 503 (Service Unavailable)"`
**Root Cause**: LiteLLM proxy NOT running on port 4000

**Solution**: Start LiteLLM proxy in a separate terminal:
```bash
python -m litellm.proxy.proxy --config litellm_config.yaml --port 4000
```

### Error 2: "listener indicated async response..." 🟢

**What It Is**: Chrome DevTools helper function error
**Impact**: NONE — doesn't affect button functionality
**Cause**: Your browser dev tools tried to use `getEventListeners()` to inspect the button
**Explanation**: This only appears in DevTools console when analyzing; doesn't affect runtime

---

## Quick Fixes

### Fix 1: Start LiteLLM Proxy (IMMEDIATE FIX)

```bash
# Terminal 1: LiteLLM Proxy
python -m litellm.proxy.proxy --config litellm_config.yaml --port 4000

# Terminal 2: FastAPI Backend
cd career-ops && python career_ops_api.py

# Terminal 3: Frontend Vite
cd career-ops/dashboard-web && npm run dev

# Terminal 4: Test in Browser
# Open: http://localhost:5173
# Go to: Jobs page
# Click: "Paste JD" button
# Fill form and click "Score Listing"
```

**Expected Result**: ✅ Job scored successfully, modal closes, score displayed

### Fix 2: Better Error Messages (FRONTEND CODE)

The frontend error handling is too generic. Here's the improved version:

**File**: `dashboard-web/src/App.jsx`
**Location**: Find `const handleScoreJob = async (job) => {`
**Replace with**:

```javascript
const handleScoreJob = async (job) => {
  setScoringJobId(job.id)
  setSelectedJob(null)
  addToast(`Evaluating match for ${job.title} at ${job.company}...`, 'info')

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
    
    // Check for 503 (LiteLLM unavailable)
    if (res.status === 503) {
      addToast(
        '❌ LiteLLM proxy offline. Start: python -m litellm.proxy.proxy --config litellm_config.yaml --port 4000',
        'error'
      )
      setScoringJobId(null)
      return
    }
    
    if (res.ok) {
      const data = await res.json()
      addToast('✅ Evaluation complete', 'success')
      setSelectedJob(data)
      refreshData()
    } else {
      const err = await res.json().catch(() => ({}))
      addToast(
        `❌ Error (${res.status}): ${err.detail || res.statusText}`,
        'error'
      )
    }
  } catch (error) {
    const msg = error.message || String(error)
    if (msg.includes('Failed to fetch')) {
      addToast(
        '❌ Cannot reach backend. Ensure: 1) FastAPI on :5000, 2) LiteLLM on :4000',
        'error'
      )
    } else if (msg.includes('timeout')) {
      addToast('❌ Request timed out. Try again in a moment.', 'error')
    } else {
      addToast(`❌ Error: ${msg}`, 'error')
    }
  } finally {
    setScoringJobId(null)
  }
}
```

### Fix 3: Add Retry Logic (RESILIENCE)

Optional: Make the Paste JD feature more resilient with retries:

```javascript
// Add this helper function before handleScoreJob
const fetchWithRetry = async (url, options, maxRetries = 3, backoff = 1000) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, options)
      if (res.status !== 503) return res
      if (attempt < maxRetries) {
        addToast(`Retry ${attempt}/${maxRetries - 1}...`, 'info')
        await new Promise(r => setTimeout(r, backoff * attempt))
      }
    } catch (err) {
      if (attempt === maxRetries) throw err
      await new Promise(r => setTimeout(r, backoff * attempt))
    }
  }
}
```

Then in `handleScoreJob`, replace the fetch call:
```javascript
const res = await fetchWithRetry(`${API_BASE}/api/score`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({...}),
})
```

---

## Complete Diagnosis Checklist

Run this checklist to verify all services are running:

### 1. Check LiteLLM Proxy
```bash
# Terminal command
curl -s http://localhost:4000/v1/models | head -20

# Expected: JSON response with model list
# If error: LiteLLM not running
```

### 2. Check FastAPI Backend
```bash
curl -s http://localhost:5000/api/stats | head -20

# Expected: JSON response with stats
# If error: FastAPI not running
```

### 3. Check Frontend
```bash
# Browser DevTools → Network tab
# Click "Paste JD" → "Score Listing"
# Look for:
#   - POST to http://localhost:5000/api/score (should get 503 if LiteLLM is down)
#   - If you see 200: Success
#   - If you see 503: LiteLLM is the problem
```

---

## The Button Code (What Actually Works)

Here's the exact code in `JobsPage.jsx` that makes the button work:

```jsx
<button className="btn btn-secondary btn-sm" onClick={() => setShowAddJdModal(true)}>
  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>add</span>
  Paste JD
</button>
```

This button opens the modal via: `setShowAddJdModal(true)` ✅

The modal form calls:
```jsx
const handleAddCustomJd = (e) => {
  e.preventDefault()
  if (!newJdText || !newJdTitle || !newJdCompany) {
    addToast('Please fill out all fields', 'warning')
    return
  }
  const mockJob = {
    id: `custom-${Date.now()}`,
    title: newJdTitle,
    company: newJdCompany,
    location: newJdLocation || 'Remote',
    description: newJdText,
    url: 'Custom Paste'
  }
  setShowAddJdModal(false)
  onScoreJob(mockJob)  // ← This is where it goes to App.jsx
  setNewJdText('')
  setNewJdTitle('')
  setNewJdCompany('')
  setNewJdLocation('')
}
```

The `onScoreJob` is passed from `App.jsx` → `JobsPage.jsx` as a prop. ✅

---

## Summary

| Issue | Cause | Fix | Difficulty |
|-------|-------|-----|------------|
| **503 Error** | LiteLLM offline on :4000 | Start LiteLLM proxy | ⭐ (Easy) |
| **Bad Error Message** | Generic catch block | Update error handling | ⭐⭐ (Medium) |
| **Chrome DevTools Error** | Not a real bug | Ignore (harmless) | N/A |

---

## Next Steps

1. **Start all three services** (LiteLLM, FastAPI, Frontend)
2. **Test Paste JD button** → Fill form → Click "Score Listing"
3. **Verify success** → Score should appear, modal should close
4. **Optional**: Apply Fix 2 code for better error messages

All three services MUST be running for scoring to work:
- **LiteLLM**: `python -m litellm.proxy.proxy --config litellm_config.yaml --port 4000`
- **FastAPI**: `python career_ops_api.py`
- **Frontend**: `npm run dev` (in dashboard-web)

---

## Files to Review

- `dashboard-web/src/App.jsx` — Contains `handleScoreJob()` (line ~180)
- `dashboard-web/src/pages/JobsPage.jsx` — Contains "Paste JD" button code
- `career_ops_api.py` — Contains `/api/score` endpoint (calls LiteLLM)

---

**Status**: ✅ **ROOT CAUSE IDENTIFIED**

**The Paste JD button works. The scoring fails because LiteLLM is not running.**

Start LiteLLM proxy and it will work immediately.
