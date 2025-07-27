@echo off
setlocal

REM Store the current directory
set "SCRIPT_DIR=%~dp0"

REM Check if running as Administrator, if not, restart with admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] FloodX requires Administrator privileges for full functionality
    echo [INFO] Requesting Administrator access...
    echo.
    
    REM Use PowerShell to restart with admin privileges, preserving working directory
    powershell -Command "Start-Process '%~f0' -Verb RunAs -WorkingDirectory '%SCRIPT_DIR%'"
    exit /b
)

REM Clear screen and show banner (now running as admin)
cls

REM Change to the script directory to ensure we're in the right location
cd /d "%SCRIPT_DIR%"

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║                         FloodX Interactive Mode                             ║
echo ║                          Author: Leo Greyson                                ║
echo ║                       [ADMINISTRATOR MODE ACTIVE]                           ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo [SUCCESS] Running with Administrator privileges
echo [INFO] All attack vectors are now fully functional
echo [INFO] Press Ctrl+C to exit at any time
echo.

python floodx.py --interactive

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to launch FloodX
    echo [INFO] Make sure Python is installed and dependencies are installed
    echo [INFO] Run install.bat first if you haven't already
    echo.
    pause
    exit /b 1
)

REM Keep window open if there was an error
if %errorlevel% neq 0 pause
