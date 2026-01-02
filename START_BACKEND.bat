@echo off
title Backend Server - FastAPI
echo ========================================
echo   Starting Backend Server (FastAPI)
echo ========================================
echo.

cd backend

echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Using system Python...
)

echo.
echo Starting FastAPI server on port 8000...
echo.
echo Backend will be available at:
echo   - API: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo.
echo ========================================
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
