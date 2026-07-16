@echo off
echo ====================================================
echo Starting LinkedIn Tender ^& Scheme Tracker...
echo ====================================================

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please set up the project first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run the python script
python main.py

:: Deactivate
call deactivate

echo.
echo Process complete. Press any key to exit...
pause >nul
