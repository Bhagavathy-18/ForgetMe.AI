@echo off
setlocal EnableExtensions EnableDelayedExpansion
title ForgetMe.AI - Privacy-First Mental Health Assistant
cd /d "%~dp0"

echo.
echo ============================================================
echo   ForgetMe.AI - Privacy-First Mental Health Assistant
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python is not installed or not on PATH.
  echo Install Python 3.11+ and enable "Add Python to PATH".
  pause
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo ERROR: Node.js/npm is not installed or not on PATH.
  echo Install Node.js 18+ and try again.
  pause
  exit /b 1
)

if not exist "venv\Scripts\python.exe" (
  echo [1/5] Creating Python virtual environment...
  python -m venv venv
  if errorlevel 1 (
    echo ERROR: Could not create the Python virtual environment.
    pause
    exit /b 1
  )
) else (
  echo [1/5] Python virtual environment already exists.
)

echo [2/5] Activating virtual environment...
call "venv\Scripts\activate.bat"

echo [3/5] Installing backend dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERROR: Python dependency installation failed.
  pause
  exit /b 1
)

echo.
echo [4/5] Groq API configuration
echo.
echo Paste your Groq API key below.
echo The key is NOT written to frontend source code or localStorage.
echo It is held only by the FastAPI process started by this batch file.
echo Leave blank to use the local demo fallback.
echo.
set "GROQ_API_KEY="
set /p "GROQ_API_KEY=Groq API key: "
set "GROQ_MODEL=llama-3.3-70b-versatile"

echo.
echo [5/5] Installing Next.js dependencies...
cd /d "%~dp0frontend"
call npm install
if errorlevel 1 (
  echo ERROR: npm install failed.
  pause
  exit /b 1
)
cd /d "%~dp0"

echo.
echo Starting FastAPI on http://localhost:8000 ...
start "ForgetMe.AI Backend" cmd /k "cd /d ""%~dp0"" && call ""%~dp0venv\Scripts\activate.bat"" && set ""GROQ_API_KEY=%GROQ_API_KEY%"" && set ""GROQ_MODEL=%GROQ_MODEL%"" && python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

echo Starting Next.js on http://localhost:3000 ...
start "ForgetMe.AI Frontend" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"

echo.
echo ============================================================
echo   ForgetMe.AI is starting
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API docs: http://localhost:8000/docs
echo   Groq model: %GROQ_MODEL%
echo ============================================================
echo.
echo Close the Backend and Frontend windows to stop the project.
pause
