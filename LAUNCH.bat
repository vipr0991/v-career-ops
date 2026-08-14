@echo off
setlocal enabledelayedexpansion

REM Career-Ops Launcher - Starts both backend and frontend
REM This script will keep both services running

cd /d "%~dp0"

echo.
echo ============================================================
echo               CAREER-OPS LAUNCHER
echo ============================================================
echo.
echo Starting services... Please wait.
echo.

REM Check if dependencies are installed
if not exist "career-ops\node_modules" (
    echo Installing frontend dependencies...
    cd dashboard-web
    call npm install
    cd ..
)

REM Kill any existing processes on ports
taskkill /F /IM python.exe /FI "MEMUSAGE gt 0" >nul 2>&1

REM Start backend in a new window and keep it running
echo Launching BACKEND (Python API on port 5000)...
start "Career-Ops API" /D "career-ops" cmd /K "python career_ops_api.py"

REM Wait for backend to start
timeout /t 2 /nobreak

REM Start frontend in a new window and keep it running
echo Launching FRONTEND (React dev server on port 5173)...
start "Career-Ops Dashboard" /D "career-ops\dashboard-web" cmd /K "npm run dev"

REM Wait for frontend to start
timeout /t 3 /nobreak

echo.
echo ============================================================
echo               CAREER-OPS IS STARTING
echo ============================================================
echo.
echo BACKEND:  http://localhost:5000
echo FRONTEND: http://localhost:5173
echo.
echo Opening browser...
timeout /t 2 /nobreak

start "" http://localhost:5173

echo.
echo ============================================================
echo The app will open in your browser shortly.
echo.
echo If it doesn't open:
echo   1. Check the terminal windows for errors
echo   2. Manually visit: http://localhost:5173/
echo   3. See TROUBLESHOOTING.md for help
echo.
echo To stop both services, close the terminal windows.
echo ============================================================
echo.

pause
