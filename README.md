# 🌊 FLOODX - Multi-Vector DDoS Toolkit
<div align="center">

```
    ███████╗██╗      ██████╗  ██████╗ ██████╗ ██╗  ██╗
    ██╔════╝██║     ██╔═══██╗██╔═══██╗██╔══██╗╚██╗██╔╝
    █████╗  ██║     ██║   ██║██║   ██║██║  ██║ ╚███╔╝ 
    ██╔══╝  ██║     ██║   ██║██║   ██║██║  ██║ ██╔██╗ 
    ██║     ███████╗╚██████╔╝╚██████╔╝██████╔╝██╔╝ ██╗
    ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
```

**Advanced Multi-Vector DDoS Testing Framework**  
*Professional Network Security Research & Penetration Testing Tool*

**Author**: Leo Greyson

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776ab?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-lightgrey)](#installation)

</div>

---

## 🚀 **What is FloodX?**

FloodX is a powerful, multi-vector DDoS testing framework that helps cybersecurity professionals assess network resilience. It features **endless continuous attacks** with automatic restart mechanisms and intelligent IP spoofing.

### ✨ **Key Features**

- 🔄 **Endless Attacks**: All vectors run continuously until manually stopped
- 🎯 **8 Attack Vectors**: SYN, HTTP, ICMP, TLS, UDP, Slowloris, WebSocket, SMTP
- 🔄 **Auto-Restart**: Intelligent worker restart for continuous operation  
- 🎭 **IP Spoofing**: Generate 1,500-2,500 randomized IP addresses per session
- 📊 **Real-time Stats**: Live performance monitoring with colored output
- 🛡️ **Safety Built-in**: Target validation and private network protection

---

## 📥 **Installation**

### <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg" width="20"> **Prerequisites**
- **Python 3.8+** (3.10+ recommended)
- **Administrator/Root privileges** (for raw sockets)

### <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20"> **Quick Install**

**🚀 Easy Installation (Recommended):**

<details>
<summary><strong>🪟 Windows</strong></summary>

```powershell
# Download and run the installer
git clone https://github.com/leogreyson/floodx.git
cd floodx
.\install.bat

# Launch FloodX (Interactive Mode)
.\floodx.bat
```

</details>

<details>
<summary><strong>🐧 Linux</strong></summary>

```bash
# Step 1: Update system and install Python + pip
sudo apt update && sudo apt install python3 python3-pip -y

# Step 2: Download FloodX
git clone https://github.com/leogreyson/floodx.git
cd floodx

# Step 3: Install dependencies (simple!)
sudo pip3 install -r requirements.txt

# Step 4: Make launcher executable and run
chmod +x floodx.sh
sudo ./floodx.sh

# Alternative: Install system packages directly (no pip needed)
# sudo apt install python3-aiohttp python3-websockets python3-requests python3-colorama python3-yaml python3-scapy
```

</details>

<details>
<summary><strong>🍎 macOS</strong></summary>

```bash
# Download and run the installer
git clone https://github.com/leogreyson/floodx.git
cd floodx
chmod +x install-macos.sh floodx.sh
./install-macos.sh

# Launch FloodX (Interactive Mode)  
./floodx.sh
```

</details>

**📦 Manual Installation:**

```bash
# Clone the repository
git clone https://github.com/leogreyson/floodx.git
cd floodx

# Method 1: Simple System Installation (RECOMMENDED)
# Step 1: Install Python and pip
sudo apt update && sudo apt install python3 python3-pip -y
# Step 2: Install dependencies with pip
sudo pip3 install -r requirements.txt

# Method 2: System packages (Ubuntu/Debian - no pip needed)
sudo apt install python3-aiohttp python3-websockets python3-requests python3-colorama python3-yaml python3-scapy

# Method 3: User installation (if no sudo access)
pip3 install --user -r requirements.txt

# Method 4: Virtual environment (if you prefer isolation)
python3 -m venv floodx-env
source floodx-env/bin/activate
pip install -r requirements.txt

# Test installation
sudo python3 main.py --help
```

### 🔧 **Troubleshooting Installation Issues**

<details>
<summary><strong>🚫 "externally-managed-environment" Error (Ubuntu 23.04+)</strong></summary>

**Problem**: Modern Linux distributions prevent system-wide pip installations

**Solutions**:
```bash
# Option 1: Install with sudo (RECOMMENDED - simple and works)
sudo pip3 install -r requirements.txt

# Option 2: Install system packages via apt (no pip needed)
sudo apt install python3-aiohttp python3-websockets python3-requests python3-colorama python3-yaml python3-scapy

# Option 3: User installation (no sudo needed)
pip3 install --user -r requirements.txt

# Option 4: Use virtual environment (if you prefer isolation)
python3 -m venv floodx-env
source floodx-env/bin/activate
pip install -r requirements.txt

# Option 5: Override system protection (NOT RECOMMENDED)
pip3 install -r requirements.txt --break-system-packages
```

**Running FloodX after installation**:
```bash
# Simple system installation - just run with sudo
sudo python3 main.py --help
sudo python3 main.py --interactive

# User installation - run normally
python3 main.py --help
python3 main.py --interactive

# Virtual environment - activate first
source floodx-env/bin/activate
python3 main.py --help
```

</details>

<details>
<summary><strong>❌ "pip3: command not found" Error</strong></summary>

**Problem**: The installer fails with "pip3: command not found"

**Solutions**:
```bash
# Option 1: Install pip3 (Ubuntu/Debian)
sudo apt update && sudo apt install python3-pip -y

# Option 2: Install pip3 (CentOS/RHEL)
sudo yum install python3-pip -y

# Option 3: Install pip3 (Fedora)
sudo dnf install python3-pip -y

# Option 4: Use alternative pip command
python3 -m pip install -r requirements.txt

# Option 5: Manual dependency installation
pip install aiohttp asyncio scapy websockets requests colorama pyyaml
```

</details>

<details>
<summary><strong>⚠️ Permission Denied Errors</strong></summary>

**Problem**: Permission errors during installation

**Solutions**:
```bash
# Always use sudo for the installer
sudo ./install.sh

# For manual installation, use --user flag
pip3 install --user -r requirements.txt

# Or install system-wide with sudo
sudo pip3 install -r requirements.txt
```

</details>

<details>
<summary><strong>🐍 Python Version Issues</strong></summary>

**Problem**: Python version compatibility issues

**Solutions**:
```bash
# Check Python version (needs 3.8+)
python3 --version

# Install newer Python on Ubuntu
sudo apt install python3.10 python3.10-pip -y

# Use specific Python version
python3.10 -m pip install -r requirements.txt
python3.10 main.py --help
```

</details>

### 🖥️ **Platform-Specific Setup**

<details>
<summary><img src="https://upload.wikimedia.org/wikipedia/commons/8/87/Windows_logo_-_2021.svg" width="20"> <strong>Windows</strong></summary>

```powershell
# Run PowerShell as Administrator
# Install Python from python.org

# Clone and setup
git clone https://github.com/leogreyson/floodx.git
cd floodx
pip install -r requirements.txt

# Test installation
python main.py --help
```

</details>

<details>
<summary><img src="https://upload.wikimedia.org/wikipedia/commons/3/35/Tux.svg" width="20"> <strong>Linux</strong></summary>

```bash
# Update packages and install dependencies
sudo apt update && sudo apt install python3 python3-pip -y

# Clone and setup (simple system installation)
git clone https://github.com/leogreyson/floodx.git
cd floodx
sudo pip3 install -r requirements.txt

# Test installation (requires sudo for raw sockets)
sudo python3 main.py --help

# Alternative: System packages installation (no pip needed)  
sudo apt install python3-aiohttp python3-websockets python3-requests python3-colorama python3-yaml python3-scapy
sudo python3 main.py --help

# Alternative: Virtual environment (if you prefer isolation)
python3 -m venv floodx-env
source floodx-env/bin/activate
pip install -r requirements.txt
sudo floodx-env/bin/python3 main.py --help
```

</details>

<details>
<summary><img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg" width="20"> <strong>macOS</strong></summary>

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and clone
brew install python3
git clone https://github.com/leogreyson/floodx.git
cd floodx
pip3 install -r requirements.txt

# Test installation (requires sudo for raw sockets)
sudo python3 main.py --help
```

</details>

---

## 🎯 **Quick Start**

### 🚀 **Two Usage Options**

**Option 1: Easy Interactive Mode (Recommended for Beginners)**
```bash
# Windows
.\floodx.bat

# Linux/macOS
./floodx.sh
```

**Option 2: Command Line Mode (Advanced Users)**
```bash
python main.py --interactive           # Interactive TUI
python main.py [attack] [options]      # Direct command
```

### 🎮 **Interactive Mode** (Recommended)
```bash
python main.py --interactive
```

### ⚡ **Command Line Examples**

All attacks now run **endlessly by default** until you press `Ctrl+C`:

```bash
# Endless SYN flood (runs until Ctrl+C)
python main.py syn --target localhost --allow-private

# Endless HTTP flood with 500 threads
python main.py http --target http://localhost:8080 --threads 500 --allow-private

# Endless multi-vector attack
python main.py multi-enhanced --target localhost --vectors syn http tls --allow-private

# Continuous attack with IP spoofing
python main.py continuous --target localhost --vector syn --spoof-ip --allow-private
```

### 🔄 **Endless Attack Features**

- **Duration 0 = Infinite**: All attacks run continuously by default
- **Auto-Restart**: Workers automatically restart every 30-60 seconds  
- **IP Spoofing Pools**: Generate 1,500-2,500 randomized addresses
- **Packet Resending**: Continuous packet generation until stopped
- **Worker Revival**: Dead workers are automatically replaced

---

## 🛠️ **Available Attack Vectors**

| Vector | Description | Command |
|--------|-------------|---------|
| 🌊 **SYN** | TCP SYN flood | `python main.py syn --target host` |
| 🌐 **HTTP** | HTTP request flood | `python main.py http --target http://host` |
| 🏓 **ICMP** | ICMP ping flood | `python main.py icmp --target host` |
| 🔐 **TLS** | TLS handshake flood | `python main.py tls --target host --port 443` |
| 📡 **UDP** | UDP amplification | `python main.py udp --target host` |
| 🐌 **Slowloris** | Slow HTTP connections | `python main.py slowloris --target host` |
| 🔌 **WebSocket** | WebSocket storm | `python main.py websocket --target ws://host/ws` |
| 📧 **SMTP** | SMTP flood | `python main.py smtp --target host --port 25` |

### 🎯 **Multi-Vector Attacks**
```bash
# Coordinated attack with multiple vectors
python main.py multi-enhanced --target localhost --vectors syn http tls dns --allow-private

# Legacy multi-vector
python main.py multi --target localhost --vectors syn http --allow-private
```

---

## ⚙️ **Configuration Options**

| Option | Description | Example |
|--------|-------------|---------|
| `--target` | Target IP/hostname/URL | `--target localhost` |
| `--port` | Target port | `--port 8080` |
| `--threads` | Concurrent workers | `--threads 1000` |
| `--duration` | Duration (0=infinite) | `--duration 0` |
| `--allow-private` | Allow localhost testing | `--allow-private` |
| `--spoof-ip` | Enable IP spoofing | `--spoof-ip` |

---

## 📊 **Real-Time Statistics**

FloodX provides live monitoring with colored output:

```
[  15.2s] ⚡12,500 pkts 📊823.4 pps 📡25 conn 💾488.3 KB 🔥10 threads ❌2 errs
🎭 Generated 1,894 spoofed IP addresses
🔄 Cycle 3: 2,847 packets, 12 errors
```

---

## 🛡️ **Safety Features**

- ✅ **Target Validation**: Automatic localhost/private network detection
- ✅ **Confirmation Prompts**: Safety checks before dangerous operations  
- ✅ **Graceful Shutdown**: Clean Ctrl+C handling with statistics
- ✅ **Error Handling**: Comprehensive error reporting and recovery

---

## 🚨 **Important Usage Notes**

### 🚀 **Easy Launch Scripts**
- **Windows**: Double-click `floodx.bat` or use `.\floodx.bat` in PowerShell
- **Linux/macOS**: Use `./floodx.sh` (after `chmod +x floodx.sh`)

| Platform | Installer | Launcher |
|----------|-----------|----------|
| 🪟 **Windows** | `install.bat` | `floodx.bat` |
| 🐧 **Linux** | `install.sh` | `floodx.sh` |
| 🍎 **macOS** | `install-macos.sh` | `floodx.sh` |

### ⚠️ **Administrator/Root Required**
- **Windows**: Run PowerShell as Administrator
- **Linux/macOS**: Use `sudo` for raw socket operations and installation

### 🚨 **Quick Fix for "externally-managed-environment" Error**
```bash
# RECOMMENDED: Simple system installation with sudo
sudo pip3 install -r requirements.txt

# OR use system packages (no pip needed)
sudo apt install python3-aiohttp python3-websockets python3-requests python3-colorama python3-yaml python3-scapy

# OR user installation (no sudo needed)
pip3 install --user -r requirements.txt

# OR virtual environment (if you prefer isolation)
python3 -m venv floodx-env && source floodx-env/bin/activate && pip install -r requirements.txt
```

### 🚨 **Quick Fix for "pip3: command not found"**
```bash
# Install pip3 first, then retry installation
sudo apt update && sudo apt install python3-pip -y
sudo ./install.sh

# OR install dependencies manually
pip3 install -r requirements.txt
# OR use alternative method
python3 -m pip install -r requirements.txt
```

### 🏠 **Testing on Localhost**
Always use `--allow-private` for local testing:
```bash
python main.py syn --target localhost --allow-private
```

### 🛑 **Stopping Attacks**
- Press `Ctrl+C` to stop any running attack
- All attacks now run endlessly until manually stopped
- Statistics are displayed on shutdown

---

## 🤝 **Contributing**

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ☕ **Buy Me Coffee**

<div align="center">

If you find FloodX useful and want to support development, you can buy me a coffee! 

### 🇰🇭 **KHQR Payment (Cambodia)**

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_Cambodia.svg/50px-Flag_of_Cambodia.svg.png" alt="Cambodia Flag" width="30">

<div align="center">

[![KHQR Payment](https://i.ibb.co/Zp2RW4B4/QR-Copy.png)](https://link.payway.com.kh/ABAPAYYB3697967)

**🔗 Quick Pay**: [link.payway.com.kh/ABAPAYYB3697967](https://link.payway.com.kh/ABAPAYYB3697967)

</div>

*Scan QR code or click the link above - works with any Cambodian banking app (ABA, ACLEDA, Wing, etc.)*

### 🌍 **International Support**

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/leogreyson)

</div>

---

## 📞 **Support & Community**

- 🐛 **Issues**: [GitHub Issues](https://github.com/leogreyson/floodx/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/leogreyson/floodx/discussions)
- 📧 **Email**: [info@leogreyson.org](mailto:info@leogreyson.org)
- 🐦 **Twitter**: [@LeoTechSecurity](https://x.com/LeoTechSecurity)
- 🌐 **Website**: [LeoGreyson.org](https://leogreyson.org/)

---

<div align="center">

**⭐ Star this repo if you find it useful!**

*Made with ❤️ for cybersecurity professionals*

</div>
