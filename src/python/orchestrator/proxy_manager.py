import asyncio
import aiohttp
import json
import os
import sys
import random
import time
from pathlib import Path

# Add parent directory to Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.logger import logger

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON from {path}: {e}")
        return []

def save_json(path, data):
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save JSON to {path}: {e}")

class Proxy:
    """Represents a single proxy with health checks and metrics."""
    def __init__(self, ip, port, scheme="http", username=None, password=None):
        self.ip = ip
        self.port = port
        self.scheme = scheme
        self.username = username
        self.password = password
        self.last_used = None
        self.status = "unknown"
        self.latency = None
        self.fail_count = 0

    @property
    def url(self):
        creds = f"{self.username}:{self.password}@" if self.username and self.password else ""
        return f"{self.scheme}://{creds}{self.ip}:{self.port}"

    async def test(self, session, test_url="http://www.google.com", timeout=5):
        """Perform an async GET request to test proxy health."""
        start = time.time()
        try:
            async with session.get(test_url, proxy=self.url, timeout=timeout) as resp:
                if resp.status == 200:
                    self.status = "alive"
                    self.latency = time.time() - start
                    self.fail_count = 0
                    return True
        except Exception as e:
            self.status = "dead"
            self.fail_count += 1
            logger.debug(f"Proxy {self.ip}:{self.port} failed: {e}")
        return False

class ProxyManager:
    """Manages a pool of proxies with async health checks, auto-fetch, and rotation."""
    def __init__(self, proxy_file=None):
        self.proxies = []
        self.proxy_file = proxy_file
        if proxy_file and Path(proxy_file).exists():
            self.load_proxies(proxy_file)

    def load_proxies(self, path):
        """Load proxies from JSON file [{ip, port, scheme, username, password}, ...]."""
        raw = load_json(path)
        for p in raw:
            self.proxies.append(Proxy(
                ip=p.get("ip"), port=p.get("port"), scheme=p.get("scheme", "http"),
                username=p.get("username"), password=p.get("password")
            ))
        logger.info(f"Loaded {len(self.proxies)} proxies from {path}")

    def save_proxies(self, path=None):
        """Save current proxy list (with credentials) to JSON file."""
        path = path or self.proxy_file
        if not path:
            return
        data = [vars(p) for p in self.proxies]
        save_json(path, data)
        logger.info(f"Saved {len(self.proxies)} proxies to {path}")

    async def test_all(self, concurrency=50):
        """Async test all proxies concurrently and update their status."""
        tasks = []
        connector = aiohttp.TCPConnector(limit=concurrency)
        async with aiohttp.ClientSession(connector=connector) as session:
            for p in self.proxies:
                tasks.append(p.test(session))
            results = await asyncio.gather(*tasks)
        alive = sum(1 for res in results if res)
        logger.info(f"Tested {len(self.proxies)} proxies: {alive} alive, {len(self.proxies)-alive} dead.")

    def get_active(self, max_fail=3):
        """Return proxies that are alive and under the failure threshold, sorted by latency."""
        active = [p for p in self.proxies if p.status == "alive" and (p.fail_count < max_fail)]
        return sorted(active, key=lambda x: x.latency or float('inf'))

    def rotate(self):
        """Rotate to the fastest active proxy."""
        active = self.get_active()
        if not active:
            return None
        chosen = random.choice(active[:5])  # pick from top 5
        chosen.last_used = time.time()
        return chosen

    def add_proxy(self, ip, port, scheme="http", username=None, password=None):
        """Add a new proxy to the pool."""
        self.proxies.append(Proxy(ip, port, scheme, username, password))
        logger.info(f"Added proxy {ip}:{port}")

    def remove_dead(self, max_fail=5):
        """Remove proxies that have failed more than max_fail times."""
        before = len(self.proxies)
        self.proxies = [p for p in self.proxies if p.fail_count < max_fail]
        logger.info(f"Removed {before-len(self.proxies)} dead proxies")

    def import_from_url(self, url, parser_fn):
        """Fetch a remote list of proxies and parse them with parser_fn(text)->list of dicts."""
        try:
            import requests
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                for entry in parser_fn(resp.text):
                    self.add_proxy(**entry)
        except Exception as e:
            logger.error(f"Failed to import from {url}: {e}")

    async def close(self):
        """Close and cleanup proxy manager resources."""
        logger.debug("🧹 Proxy manager cleanup completed")

    async def load_proxies_from_file(self, file_path):
        """Load proxies from a text file."""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"⚠️  Proxy file not found: {file_path}")
                return
            
            with open(path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        # Parse proxy format: ip:port or scheme://ip:port
                        if '://' in line:
                            scheme, rest = line.split('://', 1)
                            ip, port = rest.split(':')
                        else:
                            scheme = 'http'
                            ip, port = line.split(':')
                        
                        self.add_proxy(ip, int(port), scheme)
                    except ValueError:
                        logger.warning(f"⚠️  Invalid proxy format: {line}")
            
            logger.info(f"📡 Loaded {len(self.proxies)} proxies from {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load proxies from file: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Intelligent Proxy Manager CLI")
    parser.add_argument("--file", help="Path to proxy JSON file", required=True)
    parser.add_argument("--test", action="store_true", help="Test all proxies asynchronously")
    parser.add_argument("--stats", action="store_true", help="Show proxy pool statistics")
    parser.add_argument("--rotate", action="store_true", help="Get a proxy URL from rotation")
    parser.add_argument("--clean", action="store_true", help="Remove dead proxies")
    parser.add_argument("--save", action="store_true", help="Save current list back to file")
    args = parser.parse_args()

    manager = ProxyManager(args.file)

    if args.test:
        asyncio.run(manager.test_all())
    if args.stats:
        total = len(manager.proxies)
        alive = len(manager.get_active())
        print(f"Total: {total} \u2022 Alive: {alive}")
    if args.rotate:
        p = manager.rotate()
        print(p.url if p else "No active proxy available")
    if args.clean:
        manager.remove_dead()
    if args.save:
        manager.save_proxies()
