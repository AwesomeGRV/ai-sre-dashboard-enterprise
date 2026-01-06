@echo off
echo Starting AI-Powered SRE Dashboard Demo...
echo.

echo [1/4] Starting Sample Node.js Application...
cd /d "%~dp0apps\sample-node-app"
start "Sample App" cmd /k "npm install && npm start"
timeout /t 5 >nul

echo [2/4] Starting Backend API...
cd /d "%~dp0backend\api"
start "Backend API" cmd /k "pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5 >nul

echo [3/4] Starting Frontend Dashboard...
cd /d "%~dp0frontend\dashboard"
start "Frontend" cmd /k "npm install && npm start"
timeout /t 5 >nul

echo [4/4] Opening Dashboard in Browser...
timeout /t 10 >nul
start http://localhost:3000

echo.
echo ========================================
echo AI-Powered SRE Dashboard is starting!
echo.
echo Access URLs:
echo - Main Dashboard: http://localhost:3000
echo - Backend API:   http://localhost:8000
echo - Sample App:    http://localhost:3000
echo.
echo Services are starting in separate windows.
echo Close this window or press any key to continue...
pause >nul
