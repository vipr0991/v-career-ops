@echo off
REM Build Career-Ops images for marketdialogue namespace
REM Usage: docker-build-marketdialogue.bat [tagname]
REM Example: docker-build-marketdialogue.bat 3.5.0

setlocal enabledelayedexpansion

set REGISTRY=docker.io
set NAMESPACE=marketdialogue
set IMAGE_NAME=vcareer-ops
set TAGNAME=%1

if "!TAGNAME!"=="" (
    echo.
    echo ERROR: Tag name required
    echo Usage: docker-build-marketdialogue.bat [tagname]
    echo Example: docker-build-marketdialogue.bat 3.5.0
    echo.
    pause
    exit /b 1
)

set BACKEND_IMAGE=!REGISTRY!/!NAMESPACE!/!IMAGE_NAME!-api:!TAGNAME!
set FRONTEND_IMAGE=!REGISTRY!/!NAMESPACE!/!IMAGE_NAME!-dashboard:!TAGNAME!
set LATEST_BACKEND=!REGISTRY!/!NAMESPACE!/!IMAGE_NAME!-api:latest
set LATEST_FRONTEND=!REGISTRY!/!NAMESPACE!/!IMAGE_NAME!-dashboard:latest

echo.
echo ========================================================
echo   CAREER-OPS DOCKER BUILD
echo ========================================================
echo.
echo Registry:  !REGISTRY!
echo Namespace: !NAMESPACE!
echo Image:     !IMAGE_NAME!
echo Tagname:   !TAGNAME!
echo.

echo [1/2] Building Backend API...
echo       Image: !BACKEND_IMAGE!
docker build ^
  --file Dockerfile ^
  --tag "!BACKEND_IMAGE!" ^
  --tag "!LATEST_BACKEND!" ^
  --label "version=!TAGNAME!" ^
  --label "maintainer=marketdialogue" ^
  --label "namespace=!NAMESPACE!" ^
  .

if !errorlevel! neq 0 (
    echo ERROR: Backend build failed
    pause
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
  --label "version=!TAGNAME!" ^
  --label "maintainer=marketdialogue" ^
  --label "namespace=!NAMESPACE!" ^
  dashboard-web\

if !errorlevel! neq 0 (
    echo ERROR: Frontend build failed
    pause
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
echo Image sizes:
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | findstr "!NAMESPACE!"
echo.
echo Next steps:
echo   1. docker login
echo   2. docker-push-marketdialogue.bat !TAGNAME!
echo.

pause
