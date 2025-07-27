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

```bash
# Clone the repository
git clone https://github.com/leogreyson/floodx.git
cd floodx

# Install dependencies  
pip install -r requirements.txt

# Navigate to source
cd src/python
```

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
cd src\python

# Test installation
python main.py --help
```

</details>

<details>
<summary><img src="https://upload.wikimedia.org/wikipedia/commons/3/35/Tux.svg" width="20"> <strong>Linux</strong></summary>

```bash
# Update packages
sudo apt update && sudo apt install python3 python3-pip -y

# Clone and setup
git clone https://github.com/leogreyson/floodx.git
cd floodx
pip3 install -r requirements.txt
cd src/python

# Test installation (requires sudo for raw sockets)
sudo python3 main.py --help
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
cd src/python

# Test installation (requires sudo for raw sockets)
sudo python3 main.py --help
```

</details>

---

## 🎯 **Quick Start**

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

### ⚠️ **Administrator/Root Required**
- **Windows**: Run PowerShell as Administrator
- **Linux/macOS**: Use `sudo` for raw socket operations

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

**🔒 Remember: Use responsibly and legally**

*Made with ❤️ for cybersecurity professionals*

</div>
