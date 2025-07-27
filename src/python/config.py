"""
FloodX: Configuration Settings
Centralized configuration management for the DDoS toolkit.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class NetworkConfig:
    """Network-related configuration."""
    default_timeout: float = 5.0
    connect_timeout: float = 3.0
    read_timeout: float = 10.0
    max_retries: int = 3
    default_port: int = 80
    
    # Advanced networking
    tcp_nodelay: bool = True
    tcp_keepalive: bool = True
    socket_reuse: bool = True

@dataclass
class AttackConfig:
    """Attack-specific configuration."""
    default_duration: int = 60
    default_concurrency: int = 1000
    max_concurrency: int = 10000
    min_concurrency: int = 1
    
    # Rate limiting for safety
    max_packets_per_second: int = 100000
    max_bytes_per_second: int = 100 * 1024 * 1024  # 100MB/s
    
    # Attack profiles
    profiles: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'light': {
            'concurrency': 100,
            'duration': 30,
            'rate_limit': 1000,
            'vectors': ['http']
        },
        'moderate': {
            'concurrency': 500,
            'duration': 120,
            'rate_limit': 5000,
            'vectors': ['syn', 'http', 'udp']
        },
        'full': {
            'concurrency': 2000,
            'duration': 300,
            'rate_limit': 10000,
            'vectors': ['syn', 'udp', 'icmp', 'http', 'websocket', 'tls']
        }
    })

@dataclass
class ProxyConfig:
    """Proxy-related configuration."""
    timeout: float = 10.0
    max_concurrent_checks: int = 100
    validation_url: str = "http://httpbin.org/ip"
    retry_failed_proxies: bool = False
    
    # Proxy rotation
    rotation_interval: int = 300  # seconds
    max_proxy_failures: int = 5
    
    # Default proxy lists (for testing only)
    default_proxy_sources: List[str] = field(default_factory=lambda: [
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    ])

@dataclass
class SpoofingConfig:
    """IP spoofing configuration."""
    enabled: bool = False
    default_ranges: List[str] = field(default_factory=lambda: [
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16'
    ])
    
    # Geographic spoofing ranges
    geo_ranges: Dict[str, List[str]] = field(default_factory=lambda: {
        'asia': ['1.0.0.0/8', '14.0.0.0/8', '27.0.0.0/8'],
        'europe': ['2.0.0.0/8', '5.0.0.0/8', '31.0.0.0/8'],
        'americas': ['3.0.0.0/8', '4.0.0.0/8', '6.0.0.0/8'],
        'africa': ['41.0.0.0/8', '105.0.0.0/8', '154.0.0.0/8']
    })
    
    max_spoof_count: int = 10000
    randomize_ttl: bool = True
    randomize_packet_size: bool = True

@dataclass
class EvasionConfig:
    """Evasion and anti-detection configuration."""
    enabled: bool = False
    
    # HTTP evasion
    rotate_user_agents: bool = True
    randomize_headers: bool = True
    vary_request_timing: bool = True
    
    # Network evasion
    fragment_packets: bool = False
    randomize_tcp_options: bool = True
    vary_packet_sizes: bool = True
    
    # TLS evasion
    randomize_cipher_suites: bool = True
    vary_tls_extensions: bool = True
    
    # Timing evasion
    min_delay_ms: int = 10
    max_delay_ms: int = 1000
    jitter_factor: float = 0.2

@dataclass
class MonitoringConfig:
    """Monitoring and statistics configuration."""
    enabled: bool = True
    update_interval: float = 1.0  # seconds
    save_stats_to_file: bool = True
    stats_file_path: str = "attack_stats.json"
    
    # Real-time display
    show_progress_bar: bool = True
    show_live_stats: bool = True
    refresh_rate: float = 0.5  # seconds
    
    # Logging
    log_level: str = "INFO"
    log_to_file: bool = False
    log_file_path: str = "floodx.log"

@dataclass
class SafetyConfig:
    """Safety and validation configuration."""
    require_confirmation: bool = True
    block_private_targets: bool = True
    block_localhost: bool = True
    
    # Validation
    validate_targets: bool = True
    dns_resolution_timeout: float = 5.0
    
    # Rate limiting
    enforce_rate_limits: bool = True
    emergency_stop_threshold: float = 0.9  # CPU usage threshold
    
    # Warnings
    show_legal_warning: bool = True
    require_agreement: bool = True

@dataclass
class FloodXConfig:
    """Main configuration class containing all settings."""
    network: NetworkConfig = field(default_factory=NetworkConfig)
    attack: AttackConfig = field(default_factory=AttackConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    spoofing: SpoofingConfig = field(default_factory=SpoofingConfig)
    evasion: EvasionConfig = field(default_factory=EvasionConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    
    def __post_init__(self):
        """Post-initialization validation."""
        # Validate concurrency limits
        if self.attack.max_concurrency < self.attack.min_concurrency:
            raise ValueError("max_concurrency must be >= min_concurrency")
        
        # Ensure timeouts are positive
        if self.network.default_timeout <= 0:
            raise ValueError("default_timeout must be positive")
        
        # Validate rate limits
        if self.attack.max_packets_per_second <= 0:
            raise ValueError("max_packets_per_second must be positive")

# Global configuration instance
DEFAULT_CONFIG = FloodXConfig()

# User-Agent strings for HTTP evasion
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
]

# Common HTTP headers for evasion
COMMON_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

# TLS cipher suites for evasion
TLS_CIPHER_SUITES = [
    'TLS_AES_256_GCM_SHA384',
    'TLS_CHACHA20_POLY1305_SHA256',
    'TLS_AES_128_GCM_SHA256',
    'TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384',
    'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384',
    'TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256',
    'TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256',
    'TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256',
    'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256'
]

# DNS amplifiers for UDP attacks (educational purposes)
DNS_AMPLIFIERS = [
    '8.8.8.8',     # Google
    '1.1.1.1',     # Cloudflare
    '208.67.222.222',  # OpenDNS
    '9.9.9.9',     # Quad9
    '76.76.19.19', # Alternate DNS
]

# NTP servers for amplification (educational purposes)
NTP_AMPLIFIERS = [
    'pool.ntp.org',
    '0.pool.ntp.org',
    '1.pool.ntp.org',
    '2.pool.ntp.org',
    '3.pool.ntp.org'
]

def load_config_from_env() -> FloodXConfig:
    """Load configuration from environment variables."""
    config = FloodXConfig()
    
    # Network settings
    if timeout := os.getenv('FLOODX_TIMEOUT'):
        config.network.default_timeout = float(timeout)
    
    # Attack settings
    if duration := os.getenv('FLOODX_DURATION'):
        config.attack.default_duration = int(duration)
    
    if concurrency := os.getenv('FLOODX_CONCURRENCY'):
        config.attack.default_concurrency = int(concurrency)
    
    # Safety settings
    if os.getenv('FLOODX_ALLOW_PRIVATE', '').lower() == 'true':
        config.safety.block_private_targets = False
    
    if os.getenv('FLOODX_ALLOW_LOCALHOST', '').lower() == 'true':
        config.safety.block_localhost = False
    
    return config

def get_attack_profile(profile_name: str) -> Optional[Dict[str, Any]]:
    """Get predefined attack profile configuration."""
    return DEFAULT_CONFIG.attack.profiles.get(profile_name.lower())

def validate_config(config: FloodXConfig) -> List[str]:
    """Validate configuration and return list of issues."""
    issues = []
    
    # Check concurrency limits
    if config.attack.default_concurrency > config.attack.max_concurrency:
        issues.append(f"default_concurrency ({config.attack.default_concurrency}) exceeds max_concurrency ({config.attack.max_concurrency})")
    
    # Check timeout values
    if config.network.connect_timeout >= config.network.default_timeout:
        issues.append("connect_timeout should be less than default_timeout")
    
    # Check proxy configuration
    if not config.proxy.validation_url.startswith(('http://', 'https://')):
        issues.append("proxy validation_url must be a valid HTTP/HTTPS URL")
    
    return issues


# DNS Amplifier Servers for DNS Amplification Attacks
DNS_AMPLIFIERS = [
    # Public DNS servers that can be used for amplification
    '8.8.8.8',          # Google DNS
    '8.8.4.4',          # Google DNS
    '1.1.1.1',          # Cloudflare DNS
    '1.0.0.1',          # Cloudflare DNS
    '208.67.222.222',   # OpenDNS
    '208.67.220.220',   # OpenDNS
    '9.9.9.9',          # Quad9 DNS
    '149.112.112.112',  # Quad9 DNS
    '64.6.64.6',        # Verisign DNS
    '64.6.65.6',        # Verisign DNS
    '84.200.69.80',     # DNS.WATCH
    '84.200.70.40',     # DNS.WATCH
    '8.26.56.26',       # Comodo Secure DNS
    '8.20.247.20',      # Comodo Secure DNS
    '199.85.126.10',    # Norton ConnectSafe
    '199.85.127.10',    # Norton ConnectSafe
    '81.218.119.11',    # GreenTeam DNS
    '209.244.0.3',      # Level3 DNS
    '209.244.0.4',      # Level3 DNS
    '195.46.39.39',     # SafeDNS
    '195.46.39.40',     # SafeDNS
]
