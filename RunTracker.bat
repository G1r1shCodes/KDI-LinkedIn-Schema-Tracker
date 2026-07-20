@echo off
echo ====================================================
echo  LinkedIn Tender ^& Scheme Tracker
echo ====================================================
echo.

:: Change to the project directory (same folder as this .bat)
cd /d "%~dp0"

echo [Step 1] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [Step 2] Installing / updating dependencies...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)

echo [Step 3] Ensuring Playwright browser is installed...
python -m playwright install chromium --quiet
if errorlevel 1 (
    echo ERROR: Failed to install Playwright browser.
    pause
    exit /b 1
)

echo.
echo [Step 4] Starting the Tracker Script...
echo NOTE: A Chrome browser window will open automatically for scraping.
echo       Do NOT close it until the tracker finishes.
echo.
python main.py

echo.
echo ====================================================
echo  Process complete!
echo ====================================================
pause
