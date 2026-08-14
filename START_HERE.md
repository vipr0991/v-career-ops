# Career-Ops: Start Here 🚀

## ⚡ Fastest Way (One Click)

### Windows: Double-click one of these

**Option 1 - Batch (Simplest):**
```
LAUNCH.bat
```

**Option 2 - PowerShell:**
```
LAUNCH.ps1
```
(Right-click → "Run with PowerShell")

**Option 3 - Node.js:**
```
node launch.js
```

All three will:
1. ✅ Check Python/Node are installed
2. ✅ Start Backend API (port 5000)
3. ✅ Start Frontend (port 5173)
4. ✅ Open browser automatically

**Then see your app at:** http://localhost:5173/

---

## 🖥️ Manual Start (3 Steps)

### Step 1: Open Terminal 1 (Backend)

```bash
cd career-ops
python career_ops_api.py
```

Wait for: `Uvicorn running on http://0.0.0.0:5000`

### Step 2: Open Terminal 2 (Frontend)

```bash
cd career-ops/dashboard-web
npm run dev
```

Wait for: `Local: http://localhost:5173/`

### Step 3: Open Browser

```
http://localhost:5173/
```

---

## 🐳 Docker (Alternative)

```bash
cd career-ops
docker compose up
```

Then: http://localhost:5174/

---

## ✅ How to Know It's Working

| Check | Should See |
|-------|-----------|
| Terminal 1 | `Uvicorn running on http://0.0.0.0:5000` |
| Terminal 2 | `Local: http://localhost:5173/` |
| Browser | Career-Ops dashboard loads |
| Dashboard | Status shows "Gateway Online" (not "offline") |

---

## ❌ If It Doesn't Work

### "Connection refused" at localhost:5173?

**Check:** Is Terminal 2 (Frontend) running?
- Should show: `Local: http://localhost:5173/`
- If not: Run `cd career-ops/dashboard-web && npm run dev`

### "Backend offline" message?

**Check:** Is Terminal 1 (Backend) running?
- Should show: `Uvicorn running on http://0.0.0.0:5000`
- If not: Run `cd career-ops && python career_ops_api.py`

### Still stuck?

→ See **TROUBLESHOOTING.md**

---

## 📋 What You Can Do Now

1. **Upload Resume** → PDF/DOCX parsed automatically
2. **Search Jobs** → Find your target role
3. **Score Jobs** → See fit percentage
4. **Generate Resume** → LaTeX + visual preview
5. **Export** → Download PDF or .tex

---

## 🎯 First Time Steps

1. **Start the app** (pick one method above)
2. **Go to Resume Hub**
3. **Upload a PDF or DOCX resume** (drag & drop)
4. **Go to Jobs tab**
5. **Paste or search a job description**
6. **Click Score**
7. **Back to Resume Hub** → Select that job
8. **Generate Resume** → See preview
9. **Export** → Print or download

---

**Ready?** Pick a launcher method above and go! 🚀

If issues: Check the terminal windows for error messages, then see TROUBLESHOOTING.md
