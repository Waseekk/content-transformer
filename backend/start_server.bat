@echo off
echo ========================================
echo Starting Travel News API Server
echo ========================================
echo.

REM Kill any existing Python processes
echo Killing existing Python processes...
taskkill /F /IM python.exe >nul 2>&1

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start the server
echo Starting server on port 8000...
cd /d "%~dp0"
set DATABASE_URL=sqlite:///./test_fresh.db
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
