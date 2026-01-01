@echo off
REM ============================================================================
REM Full Stack Startup Script - React Frontend + FastAPI Backend
REM ============================================================================

color 0A
cls
echo.
echo ============================================================================
echo     TRAVEL NEWS TRANSLATOR - FULL STACK LAUNCHER
echo ============================================================================
echo.
echo This script will start:
echo   [1] FastAPI Backend    (Port 8000)
echo   [2] React Frontend     (Port 5173)
echo.
echo ============================================================================
echo.

REM Kill any existing processes
echo [*] Cleaning up existing processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq*uvicorn*" >nul 2>&1
taskkill /F /IM node.exe /FI "WINDOWTITLE eq*vite*" >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start Backend in new window
echo.
echo [*] Starting FastAPI Backend...
start "Travel News API (Port 8000)" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul

REM Start Frontend in new window
echo [*] Starting React Frontend...
start "Travel News Frontend (Port 5173)" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ============================================================================
echo     SERVICES STARTED SUCCESSFULLY!
echo ============================================================================
echo.
echo   Backend API:     http://localhost:8000
echo   API Docs:        http://localhost:8000/docs
echo   Frontend UI:     http://localhost:5173 (will open automatically)
echo.
echo ============================================================================
echo.
echo Press any key to open the frontend in your browser...
pause >nul

REM Open browser
start http://localhost:5173

echo.
echo ============================================================================
echo     SERVICES ARE RUNNING
echo ============================================================================
echo.
echo To stop services:
echo   1. Close the terminal windows titled "Travel News API" and "Travel News Frontend"
echo   2. Or run: taskkill /F /IM python.exe /IM node.exe
echo.
echo Press any key to exit this launcher...
pause >nul
