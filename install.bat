@echo off
REM Installation script for egile-mcp-notifier on Windows

echo Installing egile-mcp-notifier...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10 or later from https://www.python.org/
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install package in editable mode
echo Installing package...
pip install -e .

REM Create .env template if it doesn't exist
if not exist ".env" (
    echo Creating .env template...
    (
        echo # Email Configuration
        echo SMTP_HOST=smtp.gmail.com
        echo SMTP_PORT=587
        echo SMTP_USERNAME=your-email@gmail.com
        echo SMTP_PASSWORD=your-app-password
        echo DEFAULT_FROM_EMAIL=your-email@gmail.com
        echo.
        echo # Google Calendar Configuration
        echo GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
        echo GOOGLE_CALENDAR_TOKEN_FILE=token.json
        echo DEFAULT_CALENDAR_ID=primary
    ) > .env
    echo.
    echo .env template created. Please update with your credentials.
)

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Edit .env file with your email and Google Calendar credentials
echo 2. Set up Google Calendar API (see README.md for instructions^)
echo 3. Run: egile-mcp-notifier
echo.
pause
