@echo off
title ReferralCircle Server
echo ===================================================
echo   Starting ReferralCircle Web Platform (Windows)
echo ===================================================
echo.

:: Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3 from https://www.python.org and check "Add Python to PATH".
    pause
    exit /b
)

:: Install required packages
echo Installing dependencies (FastAPI, Uvicorn, Jinja2, Starlette)...
python -m pip install fastapi uvicorn jinja2 starlette

:: Seed database if not present
if not exist referral_platform.db (
    echo Initializing database with demo circles and leads...
    python seed_data.py
)

:: Launch the application
echo.
echo ===================================================
echo   App running at: http://localhost:8000
echo   Admin Portal:   http://localhost:8000/admin
echo ===================================================
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
