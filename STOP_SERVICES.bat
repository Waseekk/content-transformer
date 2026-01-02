@echo off
REM ============================================================================
REM Stop All Services - Kill running backend and frontend processes
REM ============================================================================

color 0C
cls
echo.
echo ============================================================================
echo     STOPPING ALL TRAVEL NEWS SERVICES
echo ============================================================================
echo.

echo [*] Stopping FastAPI Backend (Python/Uvicorn)...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq*uvicorn*" 2>nul
if %errorlevel%==0 (
    echo     [SUCCESS] Backend stopped
) else (
    echo     [INFO] No backend process found
)

echo.
echo [*] Stopping React Frontend (Node/Vite)...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq*vite*" 2>nul
if %errorlevel%==0 (
    echo     [SUCCESS] Frontend stopped
) else (
    echo     [INFO] No frontend process found
)

echo.
echo [*] Stopping Streamlit App (if running)...
taskkill /F /IM streamlit.exe 2>nul
if %errorlevel%==0 (
    echo     [SUCCESS] Streamlit stopped
) else (
    echo     [INFO] No Streamlit process found
)

echo.
echo ============================================================================
echo     ALL SERVICES STOPPED
echo ============================================================================
echo.
pause
