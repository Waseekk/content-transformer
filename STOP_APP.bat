@echo off
echo ========================================
echo   Stopping Travel News Translator
echo ========================================
echo.

echo Stopping backend (port 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %%a 2>nul

echo Stopping frontend (port 5173)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do taskkill /F /PID %%a 2>nul

timeout /t 1 /nobreak >nul

echo.
echo ========================================
echo   All servers stopped!
echo ========================================
echo.
pause
