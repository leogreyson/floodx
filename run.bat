@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║                         FloodX Interactive Mode                             ║
echo ║                          Author: Leo Greyson                                ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Not running as Administrator
    echo [INFO] Some attacks may fail without Administrator privileges
    echo [INFO] Right-click this file and select "Run as administrator" for full functionality
    echo.
)

echo [INFO] Launching FloodX Interactive Mode...
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
)
