#!/usr/bin/env python3
"""
FloodX Interactive Menu Test
Test the interactive functionality and menu system.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Any

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from common.colors import (
    create_colored_banner, create_menu_box, Colors, Symbols,
    success_text, warning_text, error_text, info_text, 
    accent_text, menu_text, print_status
)
from orchestrator.dispatcher import AttackDispatcher


class SimpleFloodXMenu:
    """Simple interactive menu for FloodX testing."""
    
    def __init__(self):
        self.dispatcher = AttackDispatcher()
        self.running = True
    
    def display_main_menu(self):
        """Display the main menu."""
        print("\n" + "="*80)
        print(create_colored_banner())
        print("="*80)
        
        # Create attack vector menu
        vectors = list(self.dispatcher.vector_handlers.keys())
        menu_items = []
        
        for i, vector in enumerate(vectors, 1):
            menu_items.append(f"{accent_text(f'{i:2d}.')} {info_text(vector.upper().ljust(15))} - {self._get_vector_description(vector)}")
        
        menu_items.append("")
        menu_items.append(f"{accent_text('99.')} {warning_text('EXIT'.ljust(15))} - {info_text('Exit FloodX')}")
        
        menu_box = create_menu_box("🚀 FloodX Attack Vectors", menu_items, width=80)
        print(menu_box)
        
        return vectors
    
    def _get_vector_description(self, vector: str) -> str:
        """Get description for attack vector."""
        descriptions = {
            'syn': 'TCP SYN flood attack',
            'udp': 'UDP amplification attack', 
            'icmp': 'ICMP flood attack',
            'http': 'HTTP flood attack',
            'websocket': 'WebSocket storm attack',
            'tls': 'TLS handshake flood attack',
            'dns': 'DNS flood attack',
            'slowloris': 'Slowloris attack',
            'rudy': 'RUDY attack',
            'ping_of_death': 'Ping of Death attack',
            'smurf': 'Smurf attack',
            'teardrop': 'Teardrop fragmentation attack',
            'dns_amplification': 'DNS amplification attack',
            'smtp': 'SMTP flood attack'
        }
        return descriptions.get(vector, 'Advanced attack vector')
    
    def get_user_input(self, prompt: str, input_type: type = str, default: Any = None):
        """Get user input with type validation."""
        while True:
            try:
                if default is not None:
                    user_input = input(f"{info_text(prompt)} [{accent_text(str(default))}]: ").strip()
                    if not user_input:
                        return default
                else:
                    user_input = input(f"{info_text(prompt)}: ").strip()
                
                if input_type == int:
                    return int(user_input)
                elif input_type == float:
                    return float(user_input)
                else:
                    return user_input
                    
            except ValueError:
                print(f"{error_text('❌ Invalid input. Please enter a valid')} {input_type.__name__}")
            except KeyboardInterrupt:
                print(f"\n{warning_text('🛑 Operation cancelled')}")
                return None
    
    async def configure_attack(self, vector: str) -> dict:
        """Configure attack parameters."""
        print(f"\n🔧 {accent_text('Configuring')} {success_text(vector.upper())} {accent_text('attack')}")
        
        config = {
            'vector': vector,
            'advanced': True
        }
        
        # Get basic parameters
        config['target'] = self.get_user_input("Target IP/hostname", str, "localhost")
        if not config['target']:
            return None
            
        config['port'] = self.get_user_input("Target port", int, 80)
        config['duration'] = self.get_user_input("Duration (seconds)", int, 10)
        config['concurrency'] = self.get_user_input("Concurrency/threads", int, 10)
        config['allow_private'] = True  # Allow for testing
        
        # Vector-specific configuration
        if vector in ['syn', 'tls', 'smtp']:
            config['spoof_ip'] = self.get_user_input("Enable IP spoofing? (y/n)", str, "n").lower() == 'y'
        
        return config
    
    async def execute_attack(self, config: dict):
        """Execute the configured attack."""
        vector = config['vector']
        
        print(f"\n🚀 {success_text('Launching')} {accent_text(vector.upper())} {success_text('attack')}")
        print(f"🎯 Target: {accent_text(config['target'])}:{accent_text(str(config['port']))}")
        print(f"⏱️  Duration: {accent_text(str(config['duration']))} seconds")
        print(f"🔥 Concurrency: {accent_text(str(config['concurrency']))}")
        
        # Confirm before executing
        confirm = self.get_user_input(f"Execute {vector.upper()} attack? (y/n)", str, "n")
        if confirm.lower() != 'y':
            print(f"{warning_text('❌ Attack cancelled')}")
            return
        
        try:
            # Execute attack via dispatcher
            await self.dispatcher.dispatch(config)
            print(f"{success_text('✅ Attack completed successfully')}")
        except Exception as e:
            print(f"{error_text(f'❌ Attack failed: {e}')}")
    
    async def run(self):
        """Run the interactive menu."""
        try:
            while self.running:
                vectors = self.display_main_menu()
                
                choice = self.get_user_input("Select attack vector", int)
                if choice is None:  # Ctrl+C
                    break
                
                if choice == 99:
                    print(f"{success_text('👋 Goodbye!')}")
                    break
                elif 1 <= choice <= len(vectors):
                    selected_vector = vectors[choice - 1]
                    
                    config = await self.configure_attack(selected_vector)
                    if config:
                        await self.execute_attack(config)
                    
                    input(f"\n{info_text('Press Enter to continue...')}")
                else:
                    print(f"{error_text('❌ Invalid choice. Please select 1-')} {len(vectors)} {error_text('or 99')}")
                    
        except KeyboardInterrupt:
            print(f"\n{success_text('🛑 FloodX terminated. Stay safe!')}")


async def main():
    """Main entry point."""
    menu = SimpleFloodXMenu()
    await menu.run()


if __name__ == "__main__":
    asyncio.run(main())
