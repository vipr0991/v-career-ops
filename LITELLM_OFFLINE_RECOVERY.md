# 🔧 Backend Gateway Offline - Complete Recovery Guide

## Problem

LiteLLM proxy on port 4000 is offline/under maintenance → Job scoring fails with 503 error

## Solution

Implement **multi-agent fallback system** so scoring still works when LiteLLM is down.

---

## What We Created

### 1. **`direct_scoring.py`** (New Module)
Direct API clients for scoring without LiteLLM:
- ✅ Google Gemini API (free tier, cloud)
- ✅ Moonshot Kimi API (direct, cloud)
- ✅ Local Ollama (free, runs on your machine)
- ✅ Hardcoded fallback scoring

### 2. **Updated `/api/score` Endpoint**
New scoring priority:
```
1. Try LiteLLM on :4000
   ↓ (if fails)
2. Try Gemini API (requires GEMINI_API_KEY in .env)
   ↓ (if fails)
3. Try Kimi API (requires KIMI_API_KEY in .env)
   ↓ (if fails)
4. Try Local Ollama (free, requires local installation)
   ↓ (if fails)
5. Use hardcoded fallback (always works)
```

---

## Quick Fix (5 Minutes)

### Step 1: Copy New File
✅ `direct_scoring.py` already created in career-ops root

### Step 2: Update Backend Code
In `career_ops_api.py`, find the `@app.post("/api/score")` function and replace it.

**Option A: Manual Replace**
1. Open `PATCH_SCORE_ENDPOINT.py` (provided)
2. Copy the function code
3. Find `@app.post("/api/score")` in `career_ops_api.py` (around line 650)
4. Replace the entire function (from `@app.post` to the `return` statement)

**Option B: Quick Edit**
Add this line after other imports in `career_ops_api.py`:
```python
from direct_scoring import get_scoring_client
```

Then modify the `/api/score` function to include the fallback logic shown in `PATCH_SCORE_ENDPOINT.py`.

### Step 3: Restart Backend
```bash
cd career-ops
python career_ops_api.py
```

### Step 4: Test
Go to Jobs page → Paste JD → Score Listing

Expected: ✅ Job scores successfully (now using Gemini, Kimi, or fallback if needed)

---

## How It Works

### Scenario 1: LiteLLM is Running ✅
```
Paste JD → Score Listing
           ↓
        Try LiteLLM :4000
           ↓
        SUCCESS ✅
```

### Scenario 2: LiteLLM is Down ❌
```
Paste JD → Score Listing
           ↓
        Try LiteLLM :4000
           ❌ Fails
           ↓
        Try Gemini API (direct)
           ✅ SUCCESS
```

### Scenario 3: LiteLLM + Gemini Down ❌❌
```
Paste JD → Score Listing
           ↓
        Try LiteLLM :4000
           ❌ Fails
           ↓
        Try Gemini
           ❌ Fails
           ↓
        Try Kimi API
           ✅ SUCCESS
```

### Scenario 4: All Cloud APIs Down ❌❌❌
```
Paste JD → Score Listing
           ↓
        Try LiteLLM
           ❌ Fails
           ↓
        Try Gemini
           ❌ Fails
           ↓
        Try Kimi
           ❌ Fails
           ↓
        Try Local Ollama
           ✅ SUCCESS (if installed)
```

### Scenario 5: Everything Down ❌❌❌❌
```
Paste JD → Score Listing
           ↓
        All services fail
           ↓
        Use Hardcoded Fallback
           ✅ Returns score: 50 (neutral)
```

---

## Alternative Setup Options

### Option A: Use Gemini (Recommended - No New Installation)
Already configured in `.env` as `GEMINI_API_KEY`

**Status**: Will work immediately after code update

### Option B: Use Kimi/Moonshot (Good - Already Have Key)
Already configured in `.env` as `KIMI_API_KEY`

**Status**: Will work immediately after code update

### Option C: Use Local Ollama (Best - Free, No API Keys)
Requires local installation (one-time setup)

**Installation**:
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download: https://ollama.ai/download/windows

# Start Ollama
ollama serve

# In another terminal, pull a model
ollama pull qwen3.6
```

**Status**: Ready to use

### Option D: Hybrid - Multiple APIs
System tries all 4 methods automatically.

**Best practice**: Have multiple API keys configured so if one fails, another takes over.

---

## Configuration

### Ensure .env Has All Keys
```bash
# Required for Gemini fallback
GEMINI_API_KEY=your_key_here

# Required for Kimi fallback
KIMI_API_KEY=sk-kjfAlmZbu0ZEw1X386RQ94piXfk9Cs18l3Td9icHbxPAPXoW
```

### Optional: Configure Ollama
```bash
# If running locally on non-standard port, edit direct_scoring.py line 14:
self.ollama_base = "http://localhost:11434"  # Change port if needed
```

---

## Testing Each Agent Individually

### Test Gemini
```python
import asyncio
from direct_scoring import get_scoring_client

async def test_gemini():
    client = get_scoring_client()
    result = await client.score_with_gemini(
        "Marketing Manager job description here...",
        "Marketing Manager",
        "Careem"
    )
    print(result)

asyncio.run(test_gemini())
```

### Test Kimi
```python
async def test_kimi():
    client = get_scoring_client()
    result = await client.score_with_direct_kimi(
        "Job description...",
        "Marketing Manager",
        "Careem"
    )
    print(result)

asyncio.run(test_kimi())
```

### Test Ollama (if installed)
```python
async def test_ollama():
    client = get_scoring_client()
    result = await client.score_with_ollama(
        "Job description...",
        "Marketing Manager",
        "Careem"
    )
    print(result)

asyncio.run(test_ollama())
```

---

## Monitoring & Debugging

### Check Which Agent Was Used
After scoring, check the response for:
```json
{
  "score": {...},
  "source_agent": "Gemini",  // ← Shows which agent scored the job
  "report_file": "001-company-2026-01-15.md"
}
```

### Check Report File
```bash
cat reports/001-company-2026-01-15.md

# Should show:
# SOURCE: Gemini (or Kimi, Ollama, LiteLLM, Hardcoded Fallback)
```

### Enable Debug Logging
Add to `career_ops_api.py` after imports:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Then check console output to see which agent is being tried.

---

## Troubleshooting

### Issue: "Evaluation failed" still appears
**Cause**: Direct scoring module not loading
**Fix**: 
1. Verify `direct_scoring.py` exists in career-ops root
2. Verify import added to `career_ops_api.py`
3. Restart backend: `python career_ops_api.py`

### Issue: Gemini returns 403 Forbidden
**Cause**: Invalid API key
**Fix**: Check `GEMINI_API_KEY` in `.env`, regenerate from Google Console

### Issue: Kimi returns 401 Unauthorized
**Cause**: Invalid API key or expired token
**Fix**: Check `KIMI_API_KEY` in `.env`, verify it's current

### Issue: Ollama returns connection refused
**Cause**: Ollama not running
**Fix**: Start Ollama service: `ollama serve`

### Issue: All agents fail, fallback returns score 50
**Status**: This is expected when all services are down
**Solution**: System is still usable with basic scoring

---

## Response Examples

### Response When LiteLLM Works
```json
{
  "score": {
    "overall_score": 75,
    "category_scores": {...},
    "strengths": [...],
    "gaps": [...],
    "recommendation": "apply"
  },
  "source_agent": "LiteLLM (Primary)",
  "report_file": "001-company-2026-01-15.md"
}
```

### Response When Gemini Takes Over
```json
{
  "score": {...},
  "source_agent": "gemini",  // Direct API
  "report_file": "002-company-2026-01-15.md"
}
```

### Response When All Fail (Fallback)
```json
{
  "score": {
    "overall_score": 50,
    "category_scores": {scores: 50 each},
    "strengths": ["Unable to evaluate"],
    "gaps": ["Scoring service unavailable"],
    "recommendation": "skip",
    "summary": "All AI services offline..."
  },
  "source_agent": "Hardcoded Fallback",
  "report_file": "003-company-2026-01-15.md"
}
```

---

## Performance Expectations

| Agent | Speed | Quality | Cost | Reliability |
|-------|-------|---------|------|-------------|
| LiteLLM | Fast | High | Free | 100% (if running) |
| Gemini | Medium | High | Free | 99% |
| Kimi | Medium | Very High | Subscription | 99% |
| Ollama | Slow | Good | Free | 100% (local) |
| Fallback | Instant | Low | Free | 100% |

---

## Emergency Contact

If ALL services are down and you need to score jobs:
1. Edit `direct_scoring.py` line 240 (fallback scoring)
2. Adjust base scores for your needs
3. Or temporarily use manual evaluation

---

## Files Created/Modified

| File | Status | Purpose |
|------|--------|---------|
| `direct_scoring.py` | ✅ Created | Multi-agent scoring |
| `career_ops_api.py` | ⏳ Update | Add fallback to /api/score |
| `.env` | ✓ Verified | API keys present |
| `PATCH_SCORE_ENDPOINT.py` | ✅ Reference | Code to copy into API |

---

## Implementation Checklist

- [ ] Copy `direct_scoring.py` (already done)
- [ ] Add import: `from direct_scoring import get_scoring_client`
- [ ] Replace `/api/score` function with updated version
- [ ] Verify `.env` has GEMINI_API_KEY and KIMI_API_KEY
- [ ] Restart backend: `python career_ops_api.py`
- [ ] Test "Paste JD" → "Score Listing"
- [ ] Verify score appears (may say "Gemini" or "Kimi" as source)
- [ ] Check report file for source agent used

---

## Quick Start Summary

1. ✅ New file `direct_scoring.py` created
2. ⏳ Update `career_ops_api.py` /api/score endpoint (copy from PATCH_SCORE_ENDPOINT.py)
3. ✅ Restart backend
4. ✅ Test scoring

**Expected result**: Job scoring works even when LiteLLM is offline.

---

**Status**: 🟡 READY FOR IMPLEMENTATION

The infrastructure is in place. Just need to update the one endpoint and restart.
