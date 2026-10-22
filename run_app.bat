@echo off
title SecureCode AI - Code Reviewer & Vulnerability Scanner
color 0b

echo =========================================================
echo    Starting SecureCode AI Dashboard...
echo =========================================================
echo.

:: 1. Navigate to the script's directory (ensures paths work from Desktop shortcut)
cd /d "%~dp0"

:: 2. Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'venv' not found in %~dp0
    echo Please create it using: python -m venv venv
    pause
    exit /b
)

:: 3. Activate virtual environment
echo [*] Activating Python virtual environment...
call venv\Scripts\activate.bat

:: 4. Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [*] Streamlit not detected. Installing dependencies from requirements.txt...
    pip install -r requirements.txt
)

:: 5. Launch the Streamlit application
echo [*] Launching Streamlit dashboard...
echo [*] Opening browser at http://localhost:8501...
echo.
streamlit run app.py --server.headless false

:: Pause on exit if it crashes unexpectedly
if errorlevel 1 (
    echo.
    echo [ERROR] Application terminated unexpectedly.
    pause
)