# 🚀 START Career-Ops - Step by Step

## ⚠️ IMPORTANT: TWO WINDOWS REQUIRED

**You MUST open TWO separate terminal/command windows and keep both running.**

The services will NOT work if you close either window.

---

## 🪟 Windows Users

### Window 1: Backend API

1. **Open Command Prompt** (Windows key → type `cmd` → Enter)
2. **Run this:**
```bash
cd career-ops
python run_api.py
```

**Wait until you see:**
```
Uvicorn running on http://0.0.0.0:5000
```

✅ **LEAVE THIS WINDOW OPEN**

---

### Window 2: Frontend

1. **Open a NEW Command Prompt** (don't close Window 1!)
2. **Run this:**
```bash
cd career-ops
node run_frontend.js
```

**Wait until you see:**
```
Local:   http://localhost:5173/
```

✅ **LEAVE THIS WINDOW OPEN**

---

### Window 3: Browser

1. **Open your browser**
2. **Go to:** http://localhost:5173/

✅ **You should see the Career-Ops dashboard**

---

## 🍎 Mac Users

### Terminal 1: Backend API

```bash
cd career-ops
python3 run_api.py
```

Wait for: `Uvicorn running on http://0.0.0.0:5000`

✅ **Leave open**

---

### Terminal 2: Frontend

Open a NEW terminal (Terminal → New Window or Cmd+N)

```bash
cd career-ops
node run_frontend.js
```

Wait for: `Local: http://localhost:5173/`

✅ **Leave open**

---

### Browser

```bash
open http://localhost:5173
```

---

## 🐧 Linux Users

### Terminal 1: Backend API

```bash
cd career-ops
python3 run_api.py
```

Wait for: `Uvicorn running on http://0.0.0.0:5000`

✅ **Leave open**

---

### Terminal 2: Frontend

Open a NEW terminal

```bash
cd career-ops
node run_frontend.js
```

Wait for: `Local: http://localhost:5173/`

✅ **Leave open**

---

### Browser

```bash
xdg-open http://localhost:5173
```

---

## ✅ How You Know It's Working

| Window | Should Show |
|--------|------------|
| **Terminal 1** | `Uvicorn running on http://0.0.0.0:5000` |
| **Terminal 2** | `Local: http://localhost:5173/` |
| **Browser** | Career-Ops dashboard loads |

---

## ❌ If Browser Shows "Connection Refused"

### Check Terminal 1 (Backend)
- Does it show `Uvicorn running on http://0.0.0.0:5000`?
- If NOT: There's an error message above. Read it!
- If YES: Close and re-run

### Check Terminal 2 (Frontend)
- Does it show `Local: http://localhost:5173/`?
- If NOT: There's an error message above. Read it!
- If YES: Wait 5 seconds and refresh browser (Ctrl+R or Cmd+R)

### Try clearing browser cache
- Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
- Select "All time"
- Click "Clear"
- Then go back to http://localhost:5173/

---

## 🆘 Common Errors

### "Address already in use"

**Backend error?**
```bash
# Kill process using port 5000
netstat -ano | findstr :5000    # Windows
lsof -i :5000                   # Mac/Linux
```

**Frontend error?**
```bash
# Kill process using port 5173
netstat -ano | findstr :5173    # Windows
lsof -i :5173                   # Mac/Linux
```

Then restart.

### "ModuleNotFoundError: No module named"

**Backend:**
```bash
cd career-ops
pip install -r requirements.txt
```

**Frontend:**
```bash
cd career-ops/dashboard-web
npm install
```

### "npm: command not found"

Install Node.js from https://nodejs.org/

### "python: command not found"

Install Python from https://www.python.org/

---

## 📝 DO NOT

❌ Close either terminal window  
❌ Run both services in the same window  
❌ Stop and start repeatedly  

## ✅ DO

✅ Keep both windows open  
✅ Run in separate windows  
✅ Wait for "running" message before opening browser  
✅ Give it 5-10 seconds to start  

---

## 🎯 Once It's Running

1. Go to **Resume Hub**
2. **Upload a PDF or DOCX resume**
3. Go to **Jobs**
4. **Search or paste a job description**
5. Click **Score**
6. Back to **Resume Hub** → select that job
7. Click **Generate Resume**
8. See the **preview** or **export as PDF/.tex**

---

## 🛑 To Stop

1. Press `Ctrl+C` in each terminal window
2. Close the terminal windows

Both services will stop.

---

**Ready? Open two terminal windows and follow the steps above! 🚀**
