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
║                         FloodX Interactive Mode                             ║
║                          Author: Leo Greyson                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF

echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${GREEN}[INFO]${NC} Running as root - full functionality available"
else
   echo -e "${YELLOW}[WARNING]${NC} Not running as root"
   echo -e "${BLUE}[INFO]${NC} Some attacks may fail without root privileges"
   echo -e "${BLUE}[INFO]${NC} Use 'sudo ./run.sh' for full functionality"
fi

echo ""
echo -e "${BLUE}[INFO]${NC} Launching FloodX Interactive Mode..."
echo -e "${BLUE}[INFO]${NC} Press Ctrl+C to exit at any time"
echo ""

python3 floodx.py --interactive

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERROR]${NC} Failed to launch FloodX"
    echo -e "${BLUE}[INFO]${NC} Make sure Python 3 is installed and dependencies are installed"
    echo -e "${BLUE}[INFO]${NC} Run ./install.sh first if you haven't already"
    echo ""
fi
