@echo off
REM Auto-restart FastAPI backend if it crashes

setlocal enabledelayedexpansion

set CAREEROPS_PATH=C:\Users\ASUS\Downloads\Career-Ops\career-ops
set CRASH_COUNT=0
set MAX_CRASHES=5

:START
cls
echo ============================================
echo  Career-Ops FastAPI Backend Auto-Restarter
echo ============================================
echo.
echo Crash Count: %CRASH_COUNT%/%MAX_CRASHES%
echo.
echo Starting FastAPI backend...
echo Endpoint: http://localhost:5000
echo.
echo Press CTRL+C to stop
echo ============================================
echo.

cd /d %CAREEROPS_PATH%
python career_ops_api.py

set /a CRASH_COUNT+=1

if %CRASH_COUNT% GEQ %MAX_CRASHES% (
    echo.
    echo ============================================
    echo  ERROR: Backend crashed %MAX_CRASHES% times!
    echo ============================================
    echo Possible causes:
    echo 1. Missing direct_scoring.py module import
    echo 2. Syntax error in career_ops_api.py
    echo 3. Missing Python dependencies
    echo 4. Port 5000 still in use
    echo.
    echo Check: BACKEND_CRASH_ANALYSIS.md
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Backend crashed! Restarting in 5 seconds...
echo  Crash #%CRASH_COUNT%/%MAX_CRASHES%
echo ============================================
echo.
timeout /t 5 /nobreak

goto START
