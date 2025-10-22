"""
Proxy configuration and utilities.

This module provides configuration management and utility functions for the
Go proxy service.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    """Configuration for a single proxy instance."""

    # Network configuration
    host: str = "127.0.0.1"
    port: int = 8080

    # Process configuration
    binary_path: str = "./proxy_service/proxy"
    startup_timeout: int = 30
    health_check_interval: float = 5.0
    max_startup_attempts: int = 3

    # Performance settings
    max_connections: int = 1000
    connection_timeout: int = 30
    read_timeout: int = 300
    write_timeout: int = 300

    # TLS configuration
    tls_version: str = "1.3"
    cipher_suites: List[str] = None
    prefer_server_cipher_suites: bool = True

    # HTTP/2 configuration
    enable_http2: bool = True
    max_concurrent_streams: int = 1000
    initial_window_size: int = 65535
    max_frame_size: int = 16777215

    # Logging configuration
    log_level: str = "info"
    log_file: Optional[str] = None
    enable_access_log: bool = True

    # Security settings
    allowed_origins: List[str] = None
    max_request_size: int = 10485760  # 10MB
    enable_compression: bool = True

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Validate port range
        if not (1024 <= self.port <= 65535):
            raise ValueError(f"Port must be between 1024 and 65535, got {self.port}")

        # Validate timeouts
        if self.startup_timeout <= 0:
            raise ValueError(f"Startup timeout must be positive, got {self.startup_timeout}")

        if self.health_check_interval <= 0:
            raise ValueError(f"Health check interval must be positive, got {self.health_check_interval}")

        # Set default values for optional fields
        if self.cipher_suites is None:
            self.cipher_suites = [
                "TLS_AES_128_GCM_SHA256",
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256",
                "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
                "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
            ]

        if self.allowed_origins is None:
            self.allowed_origins = ["*"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProxyConfig":
        """Create from dictionary."""
        return cls(**data)


class ProxyConfigManager:
    """Manager for proxy configurations."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or "proxy_config.json"
        self.configs: Dict[str, ProxyConfig] = {}

        # Load configurations
        self._load_configurations()

    def _load_configurations(self):
        """Load configurations from file."""
        config_path = Path(self.config_file)

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)

                # Load configurations
                for name, config_data in data.get('proxies', {}).items():
                    self.configs[name] = ProxyConfig.from_dict(config_data)

                logger.info(f"Loaded {len(self.configs)} proxy configurations from {self.config_file}")

            except Exception as e:
                logger.error(f"Failed to load proxy configurations: {str(e)}")
                self._create_default_config()
        else:
            logger.info(f"Configuration file {self.config_file} not found, creating default")
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration."""
        default_config = ProxyConfig()
        self.add_config("default", default_config)
        self.save_configurations()

    def add_config(self, name: str, config: ProxyConfig):
        """Add or update a configuration."""
        self.configs[name] = config
        logger.info(f"Added/updated proxy configuration: {name}")

    def get_config(self, name: str) -> Optional[ProxyConfig]:
        """Get a configuration by name."""
        return self.configs.get(name)

    def get_all_configs(self) -> Dict[str, ProxyConfig]:
        """Get all configurations."""
        return self.configs.copy()

    def remove_config(self, name: str) -> bool:
        """Remove a configuration."""
        if name in self.configs:
            del self.configs[name]
            logger.info(f"Removed proxy configuration: {name}")
            return True
        return False

    def save_configurations(self):
        """Save configurations to file."""
        try:
            # Create directory if it doesn't exist
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare data for saving
            data = {
                "proxies": {
                    name: config.to_dict()
                    for name, config in self.configs.items()
                },
                "version": "1.0",
                "last_updated": self._get_timestamp()
            }

            # Save to file
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.configs)} proxy configurations to {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to save proxy configurations: {str(e)}")

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def create_pool_configs(self, base_name: str, count: int, start_port: int = 8080) -> List[Dict[str, Any]]:
        """
        Create configurations for a proxy pool.

        Args:
            base_name: Base name for configurations
            count: Number of proxy instances
            start_port: Starting port number

        Returns:
            List of configuration dictionaries
        """
        configs = []

        for i in range(count):
            config_name = f"{base_name}_{i+1}"
            health_check_interval = 5.0 + (i * 0.5)  # Stagger health checks
            config = ProxyConfig(
                host="127.0.0.1",
                port=start_port + i,
                binary_path=f"./proxy_service/proxy_{i+1}",
                health_check_interval=health_check_interval,
                max_connections=1000,
                log_level="info"
            )

            self.add_config(config_name, config)
            configs.append(config.to_dict())

        logger.info(f"Created {count} proxy pool configurations: {base_name}")
        return configs

    def validate_config(self, config: ProxyConfig) -> List[str]:
        """
        Validate a configuration and return any issues.

        Args:
            config: Configuration to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Check binary path
        binary_path = Path(config.binary_path)
        if not binary_path.exists():
            issues.append(f"Binary not found: {config.binary_path}")
        elif not binary_path.is_file():
            issues.append(f"Binary path is not a file: {config.binary_path}")
        elif not os.access(binary_path, os.X_OK):
            issues.append(f"Binary is not executable: {config.binary_path}")

        # Check port availability
        if not (1024 <= config.port <= 65535):
            issues.append(f"Port {config.port} is out of valid range (1024-65535)")

        # Check if port is in use (basic check)
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex((config.host, config.port))
                if result == 0:
                    issues.append(f"Port {config.port} is already in use")
        except Exception:
            pass  # Skip port check if socket operations fail

        # Check log file directory
        if config.log_file:
            log_path = Path(config.log_file)
            if not log_path.parent.exists():
                try:
                    log_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create log directory: {str(e)}")

        return issues

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of all configurations."""
        summary = {
            'total_configs': len(self.configs),
            'config_names': list(self.configs.keys()),
            'config_file': self.config_file,
            'configs': {}
        }

        for name, config in self.configs.items():
            issues = self.validate_config(config)
            summary['configs'][name] = {
                'host': config.host,
                'port': config.port,
                'binary_path': config.binary_path,
                'is_valid': len(issues) == 0,
                'issues': issues
            }

        return summary


def load_environment_config() -> Dict[str, Any]:
    """Load proxy configuration from environment variables."""
    config = {}

    # Network configuration
    if os.getenv('PROXY_HOST'):
        config['host'] = os.getenv('PROXY_HOST')
    if os.getenv('PROXY_PORT'):
        config['port'] = int(os.getenv('PROXY_PORT'))

    # Process configuration
    if os.getenv('PROXY_BINARY_PATH'):
        config['binary_path'] = os.getenv('PROXY_BINARY_PATH')
    if os.getenv('PROXY_STARTUP_TIMEOUT'):
        config['startup_timeout'] = int(os.getenv('PROXY_STARTUP_TIMEOUT'))

    # Performance settings
    if os.getenv('PROXY_MAX_CONNECTIONS'):
        config['max_connections'] = int(os.getenv('PROXY_MAX_CONNECTIONS'))

    # Logging
    if os.getenv('PROXY_LOG_LEVEL'):
        config['log_level'] = os.getenv('PROXY_LOG_LEVEL')
    if os.getenv('PROXY_LOG_FILE'):
        config['log_file'] = os.getenv('PROXY_LOG_FILE')

    return config


def create_default_proxy_configs() -> List[Dict[str, Any]]:
    """Create default proxy configurations for common use cases."""

    # Single proxy configuration
    single_config = ProxyConfig(
        host="127.0.0.1",
        port=8080,
        binary_path="./proxy_service/proxy"
    )

    # High-performance configuration
    high_perf_config = ProxyConfig(
        host="127.0.0.1",
        port=8081,
        binary_path="./proxy_service/proxy_highperf",
        max_connections=5000,
        connection_timeout=10,
        health_check_interval=2.0,
        log_level="warning"
    )

    # Development configuration
    dev_config = ProxyConfig(
        host="127.0.0.1",
        port=8082,
        binary_path="./proxy_service/proxy_dev",
        startup_timeout=10,
        health_check_interval=1.0,
        log_level="debug",
        enable_access_log=True
    )

    # Testing configuration
    test_config = ProxyConfig(
        host="127.0.0.1",
        port=8083,
        binary_path="./proxy_service/proxy_test",
        max_connections=100,
        startup_timeout=5,
        health_check_interval=0.5,
        log_level="info"
    )

    return [
        {'name': 'default', 'config': single_config.to_dict()},
        {'name': 'high_performance', 'config': high_perf_config.to_dict()},
        {'name': 'development', 'config': dev_config.to_dict()},
        {'name': 'testing', 'config': test_config.to_dict()}
    ]


def get_optimized_config_for_use_case(use_case: str) -> ProxyConfig:
    """Get optimized configuration for specific use cases."""

    configs = {
        'scraping': ProxyConfig(
            host="127.0.0.1",
            port=8080,
            max_connections=500,
            connection_timeout=60,
            read_timeout=600,
            health_check_interval=5.0,
            log_level="warning",
            enable_compression=True
        ),

        'testing': ProxyConfig(
            host="127.0.0.1",
            port=8081,
            max_connections=50,
            connection_timeout=10,
            read_timeout=30,
            health_check_interval=1.0,
            log_level="debug",
            enable_access_log=True
        ),

        'production': ProxyConfig(
            host="127.0.0.1",
            port=8080,
            max_connections=2000,
            connection_timeout=30,
            read_timeout=300,
            health_check_interval=3.0,
            log_level="info",
            enable_compression=True,
            max_request_size=52428800  # 50MB
        ),

        'development': ProxyConfig(
            host="127.0.0.1",
            port=8082,
            max_connections=100,
            connection_timeout=15,
            read_timeout=60,
            health_check_interval=2.0,
            log_level="debug",
            enable_access_log=True
        )
    }

    return configs.get(use_case, ProxyConfig())