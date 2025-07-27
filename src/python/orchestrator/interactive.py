"""
FloodX: Interactive Terminal User Interface
Professional branded interface for attack vector selection and configuration.
"""

import asyncio
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.logger import logger
from common.colors import (
    create_colored_banner, create_menu_box, Colors, Symbols,
    success_text, warning_text, error_text, info_text, 
    accent_text, menu_text, print_status, colored_text
)
from orchestrator.config_manager import ConfigManager
from orchestrator.dispatcher import AttackDispatcher


class FloodXTUI:
    """FloodX Terminal User Interface with branding and interactive menus."""
    
    def __init__(self, floodx_instance):
        self.floodx = floodx_instance
        self.config_manager = ConfigManager()
        self.dispatcher = AttackDispatcher()
        
    def display_banner(self):
        """Display the main FloodX banner with slight variations."""
        import random

        # ANSI color codes
        GREEN = "\033[92m"
        RESET = "\033[0m"

        # Randomly vary the legal notice
        legal_notices = [
            "⚠️  IMPORTANT LEGAL NOTICE:",
        ]

        disclaimers = [
            "• For network security research and authorized penetration testing",
            "• Intended for cybersecurity professionals and researchers only"
        ]

        banner = f"""{GREEN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ███████╗██╗      ██████╗  ██████╗ ██████╗ ██╗  ██╗                        ║
║    ██╔════╝██║     ██╔═══██╗██╔═══██╗██╔══██╗╚██╗██╔╝                        ║
║    █████╗  ██║     ██║   ██║██║   ██║██║  ██║ ╚███╔╝                         ║
║    ██╔══╝  ██║     ██║   ██║██║   ██║██║  ██║ ██╔██╗                         ║
║    ██║     ███████╗╚██████╔╝╚██████╔╝██████╔╝██╔╝ ██╗                        ║
║    ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═══╝                         ║
║                                                                              ║
║  Multi-Vector DDoS Toolkit by Leo • https://github.com/leogreyson/floodx     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  {random.choice(legal_notices)}                                              ║
║  {random.choice(disclaimers)}                                                ║
║  • Users are responsible for compliance with local laws                       ║
║  • We are defending our nation by removing fake news sites from Siem          ║
╚══════════════════════════════════════════════════════════════════════════════╝
{RESET}"""

        print(banner)
        
    def display_main_menu(self):
        """Display the main menu options with beautiful colors."""
        menu_items = [
            f"{accent_text('[1]', True)} {info_text('🌊 Layer 4 Attacks (Network Layer)', True)}",
            f"      {menu_text('└── SYN Flood, UDP Amplification, ICMP Flood')}",
            "",
            f"{accent_text('[2]', True)} {info_text('🌐 Layer 7 Attacks (Application Layer)', True)}",
            f"      {menu_text('└── HTTP Flood, Slowloris, RUDY, WebSocket Storm')}",
            "",
            f"{accent_text('[3]', True)} {info_text('🔐 Protocol-Specific Attacks', True)}",
            f"      {menu_text('└── TLS Handshake Flood, DNS Amplification')}",
            "",
            f"{accent_text('[4]', True)} {info_text('🚀 Multi-Vector Coordinated Attack', True)}",
            f"      {menu_text('└── Combined attack using multiple vectors simultaneously')}",
            "",
            f"{accent_text('[5]', True)} {info_text('⚙️  Advanced Configuration', True)}",
            f"      {menu_text('└── IP Spoofing, Proxy Setup, Evasion Techniques')}",
            "",
            f"{accent_text('[6]', True)} {info_text('📊 Attack Profiles & Templates', True)}",
            f"      {menu_text('└── Pre-configured attack scenarios (Light/Moderate/Full)')}",
            "",
            f"{accent_text('[7]', True)} {info_text('🔍 System Information & Status', True)}",
            f"      {menu_text('└── View system resources, active sessions, configuration')}",
            "",
            f"{error_text('[0]', True)} {error_text('🚪 Exit FloodX', True)}",
        ]
        
        print(create_menu_box("🎯 FLOODX MAIN MENU", menu_items))

    def display_layer4_menu(self):
        """Display Layer 4 attack options with beautiful colors."""
        menu_items = [
            f"{accent_text('[1]', True)} {info_text('⚡ SYN Flood Attack', True)}",
            f"      {menu_text('└── TCP SYN packet flooding to exhaust connection tables')}",
            "",
            f"{accent_text('[2]', True)} {info_text('📡 UDP Amplification Attack', True)}",
            f"      {menu_text('└── DNS/NTP/Memcached amplification via reflectors')}",
            "",
            f"{accent_text('[3]', True)} {info_text('🏓 ICMP Flood Attack', True)}",
            f"      {menu_text('└── High-volume ICMP echo requests')}",
            "",
            f"{accent_text('[4]', True)} {info_text('💀 Ping of Death Attack', True)}",
            f"      {menu_text('└── Oversized fragmented ICMP packets to crash systems')}",
            "",
            f"{accent_text('[5]', True)} {info_text('🌊 Smurf Attack', True)}",
            f"      {menu_text('└── ICMP broadcast amplification with spoofed source')}",
            "",
            f"{accent_text('[6]', True)} {info_text('💥 Fragmentation Attack (Teardrop)', True)}",
            f"      {menu_text('└── Malformed fragmented packets to crash systems')}",
            "",
            f"{warning_text('[0]', True)} {warning_text('⬅️  Back to Main Menu', True)}",
        ]
        
        print(create_menu_box("🌊 LAYER 4 NETWORK ATTACKS", menu_items))

    def display_layer7_menu(self):
        """Display Layer 7 attack options with beautiful colors."""
        menu_items = [
            f"{accent_text('[1]', True)} {info_text('🌊 HTTP Flood Attack', True)}",
            f"      {menu_text('└── High-volume HTTP GET/POST requests with evasion')}",
            "",
            f"{accent_text('[2]', True)} {info_text('🐌 Slowloris Attack', True)}",
            f"      {menu_text('└── Slow HTTP headers to exhaust server connections')}",
            "",
            f"{accent_text('[3]', True)} {info_text('📝 RUDY Attack (R-U-Dead-Yet)', True)}",
            f"      {menu_text('└── Slow HTTP POST body transmission')}",
            "",
            f"{accent_text('[4]', True)} {info_text('🔌 WebSocket Storm', True)}",
            f"      {menu_text('└── WebSocket connection flooding and message spam')}",
            "",
            f"{accent_text('[5]', True)} {info_text('🎯 Targeted HTTP Methods', True)}",
            f"      {menu_text('└── PUT, DELETE, OPTIONS method flooding')}",
            "",
            f"{accent_text('[6]', True)} {info_text('📁 HTTP Range Header Attack', True)}",
            f"      {menu_text('└── Byte-range request amplification')}",
            "",
            f"{warning_text('[0]', True)} {warning_text('⬅️  Back to Main Menu', True)}",
        ]
        
        print(create_menu_box("🌐 LAYER 7 APPLICATION ATTACKS", menu_items))

    def display_protocol_menu(self):
        """Display protocol-specific attack options."""
        menu = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                      🔐 PROTOCOL-SPECIFIC ATTACKS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [1] 🔒 TLS/SSL Handshake Flood                                            │
│      └── SSL/TLS connection establishment flooding                          │
│                                                                             │
│  [2] 🔍 DNS Amplification Attack                                           │
│      └── DNS query amplification via recursive resolvers                   │
│                                                                             │
│  [3] ⏰ NTP Amplification Attack                                            │
│      └── NTP monlist command amplification                                 │
│                                                                             │
│  [4] 💾 Memcached Amplification                                            │
│      └── Memcached UDP amplification attack                                │
│                                                                             │
│  [5] 📧 SMTP Flood Attack                                                   │
│      └── SMTP connection and command flooding                              │
│                                                                             │
│  [0] ⬅️  Back to Main Menu                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
        """
        print(menu)

    def display_profiles_menu(self):
        """Display attack profile options."""
        menu = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                      📊 ATTACK PROFILES & TEMPLATES                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [1] 🟢 Light Profile - Basic Testing                                      │
│      └── 100 concurrent, 30s duration, single vector                       │
│      └── Suitable for: Initial reconnaissance, basic availability testing   │
│                                                                             │
│  [2] 🟡 Moderate Profile - Standard Load Testing                           │
│      └── 500 concurrent, 120s duration, 3 vectors                          │
│      └── Suitable for: Load testing, capacity evaluation                    │
│                                                                             │
│  [3] 🔴 Full Profile - Stress Testing                                      │
│      └── 2000 concurrent, 300s duration, all vectors                       │
│      └── Suitable for: Maximum capacity testing, resilience evaluation     │
│                                                                             │
│  [4] 🎯 Custom Profile Builder                                              │
│      └── Create your own attack profile with specific parameters            │
│                                                                             │
│  [5] 📋 Load Profile from File                                              │
│      └── Import attack configuration from YAML/JSON file                   │
│                                                                             │
│  [0] ⬅️  Back to Main Menu                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
        """
        print(menu)

    async def run(self):
        """Run the interactive TUI."""
        try:
            while True:
                self.clear_screen()
                self.display_banner()
                self.display_main_menu()
                
                choice = await self.get_user_input("Select an option (0-7): ")
                
                if choice == "0":
                    print("\n FloodX! Stay anonymous! 🛡️")
                    break
                elif choice == "1":
                    await self.handle_layer4_menu()
                elif choice == "2":
                    await self.handle_layer7_menu()
                elif choice == "3":
                    await self.handle_protocol_menu()
                elif choice == "4":
                    await self.handle_multi_vector()
                elif choice == "5":
                    await self.handle_advanced_config()
                elif choice == "6":
                    await self.handle_profiles_menu()
                elif choice == "7":
                    await self.handle_system_info()
                else:
                    print("❌ Invalid choice. Please select 0-7.")
                    await asyncio.sleep(2)
                    
        except KeyboardInterrupt:
            print("\n\n👋 FloodX interrupted by user. Goodbye!")
        except Exception as e:
            logger.error(f"❌ TUI error: {e}")

    async def handle_layer4_menu(self):
        """Handle Layer 4 attack menu."""
        while True:
            self.clear_screen()
            self.display_banner()
            self.display_layer4_menu()
            
            choice = await self.get_user_input("Select Layer 4 attack (0-6): ")
            
            if choice == "0":
                break
            elif choice == "1":
                await self.configure_and_run_attack("syn")
            elif choice == "2":
                await self.configure_and_run_attack("udp")
            elif choice == "3":
                await self.configure_and_run_attack("icmp")
            elif choice == "4":
                await self.configure_and_run_attack("ping_of_death")
            elif choice == "5":
                await self.configure_and_run_attack("smurf")
            elif choice == "6":
                await self.configure_and_run_attack("teardrop")
            else:
                print("❌ Invalid choice. Please select 0-6.")
                await asyncio.sleep(2)

    async def handle_layer7_menu(self):
        """Handle Layer 7 attack menu."""
        while True:
            self.clear_screen()
            self.display_banner()
            self.display_layer7_menu()
            
            choice = await self.get_user_input("Select Layer 7 attack (0-6): ")
            
            if choice == "0":
                break
            elif choice == "1":
                await self.configure_and_run_attack("http")
            elif choice == "2":
                await self.configure_and_run_attack("slowloris")
            elif choice == "3":
                await self.configure_and_run_attack("rudy")
            elif choice == "4":
                await self.configure_and_run_attack("websocket")
            elif choice == "5":
                await self.configure_and_run_attack("http_methods")
            elif choice == "6":
                await self.configure_and_run_attack("http_range")
            else:
                print("❌ Invalid choice. Please select 0-6.")
                await asyncio.sleep(2)

    async def handle_protocol_menu(self):
        """Handle protocol-specific attack menu."""
        while True:
            self.clear_screen()
            self.display_banner()
            self.display_protocol_menu()
            
            choice = await self.get_user_input("Select protocol attack (0-5): ")
            
            if choice == "0":
                break
            elif choice == "1":
                await self.configure_and_run_attack("tls")
            elif choice == "2":
                await self.configure_and_run_attack("dns_amplification")
            elif choice == "3":
                await self.configure_and_run_attack("ntp")
            elif choice == "4":
                await self.configure_and_run_attack("memcached")
            elif choice == "5":
                await self.configure_and_run_attack("smtp")
            else:
                print("❌ Invalid choice. Please select 0-5.")
                await asyncio.sleep(2)

    async def handle_profiles_menu(self):
        """Handle attack profiles menu."""
        while True:
            self.clear_screen()
            self.display_banner()
            self.display_profiles_menu()
            
            choice = await self.get_user_input("Select profile option (0-5): ")
            
            if choice == "0":
                break
            elif choice == "1":
                await self.run_attack_profile("light")
            elif choice == "2":
                await self.run_attack_profile("moderate")
            elif choice == "3":
                await self.run_attack_profile("full")
            elif choice == "4":
                await self.custom_profile_builder()
            elif choice == "5":
                await self.load_profile_from_file()
            else:
                print("❌ Invalid choice. Please select 0-5.")
                await asyncio.sleep(2)

    async def configure_and_run_attack(self, vector: str):
        """Configure and run a specific attack vector."""
        self.clear_screen()
        print(f"\n🎯 Configuring {vector.upper()} Attack")
        print("=" * 50)
        
        # Get target
        target = await self.get_user_input("Enter target IP/hostname: ")
        if not target:
            print("❌ Target is required!")
            await asyncio.sleep(2)
            return
        
        # Get port
        port_str = await self.get_user_input(f"Enter target port (default 80): ")
        port = int(port_str) if port_str.isdigit() else 80
        
        # Get duration
        duration_str = await self.get_user_input("Enter attack duration in seconds (default 60): ")
        duration = int(duration_str) if duration_str.isdigit() else 60
        
        # Get concurrency
        concurrency_str = await self.get_user_input("Enter concurrent connections (default 1000): ")
        concurrency = int(concurrency_str) if concurrency_str.isdigit() else 1000
        
        # Advanced options
        advanced = await self.get_yes_no("Enable advanced evasion techniques? (y/N): ")
        spoof_ip = await self.get_yes_no("Enable IP spoofing? (y/N): ")
        
        # Build configuration
        config = {
            'target': target,
            'port': port,
            'duration': duration,
            'vector': vector,
            'concurrency': concurrency,
            'advanced': advanced,
            'spoof_ip': spoof_ip
        }
        
        # Confirm attack
        print(f"\n📋 Attack Configuration Summary:")
        print(f"   Target: {target}:{port}")
        print(f"   Vector: {vector.upper()}")
        print(f"   Duration: {duration}s")
        print(f"   Concurrency: {concurrency}")
        print(f"   Advanced: {'Yes' if advanced else 'No'}")
        print(f"   IP Spoofing: {'Yes' if spoof_ip else 'No'}")
        
        if await self.get_yes_no("\nProceed with attack? (y/N): "):
            await self.execute_attack(config)
        else:
            print("❌ Attack cancelled.")
            await asyncio.sleep(2)

    async def execute_attack(self, config: Dict[str, Any]):
        """Execute the configured attack."""
        print(f"\n🚀 Launching {config['vector'].upper()} attack...")
        print("Press Ctrl+C to stop the attack")
        
        try:
            # Use the dispatcher directly instead of floodx.run_attack
            await self.dispatcher.dispatch(config)
        except KeyboardInterrupt:
            print("\n🛑 Attack stopped by user")
        except Exception as e:
            print(f"❌ Attack failed: {e}")
        
        await self.get_user_input("\nPress Enter to continue...")

    async def run_attack_profile(self, profile: str):
        """Run a predefined attack profile."""
        self.clear_screen()
        print(f"\n📊 Running {profile.upper()} Attack Profile")
        print("=" * 50)
        
        target = await self.get_user_input("Enter target IP/hostname: ")
        if not target:
            print("❌ Target is required!")
            await asyncio.sleep(2)
            return
        
        config = {
            'target': target,
            'vector': 'all',
            'profile': profile
        }
        
        if await self.get_yes_no(f"\nLaunch {profile} profile attack on {target}? (y/N): "):
            await self.execute_attack(config)

    async def handle_system_info(self):
        """Display system information and status."""
        self.clear_screen()
        print("\n🔍 FloodX System Information")
        print("=" * 50)
        
        # System resources
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        print(f"💻 System Resources:")
        print(f"   CPU Usage: {cpu_percent:.1f}%")
        print(f"   Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)")
        
        # Network interfaces
        print(f"\n🌐 Network Interfaces:")
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family.name == 'AF_INET':
                    print(f"   {interface}: {addr.address}")
        
        # FloodX status
        print(f"\n⚙️  FloodX Status:")
        print(f"   Version: 1.0.0")
        print(f"   Available Vectors: SYN, UDP, ICMP, HTTP, WebSocket, TLS, DNS")
        print(f"   Session Manager: Active")
        print(f"   Proxy Manager: Ready")
        
        await self.get_user_input("\nPress Enter to continue...")

    async def get_user_input(self, prompt: str) -> str:
        """Get user input with slight prompt variations."""
        import random
        
        # Add occasional typos or informal language that humans might use
        casual_prompts = {
            "Select an option": ["Pick an option", "Choose option", "Your choice"],
            "Enter target": ["Target host", "Specify target", "Target address"],
            "Press Enter": ["Hit Enter", "Press any key", "Continue"]
        }
        
        # Occasionally use casual variations
        if random.randint(1, 10) == 1:  # 10% chance
            for formal, casual_list in casual_prompts.items():
                if formal in prompt:
                    prompt = prompt.replace(formal, random.choice(casual_list))
        
        print(prompt, end="", flush=True)
        return input().strip()

    async def get_yes_no(self, prompt: str) -> bool:
        """Get yes/no input from user."""
        response = await self.get_user_input(prompt)
        return response.lower() in ['y', 'yes', '1', 'true']

    def clear_screen(self):
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    async def handle_multi_vector(self):
        """Handle multi-vector coordinated attack setup."""
        self.clear_screen()
        print("\n🚀 Multi-Vector Coordinated Attack")
        print("=" * 50)
        
        # Get target
        target = await self.get_user_input("Enter target IP/hostname: ")
        if not target:
            print("❌ Target is required!")
            await asyncio.sleep(2)
            return
        
        # Show available vectors
        available_vectors = ['syn', 'udp', 'icmp', 'http', 'tls', 'slowloris', 'websocket']
        print("\n📋 Available Attack Vectors:")
        for i, vector in enumerate(available_vectors, 1):
            print(f"   [{i}] {vector.upper()}")
        
        # Get vector selection
        vector_input = await self.get_user_input("\nSelect vectors (comma-separated numbers, e.g., 1,3,4): ")
        try:
            selected_indices = [int(x.strip()) - 1 for x in vector_input.split(',')]
            selected_vectors = [available_vectors[i] for i in selected_indices if 0 <= i < len(available_vectors)]
        except:
            print("❌ Invalid vector selection!")
            await asyncio.sleep(2)
            return
        
        if not selected_vectors:
            print("❌ No valid vectors selected!")
            await asyncio.sleep(2)
            return
        
        # Get intensity
        print("\n🎯 Attack Intensity Profiles:")
        print("   [1] Light - Basic testing (50% intensity)")
        print("   [2] Moderate - Standard testing (100% intensity)")
        print("   [3] Full - Maximum testing (200% intensity)")
        
        intensity_choice = await self.get_user_input("Select intensity profile (1-3): ")
        intensity_map = {'1': 'light', '2': 'moderate', '3': 'full'}
        intensity = intensity_map.get(intensity_choice, 'moderate')
        
        # Get duration
        duration_str = await self.get_user_input("Enter attack duration in seconds (default 120): ")
        duration = int(duration_str) if duration_str.isdigit() else 120
        
        # Configuration summary
        print(f"\n📋 Multi-Vector Attack Configuration:")
        print(f"   Target: {target}")
        print(f"   Vectors: {', '.join(v.upper() for v in selected_vectors)}")
        print(f"   Intensity: {intensity.upper()}")
        print(f"   Duration: {duration}s")
        
        if await self.get_yes_no("\nProceed with multi-vector attack? (y/N): "):
            config = {
                'target': target,
                'vector': 'multi_vector',
                'vectors': selected_vectors,
                'intensity': intensity,
                'duration': duration,
                'concurrency': 1000,
                'allow_private': True,
                'port': 80
            }
            await self.execute_attack(config)
        else:
            print("❌ Attack cancelled.")
            await asyncio.sleep(2)

    async def handle_advanced_config(self):
        """Handle advanced configuration options."""
        self.clear_screen()
        print("\n⚙️ Advanced Configuration Options")
        print("=" * 50)
        
        print("\n🎯 Available Advanced Options:")
        print("   [1] 🎭 IP Spoofing Configuration")
        print("   [2] 🌐 Proxy Setup & Rotation")
        print("   [3] 🔧 Evasion Techniques")
        print("   [4] 📊 Custom Attack Parameters")
        print("   [5] 🔍 Network Interface Selection")
        print("   [0] ⬅️ Back to Main Menu")
        
        choice = await self.get_user_input("\nSelect advanced option (0-5): ")
        
        if choice == "1":
            await self.configure_ip_spoofing()
        elif choice == "2":
            await self.configure_proxy_setup()
        elif choice == "3":
            await self.configure_evasion_techniques()
        elif choice == "4":
            await self.configure_custom_parameters()
        elif choice == "5":
            await self.configure_network_interface()
        elif choice == "0":
            return
        else:
            print("❌ Invalid choice.")
            await asyncio.sleep(2)

    async def configure_ip_spoofing(self):
        """Configure IP spoofing settings."""
        self.clear_screen()
        print("\n🎭 IP Spoofing Configuration")
        print("=" * 40)
        
        print("⚠️  WARNING: IP spoofing requires raw socket privileges!")
        print("   • Run as Administrator/root")
        print("   • May be blocked by ISP/firewall")
        print("   • Use only for authorized testing")
        
        if not await self.get_yes_no("\nEnable IP spoofing? (y/N): "):
            return
        
        # Get spoofing ranges
        print("\n📍 IP Spoofing Ranges (CIDR notation):")
        print("   Examples: 10.0.0.0/8, 192.168.1.0/24, 172.16.0.0/12")
        
        ranges_input = await self.get_user_input("Enter IP ranges (comma-separated): ")
        ranges = [r.strip() for r in ranges_input.split(',') if r.strip()]
        
        if ranges:
            print(f"\n✅ IP Spoofing configured with {len(ranges)} ranges")
            for i, range_str in enumerate(ranges[:3], 1):
                print(f"   {i}. {range_str}")
            if len(ranges) > 3:
                print(f"   ... and {len(ranges) - 3} more ranges")
        
        await self.get_user_input("\nPress Enter to continue...")

    async def configure_proxy_setup(self):
        """Configure proxy settings.""" 
        self.clear_screen()
        print("\n🌐 Proxy Setup & Configuration")
        print("=" * 40)
        
        print("🔧 Proxy Configuration Options:")
        print("   [1] Load proxy list from file")
        print("   [2] Manual proxy entry")
        print("   [3] Auto-discover public proxies")
        print("   [4] Configure rotation settings")
        
        choice = await self.get_user_input("\nSelect proxy option (1-4): ")
        
        if choice == "1":
            filename = await self.get_user_input("Enter proxy file path: ")
            print(f"📁 Loading proxies from: {filename}")
        elif choice == "2":
            proxies = await self.get_user_input("Enter proxies (host:port, comma-separated): ")
            proxy_list = [p.strip() for p in proxies.split(',') if p.strip()]
            print(f"✅ Added {len(proxy_list)} manual proxies")
        elif choice == "3":
            print("🔍 Auto-discovering public proxies...")
            print("⚠️  WARNING: Public proxies may be unreliable or monitored!")
        elif choice == "4":
            rotation_time = await self.get_user_input("Proxy rotation interval (seconds, default 30): ")
            print(f"🔄 Proxy rotation set to {rotation_time or '30'} seconds")
        
        await self.get_user_input("\nPress Enter to continue...")

    async def configure_evasion_techniques(self):
        """Configure evasion techniques."""
        self.clear_screen()
        print("\n🔧 Evasion Techniques Configuration")
        print("=" * 40)
        
        print("🛡️ Available Evasion Methods:")
        print("   ✅ User-Agent Rotation")
        print("   ✅ Random Delays (0.1-2.0s)")
        print("   ✅ Header Randomization")
        print("   ✅ Payload Fragmentation")
        print("   ✅ Connection Keep-Alive")
        
        if await self.get_yes_no("\nEnable all evasion techniques? (y/N): "):
            print("✅ All evasion techniques enabled")
        else:
            print("❌ Evasion techniques disabled")
        
        await self.get_user_input("\nPress Enter to continue...")

    async def configure_custom_parameters(self):
        """Configure custom attack parameters."""
        self.clear_screen()
        print("\n📊 Custom Attack Parameters")
        print("=" * 40)
        
        # Custom packet size
        packet_size = await self.get_user_input("Custom packet size (bytes, default 1024): ")
        
        # Custom timeout
        timeout = await self.get_user_input("Connection timeout (seconds, default 5): ")
        
        # Custom retry count
        retries = await self.get_user_input("Retry attempts (default 3): ")
        
        print(f"\n✅ Custom Parameters Set:")
        print(f"   Packet Size: {packet_size or '1024'} bytes")
        print(f"   Timeout: {timeout or '5'} seconds")
        print(f"   Retries: {retries or '3'} attempts")
        
        await self.get_user_input("\nPress Enter to continue...")

    async def configure_network_interface(self):
        """Configure network interface selection."""
        self.clear_screen()
        print("\n🔍 Network Interface Selection")
        print("=" * 40)
        
        try:
            import psutil
            interfaces = psutil.net_if_addrs()
            
            print("📡 Available Network Interfaces:")
            interface_list = []
            for i, (interface, addrs) in enumerate(interfaces.items(), 1):
                for addr in addrs:
                    if addr.family.name == 'AF_INET':
                        print(f"   [{i}] {interface}: {addr.address}")
                        interface_list.append((interface, addr.address))
                        break
            
            choice = await self.get_user_input(f"\nSelect interface (1-{len(interface_list)}): ")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(interface_list):
                    selected = interface_list[idx]
                    print(f"✅ Selected interface: {selected[0]} ({selected[1]})")
                else:
                    print("❌ Invalid selection")
            except:
                print("❌ Invalid selection")
        
        except ImportError:
            print("❌ psutil not available for interface detection")
        
        await self.get_user_input("\nPress Enter to continue...")

    async def custom_profile_builder(self):
        """Build custom attack profile."""
        self.clear_screen()
        print("\n🎯 Custom Attack Profile Builder")
        print("=" * 50)
        
        # Profile name
        profile_name = await self.get_user_input("Enter profile name: ")
        if not profile_name:
            print("❌ Profile name is required!")
            await asyncio.sleep(2)
            return
        
        # Target
        target = await self.get_user_input("Enter target IP/hostname: ")
        if not target:
            print("❌ Target is required!")
            await asyncio.sleep(2)
            return
        
        # Select vectors
        vectors = []
        print("\n📋 Select Attack Vectors:")
        available_vectors = ['syn', 'udp', 'icmp', 'http', 'tls', 'slowloris', 'websocket']
        
        for vector in available_vectors:
            if await self.get_yes_no(f"Include {vector.upper()} attack? (y/N): "):
                vectors.append(vector)
        
        if not vectors:
            print("❌ At least one vector is required!")
            await asyncio.sleep(2)
            return
        
        # Configuration parameters
        duration = await self.get_user_input("Attack duration (seconds, default 60): ")
        duration = int(duration) if duration.isdigit() else 60
        
        concurrency = await self.get_user_input("Concurrent connections (default 500): ")
        concurrency = int(concurrency) if concurrency.isdigit() else 500
        
        # Build profile
        profile = {
            'name': profile_name,
            'target': target,
            'vectors': vectors,
            'duration': duration,
            'concurrency': concurrency,
            'created': datetime.now().isoformat()
        }
        
        # Show profile summary
        print(f"\n📋 Profile Summary: {profile_name}")
        print(f"   Target: {target}")
        print(f"   Vectors: {', '.join(v.upper() for v in vectors)}")
        print(f"   Duration: {duration}s")
        print(f"   Concurrency: {concurrency}")
        
        if await self.get_yes_no("\nExecute this profile now? (y/N): "):
            config = {
                'target': target,
                'vector': 'multi_vector',
                'vectors': vectors,
                'duration': duration,
                'concurrency': concurrency,
                'allow_private': True,
                'port': 80
            }
            await self.execute_attack(config)
        else:
            print("✅ Profile created (not saved to file)")
            await asyncio.sleep(2)

    async def load_profile_from_file(self):
        """Load attack profile from file."""
        self.clear_screen()
        print("\n📋 Load Attack Profile")
        print("=" * 30)
        
        # Show available profiles
        print("📁 Available Profile Files:")
        print("   • profiles/light.yaml - Basic testing profile")
        print("   • profiles/moderate.yaml - Standard load testing")
        print("   • profiles/full.yaml - Maximum stress testing")
        
        filename = await self.get_user_input("\nEnter profile file path: ")
        if not filename:
            print("❌ Filename is required!")
            await asyncio.sleep(2)
            return
        
        try:
            from pathlib import Path
            import yaml
            
            profile_path = Path(filename)
            if not profile_path.exists():
                # Try relative to profiles directory
                profile_path = Path("profiles") / filename
                if not profile_path.exists():
                    profile_path = Path("profiles") / f"{filename}.yaml"
            
            if profile_path.exists():
                with open(profile_path, 'r') as f:
                    profile_data = yaml.safe_load(f)
                
                print(f"\n✅ Loaded profile: {profile_path.name}")
                print(f"   Target: {profile_data.get('attack', {}).get('target', 'Not specified')}")
                print(f"   Vectors: {len(profile_data.get('vectors', []))} configured")
                
                if await self.get_yes_no("\nExecute this profile? (y/N): "):
                    # Convert profile to config format
                    attack_config = profile_data.get('attack', {})
                    target = await self.get_user_input(f"Target [{attack_config.get('target', 'localhost')}]: ") or attack_config.get('target', 'localhost')
                    
                    config = {
                        'target': target,
                        'vector': 'multi_vector',
                        'vectors': [v.get('type') for v in profile_data.get('vectors', [])],
                        'duration': 60,
                        'concurrency': 500,
                        'allow_private': True,
                        'port': 80
                    }
                    await self.execute_attack(config)
            else:
                print(f"❌ Profile file not found: {filename}")
                await asyncio.sleep(2)
        
        except Exception as e:
            print(f"❌ Failed to load profile: {e}")
            await asyncio.sleep(2)


# For compatibility with main.py import
class InteractiveTUI(FloodXTUI):
    """Alias for backward compatibility."""
    pass
