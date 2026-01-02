@echo off
title Frontend Server - React
echo ========================================
echo   Starting Frontend Server (React)
echo ========================================
echo.

cd frontend

echo Starting React development server...
echo.
echo Frontend will be available at:
echo   - http://localhost:5173
echo.
echo ========================================
echo Press Ctrl+C to stop the server
echo ========================================
echo.

npm run dev

pause
