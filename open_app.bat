@echo off
title AI Saathi (एआई साथी) - One-Click Launcher
echo ========================================================
echo       AI Saathi (एआई साथी) - Rural Civic Assistant
echo ========================================================
echo Checking AI Saathi backend server status...

powershell -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 2 -UseBasicParsing).StatusCode } catch { exit 1 }" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend server is already running!
) else (
    echo [!] Backend server is not running. Starting backend server...
    start "AI Saathi Backend" /min cmd /c "cd /d "%~dp0backend" && python -m uvicorn main:app --host 127.0.0.1 --port 8000"
    echo Waiting for server to initialize...
    timeout /t 3 /nobreak >nul
)

echo [OK] Opening AI Saathi portal in your browser...
start http://127.0.0.1:8000/
echo.
echo ========================================================
echo AI Saathi is now active at http://127.0.0.1:8000/
echo ========================================================
exit
