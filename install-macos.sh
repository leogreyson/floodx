#!/bin/bash

# macOS Installation Script for FloodX
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
║                        FloodX Installer (macOS)                             ║
║                          Author: Leo Greyson                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF

echo ""
echo -e "${BLUE}[INFO]${NC} Starting FloodX installation for macOS..."
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}[WARNING]${NC} Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Failed to install Homebrew"
        exit 1
    fi
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${BLUE}[INFO]${NC} Installing Python 3..."
    brew install python3
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Failed to install Python 3"
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
chmod +x run-macos.sh

echo ""
echo -e "${GREEN}[SUCCESS]${NC} FloodX installation completed successfully!"
echo ""

cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                              USAGE OPTIONS                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Option 1: Run "./run-macos.sh" for interactive mode                         ║
║ Option 2: Use command line: python3 main.py [command]                      ║
║                                                                              ║
║ Examples:                                                                    ║
║   ./run-macos.sh                                                             ║
║   python3 main.py --interactive                                             ║
║   sudo python3 main.py syn --target localhost --allow-private              ║
║   sudo python3 main.py http --target http://localhost --allow-private      ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF

echo ""
echo -e "${YELLOW}[INFO]${NC} Use 'sudo' for full functionality (raw sockets)"
echo ""
