@echo off
SETLOCAL EnableDelayedExpansion

echo ========================================
echo Economic Policy Simulator - Startup
echo ========================================
echo.

:: Store the project root directory
set "PROJECT_ROOT=%~dp0"

:: Check for Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check for Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

echo Python found:
python --version
echo Node.js found:
node --version
echo npm found:
call npm --version
echo.

:: Check that backend folder exists
if not exist "%PROJECT_ROOT%backend" (
    echo ERROR: Backend folder not found at %PROJECT_ROOT%backend
    pause
    exit /b 1
)

:: Check that frontend folder exists
if not exist "%PROJECT_ROOT%frontend" (
    echo ERROR: Frontend folder not found at %PROJECT_ROOT%frontend
    pause
    exit /b 1
)

:: Setup backend
echo.
echo [1/4] Setting up Python backend...

if not exist "%PROJECT_ROOT%backend\venv" (
    echo Creating virtual environment...
    python -m venv "%PROJECT_ROOT%backend\venv"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Installing Python packages...
call "%PROJECT_ROOT%backend\venv\Scripts\pip.exe" install -r "%PROJECT_ROOT%backend\requirements.txt" --quiet
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Some packages may have failed to install
)

:: Setup frontend
echo.
echo [2/4] Setting up Node.js frontend...

if not exist "%PROJECT_ROOT%frontend\node_modules" (
    echo Installing npm packages...
    cd /d "%PROJECT_ROOT%frontend"
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo WARNING: npm install encountered issues
    )
    cd /d "%PROJECT_ROOT%"
) else (
    echo npm packages already installed.
)

:: Start servers
echo.
echo [3/4] Starting backend server...
start "Backend Server" cmd /k "cd /d "%PROJECT_ROOT%backend" && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --port 8000"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo [4/4] Starting frontend server...
start "Frontend Server" cmd /k "cd /d "%PROJECT_ROOT%frontend" && npm run dev"

echo Waiting for frontend to start...
timeout /t 5 /nobreak > nul

:: Open browser
echo.
echo ========================================
echo Opening browser...
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:5173
echo API Docs:    http://localhost:8000/docs
echo ========================================
start http://localhost:5173

echo.
echo Servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause

ENDLOCAL
