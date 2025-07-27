"""
FloodX: Enhanced Logging Module
Provides centralized logging with color support and structured output.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class FloodXFormatter(logging.Formatter):
    """Custom formatter with colors and structured output."""
    
    LEVEL_COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD
    }
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        # Create timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
        
        # Get level color
        level_color = self.LEVEL_COLORS.get(record.levelname, Colors.WHITE) if self.use_colors else ''
        reset_color = Colors.END if self.use_colors else ''
        
        # Format the message
        if self.use_colors:
            formatted = f"{Colors.BLUE}[{timestamp}]{reset_color} {level_color}{record.levelname:8}{reset_color} {record.getMessage()}"
        else:
            formatted = f"[{timestamp}] {record.levelname:8} {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted

class AttackStatsLogger:
    """Specialized logger for attack statistics with real-time updates."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = Path(log_file) if log_file else None
        self.stats = {
            'start_time': datetime.now(),
            'packets_sent': 0,
            'bytes_sent': 0,
            'connections_attempted': 0,
            'connections_successful': 0,
            'errors': 0,
            'target': '',
            'vector': '',
            'status': 'initializing',
            'active_threads': 0,
            'current_rate': 0.0
        }
        self.last_packets = 0
        self.last_update_time = datetime.now()
        self.is_running = False
    
    def start_real_time_logging(self):
        """Start real-time statistics display."""
        self.is_running = True
        import threading
        self.display_thread = threading.Thread(target=self._real_time_display, daemon=True)
        self.display_thread.start()
    
    def stop_real_time_logging(self):
        """Stop real-time statistics display."""
        self.is_running = False
    
    def _real_time_display(self):
        """Display real-time statistics every second."""
        import time
        while self.is_running:
            try:
                # Clear the current line and display updated stats
                print(f"\r{self._get_live_stats()}", end="", flush=True)
                time.sleep(1)
            except Exception:
                break
    
    def _get_live_stats(self) -> str:
        """Get live statistics line for real-time display."""
        duration = (datetime.now() - self.stats['start_time']).total_seconds()
        
        # Calculate current rate
        current_time = datetime.now()
        time_diff = (current_time - self.last_update_time).total_seconds()
        if time_diff >= 1.0:
            packet_diff = self.stats['packets_sent'] - self.last_packets
            self.stats['current_rate'] = packet_diff / time_diff
            self.last_packets = self.stats['packets_sent']
            self.last_update_time = current_time
        
        # Format bytes
        def format_bytes(bytes_val):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_val < 1024:
                    return f"{bytes_val:.1f} {unit}"
                bytes_val /= 1024
            return f"{bytes_val:.1f} TB"
        
        try:
            from colors import success_text, info_text, Colors, accent_text
            packets = self.stats['packets_sent']
            rate = self.stats['current_rate']
            connections = self.stats['connections_successful']
            threads = self.stats['active_threads']
            errors = self.stats['errors']
            bytes_formatted = format_bytes(self.stats['bytes_sent'])
            
            return (f"{Colors.PRIMARY}[{duration:6.1f}s]{Colors.RESET} "
                   f"{accent_text('⚡')} {success_text(f'{packets:,}')} pkts "
                   f"{accent_text('📊')} {success_text(f'{rate:.1f}')} pps "
                   f"{accent_text('📡')} {success_text(f'{connections:,}')} conn "
                   f"{accent_text('💾')} {success_text(bytes_formatted)} "
                   f"{accent_text('🔥')} {success_text(f'{threads:,}')} threads "
                   f"{accent_text('❌')} {success_text(f'{errors:,}')} errs")
        except ImportError:
            return (f"[{duration:6.1f}s] ⚡{self.stats['packets_sent']:,} pkts "
                   f"📊{self.stats['current_rate']:.1f} pps "
                   f"📡{self.stats['connections_successful']:,} conn "
                   f"💾{format_bytes(self.stats['bytes_sent'])} "
                   f"🔥{self.stats['active_threads']:,} threads "
                   f"❌{self.stats['errors']:,} errs")
    
    def update_stats(self, **kwargs):
        """Update attack statistics."""
        self.stats.update(kwargs)
        self.stats['last_update'] = datetime.now()
        
        if self.log_file:
            self._write_stats_to_file()
    
    def increment_packets(self, count: int = 1, bytes_sent: int = 0):
        """Increment packet and byte counters."""
        self.stats['packets_sent'] += count
        self.stats['bytes_sent'] += bytes_sent
    
    def increment_connections(self, successful: bool = True):
        """Increment connection counters."""
        self.stats['connections_attempted'] += 1
        if successful:
            self.stats['connections_successful'] += 1
    
    def increment_errors(self, count: int = 1):
        """Increment error counter."""
        self.stats['errors'] += count
    
    def set_active_threads(self, count: int):
        """Update active thread count."""
        self.stats['active_threads'] = count
    
    def _write_stats_to_file(self):
        """Write statistics to JSON log file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to write stats to file: {e}")
    
    def get_formatted_stats(self, final: bool = False) -> str:
        """Get formatted statistics string."""
        # Stop real-time logging if this is final stats
        if final and self.is_running:
            self.stop_real_time_logging()
            print()  # New line after real-time display
        
        duration = (datetime.now() - self.stats['start_time']).total_seconds()
        
        # Calculate rates
        pps = self.stats['packets_sent'] / max(duration, 1)  # packets per second
        bps = self.stats['bytes_sent'] / max(duration, 1)   # bytes per second
        
        # Format bytes
        def format_bytes(bytes_val):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_val < 1024:
                    return f"{bytes_val:.1f} {unit}"
                bytes_val /= 1024
            return f"{bytes_val:.1f} TB"
        
        # Calculate success rate
        success_rate = 0.0
        if self.stats['connections_attempted'] > 0:
            success_rate = (self.stats['connections_successful'] / self.stats['connections_attempted']) * 100
        
        # Import colors here to avoid circular imports
        try:
            from colors import accent_text, info_text, success_text, warning_text, error_text, Colors
            
            # Choose color based on success rate and errors
            status_color = success_text if self.stats['errors'] == 0 else warning_text
            if self.stats['errors'] > self.stats['packets_sent'] * 0.1:  # > 10% error rate
                status_color = error_text
            
            return f"""
{accent_text('📊 FINAL ATTACK STATISTICS', True)}
{Colors.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.PRIMARY}║{Colors.RESET} {info_text('🎯 Target:')} {success_text(self.stats['target'])}
{Colors.PRIMARY}║{Colors.RESET} {info_text('⚔️  Attack Vector:')} {success_text(self.stats['vector'].upper())}
{Colors.PRIMARY}║{Colors.RESET} {info_text('⏱️  Total Duration:')} {success_text(f"{duration:.1f} seconds")}
{Colors.PRIMARY}║{Colors.RESET} {info_text('📈 Final Status:')} {status_color(self.stats['status'])}
{Colors.PRIMARY}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}
{Colors.PRIMARY}║{Colors.RESET} {info_text('📦 Packets Sent:')} {success_text(f"{self.stats['packets_sent']:,} packets")} {accent_text(f"({pps:.1f} pps avg)")}
{Colors.PRIMARY}║{Colors.RESET} {info_text('💾 Data Transmitted:')} {success_text(format_bytes(self.stats['bytes_sent']))} {accent_text(f"({format_bytes(bps)}/s avg)")}
{Colors.PRIMARY}║{Colors.RESET} {info_text('🔗 Connections:')} {success_text(f"{self.stats['connections_successful']:,} successful")} / {info_text(f"{self.stats['connections_attempted']:,} attempted")} {accent_text(f"({success_rate:.1f}%)")}
{Colors.PRIMARY}║{Colors.RESET} {info_text('🔥 Peak Threads:')} {success_text(f"{self.stats['active_threads']:,} concurrent workers")}
{Colors.PRIMARY}║{Colors.RESET} {info_text('❌ Total Errors:')} {error_text(f"{self.stats['errors']:,}")} {accent_text(f"({(self.stats['errors']/max(self.stats['packets_sent'],1)*100):.1f}% error rate)")}
{Colors.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
            """
        except ImportError:
            # Fallback to non-colored version
            return f"""
📊 FINAL ATTACK STATISTICS
╔══════════════════════════════════════════════════════════════════════════════╗
║ 🎯 Target: {self.stats['target']}
║ ⚔️  Attack Vector: {self.stats['vector'].upper()}
║ ⏱️  Total Duration: {duration:.1f} seconds
║ 📈 Final Status: {self.stats['status']}
╠══════════════════════════════════════════════════════════════════════════════╣
║ 📦 Packets Sent: {self.stats['packets_sent']:,} packets ({pps:.1f} pps avg)
║ 💾 Data Transmitted: {format_bytes(self.stats['bytes_sent'])} ({format_bytes(bps)}/s avg)
║ 🔗 Connections: {self.stats['connections_successful']:,} successful / {self.stats['connections_attempted']:,} attempted ({success_rate:.1f}%)
║ 🔥 Peak Threads: {self.stats['active_threads']:,} concurrent workers
║ ❌ Total Errors: {self.stats['errors']:,} ({(self.stats['errors']/max(self.stats['packets_sent'],1)*100):.1f}% error rate)
╚══════════════════════════════════════════════════════════════════════════════╝
            """

# Configure main logger
def setup_logger(name: str = 'floodx', level: str = 'INFO', log_file: Optional[str] = None) -> logging.Logger:
    """Setup and configure the main logger."""
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger_instance.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FloodXFormatter(use_colors=True))
    logger_instance.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(FloodXFormatter(use_colors=False))
        logger_instance.addHandler(file_handler)
    
    return logger_instance

# Create default logger instance
logger = setup_logger()

# Convenience functions for structured logging
def log_attack_start(target: str, vector: str, port: int, duration: int):
    """Log attack start with structured information."""
    logger.info(f"🚀 Starting {vector.upper()} attack on {target}:{port} for {duration}s")

def log_attack_end(target: str, vector: str, stats: Dict[str, Any]):
    """Log attack completion with statistics."""
    logger.info(f"✅ {vector.upper()} attack on {target} completed")
    logger.info(f"📊 Final stats: {stats.get('packets_sent', 0):,} packets, {stats.get('errors', 0):,} errors")

def log_proxy_status(working: int, total: int, speed_test: float = None):
    """Log proxy validation status."""
    percentage = (working / total * 100) if total > 0 else 0
    speed_info = f" (avg: {speed_test:.2f}s)" if speed_test else ""
    logger.info(f"🌐 Proxies: {working}/{total} working ({percentage:.1f}%){speed_info}")

def log_spoof_config(ranges: list, count: int):
    """Log IP spoofing configuration."""
    logger.info(f"🎭 IP Spoofing: {len(ranges)} ranges, {count:,} random IPs")
    for i, range_str in enumerate(ranges[:3]):  # Show first 3 ranges
        logger.info(f"   └─ {range_str}")
    if len(ranges) > 3:
        logger.info(f"   └─ ... and {len(ranges) - 3} more ranges")

def log_error_with_context(error: Exception, context: Dict[str, Any]):
    """Log error with additional context information."""
    logger.error(f"❌ {type(error).__name__}: {error}")
    for key, value in context.items():
        logger.debug(f"   Context {key}: {value}")

# Global stats logger instance
stats_logger = AttackStatsLogger()
