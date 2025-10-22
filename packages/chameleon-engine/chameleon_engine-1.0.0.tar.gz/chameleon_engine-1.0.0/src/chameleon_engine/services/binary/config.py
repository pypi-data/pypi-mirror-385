"""
Binary configuration and utilities.

This module provides configuration management for custom browser binaries
including download sources, validation rules, and storage preferences.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BinaryType(Enum):
    """Types of browser binaries."""
    CHROMIUM = "chromium"
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"  # Limited support


class Platform(Enum):
    """Supported platforms."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


class Architecture(Enum):
    """Supported architectures."""
    X64 = "x64"
    X86 = "x86"
    ARM64 = "arm64"


@dataclass
class BinarySource:
    """Source configuration for downloading binaries."""

    name: str
    base_url: str
    platform_mapping: Dict[str, str]  # Maps platform+arch to URL patterns
    version_pattern: str  # Pattern to extract version from URLs
    checksum_type: str = "sha256"  # sha256, md5, sha1
    headers: Optional[Dict[str, str]] = None

    def get_download_url(self, platform: Platform, arch: Architecture, version: str) -> str:
        """Get download URL for specific platform, architecture, and version."""
        platform_key = f"{platform.value}_{arch.value}"
        pattern = self.platform_mapping.get(platform_key)

        if not pattern:
            raise ValueError(f"Platform {platform_key} not supported by {self.name}")

        return pattern.format(version=version)


@dataclass
class BinaryConfig:
    """Configuration for binary management."""

    # Storage configuration
    storage_directory: str = "./binaries"
    cache_directory: str = "./cache"
    temp_directory: str = "./temp"

    # Download configuration
    max_concurrent_downloads: int = 3
    download_timeout: int = 300  # 5 minutes
    chunk_size: int = 8192  # 8KB chunks
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Validation configuration
    verify_checksums: bool = True
    verify_signature: bool = False  # Requires GPG
    scan_malware: bool = False  # Requires virus scanner

    # Cleanup configuration
    auto_cleanup: bool = True
    max_storage_gb: int = 10  # Maximum storage in GB
    keep_versions: int = 3  # Number of versions to keep per binary

    # Performance configuration
    extract_timeout: int = 120  # 2 minutes
    installation_timeout: int = 300  # 5 minutes

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Ensure directories exist
        Path(self.storage_directory).mkdir(parents=True, exist_ok=True)
        Path(self.cache_directory).mkdir(parents=True, exist_ok=True)
        Path(self.temp_directory).mkdir(parents=True, exist_ok=True)

        # Validate numeric values
        if self.max_concurrent_downloads <= 0:
            raise ValueError("max_concurrent_downloads must be positive")

        if self.download_timeout <= 0:
            raise ValueError("download_timeout must be positive")

        if self.max_storage_gb <= 0:
            raise ValueError("max_storage_gb must be positive")

        if self.keep_versions <= 0:
            raise ValueError("keep_versions must be positive")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BinaryConfig":
        """Create from dictionary."""
        return cls(**data)


class BinaryConfigManager:
    """Manager for binary configurations."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or "binary_config.json"
        self.configs: Dict[str, BinaryConfig] = {}
        self.sources: Dict[str, BinarySource] = {}

        # Load configurations
        self._load_configurations()
        self._load_default_sources()

    def _load_configurations(self):
        """Load configurations from file."""
        config_path = Path(self.config_file)

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)

                # Load binary configurations
                for name, config_data in data.get('configs', {}).items():
                    self.configs[name] = BinaryConfig.from_dict(config_data)

                # Load binary sources
                for name, source_data in data.get('sources', {}).items():
                    self.sources[name] = BinarySource(**source_data)

                logger.info(f"Loaded {len(self.configs)} configurations and {len(self.sources)} sources from {self.config_file}")

            except Exception as e:
                logger.error(f"Failed to load binary configurations: {str(e)}")
                self._create_default_config()
        else:
            logger.info(f"Configuration file {self.config_file} not found, creating default")
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration."""
        default_config = BinaryConfig()
        self.add_config("default", default_config)
        self.save_configurations()

    def _load_default_sources(self):
        """Load default binary sources."""
        if not self.sources:
            # Chromium sources
            self.sources["chromium"] = BinarySource(
                name="chromium",
                base_url="https://commondatastorage.googleapis.com/chromium-browser-snapshots",
                platform_mapping={
                    "windows_x64": "Win_x64/{version}/chrome-win.zip",
                    "windows_x86": "Win/{version}/chrome-win.zip",
                    "linux_x64": "Linux_x64/{version}/chrome-linux.zip",
                    "linux_arm64": "Linux_arm64/{version}/chrome-linux.zip",
                    "macos_x64": "Mac/{version}/chrome-mac.zip",
                    "macos_arm64": "Mac_Arm64/{version}/chrome-mac-arm64.zip"
                },
                version_pattern=r"(\d+)",
                checksum_type="sha256"
            )

            # Chrome sources (requires authentication)
            self.sources["chrome"] = BinarySource(
                name="chrome",
                base_url="https://googlechromelabs.github.io/chrome-for-testing",
                platform_mapping={
                    "windows_x64": "win64/chrome-win.zip",
                    "windows_x86": "win32/chrome-win.zip",
                    "linux_x64": "linux64/chrome-linux.zip",
                    "macos_x64": "mac-x64/chrome-mac-x64.zip",
                    "macos_arm64": "mac-arm64/chrome-mac-arm64.zip"
                },
                version_pattern=r"(\d+\.\d+\.\d+\.\d+)",
                checksum_type="sha256"
            )

            # Firefox sources
            self.sources["firefox"] = BinarySource(
                name="firefox",
                base_url="https://download.mozilla.org",
                platform_mapping={
                    "windows_x64": "firefox-{version}.win64.zip",
                    "windows_x86": "firefox-{version}.win32.zip",
                    "linux_x64": "firefox-{version}.tar.xz",
                    "linux_arm64": "firefox-{version}.tar.xz",
                    "macos_x64": "Firefox {version}.dmg",
                    "macos_arm64": "Firefox {version}.dmg"
                },
                version_pattern=r"(\d+\.\d+)",
                checksum_type="sha256"
            )

    def add_config(self, name: str, config: BinaryConfig):
        """Add or update a configuration."""
        self.configs[name] = config
        logger.info(f"Added/updated binary configuration: {name}")

    def get_config(self, name: str) -> Optional[BinaryConfig]:
        """Get a configuration by name."""
        return self.configs.get(name)

    def get_all_configs(self) -> Dict[str, BinaryConfig]:
        """Get all configurations."""
        return self.configs.copy()

    def remove_config(self, name: str) -> bool:
        """Remove a configuration."""
        if name in self.configs:
            del self.configs[name]
            logger.info(f"Removed binary configuration: {name}")
            return True
        return False

    def add_source(self, name: str, source: BinarySource):
        """Add or update a binary source."""
        self.sources[name] = source
        logger.info(f"Added/updated binary source: {name}")

    def get_source(self, name: str) -> Optional[BinarySource]:
        """Get a binary source by name."""
        return self.sources.get(name)

    def get_all_sources(self) -> Dict[str, BinarySource]:
        """Get all binary sources."""
        return self.sources.copy()

    def save_configurations(self):
        """Save configurations to file."""
        try:
            # Create directory if it doesn't exist
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare data for saving
            data = {
                "configs": {
                    name: config.to_dict()
                    for name, config in self.configs.items()
                },
                "sources": {
                    name: {
                        "name": source.name,
                        "base_url": source.base_url,
                        "platform_mapping": source.platform_mapping,
                        "version_pattern": source.version_pattern,
                        "checksum_type": source.checksum_type,
                        "headers": source.headers
                    }
                    for name, source in self.sources.items()
                },
                "version": "1.0",
                "last_updated": self._get_timestamp()
            }

            # Save to file
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.configs)} configurations and {len(self.sources)} sources to {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to save binary configurations: {str(e)}")

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def get_platform_info(self) -> tuple[Platform, Architecture]:
        """Get current platform and architecture information."""
        import platform

        # Determine platform
        system = platform.system().lower()
        if system == "windows":
            current_platform = Platform.WINDOWS
        elif system == "darwin":
            current_platform = Platform.MACOS
        elif system == "linux":
            current_platform = Platform.LINUX
        else:
            raise ValueError(f"Unsupported platform: {system}")

        # Determine architecture
        machine = platform.machine().lower()
        if machine in ["x86_64", "amd64"]:
            arch = Architecture.X64
        elif machine in ["i386", "i686", "x86"]:
            arch = Architecture.X86
        elif machine in ["arm64", "aarch64"]:
            arch = Architecture.ARM64
        else:
            # Try to get architecture from uname
            try:
                import uname_libc
                uname_info = uname_libc.uname()
                if "arm64" in uname_info.machine.lower():
                    arch = Architecture.ARM64
                else:
                    arch = Architecture.X64  # Default fallback
            except ImportError:
                arch = Architecture.X64  # Default fallback

        return current_platform, arch

    def get_available_sources_for_binary_type(self, binary_type: BinaryType) -> List[BinarySource]:
        """Get available sources for a specific binary type."""
        available_sources = []

        # Direct match
        if binary_type.value in self.sources:
            available_sources.append(self.sources[binary_type.value])

        # Additional mappings
        type_mappings = {
            BinaryType.CHROME: ["chrome", "chromium"],
            BinaryType.CHROMIUM: ["chromium", "chrome"],
            BinaryType.FIREFOX: ["firefox"],
            BinaryType.EDGE: ["edge"],  # Would need to be added to sources
            BinaryType.SAFARI: ["safari"]  # Limited support
        }

        for source_name in type_mappings.get(binary_type, []):
            if source_name in self.sources:
                available_sources.append(self.sources[source_name])

        return available_sources

    def validate_config(self, config: BinaryConfig) -> List[str]:
        """
        Validate a configuration and return any issues.

        Args:
            config: Configuration to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Check directories
        try:
            storage_path = Path(config.storage_directory)
            if not storage_path.exists():
                storage_path.mkdir(parents=True, exist_ok=True)

            # Check write permissions
            test_file = storage_path / ".write_test"
            test_file.touch()
            test_file.unlink()

        except Exception as e:
            issues.append(f"Cannot write to storage directory: {str(e)}")

        # Check cache directory
        try:
            cache_path = Path(config.cache_directory)
            if not cache_path.exists():
                cache_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot access cache directory: {str(e)}")

        # Check temp directory
        try:
            temp_path = Path(config.temp_directory)
            if not temp_path.exists():
                temp_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot access temp directory: {str(e)}")

        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(config.storage_directory)
            free_gb = free // (1024**3)

            if free_gb < 1:  # Less than 1GB free
                issues.append(f"Low disk space: {free_gb}GB available")

        except Exception:
            issues.append("Cannot check disk space")

        return issues

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of all configurations."""
        summary = {
            'total_configs': len(self.configs),
            'total_sources': len(self.sources),
            'config_names': list(self.configs.keys()),
            'source_names': list(self.sources.keys()),
            'config_file': self.config_file,
            'configs': {},
            'platform_info': {}
        }

        # Get platform info
        try:
            platform, arch = self.get_platform_info()
            summary['platform_info'] = {
                'platform': platform.value,
                'architecture': arch.value
            }
        except Exception as e:
            summary['platform_info'] = {'error': str(e)}

        # Validate configurations
        for name, config in self.configs.items():
            issues = self.validate_config(config)
            summary['configs'][name] = {
                'storage_directory': config.storage_directory,
                'max_storage_gb': config.max_storage_gb,
                'is_valid': len(issues) == 0,
                'issues': issues
            }

        return summary


def load_environment_config() -> Dict[str, Any]:
    """Load binary configuration from environment variables."""
    config = {}

    # Storage configuration
    if os.getenv('BINARY_STORAGE_DIR'):
        config['storage_directory'] = os.getenv('BINARY_STORAGE_DIR')
    if os.getenv('BINARY_CACHE_DIR'):
        config['cache_directory'] = os.getenv('BINARY_CACHE_DIR')
    if os.getenv('BINARY_TEMP_DIR'):
        config['temp_directory'] = os.getenv('BINARY_TEMP_DIR')

    # Download configuration
    if os.getenv('BINARY_MAX_DOWNLOADS'):
        config['max_concurrent_downloads'] = int(os.getenv('BINARY_MAX_DOWNLOADS'))
    if os.getenv('BINARY_DOWNLOAD_TIMEOUT'):
        config['download_timeout'] = int(os.getenv('BINARY_DOWNLOAD_TIMEOUT'))

    # Validation configuration
    if os.getenv('BINARY_VERIFY_CHECKSUMS'):
        config['verify_checksums'] = os.getenv('BINARY_VERIFY_CHECKSUMS').lower() == 'true'
    if os.getenv('BINARY_SCAN_MALWARE'):
        config['scan_malware'] = os.getenv('BINARY_SCAN_MALWARE').lower() == 'true'

    # Cleanup configuration
    if os.getenv('BINARY_MAX_STORAGE_GB'):
        config['max_storage_gb'] = int(os.getenv('BINARY_MAX_STORAGE_GB'))
    if os.getenv('BINARY_KEEP_VERSIONS'):
        config['keep_versions'] = int(os.getenv('BINARY_KEEP_VERSIONS'))

    return config


def create_optimized_config_for_use_case(use_case: str) -> BinaryConfig:
    """Get optimized configuration for specific use cases."""

    configs = {
        'development': BinaryConfig(
            storage_directory="./dev_binaries",
            cache_directory="./dev_cache",
            temp_directory="./dev_temp",
            max_concurrent_downloads=2,
            download_timeout=180,  # 3 minutes
            verify_checksums=False,  # Skip for speed
            auto_cleanup=False,  # Keep all versions for testing
            max_storage_gb=5,
            keep_versions=5
        ),

        'testing': BinaryConfig(
            storage_directory="./test_binaries",
            cache_directory="./test_cache",
            temp_directory="./test_temp",
            max_concurrent_downloads=3,
            download_timeout=240,  # 4 minutes
            verify_checksums=True,
            auto_cleanup=True,
            max_storage_gb=3,
            keep_versions=2
        ),

        'production': BinaryConfig(
            storage_directory="./prod_binaries",
            cache_directory="./prod_cache",
            temp_directory="./prod_temp",
            max_concurrent_downloads=5,
            download_timeout=600,  # 10 minutes
            chunk_size=16384,  # 16KB chunks for faster download
            verify_checksums=True,
            verify_signature=True,
            scan_malware=True,
            auto_cleanup=True,
            max_storage_gb=20,
            keep_versions=2
        ),

        'minimal': BinaryConfig(
            storage_directory="./binaries",
            cache_directory="./cache",
            temp_directory="./temp",
            max_concurrent_downloads=1,
            download_timeout=120,  # 2 minutes
            verify_checksums=True,
            auto_cleanup=True,
            max_storage_gb=2,
            keep_versions=1
        )
    }

    return configs.get(use_case, BinaryConfig())