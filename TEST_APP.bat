@echo off
echo ========================================
echo   Travel News SaaS - Quick Test
echo ========================================
echo.

echo [1/3] Checking Backend...
cd backend
echo Starting Backend Server...
start cmd /k "title Backend Server && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak > nul

echo.
echo [2/3] Checking Frontend...
cd ..\frontend
echo Starting Frontend Server...
start cmd /k "title Frontend Server && npm run dev"

timeout /t 3 /nobreak > nul

echo.
echo [3/3] Opening Browser...
timeout /t 5 /nobreak > nul
start http://localhost:5173

echo.
echo ========================================
echo   Servers Started!
echo ========================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   Docs:     http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to stop servers...
pause > nul

echo.
echo Stopping servers...
taskkill /F /IM node.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend Server*" 2>nul
echo Done!
