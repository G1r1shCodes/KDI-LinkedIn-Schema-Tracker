@echo off
echo ====================================================
echo Starting LinkedIn Tender ^& Scheme Tracker...
echo ====================================================

:: Use a dedicated isolated Chrome profile for scraping to prevent conflicts
set "CHROME_DATA_DIR=%~dp0chrome-data"

echo [Step 1] Launching Dedicated Scraping Browser...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%CHROME_DATA_DIR%" "https://www.linkedin.com/"

echo Waiting for Chrome to load...
timeout /t 5 /nobreak >nul

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please set up the project first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run the python script
echo [Step 2] Starting the Tracker Script...
python main.py

:: Deactivate
call deactivate
pause

echo.
echo Process complete. Press any key to exit...
pause >nul
