@echo off
REM Career-Ops Diagnostic & Launch Script

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Career-Ops — System Check & Launch
echo ========================================
echo.

REM Check Python
echo [1/3] Checking Python...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
    echo   OK - Python !PY_VER!
) else (
    echo   FAIL - Python not found
    echo   Install from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Node.js
echo [2/3] Checking Node.js...
node --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VER=%%i
    echo   OK - Node.js !NODE_VER!
) else (
    echo   FAIL - Node.js not found
    echo   Install from https://nodejs.org/
    pause
    exit /b 1
)

REM Check npm
echo [3/3] Checking npm...
npm --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=1" %%i in ('npm --version 2^>^&1') do set NPM_VER=%%i
    echo   OK - npm !NPM_VER!
) else (
    echo   FAIL - npm not found
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Starting Career-Ops
echo ========================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo IMPORTANT: Open TWO terminal windows
echo.

echo Launching backend... (check window 1)
start "Career-Ops Backend" cmd /k "cd /d "%cd%" && python career_ops_api.py"

timeout /t 3 /nobreak

echo Launching frontend... (check window 2)
start "Career-Ops Frontend" cmd /k "cd /d "%cd%\dashboard-web" && npm run dev"

echo.
echo Waiting for services to start...
timeout /t 5 /nobreak

echo.
echo ========================================
echo  Opening browser...
echo ========================================
echo.

start http://localhost:5173

echo.
echo Career-Ops should open in your browser.
echo If not, manually visit: http://localhost:5173/
echo.
echo Check the terminal windows for any errors.
pause
