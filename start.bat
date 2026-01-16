@echo off
echo ================================================
echo   Swimming Pool Receipt System
echo   Starting server...
echo ================================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if required packages are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM Start the server
python run.py

pause
