#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ███████╗██╗      ██████╗  ██████╗ ██████╗ ██╗  ██╗                        ║
║    ██╔════╝██║     ██╔═══██╗██╔═══██╗██╔══██╗╚██╗██╔╝                        ║
║    █████╗  ██║     ██║   ██║██║   ██║██║  ██║ ╚███╔╝                         ║
║    ██╔══╝  ██║     ██║   ██║██║   ██║██║  ██║ ██╔██╗                         ║
║    ██║     ███████╗╚██████╔╝╚██████╔╝██████╔╝██╔╝ ██╗                        ║
║    ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝                        ║
║                                                                              ║
║                        FloodX Installer (Linux)                             ║
║                          Author: Leo Greyson                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF

echo ""
echo -e "${BLUE}[INFO]${NC} Starting FloodX installation for Linux..."
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}[WARNING]${NC} Running as root - this is recommended for full functionality"
else
   echo -e "${YELLOW}[WARNING]${NC} Not running as root - use 'sudo ./install.sh' for full functionality"
fi

echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python 3 is not installed"
    echo -e "${BLUE}[INFO]${NC} Installing Python 3..."
    
    # Detect distribution and install Python
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3 python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v pacman &> /dev/null; then
        sudo pacman -S python python-pip
    else
        echo -e "${RED}[ERROR]${NC} Could not detect package manager. Please install Python 3 manually."
        exit 1
    fi
fi

echo -e "${GREEN}[SUCCESS]${NC} Python found! Checking version..."
python3 --version

echo ""
echo -e "${BLUE}[INFO]${NC} Installing required dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Failed to install dependencies"
    echo -e "${BLUE}[INFO]${NC} Try running with sudo or check your internet connection"
    exit 1
fi

# Make run script executable
chmod +x run.sh

echo ""
echo -e "${GREEN}[SUCCESS]${NC} FloodX installation completed successfully!"
echo ""

cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                              USAGE OPTIONS                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Option 1: Run "./run.sh" for interactive mode                               ║
║ Option 2: Use command line: python3 main.py [command]                      ║
║                                                                              ║
║ Examples:                                                                    ║
║   ./run.sh                                                                   ║
║   python3 main.py --interactive                                             ║
║   sudo python3 main.py syn --target localhost --allow-private              ║
║   sudo python3 main.py http --target http://localhost --allow-private      ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF

echo ""
echo -e "${YELLOW}[INFO]${NC} Use 'sudo' for full functionality (raw sockets)"
echo ""
