@echo off
echo ============================================
echo  Process Document Agent - Web Interface
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.12+ and try again
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found
    echo Please create a .env file with your API keys
    echo See .env.example for reference
    echo.
    pause
)

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Starting Web Server...
echo ============================================
echo.
echo Server will be available at: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.

REM Start the Flask server
python web\server.py

pause
