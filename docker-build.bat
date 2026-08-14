@echo off
REM Build script for Docker Hub deployment (Windows)
REM Usage: docker-build.bat [REGISTRY] [NAMESPACE] [VERSION]
REM Example: docker-build.bat docker.io yourusername 3.5.0

setlocal enabledelayedexpansion

set REGISTRY=%1
if "!REGISTRY!"=="" set REGISTRY=docker.io

set NAMESPACE=%2
if "!NAMESPACE!"=="" set NAMESPACE=yourusername

set VERSION=%3
if "!VERSION!"=="" set VERSION=3.5.0

set BACKEND_IMAGE=!REGISTRY!/!NAMESPACE!/career-ops-api:!VERSION!
set FRONTEND_IMAGE=!REGISTRY!/!NAMESPACE!/career-ops-dashboard:!VERSION!
set LATEST_BACKEND=!REGISTRY!/!NAMESPACE!/career-ops-api:latest
set LATEST_FRONTEND=!REGISTRY!/!NAMESPACE!/career-ops-dashboard:latest

echo.
echo ========================================================
echo   CAREER-OPS DOCKER BUILD
echo ========================================================
echo.
echo Registry:  !REGISTRY!
echo Namespace: !NAMESPACE!
echo Version:   !VERSION!
echo.

echo [1/2] Building Backend API...
echo       Image: !BACKEND_IMAGE!
docker build ^
  --file Dockerfile ^
  --tag "!BACKEND_IMAGE!" ^
  --tag "!LATEST_BACKEND!" ^
  --label "version=!VERSION!" ^
  --label "maintainer=careerops" ^
  .

if !errorlevel! neq 0 (
    echo ERROR: Backend build failed
    exit /b 1
)

echo       [OK] Backend built
echo.

echo [2/2] Building Frontend Dashboard...
echo       Image: !FRONTEND_IMAGE!
docker build ^
  --file dashboard-web\Dockerfile.prod ^
  --tag "!FRONTEND_IMAGE!" ^
  --tag "!LATEST_FRONTEND!" ^
  --label "version=!VERSION!" ^
  --label "maintainer=careerops" ^
  dashboard-web\

if !errorlevel! neq 0 (
    echo ERROR: Frontend build failed
    exit /b 1
)

echo       [OK] Frontend built
echo.

echo ========================================================
echo   BUILD COMPLETE
echo ========================================================
echo.
echo Images built:
echo   Backend:  !BACKEND_IMAGE!
echo   Frontend: !FRONTEND_IMAGE!
echo.
echo Next steps:
echo   1. docker login
echo   2. docker push !BACKEND_IMAGE!
echo   3. docker push !FRONTEND_IMAGE!
echo   4. docker push !LATEST_BACKEND!
echo   5. docker push !LATEST_FRONTEND!
echo.

pause
