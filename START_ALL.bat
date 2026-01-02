@echo off
echo ========================================
echo   SWIFTOR - Start All Services
echo ========================================
echo.

echo [1/2] Starting Backend Server...
start "Backend Server" cmd /k "START_BACKEND.bat"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo [2/2] Starting Frontend Server...
start "Frontend Server" cmd /k "START_FRONTEND.bat"

echo Waiting for frontend to initialize...
timeout /t 8 /nobreak > nul

echo.
echo ========================================
echo   SWIFTOR - All Servers Started!
echo ========================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo.
echo ========================================
echo.

echo Opening browser...
start http://localhost:5173

echo.
echo Servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
