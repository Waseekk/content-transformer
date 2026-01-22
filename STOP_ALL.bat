@echo off
title Swiftor - Stopping All Services
color 0C

echo ============================================================
echo                    SWIFTOR - STOP ALL
echo ============================================================
echo.

echo [1/3] Stopping Backend (port 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
echo    Done.

echo [2/3] Stopping Frontend (ports 5173, 5174)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5174 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
echo    Done.

echo [3/3] Closing terminal windows...
taskkill /FI "WINDOWTITLE eq Swiftor Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Swiftor Frontend*" /F >nul 2>&1
echo    Done.

echo.
echo ============================================================
echo   All services stopped.
echo ============================================================
echo.
pause
