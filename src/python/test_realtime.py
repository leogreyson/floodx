#!/usr/bin/env python3
"""
Test the real-time logging system
"""

import time
import sys
import os
import signal
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.logger import stats_logger
from common.colors import success_text, info_text, warning_text, print_status

def test_real_time_logging():
    """Test the real-time logging functionality."""
    
    # Setup signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print_status("Test stopped by user (Ctrl+C)", "warning")
        stats_logger.stop_real_time_logging()
        print()  # New line
        print(stats_logger.get_formatted_stats(final=True))
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize stats
    stats_logger.update_stats(
        target="test-target.com",
        vector="SYN",
        status="running"
    )
    
    print_status("Starting real-time logging test...", "info")
    print_status("Press Ctrl+C to stop and see final statistics", "info")
    print()
    
    # Start real-time display
    stats_logger.start_real_time_logging()
    
    # Simulate attack progress
    try:
        for i in range(300):  # Run for 5 minutes max
            # Simulate packet sending
            packets_this_second = 15 + (i % 10)  # Varying packet rate
            stats_logger.increment_packets(packets_this_second, packets_this_second * 40)
            
            # Simulate some connections
            if i % 3 == 0:  # Every 3 seconds
                stats_logger.increment_connections(successful=True)
                stats_logger.increment_connections(successful=False)
            
            # Simulate occasional errors
            if i % 10 == 0:  # Every 10 seconds
                stats_logger.increment_errors(2)
            
            # Update thread count
            stats_logger.set_active_threads(min(1000, (i * 5) + 100))
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        pass
    
    # Stop real-time logging and show final stats
    stats_logger.stop_real_time_logging()
    stats_logger.update_stats(status="completed")
    print()
    print(stats_logger.get_formatted_stats(final=True))

if __name__ == "__main__":
    test_real_time_logging()
