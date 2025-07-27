"""
FloodX: Attack Monitor
Real-time monitoring of attack statistics and system resources.
"""

import asyncio
import time
import sys
import os
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

# Add parent directory to Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.logger import logger, stats_logger
import psutil


@dataclass
class AttackStats:
    """Container for attack statistics."""
    packets_sent: int = 0
    bytes_sent: int = 0
    connections_attempted: int = 0
    connections_established: int = 0
    errors: int = 0
    proxy_failures: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)


class AttackMonitor:
    """Enhanced attack monitor with async support and real-time statistics."""
    
    def __init__(self):
        self.stats = AttackStats()
        self.lock = threading.Lock()
        self.monitor_task: Optional[asyncio.Task] = None
        self.running = False
        self.interval = 1.0  # seconds
        self.config = {}
        
        # Vector-specific stats
        self.vector_stats: Dict[str, AttackStats] = {}
        
        # System resource monitoring
        self.system_stats = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'network_io': {}
        }

    async def start(self, config: Dict[str, Any]):
        """Start monitoring with configuration."""
        self.config = config
        self.running = True
        
        # Initialize stats logger
        stats_logger.update_stats(
            target=config.get('target', 'unknown'),
            vector=config.get('vector', 'unknown'),
            status='monitoring_started'
        )
        
        # Start monitoring task
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("📊 Attack monitoring started")

    async def stop(self):
        """Stop monitoring."""
        if self.running:
            logger.info("🛑 Stopping attack monitoring...")
            self.running = False
            
            if self.monitor_task and not self.monitor_task.done():
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass
            
            self._print_final_stats()
            logger.info("✅ Attack monitoring stopped")

    async def _monitor_loop(self):
        """Main monitoring loop."""
        try:
            while self.running:
                await self._collect_stats()
                await self._update_display()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            logger.debug("Monitor loop cancelled")
        except Exception as e:
            logger.error(f"❌ Monitor loop error: {e}")

    async def _collect_stats(self):
        """Collect system and attack statistics."""
        try:
            # Update system stats
            self.system_stats['cpu_usage'] = psutil.cpu_percent(interval=None)
            self.system_stats['memory_usage'] = psutil.virtual_memory().percent
            
            # Network I/O stats
            net_io = psutil.net_io_counters()
            if net_io:
                self.system_stats['network_io'] = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            
            # Update timestamps
            with self.lock:
                self.stats.last_update = datetime.now()
                
        except Exception as e:
            logger.debug(f"Stats collection error: {e}")

    async def _update_display(self):
        """Update live statistics display."""
        if not self.config.get('show_live_stats', True):
            return
        
        try:
            with self.lock:
                duration = (self.stats.last_update - self.stats.start_time).total_seconds()
                
                # Calculate rates
                pps = self.stats.packets_sent / max(duration, 1)
                bps = self.stats.bytes_sent / max(duration, 1)
                
                # Log periodic updates
                if int(duration) % 10 == 0:  # Every 10 seconds
                    logger.info(f"📊 Stats: {self.stats.packets_sent:,} packets, {pps:.1f} pps, {self._format_bytes(bps)}/s")
                    
        except Exception as e:
            logger.debug(f"Display update error: {e}")

    def update_stats(self, vector: str = None, **kwargs):
        """Update attack statistics."""
        with self.lock:
            # Update global stats
            for key, value in kwargs.items():
                if hasattr(self.stats, key):
                    current_value = getattr(self.stats, key)
                    setattr(self.stats, key, current_value + value)
            
            # Update vector-specific stats
            if vector:
                if vector not in self.vector_stats:
                    self.vector_stats[vector] = AttackStats()
                
                for key, value in kwargs.items():
                    if hasattr(self.vector_stats[vector], key):
                        current_value = getattr(self.vector_stats[vector], key)
                        setattr(self.vector_stats[vector], key, current_value + value)
            
            # Update stats logger
            stats_logger.update_stats(**kwargs)

    def get_stats(self, vector: Optional[str] = None) -> Dict[str, Any]:
        """Get current statistics."""
        with self.lock:
            if vector and vector in self.vector_stats:
                stats_obj = self.vector_stats[vector]
            else:
                stats_obj = self.stats
            
            duration = (datetime.now() - stats_obj.start_time).total_seconds()
            
            return {
                'packets_sent': stats_obj.packets_sent,
                'bytes_sent': stats_obj.bytes_sent,
                'connections_attempted': stats_obj.connections_attempted,
                'connections_established': stats_obj.connections_established,
                'errors': stats_obj.errors,
                'proxy_failures': stats_obj.proxy_failures,
                'duration': duration,
                'packets_per_second': stats_obj.packets_sent / max(duration, 1),
                'bytes_per_second': stats_obj.bytes_sent / max(duration, 1),
                'success_rate': (stats_obj.connections_established / max(stats_obj.connections_attempted, 1)) * 100,
                'system': self.system_stats.copy()
            }

    def get_vector_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all attack vectors."""
        with self.lock:
            return {
                vector: {
                    'packets_sent': stats.packets_sent,
                    'bytes_sent': stats.bytes_sent,
                    'connections_attempted': stats.connections_attempted,
                    'errors': stats.errors,
                    'duration': (datetime.now() - stats.start_time).total_seconds()
                }
                for vector, stats in self.vector_stats.items()
            }

    def _print_final_stats(self):
        """Print final attack statistics."""
        with self.lock:
            duration = (datetime.now() - self.stats.start_time).total_seconds()
            
            logger.info("📊 Final Attack Statistics:")
            logger.info(f"   Duration: {duration:.1f}s")
            logger.info(f"   Packets sent: {self.stats.packets_sent:,}")
            logger.info(f"   Bytes sent: {self._format_bytes(self.stats.bytes_sent)}")
            logger.info(f"   Connections attempted: {self.stats.connections_attempted:,}")
            logger.info(f"   Connections established: {self.stats.connections_established:,}")
            logger.info(f"   Errors: {self.stats.errors:,}")
            
            if self.stats.connections_attempted > 0:
                success_rate = (self.stats.connections_established / self.stats.connections_attempted) * 100
                logger.info(f"   Success rate: {success_rate:.1f}%")
            
            # Average rates
            if duration > 0:
                logger.info(f"   Average PPS: {self.stats.packets_sent / duration:.1f}")
                logger.info(f"   Average BPS: {self._format_bytes(self.stats.bytes_sent / duration)}/s")
            
            # Vector-specific stats
            if self.vector_stats:
                logger.info("📊 Vector-specific statistics:")
                for vector, stats in self.vector_stats.items():
                    vector_duration = (datetime.now() - stats.start_time).total_seconds()
                    logger.info(f"   {vector.upper()}: {stats.packets_sent:,} packets, {stats.errors:,} errors")

    def _format_bytes(self, bytes_value: float) -> str:
        """Format bytes value with appropriate unit."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} PB"

    def register_process(self, process, vector: str):
        """Register a process for monitoring (compatibility method)."""
        logger.debug(f"Registered {vector} process for monitoring")
        
        # Initialize vector stats if not exists
        if vector not in self.vector_stats:
            self.vector_stats[vector] = AttackStats()

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        return self.system_stats.copy()

    # Legacy compatibility methods
    def start_monitoring(self):
        """Legacy method for backward compatibility."""
        logger.warning("⚠️  Using deprecated start_monitoring(), use async start() instead")

    def stop_monitoring(self):
        """Legacy method for backward compatibility."""
        logger.warning("⚠️  Using deprecated stop_monitoring(), use async stop() instead")
        self.running = False

    def print_final_stats(self):
        """Legacy method for backward compatibility."""
        self._print_final_stats()
