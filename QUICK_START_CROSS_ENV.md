# Career-Ops Quick Start Guide

## 🚀 Cross-Environment Setup (Windows, macOS, Linux)

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- API Keys: `KIMI_API_KEY`, `GEMINI_API_KEY`, `SERPAPI_KEY` (in `.env`)

---

## 📦 **Option 1: Docker (Recommended for any environment)**

### Run with Docker Compose
```bash
cd career-ops
docker compose up --pull always
```

**What this does:**
- Starts backend API at `http://localhost:5000`
- Starts frontend at `http://localhost:5174`
- Auto-healthchecks and cross-service communication
- Works identically on Windows, Mac, Linux

**Access the app:** Open http://localhost:5173/ in any browser

**Stop:** `docker compose down`

---

## 🛠️ **Option 2: Local Development (No Docker)**

### 1. Backend Setup
```bash
cd career-ops

# Install Python dependencies
pip install -r requirements.txt

# Ensure .env has your API keys
cat .env  # Check KIMI_API_KEY, GEMINI_API_KEY, SERPAPI_KEY are set

# Start the API server
python career_ops_api.py
```
✅ Backend runs at `http://localhost:5000`

### 2. Frontend Setup (new terminal/tab)
```bash
cd career-ops/dashboard-web

# Install dependencies
npm install

# Start dev server
npm run dev

**Access the app:** Open http://localhost:5173/ in any browser

---

## 🌐 Browser Compatibility

Career-Ops works across all modern browsers:
- ✅ **Chrome** / **Edge** (Chromium-based)
- ✅ **Firefox**
- ✅ **Safari** (macOS/iOS)
- ✅ **Mobile browsers**

**Why?** The app uses:
- Standard React + Vite (no vendor lock-in)
- Modern CSS Grid/Flexbox (works everywhere)
- No browser-specific APIs
- Environment-aware HTTP (works in Docker, local, production)

---

## 📋 Resume Hub Workflow

### Step 1: Upload Your Resume
- Drag & drop **PDF, DOCX, or TEX** file
- Auto-parses to extract:
  - Experience
  - Skills
  - Education
  - Certifications
  - Projects
  - Achievements

### Step 2: Score a Job
1. Go to **Jobs** page
2. Search for or paste a job description
3. Click **Score** to evaluate fit
4. Resume Hub unlocks with that job selected

### Step 3: Generate Tailored Resume
1. Go to **Resume Hub**
2. Select scored job from dropdown
3. Edit experience/skills as needed (wording refined, core content preserved)
4. Click **Generate Resume**
5. View **Visual Preview** (print-ready)

### Step 4: Export
- **Print / PDF**: Browser print dialog → save as PDF
- **.tex**: Download LaTeX source for Overleaf or local compile

---

## 🔄 Pipeline Execution Order

**Current flow:**

1. ✅ **Upload Resume** → API receives file
2. ✅ **Parse Sections** → Extract experience, skills, education, etc.
3. ✅ **View Resume** → See full content in library
4. ✅ **Search/Score Job** → Find target role
5. ✅ **Select Job** → Resume Hub auto-fills with target role
6. ✅ **Edit Content** → Tailor bullets, skills, summary
7. ✅ **Generate LaTeX** → Build .tex from edited data
8. ✅ **Visual Preview** → See rendered resume
9. ✅ **Export** → Print to PDF or download .tex

---

## ⚙️ Environment Configuration

### Development (Local)
```bash
# dashboard-web/.env
VITE_API_BASE=http://localhost:5000
```

### Docker/Container
```bash
# docker-compose.yml auto-sets:
VITE_API_BASE=http://api:5000  # uses container service name
```

### Production
```bash
# dashboard-web/.env
VITE_API_BASE=https://api.yourdomain.com:5000
```

No code changes needed—just environment variables!

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check port 5000 is free
# Or edit career_ops_api.py to use different port
uvicorn.run(app, host="0.0.0.0", port=5001)
```

### Frontend won't load
- Clear browser cache: `Ctrl+Shift+Delete` (or `Cmd+Shift+Delete` Mac)
- Restart dev server: `npm run dev`
- Check http://localhost:5000/ responds (backend alive?)

### Resume upload fails
- File size < 10MB?
- Supported format: `.pdf`, `.docx`, `.doc`, `.tex`?
- Backend logs: `python career_ops_api.py` output

### LaTeX export broken
- Ensure experience/skills are filled
- Generate LaTeX first via **Generate Resume** button
- Compile on [Overleaf.com](https://overleaf.com) for quick PDF

---

## 📁 File Structure

```
career-ops/
├── career_ops_api.py          # FastAPI backend
├── requirements.txt            # Python dependencies
├── .env                        # API keys (secret!)
├── docker-compose.yml          # Container orchestration
├── Dockerfile.backend          # Backend image
│
├── dashboard-web/
│   ├── package.json            # Node dependencies
│   ├── .env                    # VITE_API_BASE
│   ├── Dockerfile              # Frontend image
│   ├── vite.config.js          # Build config
│   └── src/
│       ├── App.jsx             # Main app
│       ├── pages/
│       │   ├── ResumeHubPage.jsx
│       │   ├── JobsPage.jsx
│       │   └── ...
│       └── components/
│
├── reports/                    # Scored jobs (auto-generated)
├── resumes/                    # Uploaded resumes
├── latex_resumes/              # Generated .tex files
└── config/                     # profile.yml, etc.
```

---

## 📚 Key Features Enabled

✅ **Cross-Environment**: Works locally, Docker, or cloud  
✅ **Multi-Browser**: Chrome, Firefox, Safari, Edge  
✅ **Full Resume Parsing**: PDF, DOCX extraction  
✅ **LaTeX + Visual**: Both source code and preview  
✅ **Job Tailoring**: Preserve core skills, refine wording  
✅ **Export Options**: Print to PDF or download .tex  

---

## 🚀 Next Steps

1. **Start the app**: `docker compose up` or local scripts
2. **Open browser**: http://localhost:5174/
3. **Upload resume**: Drag PDF/DOCX
4. **Score a job**: Search and evaluate
5. **Tailor resume**: Edit and generate LaTeX
6. **Export**: Print or download

---

**Questions?** Check logs at:
- Backend: stdout from `python career_ops_api.py`
- Frontend: Browser DevTools (F12)
