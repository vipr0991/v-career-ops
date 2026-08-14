# Career-Ops Quick Reference

## 🚀 Three Ways to Start

```
┌─────────────────────────────────────────────────────┐
│         PICK ONE AND GO                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. EASIEST (Windows)                              │
│     └─ Double-click: LAUNCH.bat                    │
│                                                     │
│  2. MANUAL (All OS)                                │
│     └─ Terminal 1: python career_ops_api.py        │
│     └─ Terminal 2: cd dashboard-web && npm run dev │
│                                                     │
│  3. DOCKER                                         │
│     └─ docker compose up                           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 What Happens

```
Step 1: Launch
   └─> Backend starts: http://localhost:5000 ✓
   └─> Frontend starts: http://localhost:5173 ✓

Step 2: Browser opens automatically
   └─> http://localhost:5173/

Step 3: You see Career-Ops Dashboard
   └─> Status: "Gateway Online" ✓
```

---

## ✅ Check It's Working

```
Backend Up?
   curl http://localhost:5000/
   → Should return JSON with "status": "online"

Frontend Up?
   Visit http://localhost:5173/
   → Should load the dashboard

Connected?
   Dashboard status should say "Gateway Online"
   → Not "Gateway Offline"
```

---

## 📲 On Another Computer?

Instead of `localhost:5173`, use your computer's IP:

```bash
# Find your IP
ipconfig    # Windows
ifconfig    # Mac/Linux

# Then visit
http://YOUR_IP:5173/
```

---

## 🆘 Quick Fixes

| Problem | Fix |
|---------|-----|
| Port 5000 taken | Restart computer or kill Python process |
| Port 5173 taken | Kill Node.js process |
| npm not found | Install Node.js from nodejs.org |
| python not found | Install Python from python.org |
| Still broken? | See TROUBLESHOOTING.md |

---

## 📝 File Locations

```
career-ops/
├── LAUNCH.bat                    ← Double-click (Windows)
├── LAUNCH.ps1                    ← Right-click → Run (PowerShell)
├── launch.js                     ← node launch.js
├── START_HERE.md                 ← Read this first
├── TROUBLESHOOTING.md            ← If stuck
│
├── career_ops_api.py             ← Backend (Python)
├── requirements.txt              ← Python dependencies
│
└── dashboard-web/
    ├── package.json              ← Node dependencies
    ├── src/App.jsx               ← React app
    └── vite.config.js            ← Vite config
```

---

## 🎨 Feature Quick Start

After app loads, here's what to do:

### Generate a Tailored Resume

```
1. Resume Hub
   └─ Upload PDF/DOCX

2. Jobs page
   └─ Search or paste job
   └─ Click "Score"

3. Resume Hub
   └─ Select that job
   └─ Edit content
   └─ Click "Generate"

4. Preview or Export
   └─ Visual preview
   └─ Print to PDF
   └─ Download .tex
```

---

## 🔗 Important URLs (When Running)

| Service | URL | Port |
|---------|-----|------|
| API | http://localhost:5000 | 5000 |
| App | http://localhost:5173 | 5173 |
| API Health | http://localhost:5000/api/stats | 5000 |

---

## 📞 Still Stuck?

1. Check the terminal windows for red error messages
2. Read TROUBLESHOOTING.md
3. Try restarting everything:
   - Close terminals
   - Close browser
   - Start fresh

---

**Good luck! 🚀**
