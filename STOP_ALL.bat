@echo off
echo ========================================
echo   Stopping All Servers
echo ========================================
echo.

echo Stopping Node.js processes (Frontend)...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo   Frontend stopped successfully
) else (
    echo   No frontend server running
)

echo.
echo Stopping Python processes (Backend)...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend Server*" 2>nul
if %errorlevel% equ 0 (
    echo   Backend stopped successfully
) else (
    echo   No backend server running
)

echo.
echo ========================================
echo   All servers stopped
echo ========================================
echo.
pause
