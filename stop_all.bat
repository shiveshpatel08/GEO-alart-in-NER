@echo off
title GeoAlert-NER -- Service Shutdown
echo ============================================================
echo   Stopping GeoAlert-NER Services
echo ============================================================
echo.

REM Stop uvicorn/python
echo [*] Stopping backend servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq GeoAlert-NER Backend*" >nul 2>&1

REM Stop vite/node
echo [*] Stopping frontend servers...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq GeoAlert-NER Frontend*" >nul 2>&1

REM Stop postgres cleanly
echo [*] Stopping PostgreSQL server...
if exist "%USERPROFILE%\pgsql\pgsql\bin\pg_ctl.exe" (
    "%USERPROFILE%\pgsql\pgsql\bin\pg_ctl.exe" -D "%USERPROFILE%\pgsql\data" stop -m fast
)

echo.
echo ============================================================
echo [SUCCESS] All GeoAlert-NER services stopped cleanly.
echo ============================================================
pause
