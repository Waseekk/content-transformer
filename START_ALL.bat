@echo off
title Swiftor - Starting All Services
color 0A

echo ============================================================
echo                    SWIFTOR - START ALL
echo ============================================================
echo.

:: Kill any existing processes on ports 8000 and 5173
echo [1/4] Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5174 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
echo    Done.
echo.

:: Start Backend
echo [2/4] Starting Backend (FastAPI on port 8000)...
cd /d "%~dp0backend"
start "Swiftor Backend" cmd /k "call venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd /d "%~dp0"
timeout /t 3 /nobreak >nul
echo    Backend starting...
echo.

:: Start Frontend
echo [3/4] Starting Frontend (Vite on port 5173)...
cd /d "%~dp0frontend"
start "Swiftor Frontend" cmd /k "npm run dev"
cd /d "%~dp0"
timeout /t 3 /nobreak >nul
echo    Frontend starting...
echo.

:: Done
echo [4/4] All services started!
echo.
echo ============================================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo ============================================================
echo.
echo Press any key to exit this window...
pause >nul
