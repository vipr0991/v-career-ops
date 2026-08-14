# 📖 Career-Ops Documentation Index

## 🚀 GETTING STARTED (Pick One)

**👉 Start here:**
- **[NOW_IT_WORKS.md](NOW_IT_WORKS.md)** — 2-minute overview of what works & how to start
- **[START_HERE.md](START_HERE.md)** — Step-by-step instructions

**Quick reference:**
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** — Cheat sheet with visual diagrams

---

## 🎯 LAUNCH APPLICATIONS

**Windows (easiest):**
- `LAUNCH.bat` — Double-click to start (Batch script)
- `LAUNCH.ps1` — Right-click → Run with PowerShell
- `launch.js` — Or run `node launch.js`

**All Platforms:**
- **[Manual Start Guide](START_HERE.md#manual-start-3-steps)** — 3 terminal approach

**Docker:**
```bash
cd career-ops
docker compose up
```

---

## 🆘 TROUBLESHOOTING

**[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Fix common issues:
- Port already in use
- Backend won't start
- Frontend won't load
- "Backend offline" message

---

## 📚 DETAILED DOCUMENTATION

- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** — All features implemented
- **[QUICK_START_CROSS_ENV.md](QUICK_START_CROSS_ENV.md)** — Environment setup
- **[CROSS_ENV_BROWSER_UPDATE.md](CROSS_ENV_BROWSER_UPDATE.md)** — Technical details

---

## ✅ What's Working

| Feature | Status |
|---------|--------|
| Backend API (Python) | ✅ Running on port 5000 |
| Frontend App (React) | ✅ Running on port 5173 |
| Resume Upload | ✅ PDF/DOCX auto-parse |
| Job Search & Score | ✅ Scoring algorithm |
| Resume Tailoring | ✅ Edit & preserve core |
| LaTeX Generation | ✅ .tex source + preview |
| Visual Preview | ✅ Print-ready rendering |
| Export Options | ✅ PDF + .tex download |
| Cross-Browser | ✅ Chrome, Firefox, Safari |
| Docker Support | ✅ docker-compose ready |

---

## 📁 Important Files

```
career-ops/
├── NOW_IT_WORKS.md              ← Read this first
├── START_HERE.md                ← Then this
├── QUICK_REFERENCE.md           ← Cheat sheet
├── TROUBLESHOOTING.md           ← If stuck
│
├── LAUNCH.bat                   ← Windows: Double-click
├── LAUNCH.ps1                   ← Windows: PowerShell
├── launch.js                    ← Node.js launcher
│
├── career_ops_api.py            ← Backend (Python)
├── requirements.txt             ← Python deps
├── .env                         ← API keys (secret)
│
├── docker-compose.yml           ← Docker config
├── Dockerfile.backend           ← Backend image
│
├── dashboard-web/
│   ├── package.json             ← Node deps
│   ├── Dockerfile               ← Frontend image
│   ├── vite.config.js           ← Vite config
│   ├── .env                     ← VITE_API_BASE
│   └── src/
│       ├── App.jsx              ← Main app
│       └── pages/
│           ├── ResumeHubPage.jsx
│           ├── JobsPage.jsx
│           └── ...
```

---

## 🚀 Quick Start (60 seconds)

### Windows
```bash
cd career-ops
LAUNCH.bat
```

### Mac/Linux
```bash
cd career-ops
node launch.js
```

Then open: **http://localhost:5173/**

---

## 🔄 Services

| Service | Port | URL | Type |
|---------|------|-----|------|
| Backend API | 5000 | http://localhost:5000 | Python FastAPI |
| Frontend | 5173 | http://localhost:5173 | React + Vite |
| Docker Frontend | 5174 | http://localhost:5174 | Docker mapped |

---

## 🎯 Feature Workflow

```
1. Upload Resume (PDF/DOCX)
   ↓ Auto-parsed → Extract sections
2. Search & Score Job
   ↓ Evaluate fit
3. Resume Hub: Select Job
   ↓ Auto-fill target role
4. Edit Experience/Skills
   ↓ Tailor wording
5. Generate LaTeX
   ↓ Build .tex source
6. Visual Preview
   ↓ Render as PDF page
7. Export
   ↓ Print or Download .tex
```

---

## 📞 Support

| Issue | Docs |
|-------|------|
| Won't start | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Port errors | [TROUBLESHOOTING.md](TROUBLESHOOTING.md#error-port-already-in-use) |
| Backend offline | [TROUBLESHOOTING.md](TROUBLESHOOTING.md#error-backend-offline) |
| General help | [START_HERE.md](START_HERE.md) |

---

## 🏁 Status

🟢 **PRODUCTION READY**

All requirements implemented and tested.

- ✅ Cross-environment compatible
- ✅ Multi-browser support
- ✅ Full Resume Hub
- ✅ LaTeX generation
- ✅ Visual preview
- ✅ Job tailoring
- ✅ Docker ready

---

**👉 Start here:** Open `NOW_IT_WORKS.md` or run `LAUNCH.bat`
