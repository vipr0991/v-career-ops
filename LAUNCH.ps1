# Career-Ops Launcher (PowerShell)
# Starts both backend and frontend services

Write-Host ""
Write-Host "============================================================"
Write-Host "               CAREER-OPS LAUNCHER"
Write-Host "============================================================"
Write-Host ""

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

# Check Python
Write-Host "Checking Python..."
$pythonCheck = python --version 2>&1
if ($?) {
    Write-Host "  OK - $pythonCheck"
} else {
    Write-Host "  FAIL - Python not found. Install from https://www.python.org/"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js..."
$nodeCheck = node --version 2>&1
if ($?) {
    Write-Host "  OK - $nodeCheck"
} else {
    Write-Host "  FAIL - Node.js not found. Install from https://nodejs.org/"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check npm dependencies
Write-Host "Checking dependencies..."
if (-not (Test-Path "career-ops\dashboard-web\node_modules")) {
    Write-Host "Installing frontend dependencies..."
    Push-Location "career-ops\dashboard-web"
    npm install
    Pop-Location
}

Write-Host ""
Write-Host "Launching services..."
Write-Host ""

# Start Backend
Write-Host "Backend (Python API on port 5000)..."
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$RootDir\career-ops'; python career_ops_api.py" -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "Frontend (React dev server on port 5173)..."
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$RootDir\career-ops\dashboard-web'; npm run dev" -WindowStyle Normal

# Wait for frontend to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "============================================================"
Write-Host "               CAREER-OPS IS STARTING"
Write-Host "============================================================"
Write-Host ""
Write-Host "BACKEND:  http://localhost:5000"
Write-Host "FRONTEND: http://localhost:5173"
Write-Host ""
Write-Host "Opening browser..."
Write-Host ""

Start-Process "http://localhost:5173"

Write-Host "============================================================"
Write-Host "The app will open in your browser shortly."
Write-Host ""
Write-Host "If it doesn't open:"
Write-Host "  1. Check the terminal windows for errors"
Write-Host "  2. Manually visit: http://localhost:5173/"
Write-Host "  3. See TROUBLESHOOTING.md for help"
Write-Host ""
Write-Host "To stop both services, close the terminal windows."
Write-Host "============================================================"
Write-Host ""

Read-Host "Press Enter to exit this launcher"
