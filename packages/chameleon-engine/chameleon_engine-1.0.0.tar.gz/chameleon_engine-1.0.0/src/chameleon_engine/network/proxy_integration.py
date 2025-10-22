"""
Proxy integration manager for network obfuscation.

This module provides integration between the NetworkObfuscator and various
proxy services, managing connection pooling, load balancing, and failover.
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

from ..services.proxy.manager import GoProxyManager, ProxyManagerPool, ProxyConfig
from ..core.profiles import BrowserProfile

logger = logging.getLogger(__name__)


class ProxyHealthStatus(Enum):
    """Proxy health status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProxyConnectionInfo:
    """Information about a proxy connection."""
    proxy_url: str
    manager: GoProxyManager
    profile_id: str
    established_at: datetime
    last_used: datetime
    request_count: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    health_status: ProxyHealthStatus = ProxyHealthStatus.UNKNOWN
    current_profile: Optional[BrowserProfile] = None
    connection_pool_size: int = 0
    active_requests: int = 0


@dataclass
class ProxyIntegrationConfig:
    """Configuration for proxy integration."""

    # Connection management
    max_connections_per_proxy: int = 100
    connection_timeout: int = 30
    connection_idle_timeout: int = 300
    max_retries: int = 3
    retry_delay: float = 1.0

    # Health checking
    health_check_interval: float = 30.0
    health_check_timeout: int = 10
    unhealthy_threshold: int = 3  # Consecutive failures before marking unhealthy
    recovery_threshold: int = 2  # Consecutive successes before recovery

    # Load balancing
    load_balancing_strategy: str = "round_robin"  # round_robin, least_connections, weighted, random
    enable_failover: bool = True
    failover_timeout: int = 60

    # Performance
    enable_connection_pooling: bool = True
    enable_request_caching: bool = False
    cache_ttl: int = 60
    max_cache_size: int = 1000

    # Monitoring
    enable_metrics: bool = True
    metrics_retention_period: timedelta = field(default_factory=lambda: timedelta(hours=1))


class ProxyIntegrationManager:
    """
    Manager for proxy integration with advanced features.

    This class provides comprehensive proxy integration including connection
    pooling, load balancing, health monitoring, and failover capabilities.
    """

    def __init__(self, config: Optional[ProxyIntegrationConfig] = None):
        """
        Initialize proxy integration manager.

        Args:
            config: Integration configuration
        """
        self.config = config or ProxyIntegrationConfig()

        # Proxy management
        self.proxy_managers: Dict[str, GoProxyManager] = {}
        self.proxy_pool: Optional[ProxyManagerPool] = None
        self.connection_info: Dict[str, ProxyConnectionInfo] = {}

        # Load balancing
        self._current_proxy_index = 0
        self._load_balancer_lock = asyncio.Lock()

        # Health monitoring
        self._health_check_task: Optional[asyncio.Task] = None
        self._proxy_health_history: Dict[str, List[bool]] = {}

        # Request handling
        self._active_requests: Dict[str, List[asyncio.Task]] = {}
        self._request_cache: Dict[str, Dict[str, Any]] = {}

        # Metrics
        self._metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "proxy_switches": 0,
            "health_checks": 0,
            "failover_events": 0
        }

        # Event callbacks
        self._proxy_health_callbacks: List[Callable[[str, ProxyHealthStatus], None]] = []
        self._request_callbacks: List[Callable[[Dict[str, Any]], None]] = []

        logger.info("Proxy integration manager initialized")

    async def add_proxy(
        self,
        proxy_config: ProxyConfig,
        profile: Optional[BrowserProfile] = None
    ) -> str:
        """
        Add a proxy to the integration manager.

        Args:
            proxy_config: Proxy configuration
            profile: Browser profile for the proxy

        Returns:
            Proxy ID
        """
        proxy_id = f"proxy_{len(self.proxy_managers)}"

        try:
            # Create proxy manager
            manager = GoProxyManager(proxy_config=proxy_config)
            await manager.start()

            # Configure with profile if provided
            if profile:
                await manager.set_profile(profile)
                profile_id = profile.profile_id
            else:
                profile_id = "default"

            # Store connection info
            self.connection_info[proxy_id] = ProxyConnectionInfo(
                proxy_url=manager.get_proxy_url(),
                manager=manager,
                profile_id=profile_id,
                established_at=datetime.now(),
                last_used=datetime.now(),
                current_profile=profile
            )

            self.proxy_managers[proxy_id] = manager
            self._proxy_health_history[proxy_id] = []

            logger.info(f"Added proxy {proxy_id} at {manager.get_proxy_url()}")
            return proxy_id

        except Exception as e:
            logger.error(f"Failed to add proxy: {str(e)}")
            raise

    async def remove_proxy(self, proxy_id: str) -> bool:
        """
        Remove a proxy from the integration manager.

        Args:
            proxy_id: Proxy ID to remove

        Returns:
            True if removed successfully
        """
        if proxy_id not in self.proxy_managers:
            return False

        try:
            # Stop active requests
            if proxy_id in self._active_requests:
                for task in self._active_requests[proxy_id]:
                    if not task.done():
                        task.cancel()
                del self._active_requests[proxy_id]

            # Stop proxy manager
            await self.proxy_managers[proxy_id].stop()

            # Clean up
            del self.proxy_managers[proxy_id]
            del self.connection_info[proxy_id]
            del self._proxy_health_history[proxy_id]

            logger.info(f"Removed proxy {proxy_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove proxy {proxy_id}: {str(e)}")
            return False

    async def get_proxy_for_request(
        self,
        profile: Optional[BrowserProfile] = None,
        preferred_proxy_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Get a proxy ID for handling a request.

        Args:
            profile: Browser profile for the request
            preferred_proxy_id: Preferred proxy ID (if any)

        Returns:
            Proxy ID or None if no healthy proxies available
        """
        if not self.proxy_managers:
            return None

        # Use preferred proxy if specified and healthy
        if preferred_proxy_id and preferred_proxy_id in self.proxy_managers:
            if self._is_proxy_healthy(preferred_proxy_id):
                return preferred_proxy_id
            else:
                logger.warning(f"Preferred proxy {preferred_proxy_id} is unhealthy")

        # Select proxy based on load balancing strategy
        proxy_id = await self._select_proxy_load_balanced()

        if proxy_id:
            # Configure proxy with profile if needed
            if profile and profile != self.connection_info[proxy_id].current_profile:
                try:
                    await self.proxy_managers[proxy_id].set_profile(profile)
                    self.connection_info[proxy_id].current_profile = profile
                    self.connection_info[proxy_id].profile_id = profile.profile_id
                except Exception as e:
                    logger.error(f"Failed to configure proxy {proxy_id}: {str(e)}")
                    return None

        return proxy_id

    async def execute_request(
        self,
        proxy_id: str,
        request_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a request through a specific proxy.

        Args:
            proxy_id: Proxy ID to use
            request_func: Request function to execute
            *args: Arguments for request function
            **kwargs: Keyword arguments for request function

        Returns:
            Request result
        """
        if proxy_id not in self.proxy_managers:
            raise ValueError(f"Proxy {proxy_id} not found")

        if not self._is_proxy_healthy(proxy_id):
            if self.config.enable_failover:
                # Try to get an alternative proxy
                alternative_proxy = await self.get_proxy_for_request()
                if alternative_proxy:
                    logger.info(f"Failing over from {proxy_id} to {alternative_proxy}")
                    self._metrics["failover_events"] += 1
                    proxy_id = alternative_proxy
                else:
                    raise RuntimeError(f"No healthy proxies available for failover")
            else:
                raise RuntimeError(f"Proxy {proxy_id} is unhealthy and failover is disabled")

        start_time = time.time()
        connection_info = self.connection_info[proxy_id]

        try:
            # Update usage stats
            connection_info.last_used = datetime.now()
            connection_info.request_count += 1
            connection_info.active_requests += 1

            # Execute request
            result = await request_func(*args, **kwargs)

            # Update metrics
            request_time = time.time() - start_time
            self._update_proxy_metrics(proxy_id, request_time, True)

            self._metrics["total_requests"] += 1
            self._metrics["successful_requests"] += 1

            # Notify callbacks
            await self._notify_request_callbacks({
                "proxy_id": proxy_id,
                "success": True,
                "duration": request_time,
                "timestamp": datetime.now()
            })

            return result

        except Exception as e:
            # Update error metrics
            self._update_proxy_metrics(proxy_id, time.time() - start_time, False)

            self._metrics["total_requests"] += 1
            self._metrics["failed_requests"] += 1

            # Update health status
            self._record_health_result(proxy_id, False)

            # Notify callbacks
            await self._notify_request_callbacks({
                "proxy_id": proxy_id,
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "timestamp": datetime.now()
            })

            logger.error(f"Request failed through proxy {proxy_id}: {str(e)}")
            raise

        finally:
            connection_info.active_requests -= 1

    async def _select_proxy_load_balanced(self) -> Optional[str]:
        """Select proxy based on load balancing strategy."""
        healthy_proxies = [
            proxy_id for proxy_id in self.proxy_managers.keys()
            if self._is_proxy_healthy(proxy_id)
        ]

        if not healthy_proxies:
            return None

        async with self._load_balancer_lock:
            if self.config.load_balancing_strategy == "round_robin":
                proxy_id = healthy_proxies[self._current_proxy_index % len(healthy_proxies)]
                self._current_proxy_index += 1

            elif self.config.load_balancing_strategy == "least_connections":
                proxy_id = min(
                    healthy_proxies,
                    key=lambda pid: self.connection_info[pid].active_requests
                )

            elif self.config.load_balancing_strategy == "weighted":
                # Weight by health score and connection count
                def weight_score(pid):
                    info = self.connection_info[pid]
                    health_weight = 1.0 if info.health_status == ProxyHealthStatus.HEALTHY else 0.5
                    connection_weight = 1.0 / (1.0 + info.active_requests)
                    return health_weight * connection_weight

                weights = [weight_score(pid) for pid in healthy_proxies]
                total_weight = sum(weights)
                if total_weight > 0:
                    normalized_weights = [w / total_weight for w in weights]
                    proxy_id = random.choices(healthy_proxies, weights=normalized_weights)[0]
                else:
                    proxy_id = random.choice(healthy_proxies)

            else:  # random
                proxy_id = random.choice(healthy_proxies)

            self._metrics["proxy_switches"] += 1
            return proxy_id

    def _is_proxy_healthy(self, proxy_id: str) -> bool:
        """Check if a proxy is healthy."""
        if proxy_id not in self.connection_info:
            return False

        connection_info = self.connection_info[proxy_id]
        return connection_info.health_status in [
            ProxyHealthStatus.HEALTHY,
            ProxyHealthStatus.DEGRADED
        ]

    async def _update_proxy_metrics(
        self,
        proxy_id: str,
        response_time: float,
        success: bool
    ):
        """Update proxy metrics."""
        if proxy_id not in self.connection_info:
            return

        connection_info = self.connection_info[proxy_id]

        # Update response time (moving average)
        if connection_info.average_response_time == 0:
            connection_info.average_response_time = response_time
        else:
            # Exponential moving average with alpha=0.1
            connection_info.average_response_time = (
                0.9 * connection_info.average_response_time +
                0.1 * response_time
            )

        # Update error count
        if not success:
            connection_info.error_count += 1

        # Record health result
        self._record_health_result(proxy_id, success)

    def _record_health_result(self, proxy_id: str, is_healthy: bool):
        """Record health check result."""
        if proxy_id not in self._proxy_health_history:
            self._proxy_health_history[proxy_id] = []

        history = self._proxy_health_history[proxy_id]
        history.append(is_healthy)

        # Keep only recent results
        max_history = self.config.unhealthy_threshold + self.config.recovery_threshold + 5
        if len(history) > max_history:
            self._proxy_health_history[proxy_id] = history[-max_history:]

        # Update health status
        self._update_proxy_health_status(proxy_id)

    def _update_proxy_health_status(self, proxy_id: str):
        """Update proxy health status based on recent results."""
        if proxy_id not in self._proxy_health_history:
            return

        history = self._proxy_health_history[proxy_id]
        connection_info = self.connection_info[proxy_id]
        old_status = connection_info.health_status

        if not history:
            return

        recent_results = history[-self.config.unhealthy_threshold:]
        recent_successes = sum(recent_results)

        if recent_successes == 0 and len(recent_results) >= self.config.unhealthy_threshold:
            connection_info.health_status = ProxyHealthStatus.UNHEALTHY
        elif recent_successes < len(recent_results) * 0.7:
            connection_info.health_status = ProxyHealthStatus.DEGRADED
        else:
            connection_info.health_status = ProxyHealthStatus.HEALTHY

        # Notify callbacks if status changed
        if old_status != connection_info.health_status:
            self._notify_proxy_health_change(proxy_id, connection_info.health_status)

    async def start_health_monitoring(self):
        """Start background health monitoring."""
        if self._health_check_task and not self._health_check_task.done():
            return

        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Proxy health monitoring started")

    async def stop_health_monitoring(self):
        """Stop background health monitoring."""
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None

        logger.info("Proxy health monitoring stopped")

    async def _health_check_loop(self):
        """Background health check loop."""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {str(e)}")
                await asyncio.sleep(self.config.health_check_interval)

    async def _perform_health_checks(self):
        """Perform health checks on all proxies."""
        for proxy_id, manager in self.proxy_managers.items():
            try:
                # Get proxy status
                status = await manager.get_status()
                is_healthy = status.get('status') == 'running'

                # Record health result
                self._record_health_result(proxy_id, is_healthy)
                self._metrics["health_checks"] += 1

            except Exception as e:
                logger.warning(f"Health check failed for proxy {proxy_id}: {str(e)}")
                self._record_health_result(proxy_id, False)
                self._metrics["health_checks"] += 1

    def add_proxy_health_callback(self, callback: Callable[[str, ProxyHealthStatus], None]):
        """Add callback for proxy health changes."""
        self._proxy_health_callbacks.append(callback)

    def add_request_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for request events."""
        self._request_callbacks.append(callback)

    def _notify_proxy_health_change(self, proxy_id: str, status: ProxyHealthStatus):
        """Notify proxy health change callbacks."""
        for callback in self._proxy_health_callbacks:
            try:
                callback(proxy_id, status)
            except Exception as e:
                logger.error(f"Proxy health callback error: {str(e)}")

    async def _notify_request_callbacks(self, request_info: Dict[str, Any]):
        """Notify request event callbacks."""
        for callback in self._request_callbacks:
            try:
                callback(request_info)
            except Exception as e:
                logger.error(f"Request callback error: {str(e)}")

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information."""
        healthy_count = sum(
            1 for info in self.connection_info.values()
            if info.health_status == ProxyHealthStatus.HEALTHY
        )
        degraded_count = sum(
            1 for info in self.connection_info.values()
            if info.health_status == ProxyHealthStatus.DEGRADED
        )
        unhealthy_count = sum(
            1 for info in self.connection_info.values()
            if info.health_status == ProxyHealthStatus.UNHEALTHY
        )

        total_requests = sum(info.request_count for info in self.connection_info.values())
        total_errors = sum(info.error_count for info in self.connection_info.values())
        active_requests = sum(info.active_requests for info in self.connection_info.values())

        return {
            "total_proxies": len(self.proxy_managers),
            "healthy_proxies": healthy_count,
            "degraded_proxies": degraded_count,
            "unhealthy_proxies": unhealthy_count,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "active_requests": active_requests,
            "success_rate": (total_requests - total_errors) / max(1, total_requests) * 100,
            "load_balancing_strategy": self.config.load_balancing_strategy,
            "health_monitoring_active": self._health_check_task is not None,
            "metrics": self._metrics.copy(),
            "proxies": {
                proxy_id: {
                    "url": info.proxy_url,
                    "health_status": info.health_status.value,
                    "request_count": info.request_count,
                    "error_count": info.error_count,
                    "average_response_time": info.average_response_time,
                    "active_requests": info.active_requests,
                    "profile_id": info.profile_id,
                    "established_at": info.established_at.isoformat(),
                    "last_used": info.last_used.isoformat()
                }
                for proxy_id, info in self.connection_info.items()
            }
        }

    async def cleanup(self):
        """Clean up resources."""
        # Stop health monitoring
        await self.stop_health_monitoring()

        # Stop all proxy managers
        for proxy_id in list(self.proxy_managers.keys()):
            await self.remove_proxy(proxy_id)

        # Clear caches and metrics
        self._request_cache.clear()
        self._active_requests.clear()

        logger.info("Proxy integration manager cleaned up")