@echo off
echo ========================================
echo   Travel News Translator - Startup
echo ========================================
echo.

REM Kill any existing processes on ports 8000 and 5173
echo [1/4] Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul

REM Check if virtual environment exists
echo.
echo [2/4] Checking backend environment...
if exist "backend\venv\Scripts\activate.bat" (
    echo Virtual environment found - using existing venv
) else if exist "venv\Scripts\activate.bat" (
    echo Using root venv folder
) else (
    echo Virtual environment not found. Creating one...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
)

REM Start backend
echo.
echo [3/4] Starting backend server...
cd backend
start "Travel News Backend" cmd /k "venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"
cd ..
timeout /t 3 /nobreak >nul

REM Start frontend
echo.
echo [4/4] Starting frontend...
cd frontend
start "Travel News Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   Both servers are starting!
echo ========================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to exit this window...
echo (Backend and Frontend will keep running)
pause >nul
