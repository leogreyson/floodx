# 🌊 FloodX - Multi-Vector DDoS Toolkit

<div align="center">

```
    ███████╗██╗      ██████╗  ██████╗ ██████╗ ██╗  ██╗
    ██╔════╝██║     ██╔═══██╗██╔═══██╗██╔══██╗╚██╗██╔╝
    █████╗  ██║     ██║   ██║██║   ██║██║  ██║ ╚███╔╝ 
    ██╔══╝  ██║     ██║   ██║██║   ██║██║  ██║ ██╔██╗ 
    ██║     ███████╗╚██████╔╝╚██████╔╝██████╔╝██╔╝ ██╗
    ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
```

**Professional Multi-Vector DDoS Testing Framework**  
*Network Security Research & Authorized Penetration Testing Tool*

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#installation)
[![Status](https://img.shields.io/badge/Status-Active%20Development-green.svg)](#)

</div>

---

## ⚠️ **IMPORTANT LEGAL DISCLAIMER**

> **🛡️ EDUCATIONAL & AUTHORIZED TESTING ONLY**
> 
> This tool is designed exclusively for:
> - **Educational purposes** and cybersecurity research
> - **Authorized penetration testing** with explicit permission
> - **Network security assessment** of your own infrastructure
> - **Academic research** in controlled environments
>
> **Users are fully responsible for compliance with all applicable laws and regulations.**  
> Unauthorized use against systems you don't own is **illegal** and **unethical**.

---

## 🎯 **Overview**

FloodX is a comprehensive, multi-vector DDoS testing framework designed for cybersecurity professionals, researchers, and authorized penetration testers. It provides both interactive and command-line interfaces for testing network resilience and capacity limits.

### ✨ **Key Features**

- 🌊 **Multi-Vector Attacks**: SYN, UDP, ICMP, HTTP, WebSocket, TLS, DNS
- 🎮 **Interactive TUI**: Beautiful terminal interface for easy operation
- 🚀 **High Performance**: Async/await architecture for maximum throughput
- 🎯 **Precise Targeting**: URL parsing, automatic port detection
- 📊 **Real-time Statistics**: Live monitoring with detailed metrics
- 🔒 **Safety Features**: Built-in protections against misuse
- 🌐 **Cross-Platform**: Windows, Linux, macOS support
- 🔧 **Extensible**: Modular architecture for custom attacks

---

## 🚀 **Quick Start**

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/floodx-ddos-toolkit.git
cd floodx-ddos-toolkit

# Install dependencies
pip install -r requirements.txt

# Navigate to source directory  
cd src/python
```

### 2. Basic Usage

```bash
# Interactive mode (recommended for beginners)
python main.py --interactive

# Direct command examples
python main.py syn --target localhost --allow-private --duration 10
python main.py http --target http://localhost:8080 --allow-private --threads 100
```

---

## 📦 **Installation Guide**

### Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **Administrator/Root privileges** (for raw socket operations)
- **Network access** to target systems

### Step-by-Step Installation

<details>
<summary>🐧 <strong>Linux Installation</strong></summary>

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Clone repository
git clone https://github.com/your-username/floodx-ddos-toolkit.git
cd floodx-ddos-toolkit

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test installation
cd src/python
python main.py --help
```

</details>

<details>
<summary>🪟 <strong>Windows Installation</strong></summary>

```powershell
# Install Python from python.org or Microsoft Store
# Ensure Python is in PATH

# Clone repository
git clone https://github.com/your-username/floodx-ddos-toolkit.git
cd floodx-ddos-toolkit

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test installation (Run as Administrator)
cd src\python
python main.py --help
```

</details>

<details>
<summary>🍎 <strong>macOS Installation</strong></summary>

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3

# Clone repository
git clone https://github.com/your-username/floodx-ddos-toolkit.git
cd floodx-ddos-toolkit

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test installation
cd src/python
python main.py --help
```

</details>

### Required Dependencies

Create `requirements.txt` in the root directory:

```txt
scapy>=2.4.5
asyncio-throttle>=1.0.2
aiohttp>=3.8.0
websockets>=10.0
psutil>=5.8.0
colorama>=0.4.4
pyyaml>=6.0
requests>=2.28.0
```

---

## 🎮 **Usage Guide**

### Interactive Mode (Recommended)

The interactive TUI provides the easiest way to use FloodX:

```bash
python main.py --interactive
```

**Features:**
- 📋 Guided attack configuration
- 🎯 Target validation with safety checks
- 📊 Real-time statistics display
- 🛡️ Built-in safety prompts
- 💡 Helpful tips and warnings

### Command Line Mode

For automated testing and scripting:

#### Basic Syntax
```bash
python main.py [ATTACK_TYPE] --target [TARGET] [OPTIONS]
```

#### Available Attack Types

<details>
<summary>🌊 <strong>Layer 4 Attacks</strong></summary>

**SYN Flood**
```bash
python main.py syn --target 192.168.1.100 --port 80 --threads 1000 --duration 60
```

**UDP Amplification**
```bash
python main.py udp --target 192.168.1.100 --port 53 --threads 500 --amplifier-type dns
```

**ICMP Flood**
```bash
python main.py icmp --target 192.168.1.100 --threads 100 --packet-size 1024
```

</details>

<details>
<summary>🌐 <strong>Layer 7 Attacks</strong></summary>

**HTTP Flood**
```bash
python main.py http --target http://example.com --threads 200 --method GET --user-agents
```

**Slowloris**
```bash
python main.py slowloris --target example.com --port 80 --connections 200 --duration 300
```

**WebSocket Storm**
```bash
python main.py websocket --target ws://example.com/ws --connections 100 --message-rate 10
```

</details>

<details>
<summary>🔐 <strong>Protocol-Specific Attacks</strong></summary>

**TLS Handshake Flood**
```bash
python main.py tls --target example.com --port 443 --threads 100 --duration 60
```

**Multi-Vector Attack**
```bash
python main.py multi --target example.com --vectors syn http tls --intensity moderate
```

</details>

#### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--target` | Target IP/hostname/URL | `--target localhost` |
| `--port` | Target port (auto-detected from URLs) | `--port 8080` |
| `--threads` | Concurrent threads/connections | `--threads 1000` |
| `--duration` | Attack duration in seconds | `--duration 60` |
| `--allow-private` | Allow localhost/private network testing | `--allow-private` |
| `--verbose` | Enable detailed logging | `--verbose` |

---

## 📊 **Attack Profiles**

FloodX includes pre-configured attack profiles for different testing scenarios:

### 🟢 Light Profile
- **Purpose**: Basic availability testing
- **Intensity**: 100 concurrent connections
- **Duration**: 30 seconds
- **Use Case**: Initial reconnaissance

### 🟡 Moderate Profile  
- **Purpose**: Standard load testing
- **Intensity**: 500 concurrent connections
- **Duration**: 120 seconds
- **Use Case**: Capacity evaluation

### 🔴 Full Profile
- **Purpose**: Stress testing
- **Intensity**: 2000+ concurrent connections
- **Duration**: 300 seconds
- **Use Case**: Maximum resilience testing

```bash
# Use predefined profiles
python main.py profile --config profiles/moderate.yaml
```

---

## 🛡️ **Safety Features**

FloodX includes multiple safety mechanisms:

### 🔒 **Target Validation**
- Automatic detection of private/localhost addresses
- DNS resolution safety checks
- Confirmation prompts for dangerous operations

### 📋 **Logging & Monitoring**
- Comprehensive attack logging
- Real-time statistics tracking
- Error reporting and debugging

### ⚙️ **Rate Limiting**
- Built-in traffic throttling
- Resource consumption monitoring
- Graceful shutdown mechanisms

---

## 🔧 **Advanced Configuration**

### Profile-Based Attacks

Create custom YAML configuration files:

```yaml
# custom_attack.yaml
attack:
  target: "https://example.com"
  vectors:
    - type: "syn"
      threads: 1000
      duration: 60
    - type: "http"
      threads: 200
      method: "GET"
      user_agents: true
  
options:
  allow_private: false
  verbose: true
  proxy_rotation: true
```

```bash
python main.py profile custom_attack.yaml
```

### IP Spoofing Configuration

```python
# Enable IP spoofing (requires root/admin)
python main.py syn --target example.com --spoof-ip --spoof-ranges "10.0.0.0/8,172.16.0.0/12"
```

---

## 📈 **Performance Optimization**

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 2GB | 8GB+ |
| **Network** | 10 Mbps | 100+ Mbps |
| **OS** | Any modern OS | Linux/Windows Server |

### Optimization Tips

1. **Increase system limits**:
   ```bash
   # Linux - increase file descriptors
   ulimit -n 65536
   
   # Windows - run as Administrator
   ```

2. **Network optimization**:
   ```bash
   # Linux - optimize network stack
   echo 'net.core.somaxconn = 65536' >> /etc/sysctl.conf
   sysctl -p
   ```

3. **Python optimization**:
   ```bash
   # Use PyPy for better performance
   pypy3 main.py syn --target example.com
   ```

---

## 🐛 **Troubleshooting**

<details>
<summary>❌ <strong>Common Issues</strong></summary>

**Permission Denied Errors**
```bash
# Solution: Run with elevated privileges
sudo python main.py  # Linux/macOS
# Run PowerShell as Administrator on Windows
```

**Scapy Import Errors**
```bash
# Solution: Install scapy dependencies
pip install scapy[complete]
```

**Network Unreachable**
```bash
# Solution: Check target accessibility
ping target_host
telnet target_host target_port
```

**Low Attack Performance**
```bash
# Solution: Increase system resources
python main.py syn --target example.com --threads 100  # Start small
```

</details>

---

## 🤝 **Contributing**

We welcome contributions from the cybersecurity community!

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-attack-vector`
3. **Commit changes**: `git commit -am 'Add new attack vector'`
4. **Push to branch**: `git push origin feature/new-attack-vector`
5. **Submit Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/leogreyson/floodx
cd floodx

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black src/
flake8 src/
```

### Contribution Guidelines

- 📝 Write clear, documented code
- 🧪 Include tests for new features
- 🛡️ Maintain security best practices
- 📋 Update documentation
- ⚖️ Ensure legal compliance

---

## 📚 **Documentation**

### Project Structure

```
floodx-ddos-toolkit/
├── 📁 src/
│   ├── 📁 python/           # Main Python implementation
│   │   ├── 📁 app_layer_attacks/   # Layer 7 attacks
│   │   ├── 📁 common/              # Shared utilities
│   │   ├── 📁 dns_utils/           # DNS utilities
│   │   ├── 📁 orchestrator/        # Core orchestration
│   │   └── main.py                 # Entry point
│   ├── 📁 c_cpp/            # High-performance C/C++ modules
│   ├── 📁 go/               # Go implementations
│   └── 📁 main/             # Main orchestrator
├── 📁 build/                # Build scripts
├── 📁 run/                  # Runtime scripts
├── 📁 profiles/             # Attack profiles
├── 📁 docs/                 # Detailed documentation
├── 📁 tests/                # Test suite
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### API Documentation

For detailed API documentation, see [docs/API.md](docs/API.md).

---

## 🔒 **Security Considerations**

### Ethical Guidelines

- ✅ **DO**: Test your own systems
- ✅ **DO**: Get explicit written permission
- ✅ **DO**: Use in controlled environments
- ✅ **DO**: Report findings responsibly

- ❌ **DON'T**: Attack systems without permission
- ❌ **DON'T**: Use for malicious purposes
- ❌ **DON'T**: Exceed authorized scope
- ❌ **DON'T**: Share attack logs publicly

### Reporting Security Issues

If you discover security vulnerabilities in FloodX:

1. **Do NOT** create public issues
2. Email security concerns to: [info@leogreyson.org/](leo:info@leogreyson.org)
3. Include detailed reproduction steps
4. Allow reasonable time for fixes

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 FloodX Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🌟 **Acknowledgments**

- **Scapy Team** - For the excellent packet manipulation library
- **Python AsyncIO** - For high-performance async networking
- **Cybersecurity Community** - For responsible disclosure practices
- **Contributors** - For making this project better

---

## 📞 **Support**

### Getting Help

- 📖 **Documentation**: [docs/](docs/)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/leogreyson/floodx/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/leogreyson/floodx/discussions)
- 📧 **Email**: [info@leogreyson.org](mailto:info@leogreyson.org)

### Community

- 🐦 **Twitter**: [@LeoTechSecurity](https://x.com/LeoTechSecurity)
- 💼 **LinkedIn**: [Leo Technology](https://www.linkedin.com/in/leo-technology/)
- 🌐 **Website**: [LeoTech Community](https://leogreyson.org/)

---

<div align="center">

**⭐ Star this repository if you find it useful!**

**🔒 Remember: With great power comes great responsibility**

*Made with ❤️ by cybersecurity professionals, for cybersecurity professionals*

</div>
