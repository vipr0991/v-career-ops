@echo off
REM Push Career-Ops images to Docker Hub
REM Usage: docker-push-marketdialogue.bat [tagname]
REM Example: docker-push-marketdialogue.bat 3.5.0

setlocal enabledelayedexpansion

set REGISTRY=docker.io
set NAMESPACE=marketdialogue
set IMAGE_NAME=vcareer-ops
set TAGNAME=%1

if "!TAGNAME!"=="" (
    echo.
    echo ERROR: Tag name required
    echo Usage: docker-push-marketdialogue.bat [tagname]
    echo Example: docker-push-marketdialogue.bat 3.5.0
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
echo   CAREER-OPS DOCKER PUSH
echo ========================================================
echo.
echo Registry:  !REGISTRY!
echo Namespace: !NAMESPACE!
echo Image:     !IMAGE_NAME!
echo Tagname:   !TAGNAME!
echo.
echo Images to push:
echo   Backend:  !BACKEND_IMAGE!
echo   Frontend: !FRONTEND_IMAGE!
echo.

REM Verify authentication
docker info >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Not logged into Docker Hub
    echo Run: docker login
    echo Then try again
    echo.
    pause
    exit /b 1
)

echo [1/4] Verifying images exist...
docker image inspect !BACKEND_IMAGE! >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Backend image not found: !BACKEND_IMAGE!
    echo Build first with: docker-build-marketdialogue.bat !TAGNAME!
    echo.
    pause
    exit /b 1
)

docker image inspect !FRONTEND_IMAGE! >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Frontend image not found: !FRONTEND_IMAGE!
    echo Build first with: docker-build-marketdialogue.bat !TAGNAME!
    echo.
    pause
    exit /b 1
)

echo   OK - Both images found
echo.

echo [2/4] Pushing Backend (!BACKEND_IMAGE!)...
docker push !BACKEND_IMAGE!
if !errorlevel! neq 0 (
    echo ERROR: Backend push failed
    pause
    exit /b 1
)
echo   OK - Backend pushed
echo.

echo [3/4] Pushing Frontend (!FRONTEND_IMAGE!)...
docker push !FRONTEND_IMAGE!
if !errorlevel! neq 0 (
    echo ERROR: Frontend push failed
    pause
    exit /b 1
)
echo   OK - Frontend pushed
echo.

echo ========================================================
echo   PUSH COMPLETE
echo ========================================================
echo.
echo Images pushed successfully:
echo   Backend:  !BACKEND_IMAGE!
echo   Frontend: !FRONTEND_IMAGE!
echo.
echo View on Docker Hub:
echo   https://hub.docker.com/r/!NAMESPACE!/!IMAGE_NAME!-api
echo   https://hub.docker.com/r/!NAMESPACE!/!IMAGE_NAME!-dashboard
echo.
echo Pull commands:
echo   docker pull !BACKEND_IMAGE!
echo   docker pull !FRONTEND_IMAGE!
echo.

pause
