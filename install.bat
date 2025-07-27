@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║    ███████╗██╗      ██████╗  ██████╗ ██████╗ ██╗  ██╗                        ║
echo ║    ██╔════╝██║     ██╔═══██╗██╔═══██╗██╔══██╗╚██╗██╔╝                        ║
echo ║    █████╗  ██║     ██║   ██║██║   ██║██║  ██║ ╚███╔╝                         ║
echo ║    ██╔══╝  ██║     ██║   ██║██║   ██║██║  ██║ ██╔██╗                         ║
echo ║    ██║     ███████╗╚██████╔╝╚██████╔╝██████╔╝██╔╝ ██╗                        ║
echo ║    ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝                        ║
echo ║                                                                              ║
echo ║                        FloodX Installer (Windows)                           ║
echo ║                          Author: Leo Greyson                                ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo [INFO] Starting FloodX installation for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Please install Python 3.8+ from https://python.org
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [INFO] Python found! Checking version...
python --version

echo.
echo [INFO] Installing required dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo [INFO] Try running as Administrator or check your internet connection
    pause
    exit /b 1
)

echo.
echo [SUCCESS] FloodX installation completed successfully!
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                              USAGE OPTIONS                                  ║
echo ╠══════════════════════════════════════════════════════════════════════════════╣
echo ║ Option 1: Double-click "run.bat" for interactive mode                       ║
echo ║ Option 2: Use command line: python main.py [command]                       ║
echo ║                                                                              ║
echo ║ Examples:                                                                    ║
echo ║   python main.py --interactive                                              ║
echo ║   python main.py syn --target localhost --allow-private                    ║
echo ║   python main.py http --target http://localhost --allow-private            ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Run as Administrator for full functionality (raw sockets)
echo.
pause
