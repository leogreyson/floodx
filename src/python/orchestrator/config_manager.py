"""
FloodX: Enhanced Configuration Manager
Handles configuration loading, validation, and runtime updates.
"""

import json
import yaml
import os
import sys
import ipaddress
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import asdict

# Add parent directory to Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.logger import logger
from config import FloodXConfig, get_attack_profile, validate_config, DEFAULT_CONFIG


class ConfigManager:
    """Enhanced configuration manager with validation and persistence."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else Path("floodx_config.yaml")
        self.config = FloodXConfig()
        self._runtime_overrides = {}
        
        # Load configuration from file if it exists
        if self.config_file.exists():
            self.load_from_file()
        else:
            logger.info(f"📁 Config file not found, using defaults: {self.config_file}")

    def load_from_file(self) -> bool:
        """Load configuration from YAML or JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # Apply loaded configuration
            self._apply_config_data(data)
            logger.info(f"✅ Configuration loaded from {self.config_file}")
            
            # Validate loaded configuration
            issues = validate_config(self.config)
            if issues:
                logger.warning(f"⚠️  Configuration validation issues:")
                for issue in issues:
                    logger.warning(f"   - {issue}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load config file: {e}")
            logger.info("Using default configuration")
            return False

    def save_to_file(self) -> bool:
        """Save current configuration to file."""
        try:
            config_dict = asdict(self.config)
            
            # Create directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                if self.config_file.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, default=str)
            
            logger.info(f"💾 Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save config file: {e}")
            return False

    def _apply_config_data(self, data: Dict[str, Any]):
        """Apply configuration data to the config object."""
        for section, section_data in data.items():
            if hasattr(self.config, section) and isinstance(section_data, dict):
                section_obj = getattr(self.config, section)
                for key, value in section_data.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)

    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path."""
        try:
            # Check runtime overrides first
            if path in self._runtime_overrides:
                return self._runtime_overrides[path]
            
            # Navigate through config object
            value = self.config
            for part in path.split('.'):
                value = getattr(value, part)
            return value
            
        except (AttributeError, KeyError):
            return default

    def set(self, path: str, value: Any, runtime_only: bool = False):
        """Set configuration value by dot-separated path."""
        if runtime_only:
            self._runtime_overrides[path] = value
            logger.debug(f"🔧 Runtime override: {path} = {value}")
            return
        
        try:
            # Navigate to parent object
            obj = self.config
            parts = path.split('.')
            for part in parts[:-1]:
                obj = getattr(obj, part)
            
            # Set the value
            setattr(obj, parts[-1], value)
            logger.debug(f"🔧 Config updated: {path} = {value}")
            
        except (AttributeError, TypeError) as e:
            logger.error(f"❌ Failed to set config value {path}: {e}")

    def apply_profile(self, profile_name: str) -> bool:
        """Apply a predefined attack profile."""
        profile = get_attack_profile(profile_name)
        if not profile:
            logger.error(f"❌ Unknown attack profile: {profile_name}")
            return False
        
        logger.info(f"🎯 Applying attack profile: {profile_name}")
        
        # Apply profile settings
        for key, value in profile.items():
            if key == 'vectors':
                continue  # Handled separately
            self.set(f"attack.{key}", value, runtime_only=True)
        
        logger.info(f"✅ Profile '{profile_name}' applied successfully")
        return True

    def validate_target(self, target: str, allow_private: bool = None) -> tuple[bool, str]:
        """Validate target address with safety checks."""
        if allow_private is None:
            allow_private = not self.get('safety.block_private_targets', True)
        
        try:
            # Try to parse as IP address
            ip = ipaddress.ip_address(target)
            
            # Check for localhost
            if ip.is_loopback:
                if self.get('safety.block_localhost', True) and not allow_private:
                    return False, "Localhost targets are blocked for safety"
                return True, "Localhost target allowed"
            
            # Check for private networks
            if ip.is_private:
                if self.get('safety.block_private_targets', True) and not allow_private:
                    return False, "Private network targets are blocked for safety"
                return True, "Private network target allowed"
            
            return True, "Valid public IP address"
            
        except ValueError:
            # It's a hostname - basic validation
            if target.lower() in ['localhost', '127.0.0.1', '::1']:
                if self.get('safety.block_localhost', True) and not allow_private:
                    return False, "Localhost hostnames are blocked for safety"
            
            return True, "Hostname appears valid"

    def get_spoof_ranges(self) -> List[ipaddress.IPv4Network]:
        """Get configured IP spoofing ranges."""
        ranges = self.get('spoofing.default_ranges', [])
        networks = []
        
        for range_str in ranges:
            try:
                network = ipaddress.IPv4Network(range_str, strict=False)
                networks.append(network)
            except ValueError as e:
                logger.warning(f"⚠️  Invalid spoof range '{range_str}': {e}")
        
        return networks

    def get_geo_spoof_ranges(self, region: str) -> List[ipaddress.IPv4Network]:
        """Get geographic spoofing ranges for a region."""
        geo_ranges = self.get('spoofing.geo_ranges', {})
        ranges = geo_ranges.get(region.lower(), [])
        networks = []
        
        for range_str in ranges:
            try:
                network = ipaddress.IPv4Network(range_str, strict=False)
                networks.append(network)
            except ValueError as e:
                logger.warning(f"⚠️  Invalid geo range '{range_str}': {e}")
        
        return networks

    def create_attack_config(self, 
                           target: str,
                           vector: str,
                           port: int = None,
                           duration: int = None,
                           concurrency: int = None,
                           **kwargs) -> Dict[str, Any]:
        """Create attack configuration with validation."""
        config = {
            'target': target,
            'vector': vector,
            'port': port or self.get('network.default_port', 80),
            'duration': duration or self.get('attack.default_duration', 60),
            'concurrency': concurrency or self.get('attack.default_concurrency', 1000),
        }
        
        # Add additional parameters
        config.update(kwargs)
        
        # Apply concurrency limits
        max_concurrency = self.get('attack.max_concurrency', 10000)
        min_concurrency = self.get('attack.min_concurrency', 1)
        
        config['concurrency'] = max(min_concurrency, 
                                  min(config['concurrency'], max_concurrency))
        
        # Add safety checks
        config['enforce_rate_limits'] = self.get('safety.enforce_rate_limits', True)
        config['max_packets_per_second'] = self.get('attack.max_packets_per_second', 100000)
        
        return config

    def get_evasion_config(self) -> Dict[str, Any]:
        """Get evasion configuration for advanced attacks."""
        return {
            'enabled': self.get('evasion.enabled', False),
            'rotate_user_agents': self.get('evasion.rotate_user_agents', True),
            'randomize_headers': self.get('evasion.randomize_headers', True),
            'vary_request_timing': self.get('evasion.vary_request_timing', True),
            'fragment_packets': self.get('evasion.fragment_packets', False),
            'randomize_tcp_options': self.get('evasion.randomize_tcp_options', True),
            'min_delay_ms': self.get('evasion.min_delay_ms', 10),
            'max_delay_ms': self.get('evasion.max_delay_ms', 1000),
            'jitter_factor': self.get('evasion.jitter_factor', 0.2)
        }

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return {
            'enabled': self.get('monitoring.enabled', True),
            'update_interval': self.get('monitoring.update_interval', 1.0),
            'save_stats_to_file': self.get('monitoring.save_stats_to_file', True),
            'stats_file_path': self.get('monitoring.stats_file_path', 'attack_stats.json'),
            'show_progress_bar': self.get('monitoring.show_progress_bar', True),
            'show_live_stats': self.get('monitoring.show_live_stats', True),
            'refresh_rate': self.get('monitoring.refresh_rate', 0.5)
        }

    def export_config(self) -> Dict[str, Any]:
        """Export current configuration as dictionary."""
        config_dict = asdict(self.config)
        
        # Add runtime overrides
        if self._runtime_overrides:
            config_dict['runtime_overrides'] = self._runtime_overrides
        
        return config_dict

    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = FloodXConfig()
        self._runtime_overrides.clear()
        logger.info("🔄 Configuration reset to defaults")

    def __str__(self) -> str:
        """String representation of current configuration."""
        return f"FloodXConfig(file={self.config_file}, overrides={len(self._runtime_overrides)})"
