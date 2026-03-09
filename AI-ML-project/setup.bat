@echo off
setlocal

echo ============================================
echo  Miro Face Detector - Environment Setup
echo ============================================
echo.

REM --- Create virtual environment ---
if exist .venv (
    echo Virtual environment already exists, skipping creation.
) else (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        echo Make sure Python 3.8+ is installed and on your PATH.
        pause
        exit /b 1
    )
    echo Done.
)

echo.

REM --- Activate and install dependencies ---
echo Installing dependencies from requirements.txt...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

echo.

REM --- Download MediaPipe model files ---
echo Downloading required MediaPipe model files...
python main.py setup
if errorlevel 1 (
    echo ERROR: Model download failed.
    pause
    exit /b 1
)

echo.

echo ============================================
echo  Setup complete.
echo  To activate the environment later, run:
echo    CMD:      .venv\Scripts\activate
echo    Git Bash: source .venv/Scripts/activate
echo  Then use: python main.py ^<command^>
echo ============================================
echo.

pause