"""
Advanced Network Obfuscator for Chameleon Engine.

This module provides comprehensive network-level obfuscation capabilities
integrating TLS fingerprinting, HTTP/2 rewriting, and proxy management.
"""

import asyncio
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from pathlib import Path

from ..core.profiles import BrowserProfile, TLSFingerprint, HTTP2Settings
from ..services.proxy.manager import GoProxyManager
from ..services.proxy.config import ProxyConfig
from ..services.fingerprint.client import FingerprintServiceClient
from ..services.binary.manager import CustomBinaryManager, BinaryType

logger = logging.getLogger(__name__)


class ObfuscationStatus(Enum):
    """Network obfuscation status values."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    RECONFIGURING = "reconfiguring"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ObfuscationConfig:
    """Configuration for network obfuscation."""

    # Proxy configuration
    proxy_enabled: bool = True
    proxy_port: int = 8080
    proxy_host: str = "127.0.0.1"
    proxy_startup_timeout: int = 30
    proxy_health_check_interval: float = 5.0

    # TLS configuration
    tls_obfuscation_enabled: bool = True
    tls_fingerprint_rotation_enabled: bool = True
    tls_fingerprint_rotation_interval: int = 3600  # 1 hour

    # HTTP/2 configuration
    http2_obfuscation_enabled: bool = True
    http2_settings_randomization: bool = True

    # Fingerprint service configuration
    fingerprint_service_url: str = "http://localhost:8000"
    fingerprint_cache_enabled: bool = True
    fingerprint_cache_ttl: int = 1800  # 30 minutes

    # Performance configuration
    connection_pool_size: int = 100
    max_concurrent_requests: int = 50
    request_timeout: int = 30

    # Monitoring configuration
    metrics_enabled: bool = True
    health_check_enabled: bool = True

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.proxy_port < 1024 or self.proxy_port > 65535:
            raise ValueError(f"Proxy port must be between 1024 and 65535, got {self.proxy_port}")

        if self.proxy_startup_timeout <= 0:
            raise ValueError(f"Proxy startup timeout must be positive, got {self.proxy_startup_timeout}")

        if self.tls_fingerprint_rotation_interval <= 0:
            raise ValueError(f"TLS fingerprint rotation interval must be positive, got {self.tls_fingerprint_rotation_interval}")


@dataclass
class ObfuscationMetrics:
    """Metrics for network obfuscation performance."""
    start_time: Optional[datetime] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    active_connections: int = 0
    proxy_uptime: float = 0.0
    tls_fingerprints_rotated: int = 0
    last_health_check: Optional[datetime] = None
    average_response_time: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate request success rate."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def uptime_seconds(self) -> float:
        """Calculate uptime in seconds."""
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()


class NetworkObfuscator:
    """
    Advanced Network Obfuscator for Chameleon Engine.

    This class provides comprehensive network-level obfuscation by integrating
    proxy management, TLS fingerprinting, HTTP/2 rewriting, and fingerprint
    service integration.
    """

    def __init__(self, config: Optional[ObfuscationConfig] = None):
        """
        Initialize the Network Obfuscator.

        Args:
            config: Obfuscation configuration (default: optimized config)
        """
        self.config = config or ObfuscationConfig()
        self.status = ObfuscationStatus.STOPPED

        # Component managers
        self.proxy_manager: Optional[GoProxyManager] = None
        self.fingerprint_client: Optional[FingerprintServiceClient] = None
        self.binary_manager: Optional[CustomBinaryManager] = None

        # Current state
        self.current_profile: Optional[BrowserProfile] = None
        self.current_proxy_url: Optional[str] = None
        self.active_tls_fingerprint: Optional[TLSFingerprint] = None

        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        self._tls_rotation_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None

        # Metrics and monitoring
        self.metrics = ObfuscationMetrics()
        self._request_times: List[float] = []
        self._max_request_times = 100  # Keep last 100 request times

        # Event callbacks
        self._status_callbacks: List[Callable[[ObfuscationStatus], None]] = []
        self._error_callbacks: List[Callable[[Exception], None]] = []

        logger.info("Network Obfuscator initialized")

    async def start(self, profile: Optional[BrowserProfile] = None) -> str:
        """
        Start the network obfuscation with given profile.

        Args:
            profile: Browser profile to use for obfuscation

        Returns:
            Proxy URL for browser configuration

        Raises:
            RuntimeError: If obfuscator is already running
            Exception: If startup fails
        """
        if self.status in [ObfuscationStatus.STARTING, ObfuscationStatus.RUNNING]:
            raise RuntimeError(f"Network obfuscator is already {self.status.value}")

        try:
            await self._set_status(ObfuscationStatus.STARTING)
            self.metrics.start_time = datetime.now()

            # Generate or use provided profile
            if not profile:
                profile = await self._generate_fingerprint_profile()

            self.current_profile = profile

            # Initialize component managers
            await self._initialize_managers()

            # Start proxy service
            proxy_url = await self._start_proxy_service()
            self.current_proxy_url = proxy_url

            # Configure proxy with profile
            await self._configure_proxy_with_profile()

            # Start background tasks
            await self._start_background_tasks()

            await self._set_status(ObfuscationStatus.RUNNING)

            logger.info(f"Network obfuscation started successfully at {proxy_url}")
            return proxy_url

        except Exception as e:
            await self._set_status(ObfuscationStatus.ERROR)
            await self._notify_error(e)
            logger.error(f"Failed to start network obfuscation: {str(e)}")
            raise

    async def stop(self):
        """Stop the network obfuscation and cleanup resources."""
        if self.status == ObfuscationStatus.STOPPED:
            return

        try:
            await self._set_status(ObfuscationStatus.STOPPING)

            # Stop background tasks
            await self._stop_background_tasks()

            # Stop proxy service
            if self.proxy_manager:
                await self.proxy_manager.stop()
                self.proxy_manager = None

            # Close fingerprint client
            if self.fingerprint_client:
                await self.fingerprint_client.close()
                self.fingerprint_client = None

            # Stop binary manager
            if self.binary_manager:
                await self.binary_manager.stop()
                self.binary_manager = None

            # Reset state
            self.current_profile = None
            self.current_proxy_url = None
            self.active_tls_fingerprint = None

            await self._set_status(ObfuscationStatus.STOPPED)

            logger.info("Network obfuscation stopped successfully")

        except Exception as e:
            await self._set_status(ObfuscationStatus.ERROR)
            await self._notify_error(e)
            logger.error(f"Error stopping network obfuscation: {str(e)}")

    async def reconfigure(self, new_profile: BrowserProfile) -> str:
        """
        Reconfigure obfuscation with a new profile.

        Args:
            new_profile: New browser profile to use

        Returns:
            New proxy URL
        """
        if self.status != ObfuscationStatus.RUNNING:
            raise RuntimeError(f"Cannot reconfigure obfuscator in {self.status.value} state")

        try:
            await self._set_status(ObfuscationStatus.RECONFIGURING)

            # Update profile
            self.current_profile = new_profile

            # Reconfigure proxy with new profile
            await self._configure_proxy_with_profile()

            await self._set_status(ObfuscationStatus.RUNNING)

            logger.info("Network obfuscation reconfigured successfully")
            return self.current_proxy_url or ""

        except Exception as e:
            await self._set_status(ObfuscationStatus.ERROR)
            await self._notify_error(e)
            logger.error(f"Failed to reconfigure network obfuscation: {str(e)}")
            raise

    async def get_proxy_url(self) -> Optional[str]:
        """Get the current proxy URL."""
        return self.current_proxy_url

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information."""
        status_info = {
            "status": self.status.value,
            "uptime_seconds": self.metrics.uptime_seconds,
            "proxy_url": self.current_proxy_url,
            "profile_id": self.current_profile.profile_id if self.current_profile else None,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": self.metrics.success_rate,
                "active_connections": self.metrics.active_connections,
                "average_response_time": self.metrics.average_response_time,
                "tls_fingerprints_rotated": self.metrics.tls_fingerprints_rotated
            },
            "components": {
                "proxy_manager": self.proxy_manager is not None,
                "fingerprint_client": self.fingerprint_client is not None,
                "binary_manager": self.binary_manager is not None
            }
        }

        # Add component-specific status
        if self.proxy_manager:
            try:
                proxy_status = await self.proxy_manager.get_status()
                status_info["proxy_status"] = proxy_status
            except Exception as e:
                status_info["proxy_status"] = {"error": str(e)}

        if self.fingerprint_client:
            try:
                service_status = await self.fingerprint_client.health_check()
                status_info["fingerprint_service_status"] = service_status
            except Exception as e:
                status_info["fingerprint_service_status"] = {"error": str(e)}

        return status_info

    async def rotate_tls_fingerprint(self) -> bool:
        """
        Manually rotate TLS fingerprint.

        Returns:
            True if rotation was successful
        """
        if not self.current_profile or not self.proxy_manager:
            return False

        try:
            # Generate new TLS fingerprint
            new_fingerprint = await self._generate_tls_fingerprint()

            if new_fingerprint:
                self.active_tls_fingerprint = new_fingerprint
                self.current_profile.tls_fingerprint = new_fingerprint

                # Update proxy configuration
                await self._configure_proxy_with_profile()

                self.metrics.tls_fingerprints_rotated += 1
                logger.info("TLS fingerprint rotated successfully")
                return True

        except Exception as e:
            await self._notify_error(e)
            logger.error(f"Failed to rotate TLS fingerprint: {str(e)}")

        return False

    def add_status_callback(self, callback: Callable[[ObfuscationStatus], None]):
        """Add callback for status changes."""
        self._status_callbacks.append(callback)

    def add_error_callback(self, callback: Callable[[Exception], None]):
        """Add callback for error notifications."""
        self._error_callbacks.append(callback)

    async def _initialize_managers(self):
        """Initialize component managers."""
        # Initialize binary manager
        self.binary_manager = CustomBinaryManager()
        await self.binary_manager.start()

        # Initialize fingerprint client
        self.fingerprint_client = FingerprintServiceClient(
            base_url=self.config.fingerprint_service_url
        )

        # Initialize proxy manager with custom configuration
        proxy_config = ProxyConfig(
            host=self.config.proxy_host,
            port=self.config.proxy_port,
            startup_timeout=self.config.proxy_startup_timeout,
            health_check_interval=self.config.proxy_health_check_interval
        )

        self.proxy_manager = GoProxyManager(proxy_config=proxy_config)

    async def _generate_fingerprint_profile(self) -> BrowserProfile:
        """Generate a fingerprint profile from the service."""
        try:
            from ..services.fingerprint.models import FingerprintRequest, BrowserType, OperatingSystem

            request = FingerprintRequest(
                browser=BrowserType.CHROME,
                os=OperatingSystem.WINDOWS,
                include_advanced_fingerprinting=True
            )

            response = await self.fingerprint_client.get_fingerprint(request)
            return response.browser_profile

        except Exception as e:
            logger.error(f"Failed to generate fingerprint profile: {str(e)}")
            # Fallback to basic profile
            return self._create_fallback_profile()

    async def _generate_tls_fingerprint(self) -> Optional[TLSFingerprint]:
        """Generate a new TLS fingerprint."""
        try:
            # For now, return a variation of the current fingerprint
            if self.current_profile and self.current_profile.tls_fingerprint:
                current = self.current_profile.tls_fingerprint
                return TLSFingerprint(
                    id=current.id + "_rotated",
                    utls_config=current.utls_config.copy(),
                    ja3_hash=None,  # Will be generated by proxy
                    cipher_suites=current.cipher_suites.copy() if current.cipher_suites else None,
                    extensions=current.extensions.copy() if current.extensions else None,
                    version=current.version
                )
        except Exception as e:
            logger.error(f"Failed to generate TLS fingerprint: {str(e)}")

        return None

    def _create_fallback_profile(self) -> BrowserProfile:
        """Create a fallback profile when service is unavailable."""
        from ..core.profiles import ScreenResolution, NavigatorProperties, HTTPHeaders

        return BrowserProfile(
            profile_id="fallback_profile",
            browser_type="chrome",
            operating_system="windows",
            version="120.0.0.0",
            screen=ScreenResolution(width=1920, height=1080),
            navigator=NavigatorProperties(
                hardware_concurrency=8,
                device_memory=8.0,
                platform="Win32",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ),
            headers=HTTPHeaders(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ),
            tls_fingerprint=TLSFingerprint(
                id="chrome_120_windows",
                utls_config={}
            ),
            http2_settings=HTTP2Settings()
        )

    async def _start_proxy_service(self) -> str:
        """Start the Go proxy service."""
        if not self.proxy_manager:
            raise RuntimeError("Proxy manager not initialized")

        proxy_url = await self.proxy_manager.start()
        logger.info(f"Proxy service started at {proxy_url}")
        return proxy_url

    async def _configure_proxy_with_profile(self):
        """Configure proxy with current browser profile."""
        if not self.proxy_manager or not self.current_profile:
            raise RuntimeError("Proxy manager or profile not available")

        success = await self.proxy_manager.set_profile(self.current_profile)
        if not success:
            raise RuntimeError("Failed to configure proxy with browser profile")

        logger.info(f"Proxy configured with profile {self.current_profile.profile_id}")

    async def _start_background_tasks(self):
        """Start background monitoring and maintenance tasks."""
        if self.config.health_check_enabled:
            self._health_check_task = asyncio.create_task(self._health_check_loop())

        if self.config.tls_fingerprint_rotation_enabled:
            self._tls_rotation_task = asyncio.create_task(self._tls_rotation_loop())

        if self.config.metrics_enabled:
            self._metrics_task = asyncio.create_task(self._metrics_update_loop())

    async def _stop_background_tasks(self):
        """Stop background tasks."""
        tasks = [
            self._health_check_task,
            self._tls_rotation_task,
            self._metrics_task
        ]

        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self._health_check_task = None
        self._tls_rotation_task = None
        self._metrics_task = None

    async def _health_check_loop(self):
        """Background health check loop."""
        while self.status == ObfuscationStatus.RUNNING:
            try:
                # Check proxy health
                if self.proxy_manager:
                    proxy_status = await self.proxy_manager.get_status()
                    if proxy_status.get('status') != 'running':
                        logger.warning("Proxy health check failed")
                        await self._handle_proxy_failure()

                # Check fingerprint service health
                if self.fingerprint_client:
                    service_health = await self.fingerprint_client.health_check()
                    if not service_health.get('healthy', False):
                        logger.warning("Fingerprint service health check failed")

                self.metrics.last_health_check = datetime.now()

            except Exception as e:
                logger.error(f"Health check error: {str(e)}")
                await self._notify_error(e)

            await asyncio.sleep(self.config.proxy_health_check_interval)

    async def _tls_rotation_loop(self):
        """Background TLS fingerprint rotation loop."""
        while self.status == ObfuscationStatus.RUNNING:
            try:
                await asyncio.sleep(self.config.tls_fingerprint_rotation_interval)

                if self.status == ObfuscationStatus.RUNNING:
                    await self.rotate_tls_fingerprint()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"TLS rotation error: {str(e)}")
                await self._notify_error(e)

    async def _metrics_update_loop(self):
        """Background metrics update loop."""
        while self.status == ObfuscationStatus.RUNNING:
            try:
                # Update average response time
                if self._request_times:
                    self.metrics.average_response_time = sum(self._request_times) / len(self._request_times)

                # Update proxy uptime
                if self.proxy_manager and self.metrics.start_time:
                    self.metrics.proxy_uptime = self.metrics.uptime_seconds

                await asyncio.sleep(60)  # Update every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics update error: {str(e)}")

    async def _handle_proxy_failure(self):
        """Handle proxy failure."""
        logger.error("Proxy failure detected, attempting recovery")

        try:
            # Stop current proxy
            if self.proxy_manager:
                await self.proxy_manager.stop()

            # Restart proxy
            if self.current_profile:
                await self._start_proxy_service()
                await self._configure_proxy_with_profile()
                logger.info("Proxy recovery successful")

        except Exception as e:
            logger.error(f"Proxy recovery failed: {str(e)}")
            await self._notify_error(e)

    async def _set_status(self, status: ObfuscationStatus):
        """Set obfuscation status and notify callbacks."""
        old_status = self.status
        self.status = status

        if old_status != status:
            logger.info(f"Network obfuscation status changed: {old_status.value} -> {status.value}")

            for callback in self._status_callbacks:
                try:
                    callback(status)
                except Exception as e:
                    logger.error(f"Status callback error: {str(e)}")

    async def _notify_error(self, error: Exception):
        """Notify error callbacks."""
        for callback in self._error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error callback error: {str(e)}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()