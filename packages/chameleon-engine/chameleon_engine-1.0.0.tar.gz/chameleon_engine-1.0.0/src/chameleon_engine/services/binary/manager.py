"""
Custom binary manager.

This module provides comprehensive management of custom browser binaries
including downloading, validation, installation, and lifecycle management.
"""

import asyncio
import json
import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

from .config import BinaryConfig, BinaryConfigManager, BinaryType, Platform, Architecture, get_optimized_config_for_use_case
from .downloader import BinaryDownloader, DownloadTask, DownloadProgress, DownloadStatus
from .validator import BinaryValidator, ValidationResult, ValidationStatus

logger = logging.getLogger(__name__)


class BinaryStatus(Enum):
    """Binary status values."""
    UNKNOWN = "unknown"
    DOWNLOADING = "downloading"
    VALIDATING = "validating"
    INSTALLING = "installing"
    INSTALLED = "installed"
    OUTDATED = "outdated"
    CORRUPTED = "corrupted"
    ERROR = "error"


@dataclass
class BinaryInfo:
    """Information about a managed binary."""
    binary_type: BinaryType
    version: str
    platform: Platform
    architecture: Architecture
    status: BinaryStatus
    install_path: Path
    executable_path: Path
    source_url: Optional[str] = None
    checksum: Optional[str] = None
    size: int = 0
    install_date: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if data['install_date']:
            data['install_date'] = data['install_date'].isoformat()
        if data['last_used']:
            data['last_used'] = data['last_used'].isoformat()
        # Convert Path objects to strings
        data['install_path'] = str(data['install_path'])
        data['executable_path'] = str(data['executable_path'])
        # Convert enums to strings
        data['binary_type'] = data['binary_type'].value
        data['platform'] = data['platform'].value
        data['architecture'] = data['architecture'].value
        data['status'] = data['status'].value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BinaryInfo":
        """Create from dictionary."""
        # Convert ISO strings back to datetime objects
        if data.get('install_date'):
            data['install_date'] = datetime.fromisoformat(data['install_date'])
        if data.get('last_used'):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        # Convert strings back to Path objects
        data['install_path'] = Path(data['install_path'])
        data['executable_path'] = Path(data['executable_path'])
        # Convert strings back to enums
        data['binary_type'] = BinaryType(data['binary_type'])
        data['platform'] = Platform(data['platform'])
        data['architecture'] = Architecture(data['architecture'])
        data['status'] = BinaryStatus(data['status'])
        return cls(**data)


class CustomBinaryManager:
    """Manager for custom browser binaries."""

    def __init__(self, config_name: str = "default", config: Optional[BinaryConfig] = None):
        """
        Initialize the binary manager.

        Args:
            config_name: Configuration name
            config: Custom configuration (overrides config_name)
        """
        self.config_manager = BinaryConfigManager()
        self.config = config or self.config_manager.get_config(config_name) or get_optimized_config_for_use_case('production')

        # Initialize components
        self.downloader = BinaryDownloader(self.config.to_dict())
        self.validator = BinaryValidator({
            'verify_checksums': self.config.verify_checksums,
            'verify_signature': self.config.verify_signature,
            'scan_malware': self.config.scan_malware,
            'test_execution': True
        })

        # Get current platform info
        self.current_platform, self.current_arch = self.config_manager.get_platform_info()

        # Binary registry
        self.binaries: Dict[str, BinaryInfo] = {}
        self.registry_file = Path(self.config.storage_directory) / "binary_registry.json"

        # Load existing registry
        self._load_registry()

        # Start background tasks
        self._cleanup_task = None
        self._running = False

    async def start(self):
        """Start the binary manager and background tasks."""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._background_cleanup())
        logger.info("Custom binary manager started")

    async def stop(self):
        """Stop the binary manager and background tasks."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Custom binary manager stopped")

    async def _background_cleanup(self):
        """Background task for cleanup operations."""
        while self._running:
            try:
                # Run cleanup every hour
                await asyncio.sleep(3600)

                if self._running:
                    await self._perform_cleanup()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background cleanup error: {str(e)}")

    async def install_binary(
        self,
        binary_type: BinaryType,
        version: Optional[str] = None,
        platform: Optional[Platform] = None,
        architecture: Optional[Architecture] = None,
        source_url: Optional[str] = None,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> BinaryInfo:
        """
        Install a browser binary.

        Args:
            binary_type: Type of binary to install
            version: Specific version to install (latest if not provided)
            platform: Target platform (default: current)
            architecture: Target architecture (default: current)
            source_url: Custom download URL (auto-detected if not provided)
            progress_callback: Optional progress callback

        Returns:
            BinaryInfo for the installed binary
        """
        # Use current platform/arch if not specified
        platform = platform or self.current_platform
        architecture = architecture or self.current_arch

        # Generate binary ID
        binary_id = f"{binary_type.value}_{version or 'latest'}_{platform.value}_{architecture.value}"

        # Check if already installed
        if binary_id in self.binaries:
            existing = self.binaries[binary_id]
            if existing.status == BinaryStatus.INSTALLED:
                logger.info(f"Binary {binary_id} already installed")
                return existing

        # Get download URL if not provided
        if not source_url:
            source_url = await self._get_download_url(binary_type, version, platform, architecture)
            if not source_url:
                raise ValueError(f"No download source found for {binary_type.value} {version or 'latest'} on {platform.value}_{architecture.value}")

        # Create install directory
        install_dir = Path(self.config.storage_directory) / binary_id
        install_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Create binary info
            binary_info = BinaryInfo(
                binary_type=binary_type,
                version=version or "latest",
                platform=platform,
                architecture=architecture,
                status=BinaryStatus.DOWNLOADING,
                install_path=install_dir,
                executable_path=install_dir,  # Will be updated after extraction
                source_url=source_url
            )

            # Update registry
            self.binaries[binary_id] = binary_info
            self._save_registry()

            # Download and extract
            await self._download_and_install(binary_info, progress_callback)

            # Validate binary
            await self._validate_installed_binary(binary_info)

            # Update status
            binary_info.status = BinaryStatus.INSTALLED
            binary_info.install_date = datetime.now()
            self._save_registry()

            logger.info(f"Successfully installed {binary_type.value} {version or 'latest'} for {platform.value}_{architecture.value}")
            return binary_info

        except Exception as e:
            # Update status to error
            if binary_id in self.binaries:
                self.binaries[binary_id].status = BinaryStatus.ERROR
                self._save_registry()

            logger.error(f"Failed to install {binary_type.value} {version or 'latest'}: {str(e)}")
            raise

    async def _download_and_install(
        self,
        binary_info: BinaryInfo,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ):
        """
        Download and install binary.

        Args:
            binary_info: Binary information
            progress_callback: Optional progress callback
        """
        # Create download task
        file_extension = self._get_file_extension(binary_info.binary_type, binary_info.platform)
        download_path = Path(self.config.temp_directory) / f"{binary_info.binary_type.value}_{binary_info.version}{file_extension}"

        download_task = DownloadTask(
            url=binary_info.source_url,
            file_path=download_path,
            timeout=self.config.download_timeout,
            chunk_size=self.config.chunk_size,
            max_retries=self.config.retry_attempts,
            retry_delay=self.config.retry_delay,
            resume=True
        )

        # Download and extract
        progress = await self.downloader.download_and_extract(
            download_task,
            extract_to=binary_info.install_path,
            delete_after_extract=True
        )

        if progress.status != DownloadStatus.COMPLETED:
            raise RuntimeError(f"Download failed: {progress.error}")

        # Find executable path
        executable_path = await self._find_executable(binary_info)
        binary_info.executable_path = executable_path
        binary_info.size = self._calculate_directory_size(binary_info.install_path)

    async def _validate_installed_binary(self, binary_info: BinaryInfo):
        """
        Validate installed binary.

        Args:
            binary_info: Binary information to validate
        """
        binary_info.status = BinaryStatus.VALIDATING

        # Validate executable
        validation_result = await self.validator.validate_binary(
            binary_info.executable_path
        )

        if validation_result.status == ValidationStatus.VALID:
            binary_info.status = BinaryStatus.INSTALLED
        else:
            binary_info.status = BinaryStatus.CORRUPTED
            raise RuntimeError(f"Binary validation failed: {validation_result.message}")

    async def get_binary(
        self,
        binary_type: BinaryType,
        version: Optional[str] = None,
        platform: Optional[Platform] = None,
        architecture: Optional[Architecture] = None,
        auto_install: bool = True
    ) -> BinaryInfo:
        """
        Get an installed binary, optionally installing it if not available.

        Args:
            binary_type: Type of binary
            version: Specific version (latest if not provided)
            platform: Target platform (default: current)
            architecture: Target architecture (default: current)
            auto_install: Whether to auto-install if not found

        Returns:
            BinaryInfo for the requested binary

        Raises:
            ValueError: If binary not found and auto_install is False
        """
        platform = platform or self.current_platform
        architecture = architecture or self.current_arch

        # Generate binary ID
        binary_id = f"{binary_type.value}_{version or 'latest'}_{platform.value}_{architecture.value}"

        # Check if installed
        if binary_id in self.binaries:
            binary_info = self.binaries[binary_id]

            # Update usage stats
            binary_info.last_used = datetime.now()
            binary_info.usage_count += 1
            self._save_registry()

            # Validate if needed
            if binary_info.status == BinaryStatus.INSTALLED:
                if await self._is_binary_valid(binary_info):
                    return binary_info
                else:
                    logger.warning(f"Binary {binary_id} validation failed, marking as corrupted")
                    binary_info.status = BinaryStatus.CORRUPTED
                    self._save_registry()

        # Auto-install if requested
        if auto_install:
            return await self.install_binary(binary_type, version, platform, architecture)
        else:
            raise ValueError(f"Binary {binary_id} not found and auto-install is disabled")

    async def update_binary(
        self,
        binary_type: BinaryType,
        current_version: Optional[str] = None,
        platform: Optional[Platform] = None,
        architecture: Optional[Architecture] = None
    ) -> BinaryInfo:
        """
        Update a binary to the latest version.

        Args:
            binary_type: Type of binary to update
            current_version: Current version to replace
            platform: Target platform
            architecture: Target architecture

        Returns:
            BinaryInfo for the updated binary
        """
        platform = platform or self.current_platform
        architecture = architecture or self.current_arch

        # Find current binary
        if current_version:
            current_binary_id = f"{binary_type.value}_{current_version}_{platform.value}_{architecture.value}"
            if current_binary_id not in self.binaries:
                raise ValueError(f"Current binary {current_binary_id} not found")
        else:
            # Find the latest installed version
            current_binary = await self._find_latest_installed(binary_type, platform, architecture)
            if not current_binary:
                raise ValueError(f"No installed {binary_type.value} found for {platform.value}_{architecture.value}")
            current_binary_id = f"{binary_type.value}_{current_binary.version}_{platform.value}_{architecture.value}"

        # Get latest version
        latest_version = await self._get_latest_version(binary_type, platform, architecture)
        if not latest_version:
            raise ValueError(f"Cannot determine latest version for {binary_type.value}")

        # Check if already latest
        if current_binary and current_binary.version == latest_version:
            logger.info(f"{binary_type.value} is already up to date ({latest_version})")
            return current_binary

        # Install latest version
        new_binary = await self.install_binary(binary_type, latest_version, platform, architecture)

        # Optionally uninstall old version
        if self.config.auto_cleanup:
            await self.uninstall_binary(current_binary_id)

        return new_binary

    async def uninstall_binary(self, binary_id: str) -> bool:
        """
        Uninstall a binary.

        Args:
            binary_id: Binary ID to uninstall

        Returns:
            True if uninstalled successfully
        """
        if binary_id not in self.binaries:
            logger.warning(f"Binary {binary_id} not found in registry")
            return False

        binary_info = self.binaries[binary_id]

        try:
            # Remove files
            if binary_info.install_path.exists():
                shutil.rmtree(binary_info.install_path)

            # Remove from registry
            del self.binaries[binary_id]
            self._save_registry()

            logger.info(f"Successfully uninstalled {binary_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to uninstall {binary_id}: {str(e)}")
            return False

    async def list_binaries(
        self,
        binary_type: Optional[BinaryType] = None,
        status: Optional[BinaryStatus] = None
    ) -> List[BinaryInfo]:
        """
        List managed binaries.

        Args:
            binary_type: Filter by binary type
            status: Filter by status

        Returns:
            List of matching binaries
        """
        binaries = list(self.binaries.values())

        if binary_type:
            binaries = [b for b in binaries if b.binary_type == binary_type]

        if status:
            binaries = [b for b in binaries if b.status == status]

        return binaries

    async def get_binary_info(self, binary_id: str) -> Optional[BinaryInfo]:
        """
        Get information about a specific binary.

        Args:
            binary_id: Binary ID

        Returns:
            BinaryInfo if found
        """
        return self.binaries.get(binary_id)

    async def cleanup_old_versions(self, keep_count: Optional[int] = None) -> int:
        """
        Clean up old versions of binaries.

        Args:
            keep_count: Number of versions to keep (default: from config)

        Returns:
            Number of binaries cleaned up
        """
        keep_count = keep_count or self.config.keep_versions
        cleaned_count = 0

        # Group binaries by type and platform
        groups = {}
        for binary_info in self.binaries.values():
            key = f"{binary_info.binary_type.value}_{binary_info.platform.value}_{binary_info.architecture.value}"
            if key not in groups:
                groups[key] = []
            groups[key].append(binary_info)

        # Clean up each group
        for group_binaries in groups.values():
            # Sort by install date (newest first)
            group_binaries.sort(key=lambda b: b.install_date or datetime.min, reverse=True)

            # Remove excess versions
            for binary_info in group_binaries[keep_count:]:
                if await self.uninstall_binary(f"{binary_info.binary_type.value}_{binary_info.version}_{binary_info.platform.value}_{binary_info.architecture.value}"):
                    cleaned_count += 1

        logger.info(f"Cleaned up {cleaned_count} old binary versions")
        return cleaned_count

    async def _get_download_url(
        self,
        binary_type: BinaryType,
        version: Optional[str],
        platform: Platform,
        architecture: Architecture
    ) -> Optional[str]:
        """
        Get download URL for a binary.

        Args:
            binary_type: Type of binary
            version: Version to download
            platform: Target platform
            architecture: Target architecture

        Returns:
            Download URL if found
        """
        # Get available sources
        sources = self.config_manager.get_available_sources_for_binary_type(binary_type)

        if not sources:
            logger.warning(f"No sources found for {binary_type.value}")
            return None

        # Try each source
        for source in sources:
            try:
                if version:
                    return source.get_download_url(platform, architecture, version)
                else:
                    # Get latest version
                    latest_version = await self._get_latest_version_from_source(source, binary_type, platform, architecture)
                    if latest_version:
                        return source.get_download_url(platform, architecture, latest_version)

            except Exception as e:
                logger.debug(f"Source {source.name} failed: {str(e)}")
                continue

        return None

    async def _get_latest_version(
        self,
        binary_type: BinaryType,
        platform: Platform,
        architecture: Architecture
    ) -> Optional[str]:
        """Get latest version for a binary."""
        sources = self.config_manager.get_available_sources_for_binary_type(binary_type)

        for source in sources:
            try:
                version = await self._get_latest_version_from_source(source, binary_type, platform, architecture)
                if version:
                    return version
            except Exception as e:
                logger.debug(f"Failed to get latest version from {source.name}: {str(e)}")
                continue

        return None

    async def _get_latest_version_from_source(
        self,
        source,
        binary_type: BinaryType,
        platform: Platform,
        architecture: Architecture
    ) -> Optional[str]:
        """
        Get latest version from a specific source.

        This is a simplified implementation. In practice, you would need
        to implement version detection logic for each source.
        """
        # This would typically involve:
        # 1. Fetching version information from the source
        # 2. Parsing version numbers
        # 3. Returning the latest version

        # For now, return a placeholder
        return "latest"

    async def _find_executable(self, binary_info: BinaryInfo) -> Path:
        """
        Find the main executable in the installation directory.

        Args:
            binary_info: Binary information

        Returns:
            Path to executable
        """
        # Common executable names based on binary type
        executable_names = {
            BinaryType.CHROMIUM: ["chrome", "chromium", "chrome.exe", "chromium.exe"],
            BinaryType.CHROME: ["chrome", "chrome.exe"],
            BinaryType.FIREFOX: ["firefox", "firefox.exe"],
            BinaryType.EDGE: ["msedge", "msedge.exe"],
            BinaryType.SAFARI: ["safari"]  # macOS only
        }

        names = executable_names.get(binary_info.binary_type, [])

        # Search in install directory
        for name in names:
            # Direct search
            executable_path = binary_info.install_path / name
            if executable_path.exists() and executable_path.is_file():
                return executable_path

            # Search in subdirectories
            for path in binary_info.install_path.rglob(name):
                if path.is_file():
                    return path

        raise RuntimeError(f"Executable not found for {binary_info.binary_type.value}")

    def _get_file_extension(self, binary_type: BinaryType, platform: Platform) -> str:
        """Get file extension for binary archive."""
        if platform == Platform.WINDOWS:
            return ".zip"
        elif platform == Platform.MACOS:
            return ".zip"
        else:  # Linux
            return ".tar.xz"

    def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of directory."""
        total_size = 0
        try:
            for path in directory.rglob("*"):
                if path.is_file():
                    total_size += path.stat().st_size
        except Exception as e:
            logger.warning(f"Failed to calculate directory size: {str(e)}")
        return total_size

    async def _is_binary_valid(self, binary_info: BinaryInfo) -> bool:
        """Check if binary is still valid."""
        try:
            # Check if executable exists
            if not binary_info.executable_path.exists():
                return False

            # Quick validation
            result = await self.validator.validate_binary(binary_info.executable_path)
            return result.status == ValidationStatus.VALID

        except Exception as e:
            logger.warning(f"Binary validation error: {str(e)}")
            return False

    async def _find_latest_installed(
        self,
        binary_type: BinaryType,
        platform: Platform,
        architecture: Architecture
    ) -> Optional[BinaryInfo]:
        """Find the latest installed binary for given criteria."""
        candidates = [
            b for b in self.binaries.values()
            if b.binary_type == binary_type and
               b.platform == platform and
               b.architecture == architecture and
               b.status == BinaryStatus.INSTALLED
        ]

        if not candidates:
            return None

        # Sort by install date (newest first)
        candidates.sort(key=lambda b: b.install_date or datetime.min, reverse=True)
        return candidates[0]

    async def _perform_cleanup(self):
        """Perform routine cleanup operations."""
        try:
            # Clean up old versions
            await self.cleanup_old_versions()

            # Clean up temp files
            await self.downloader.cleanup_temp_files()

            # Check disk space
            if self.config.max_storage_gb > 0:
                total_size = sum(
                    b.size for b in self.binaries.values()
                    if b.install_path.exists()
                )
                max_size_bytes = self.config.max_storage_gb * 1024 * 1024 * 1024

                if total_size > max_size_bytes:
                    logger.warning(f"Storage usage ({total_size / (1024**3):.1f} GB) exceeds limit ({self.config.max_storage_gb} GB)")
                    # Clean up more aggressively
                    await self.cleanup_old_versions(keep_count=1)

        except Exception as e:
            logger.error(f"Cleanup operation failed: {str(e)}")

    def _load_registry(self):
        """Load binary registry from file."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)

                for binary_id, binary_data in data.get('binaries', {}).items():
                    try:
                        binary_info = BinaryInfo.from_dict(binary_data)
                        self.binaries[binary_id] = binary_info
                    except Exception as e:
                        logger.warning(f"Failed to load binary {binary_id}: {str(e)}")

                logger.info(f"Loaded {len(self.binaries)} binaries from registry")

            except Exception as e:
                logger.error(f"Failed to load binary registry: {str(e)}")
        else:
            logger.info("Binary registry not found, starting fresh")

    def _save_registry(self):
        """Save binary registry to file."""
        try:
            # Ensure directory exists
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)

            # Prepare data
            data = {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'binaries': {
                    binary_id: binary_info.to_dict()
                    for binary_id, binary_info in self.binaries.items()
                }
            }

            # Save to file
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save binary registry: {str(e)}")

    async def get_status(self) -> Dict[str, Any]:
        """Get manager status."""
        total_size = sum(
            b.size for b in self.binaries.values()
            if b.install_path.exists()
        )

        status_counts = {}
        for binary in self.binaries.values():
            status = binary.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            'total_binaries': len(self.binaries),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'status_counts': status_counts,
            'storage_directory': self.config.storage_directory,
            'platform': self.current_platform.value,
            'architecture': self.current_arch.value,
            'running': self._running
        }