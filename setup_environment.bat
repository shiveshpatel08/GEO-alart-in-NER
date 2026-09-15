@echo off
title GeoAlert-NER -- Environment Setup
echo ============================================================
echo   GeoAlert-NER: North Eastern Region Disaster Management
echo   Automated Environment Setup for Team Leader Laptop
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+ from python.org.
    pause
    exit /b 1
)
python --version

echo.
echo [2/5] Installing Python backend requirements...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] pip install had warnings, continuing...
)

echo.
echo [3/5] Setting up Portable PostgreSQL 16 + PostGIS 3.6...
python scripts\setup_portable_postgres.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to set up PostgreSQL. Check logs above.
    pause
    exit /b 1
)

echo.
echo [4/5] Applying Alembic database migrations & Seeding Data...
python scripts\init_db_and_postgis.py
alembic upgrade head
python scripts\seed_data.py
python scripts\import_real_landslides.py

echo.
echo [5/5] Installing Frontend Dependencies...
cd frontend
call npm install
cd ..

echo.
echo ============================================================
echo [SUCCESS] Environment is fully set up and ready!
echo You can now double-click 'start_all.bat' to launch the project.
echo ============================================================
pause
