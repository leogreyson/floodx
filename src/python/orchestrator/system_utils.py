# System Utilities

import os
import sys
import platform
import socket
import subprocess
import psutil
import requests

# Add parent directory to Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.logger import logger

def check_root():
    """Check if the current user has root/admin privileges"""
    try:
        return os.geteuid() == 0
    except AttributeError:
        # Windows
        try:
            return subprocess.check_call(["net", "session"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0
        except subprocess.CalledProcessError:
            return False

def check_ip_spoofing_capability():
    """Check if IP spoofing is supported on the current platform"""
    if not check_root():
        return False

    # Check for raw socket capability
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        s.close()
        return True
    except PermissionError:
        return False
    except Exception as e:
        logger.error(f"Error checking IP spoofing capability: {e}")
        return False

def get_platform():
    """Get the current platform in a format suitable for binary selection"""
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        logger.warning(f"Unsupported platform: {system}")
        return "unknown"

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP
    except Exception as e:
        logger.error(f"Error getting local IP: {e}")
        return None

def get_public_ip():
    """Get the public IP address of the machine"""
    try:
        response = requests.get("https://api.ipify.org")
        if response.status_code == 200:
            return response.text
    except Exception as e:
        logger.error(f"Error getting public IP: {e}")
    return None

def is_port_open(ip, port):
    """Check if a specific port is open on a given IP"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((ip, port)) == 0

def get_open_ports(ip):
    """Scan for open ports on a target IP"""
    open_ports = []
    for port in range(1, 1025):
        if is_port_open(ip, port):
            open_ports.append(port)
    return open_ports

def execute_command(command):
    """Execute a system command and return the output"""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command execution failed: {e}")
        return None

def get_system_info():
    """Get detailed system information"""
    info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "memory": psutil.virtual_memory().total,
        "network_interfaces": psutil.net_if_addrs()
    }
    return info

def check_internet_connection():
    """Check if there is an active internet connection"""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False
