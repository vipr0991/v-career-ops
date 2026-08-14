# ⚠️ Career-Ops Troubleshooting

## Issue: App won't load

### Step 1: Check Backend (Port 5000)

```bash
cd career-ops
python career_ops_api.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:5000
```

**If it fails:**
- Port 5000 already in use? Kill the process or use different port
- Missing dependencies? Run: `pip install -r requirements.txt`

### Step 2: Check Frontend (Port 5173)

**In a NEW terminal/tab:**

```bash
cd career-ops/dashboard-web
npm run dev
```

**Expected output:**
```
➜  Local:   http://localhost:5173/
```

**If it fails:**
- npm not installed? Install Node.js from https://nodejs.org/
- Dependencies missing? Run: `npm install`

### Step 3: Test Connection

**Open browser:** http://localhost:5173/

**If frontend loads but shows "Backend offline":**
- Backend crashed? Check Step 1 window for errors
- API_BASE wrong? Check `dashboard-web/.env`
  - Should be: `VITE_API_BASE=http://localhost:5000`

### Step 4: Check Backend is Responding

```powershell
# Test from PowerShell:
(Invoke-WebRequest -Uri http://localhost:5000/ -UseBasicParsing).Content | ConvertFrom-Json
```

**Should return:**
```json
{
  "service": "Career-Ops API",
  "version": "3.5.0",
  "status": "online"
}
```

---

## Common Errors

### Error: "Backend offline" (on dashboard)

**Cause:** API not running or frontend can't reach it

**Fix:**
1. Check Step 1 above (is backend running?)
2. Is it on correct port? `http://localhost:5000/`
3. Check `dashboard-web/.env`:
   ```
   VITE_API_BASE=http://localhost:5000
   ```

### Error: "Module not found" (backend)

**Cause:** Missing Python dependencies

**Fix:**
```bash
cd career-ops
pip install -r requirements.txt
```

### Error: npm ERR! (frontend)

**Cause:** Missing Node dependencies

**Fix:**
```bash
cd career-ops/dashboard-web
npm install
```

### Error: Port already in use

**Backend (5000):**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill it (replace PID)
taskkill /PID <PID> /F
```

**Frontend (5173):**
```powershell
# Find process using port 5173
netstat -ano | findstr :5173

# Kill it (replace PID)
taskkill /PID <PID> /F
```

---

## Manual Startup (Windows)

**Terminal 1 - Backend:**
```powershell
cd career-ops
python career_ops_api.py
```

**Terminal 2 - Frontend:**
```powershell
cd career-ops\dashboard-web
npm run dev
```

**Terminal 3 - Open browser:**
```powershell
start http://localhost:5173
```

---

## Manual Startup (macOS/Linux)

**Terminal 1 - Backend:**
```bash
cd career-ops
python career_ops_api.py
```

**Terminal 2 - Frontend:**
```bash
cd career-ops/dashboard-web
npm run dev
```

**Terminal 3 - Open browser:**
```bash
open http://localhost:5173
# or
xdg-open http://localhost:5173
```

---

## Using Docker

```bash
cd career-ops
docker compose up --pull always
```

Then open: http://localhost:5174/

**If Docker fails:**
- Docker not installed? Install from https://docker.com
- Port conflicts? Edit `docker-compose.yml` ports section
- Memory issues? Increase Docker memory allocation

---

## Check Logs

### Backend logs
Watch the terminal where `python career_ops_api.py` is running

### Frontend logs
1. Open browser DevTools: Press `F12`
2. Click **Console** tab
3. Look for red errors

### API connection
1. DevTools → **Network** tab
2. Click any request
3. Check **Response** for errors

---

## Still stuck?

1. **Check files exist:**
   ```
   career-ops/
   ├── career_ops_api.py      ✓ exists?
   ├── requirements.txt         ✓ exists?
   └── dashboard-web/
       ├── package.json         ✓ exists?
       ├── .env                 ✓ exists?
       └── src/App.jsx          ✓ exists?
   ```

2. **Check .env files:**
   ```
   career-ops/.env
   → Has KIMI_API_KEY, etc?
   
   career-ops/dashboard-web/.env
   → Has VITE_API_BASE=http://localhost:5000?
   ```

3. **Clear browser cache:**
   - Press: `Ctrl+Shift+Delete` (Windows)
   - Or: `Cmd+Shift+Delete` (Mac)
   - Clear "All time"

4. **Restart everything:**
   - Close all terminals
   - Close browser
   - Start fresh from Step 1

---

## Expected URLs

| Service | URL | Status |
|---------|-----|--------|
| Backend | http://localhost:5000/ | {"status": "online"} |
| Frontend | http://localhost:5173/ | Loads page |
| API Health | http://localhost:5000/api/stats | JSON response |

If all three respond correctly, the app is working.

---

**Need help?** Check:
- Backend terminal for Python errors
- Browser DevTools (F12) for frontend errors
- Docker logs: `docker compose logs -f`
