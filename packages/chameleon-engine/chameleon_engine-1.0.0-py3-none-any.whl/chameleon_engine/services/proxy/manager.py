"""
Go Proxy Manager for network-level obfuscation.

This module provides a Python client for managing the Go-based network obfuscation
proxy that handles TLS fingerprinting and HTTP/2 rewriting.
"""

import asyncio
import subprocess
import json
import logging
import time
import signal
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import httpx

from ...core.profiles import BrowserProfile

logger = logging.getLogger(__name__)


class GoProxyManagerError(Exception):
    """Base exception for Go proxy manager errors."""
    pass


class GoProxyNotAvailableError(GoProxyManagerError):
    """Exception raised when the Go proxy binary is not available."""
    pass


class GoProxyManager:
    """
    Manager for the Go-based network obfuscation proxy.

    This manager handles proxy lifecycle management, profile configuration,
    and health monitoring for the Go proxy service.
    """

    def __init__(
        self,
        proxy_binary_path: str = "./proxy_service/proxy",
        proxy_host: str = "127.0.0.1",
        proxy_port: int = 8080,
        startup_timeout: int = 30,
        health_check_interval: float = 5.0,
        max_startup_attempts: int = 3
    ):
        """
        Initialize the Go proxy manager.

        Args:
            proxy_binary_path: Path to the Go proxy binary
            proxy_host: Host for the proxy server
            proxy_port: Port for the proxy server
            startup_timeout: Timeout for proxy startup in seconds
            health_check_interval: Interval between health checks in seconds
            max_startup_attempts: Maximum attempts to start the proxy
        """
        self.proxy_binary_path = Path(proxy_binary_path)
        self.proxy_url = f"http://{proxy_host}:{proxy_port}"
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.startup_timeout = startup_timeout
        self.health_check_interval = health_check_interval
        self.max_startup_attempts = max_startup_attempts

        # Process management
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.startup_time: Optional[float] = None

        # Health monitoring
        self.health_task: Optional[asyncio.Task] = None
        self.last_health_check: Optional[float] = None
        self.health_status: str = "unknown"

        # HTTP client for proxy communication
        self.client_config = {
            'timeout': httpx.Timeout(10.0),
            'headers': {
                'User-Agent': 'ChameleonEngine/1.0 ProxyManager',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }
        self._client: Optional[httpx.AsyncClient] = None

        logger.info(f"Go Proxy Manager initialized for {self.proxy_url}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()

    async def start(self) -> str:
        """
        Start the Go proxy service.

        Returns:
            Proxy URL for the running service

        Raises:
            GoProxyNotAvailableError: If the proxy binary is not found
            GoProxyManagerError: If startup fails
        """
        if self.is_running:
            logger.warning("Proxy is already running")
            return self.proxy_url

        # Check if binary exists
        if not self.proxy_binary_path.exists():
            raise GoProxyNotAvailableError(
                f"Go proxy binary not found at {self.proxy_binary_path}"
            )

        # Start HTTP client
        self._client = httpx.AsyncClient(**self.client_config)

        # Start the proxy process
        for attempt in range(self.max_startup_attempts):
            try:
                logger.info(f"Starting Go proxy (attempt {attempt + 1}/{self.max_startup_attempts})")
                await self._start_proxy_process()
                await self._wait_for_proxy_ready()

                # Start health monitoring
                await self._start_health_monitoring()

                self.is_running = True
                self.startup_time = time.time()

                logger.info(f"Go proxy started successfully at {self.proxy_url}")
                return self.proxy_url

            except Exception as e:
                logger.error(f"Failed to start proxy (attempt {attempt + 1}): {str(e)}")

                # Cleanup failed attempt
                await self._cleanup_process()

                if attempt < self.max_startup_attempts - 1:
                    await asyncio.sleep(2.0)  # Wait before retry
                else:
                    raise GoProxyManagerError(
                        f"Failed to start Go proxy after {self.max_startup_attempts} attempts: {str(e)}"
                    ) from e

    async def stop(self):
        """Stop the Go proxy service."""
        if not self.is_running:
            logger.warning("Proxy is not running")
            return

        logger.info("Stopping Go proxy service")

        # Stop health monitoring
        if self.health_task:
            self.health_task.cancel()
            try:
                await self.health_task
            except asyncio.CancelledError:
                pass

        # Stop the proxy process
        await self._cleanup_process()

        # Close HTTP client
        if self._client:
            await self._client.aclose()
            self._client = None

        self.is_running = False
        self.startup_time = None

        logger.info("Go proxy service stopped")

    async def _start_proxy_process(self):
        """Start the Go proxy subprocess."""
        startup_args = [
            str(self.proxy_binary_path),
            "--host", self.proxy_host,
            "--port", str(self.proxy_port),
            "--log-level", "info"
        ]

        # Set up environment variables
        env = os.environ.copy()
        env.update({
            'PROXY_HOST': self.proxy_host,
            'PROXY_PORT': str(self.proxy_port),
            'RUST_LOG': 'info'  # If using Rust components
        })

        try:
            self.process = subprocess.Popen(
                startup_args,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Give the process a moment to start
            await asyncio.sleep(0.5)

            # Check if process is still running
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                error_msg = f"Proxy process exited immediately. Stdout: {stdout}. Stderr: {stderr}"
                raise GoProxyManagerError(error_msg)

            logger.info(f"Go proxy process started with PID {self.process.pid}")

        except Exception as e:
            raise GoProxyManagerError(f"Failed to start proxy process: {str(e)}") from e

    async def _wait_for_proxy_ready(self):
        """Wait for the proxy to be ready to accept connections."""
        logger.info(f"Waiting for proxy to be ready (timeout: {self.startup_timeout}s)")

        start_time = time.time()
        while time.time() - start_time < self.startup_timeout:
            try:
                # Try health check
                health = await self._check_proxy_health()
                if health.get('status') == 'healthy':
                    logger.info("Proxy is ready and healthy")
                    return

                # Check if process is still running
                if self.process and self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    error_msg = f"Proxy process died during startup. Stderr: {stderr}"
                    raise GoProxyManagerError(error_msg)

                await asyncio.sleep(1.0)

            except httpx.RequestError:
                # Connection not ready yet, continue waiting
                await asyncio.sleep(1.0)
            except Exception as e:
                logger.debug(f"Health check failed (expected during startup): {str(e)}")
                await asyncio.sleep(1.0)

        raise GoProxyManagerError(f"Proxy did not become ready within {self.startup_timeout} seconds")

    async def _start_health_monitoring(self):
        """Start background health monitoring task."""
        self.health_task = asyncio.create_task(self._health_monitoring_loop())
        logger.info("Health monitoring started")

    async def _health_monitoring_loop(self):
        """Background task for continuous health monitoring."""
        while self.is_running:
            try:
                await asyncio.sleep(self.health_check_interval)

                if not self.is_running:
                    break

                health = await self._check_proxy_health()
                self.last_health_check = time.time()
                self.health_status = health.get('status', 'unknown')

                if self.health_status != 'healthy':
                    logger.warning(f"Proxy health degraded: {self.health_status}")

            except asyncio.CancelledError:
                logger.info("Health monitoring cancelled")
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(self.health_check_interval)

    async def _check_proxy_health(self) -> Dict[str, Any]:
        """Check proxy health status."""
        try:
            response = await self._client.get(f"{self.proxy_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.debug(f"Health check failed: {str(e)}")
            return {'status': 'unhealthy', 'error': str(e)}

    async def _cleanup_process(self):
        """Clean up the proxy process."""
        if self.process:
            try:
                # Try graceful shutdown first
                logger.info(f"Attempting graceful shutdown of PID {self.process.pid}")
                self.process.terminate()

                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=10)
                    logger.info("Proxy process terminated gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning("Graceful shutdown timed out, forcing termination")
                    self.process.kill()
                    self.process.wait()
                    logger.info("Proxy process terminated forcefully")

            except Exception as e:
                logger.error(f"Error during process cleanup: {str(e)}")
            finally:
                self.process = None

    async def set_profile(self, profile: BrowserProfile) -> bool:
        """
        Set the fingerprint profile for the proxy.

        Args:
            profile: Browser profile to configure

        Returns:
            True if profile was set successfully

        Raises:
            GoProxyManagerError: If proxy is not running or request fails
        """
        if not self.is_running:
            raise GoProxyManagerError("Proxy is not running")

        try:
            logger.info(f"Setting profile: {profile.profile_id}")

            response = await self._client.post(
                f"{self.proxy_url}/set-profile",
                json=profile.model_dump(exclude_none=True)
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Profile set successfully: {result.get('message', 'OK')}")
            return True

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Failed to set profile ({e.response.status_code}): {error_data.get('error', 'Unknown error')}"
            logger.error(error_msg)
            raise GoProxyManagerError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error setting profile: {str(e)}"
            logger.error(error_msg)
            raise GoProxyManagerError(error_msg) from e

    async def get_status(self) -> Dict[str, Any]:
        """
        Get current proxy status and statistics.

        Returns:
            Proxy status information

        Raises:
            GoProxyManagerError: If proxy is not running or request fails
        """
        if not self.is_running:
            raise GoProxyManagerError("Proxy is not running")

        try:
            response = await self._client.get(f"{self.proxy_url}/status")
            response.raise_for_status()

            status_data = response.json()

            # Add manager-specific information
            status_data.update({
                'manager_status': 'running' if self.is_running else 'stopped',
                'startup_time': self.startup_time,
                'uptime_seconds': time.time() - self.startup_time if self.startup_time else 0,
                'last_health_check': self.last_health_check,
                'health_status': self.health_status,
                'process_id': self.process.pid if self.process else None
            })

            return status_data

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Failed to get status ({e.response.status_code}): {error_data.get('error', 'Unknown error')}"
            logger.error(error_msg)
            raise GoProxyManagerError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error getting status: {str(e)}"
            logger.error(error_msg)
            raise GoProxyManagerError(error_msg) from e

    async def clear_profile(self) -> bool:
        """
        Clear the current profile from the proxy.

        Returns:
            True if profile was cleared successfully

        Raises:
            GoProxyManagerError: If proxy is not running or request fails
        """
        if not self.is_running:
            raise GoProxyManagerError("Proxy is not running")

        try:
            logger.info("Clearing proxy profile")

            response = await self._client.post(f"{self.proxy_url}/clear-profile")
            response.raise_for_status()

            result = response.json()
            logger.info(f"Profile cleared successfully: {result.get('message', 'OK')}")
            return True

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Failed to clear profile ({e.response.status_code}): {error_data.get('error', 'Unknown error')}"
            logger.error(error_msg)
            raise GoProxyManagerError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error clearing profile: {str(e)}"
            logger.error(error_msg)
            raise GoProxyManagerError(error_msg) from e

    async def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get connection statistics from the proxy.

        Returns:
            Connection statistics

        Raises:
            GoProxyManagerError: If proxy is not running or request fails
        """
        if not self.is_running:
            raise GoProxyManagerError("Proxy is not running")

        try:
            response = await self._client.get(f"{self.proxy_url}/stats/connections")
            response.raise_for_status()

            stats = response.json()
            logger.debug(f"Connection stats: {stats}")
            return stats

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Failed to get connection stats ({e.response.status_code}): {error_data.get('error', 'Unknown error')}"
            logger.error(error_msg)
            raise GoProxyManagerError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error getting connection stats: {str(e)}"
            logger.error(error_msg)
            raise GoProxyManagerError(error_msg) from e

    async def reload_config(self) -> bool:
        """
        Reload proxy configuration.

        Returns:
            True if configuration was reloaded successfully

        Raises:
            GoProxyManagerError: If proxy is not running or request fails
        """
        if not self.is_running:
            raise GoProxyManagerError("Proxy is not running")

        try:
            logger.info("Reloading proxy configuration")

            response = await self._client.post(f"{self.proxy_url}/reload-config")
            response.raise_for_status()

            result = response.json()
            logger.info(f"Configuration reloaded: {result.get('message', 'OK')}")
            return True

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Failed to reload config ({e.response.status_code}): {error_data.get('error', 'Unknown error')}"
            logger.error(error_msg)
            raise GoProxyManagerError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error reloading config: {str(e)}"
            logger.error(error_msg)
            raise GoProxyManagerError(error_msg) from e

    def _extract_error_data(self, response: httpx.Response) -> Dict[str, Any]:
        """Extract error data from HTTP response."""
        try:
            return response.json()
        except Exception:
            return {
                "error": f"HTTP {response.status_code}",
                "message": response.text or f"HTTP {response.status_code} error"
            }

    def get_proxy_url(self) -> str:
        """Get the proxy URL for browser configuration."""
        return self.proxy_url

    def is_proxy_running(self) -> bool:
        """Check if the proxy is currently running."""
        return self.is_running

    def get_process_info(self) -> Dict[str, Any]:
        """Get information about the proxy process."""
        info = {
            'is_running': self.is_running,
            'proxy_url': self.proxy_url,
            'binary_path': str(self.proxy_binary_path),
            'process_id': self.process.pid if self.process else None,
            'startup_time': self.startup_time,
            'uptime_seconds': time.time() - self.startup_time if self.startup_time else 0,
            'health_status': self.health_status,
            'last_health_check': self.last_health_check
        }

        return info


class ProxyManagerPool:
    """
    Pool of proxy managers for load balancing and redundancy.

    This manages multiple Go proxy instances to provide load balancing
    and failover capabilities.
    """

    def __init__(self, proxy_configs: List[Dict[str, Any]]):
        """
        Initialize the proxy manager pool.

        Args:
            proxy_configs: List of proxy configuration dictionaries
        """
        self.proxy_managers = []
        self.current_index = 0
        self.healthy_managers = []

        # Create proxy managers from configurations
        for config in proxy_configs:
            manager = GoProxyManager(**config)
            self.proxy_managers.append(manager)

        logger.info(f"Proxy manager pool initialized with {len(self.proxy_managers)} managers")

    async def start_all(self) -> List[str]:
        """Start all proxy managers."""
        started_proxies = []

        for i, manager in enumerate(self.proxy_managers):
            try:
                proxy_url = await manager.start()
                started_proxies.append(proxy_url)
                self.healthy_managers.append(manager)
                logger.info(f"Proxy manager {i+1} started successfully")
            except Exception as e:
                logger.error(f"Failed to start proxy manager {i+1}: {str(e)}")

        logger.info(f"Started {len(started_proxies)}/{len(self.proxy_managers)} proxy managers")
        return started_proxies

    async def stop_all(self):
        """Stop all proxy managers."""
        for i, manager in enumerate(self.proxy_managers):
            try:
                await manager.stop()
                logger.info(f"Proxy manager {i+1} stopped successfully")
            except Exception as e:
                logger.error(f"Failed to stop proxy manager {i+1}: {str(e)}")

        self.healthy_managers.clear()

    def get_next_manager(self) -> Optional[GoProxyManager]:
        """Get the next available proxy manager (round-robin)."""
        if not self.healthy_managers:
            return None

        manager = self.healthy_managers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.healthy_managers)
        return manager

    async def set_profile_all(self, profile: BrowserProfile) -> Dict[str, Any]:
        """Set profile on all healthy proxy managers."""
        results = {}

        for i, manager in enumerate(self.proxy_managers):
            try:
                success = await manager.set_profile(profile)
                results[f"manager_{i+1}"] = success
            except Exception as e:
                results[f"manager_{i+1}"] = False
                logger.error(f"Failed to set profile on manager {i+1}: {str(e)}")

        return results

    def get_pool_status(self) -> Dict[str, Any]:
        """Get status of the entire proxy pool."""
        status = {
            'total_managers': len(self.proxy_managers),
            'healthy_managers': len(self.healthy_managers),
            'current_index': self.current_index,
            'managers': []
        }

        for i, manager in enumerate(self.proxy_managers):
            status['managers'].append({
                'index': i,
                'info': manager.get_process_info()
            })

        return status