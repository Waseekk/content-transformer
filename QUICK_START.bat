@echo off
REM ============================================================================
REM Quick Start Menu for Travel News Translator
REM ============================================================================

:menu
cls
echo.
echo ============================================================================
echo           TRAVEL NEWS TRANSLATOR - QUICK START MENU
echo ============================================================================
echo.
echo 📊 Current Branch:
git branch --show-current 2>nul || echo Not a git repository yet
echo.
echo ============================================================================
echo.
echo Choose an option:
echo.
echo  1. 🚀 Run Streamlit App (Legacy - Single User)
echo  2. 🎯 Run Full Stack (React + FastAPI) [RECOMMENDED]
echo  3. 🔧 Run Backend API Only
echo  4. 🌿 Setup Git Branches (for Streamlit Cloud)
echo  5. 📝 Test OpenAI Translation
echo  6. 🔍 View Logs
echo  7. ℹ️  Show Project Status
echo  8. 📖 Open Documentation
echo  9. 🛑 Stop All Services
echo  0. ❌ Exit
echo.
echo ============================================================================
echo.

set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto streamlit
if "%choice%"=="2" goto fullstack
if "%choice%"=="3" goto backend
if "%choice%"=="4" goto git_setup
if "%choice%"=="5" goto test_openai
if "%choice%"=="6" goto logs
if "%choice%"=="7" goto status
if "%choice%"=="8" goto docs
if "%choice%"=="9" goto stop
if "%choice%"=="0" goto end

echo Invalid choice. Please try again.
pause
goto menu

:streamlit
cls
echo.
echo ============================================================================
echo 🚀 Starting Streamlit App...
echo ============================================================================
echo.
echo The app will open in your browser at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================================
echo.
streamlit run app.py
goto menu

:fullstack
cls
echo.
echo ============================================================================
echo 🎯 Starting Full Stack (React + FastAPI)...
echo ============================================================================
echo.
call START_FULLSTACK.bat
goto menu

:backend
cls
echo.
echo ============================================================================
echo 🔧 Starting FastAPI Backend...
echo ============================================================================
echo.
echo API will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================================
echo.
cd backend
uvicorn app.main:app --reload
cd ..
goto menu

:git_setup
cls
echo.
echo ============================================================================
echo 🌿 Setting up Git Branches...
echo ============================================================================
echo.
call setup_git_branches.bat
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:test_openai
cls
echo.
echo ============================================================================
echo 📝 Testing OpenAI Translation...
echo ============================================================================
echo.
cd backend
python test_openai_direct.py
cd ..
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:logs
cls
echo.
echo ============================================================================
echo 🔍 Recent Logs
echo ============================================================================
echo.
echo --- Webapp Logs (last 20 lines) ---
echo.
if exist logs\webapp_*.log (
    for /f %%i in ('dir /b /o-d logs\webapp_*.log') do (
        type "logs\%%i" | more /E +0 | findstr /N "^" | findstr /R "[0-9]*:.*ERROR [0-9]*:.*WARNING [0-9]*:.*INFO" | more
        goto logs_done
    )
) else (
    echo No logs found yet.
)
:logs_done
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:status
cls
echo.
echo ============================================================================
echo 📊 PROJECT STATUS
echo ============================================================================
echo.
echo 📁 Location:
cd
echo.
echo 🌿 Git Status:
git status -s 2>nul || echo Not a git repository yet
echo.
echo 📦 Backend Progress:
echo   ✅ Phase 1: Backend Foundation (Complete)
echo   ✅ Phase 2: Core APIs (Complete)
echo   ⏳ Phase 3: Celery + WebSocket (Not started)
echo   ⏳ Phase 4: Admin Panel (Not started)
echo   ⏳ Phase 5-6: React Frontend (Not started)
echo   ⏳ Phase 7: Playwright (Not started)
echo   ⏳ Phase 8: Optimization (Not started)
echo.
echo 🎯 Progress: 2/8 Phases (25%%)
echo.
echo 📝 Recent Files:
dir /o-d /b *.md 2>nul | findstr /V "README" | more
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:docs
cls
echo.
echo ============================================================================
echo 📖 DOCUMENTATION
echo ============================================================================
echo.
echo Available documentation files:
echo.
if exist FIXES_AND_SOLUTIONS.md echo  ✅ FIXES_AND_SOLUTIONS.md - Latest fixes
if exist STREAMLIT_DEPLOYMENT_GUIDE.md echo  ✅ STREAMLIT_DEPLOYMENT_GUIDE.md - Deployment guide
if exist OPENAI_TRANSLATION_MIGRATION.md echo  ✅ OPENAI_TRANSLATION_MIGRATION.md - Translation system
if exist PHASE1_COMPLETE.md echo  ✅ PHASE1_COMPLETE.md - Phase 1 details
if exist PHASE2_COMPLETE.md echo  ✅ PHASE2_COMPLETE.md - Phase 2 details
if exist CLAUDE.md echo  ✅ CLAUDE.md - Project overview
echo.
echo Opening FIXES_AND_SOLUTIONS.md...
start FIXES_AND_SOLUTIONS.md
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:stop
cls
echo.
echo ============================================================================
echo 🛑 Stopping All Services...
echo ============================================================================
echo.
call STOP_SERVICES.bat
goto menu

:end
cls
echo.
echo ============================================================================
echo Thanks for using Travel News Translator!
echo ============================================================================
echo.
echo 📝 Quick Commands:
echo   • Full Stack: START_FULLSTACK.bat
echo   • Streamlit:  streamlit run app.py (legacy)
echo   • Backend:    cd backend ^&^& uvicorn app.main:app --reload
echo   • Frontend:   cd frontend ^&^& npm run dev
echo   • Stop All:   STOP_SERVICES.bat
echo.
echo ============================================================================
echo.
