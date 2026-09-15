@echo off
title GeoAlert-NER -- System Launcher
echo ============================================================
echo   GeoAlert-NER: North Eastern Region Disaster Management
echo   Starting Full Stack System
echo ============================================================
echo.

cd /d "%~dp0"

REM 1. Start PostgreSQL if not already running
echo [*] Checking PostgreSQL server...
netstat -ano | findstr :5432 >nul 2>&1
if %errorlevel% equ 0 (
    echo [+] PostgreSQL is already running on port 5432.
) else (
    echo [*] Starting PostgreSQL server in background...
    if exist "%USERPROFILE%\pgsql\pgsql\bin\pg_ctl.exe" (
        "%USERPROFILE%\pgsql\pgsql\bin\pg_ctl.exe" -D "%USERPROFILE%\pgsql\data" -l "%USERPROFILE%\pgsql\server.log" start
    ) else (
        echo [ERROR] PostgreSQL not found at %USERPROFILE%\pgsql. Please run setup_environment.bat first!
        pause
        exit /b 1
    )
    timeout /t 2 >nul
)

REM 2. Start FastAPI Backend in new window
echo [*] Starting FastAPI Backend on http://localhost:8000 ...
start "GeoAlert-NER Backend (FastAPI)" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 >nul

REM 3. Start Vite Frontend in new window
echo [*] Starting Vite Frontend on http://localhost:5173 ...
start "GeoAlert-NER Frontend (Vite/React)" cmd /k "cd frontend && npm run dev"

timeout /t 3 >nul

REM 4. Open default web browser
echo [*] Opening GeoAlert-NER Dashboard in your browser...
start http://localhost:5173

echo.
echo ============================================================
echo [SUCCESS] GeoAlert-NER is running!
echo.
echo   - Web Dashboard:     http://localhost:5173
echo   - Backend API Docs:  http://localhost:8000/docs
echo   - Health Check:      http://localhost:8000/health
echo.
echo Leave the backend and frontend command windows open while using.
echo Double-click 'stop_all.bat' to stop all services when finished.
echo ============================================================
pause
