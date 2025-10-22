"""
Fingerprint Generator - API-based Browser Profile Generation

This module provides the FingerprintGenerator class that integrates with the Fingerprint Service
to generate browser profiles on-demand with advanced caching and performance optimization.
"""

import asyncio
import logging
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta

from ..services.fingerprint.client import FingerprintServiceClient, CachingFingerprintClient
from ..services.fingerprint.models import (
    FingerprintRequest,
    FingerprintResponse,
    ProfileConstraints,
    ProfileMetadata,
    BrowserType,
    OperatingSystem,
    ServiceStatus
)
from ..core.profiles import BrowserProfile

logger = logging.getLogger(__name__)


class FingerprintGeneratorError(Exception):
    """Base exception for fingerprint generator errors"""
    pass


class ServiceUnavailableError(FingerprintGeneratorError):
    """Raised when fingerprint service is unavailable"""
    pass


class ProfileGenerationError(FingerprintGeneratorError):
    """Raised when profile generation fails"""
    pass


class FingerprintCache:
    """In-memory cache for generated fingerprints with LRU eviction"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[BrowserProfile, datetime]] = {}
        self._access_order: List[str] = []
        self._lock = asyncio.Lock()

    def _generate_key(self, request: FingerprintRequest) -> str:
        """Generate cache key from request parameters"""
        key_data = {
            'browser': request.browser.value if request.browser else 'chrome',
            'os': request.os.value if request.os else 'windows',
            'version': request.version or 'latest',
            'region': request.region or 'us',
            'device_type': request.device_type.value if request.device_type else 'desktop',
            'quality_threshold': request.quality_threshold,
            'constraints': request.constraints.model_dump() if request.constraints else {}
        }
        key_str = str(sorted(key_data.items()))
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    async def get(self, request: FingerprintRequest) -> Optional[BrowserProfile]:
        """Get cached profile if valid"""
        async with self._lock:
            key = self._generate_key(request)

            if key not in self._cache:
                return None

            profile, timestamp = self._cache[key]

            # Check TTL
            if datetime.now() - timestamp > timedelta(seconds=self.ttl_seconds):
                del self._cache[key]
                self._access_order.remove(key)
                return None

            # Move to end (LRU)
            self._access_order.remove(key)
            self._access_order.append(key)

            return profile

    async def put(self, request: FingerprintRequest, profile: BrowserProfile) -> None:
        """Cache profile with LRU eviction"""
        async with self._lock:
            key = self._generate_key(request)
            now = datetime.now()

            # Remove existing entry if present
            if key in self._cache:
                self._access_order.remove(key)

            # Evict oldest if at capacity
            while len(self._cache) >= self.max_size:
                oldest_key = self._access_order.pop(0)
                del self._cache[oldest_key]

            # Add new entry
            self._cache[key] = (profile, now)
            self._access_order.append(key)

    async def clear(self) -> None:
        """Clear all cached entries"""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            now = datetime.now()
            valid_entries = sum(
                1 for _, timestamp in self._cache.values()
                if now - timestamp <= timedelta(seconds=self.ttl_seconds)
            )

            return {
                'total_entries': len(self._cache),
                'valid_entries': valid_entries,
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds,
                'utilization': len(self._cache) / self.max_size if self.max_size > 0 else 0
            }


class FingerprintGenerator:
    """
    Advanced fingerprint generator with API integration and intelligent caching.

    This class provides a high-level interface for generating browser profiles
    using the Fingerprint Service API with comprehensive error handling,
    caching, and performance optimization.
    """

    def __init__(
        self,
        service_url: str = "http://localhost:8000",
        cache_size: int = 1000,
        cache_ttl: int = 3600,
        timeout: float = 30.0,
        max_retries: int = 3,
        use_cache: bool = True
    ):
        """
        Initialize fingerprint generator

        Args:
            service_url: URL of the fingerprint service API
            cache_size: Maximum number of profiles to cache
            cache_ttl: Cache TTL in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            use_cache: Whether to use in-memory caching
        """
        self.service_url = service_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.use_cache = use_cache

        # Initialize client
        self.client = FingerprintServiceClient(
            base_url=service_url,
            timeout=timeout,
            max_retries=max_retries
        )

        # Initialize cache if enabled
        self.cache = FingerprintCache(max_size=cache_size, ttl_seconds=cache_ttl) if use_cache else None

        # Statistics
        self._stats = {
            'requests_made': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'generation_failures': 0,
            'service_errors': 0,
            'total_generation_time': 0.0,
            'average_generation_time': 0.0
        }

        logger.info(f"FingerprintGenerator initialized with service_url={service_url}")

    async def generate(
        self,
        browser: BrowserType = BrowserType.CHROME,
        os: OperatingSystem = OperatingSystem.WINDOWS,
        version: Optional[str] = None,
        region: Optional[str] = None,
        device_type: Optional[str] = "desktop",
        quality_threshold: float = 0.7,
        constraints: Optional[ProfileConstraints] = None,
        seed: Optional[str] = None,
        use_cache: Optional[bool] = None,
        **kwargs
    ) -> BrowserProfile:
        """
        Generate a browser profile from the fingerprint service

        Args:
            browser: Browser type (chrome, firefox, safari, edge)
            os: Operating system (windows, macos, linux)
            version: Browser version (None for latest)
            region: Geographic region for profile
            device_type: Device type (desktop, mobile, tablet)
            quality_threshold: Minimum quality score (0.0-1.0)
            constraints: Additional generation constraints
            seed: Seed for reproducible generation
            use_cache: Override default caching behavior
            **kwargs: Additional generation parameters

        Returns:
            BrowserProfile: Generated browser profile

        Raises:
            ServiceUnavailableError: If fingerprint service is unavailable
            ProfileGenerationError: If profile generation fails
        """
        start_time = datetime.now()

        try:
            # Create request
            request = FingerprintRequest(
                browser=browser,
                os=os,
                version=version,
                region=region,
                device_type=device_type,
                quality_threshold=quality_threshold,
                constraints=constraints,
                seed=seed,
                **kwargs
            )

            # Check cache first if enabled
            should_cache = use_cache if use_cache is not None else self.use_cache
            if should_cache and self.cache:
                cached_profile = await self.cache.get(request)
                if cached_profile:
                    self._stats['cache_hits'] += 1
                    logger.debug(f"Cache hit for profile request: {browser.value}/{os.value}")
                    return cached_profile

                self._stats['cache_misses'] += 1

            # Generate profile via API
            self._stats['requests_made'] += 1

            try:
                response = await self.client.get_fingerprint(request)
                profile = response.browser_profile

                # Cache the generated profile if caching is enabled
                if should_cache and self.cache:
                    await self.cache.put(request, profile)

                # Update statistics
                generation_time = (datetime.now() - start_time).total_seconds()
                self._update_generation_stats(generation_time, success=True)

                logger.info(
                    f"Generated profile: {browser.value}/{os.value} "
                    f"(quality: {response.metadata.quality_score:.2f}, "
                    f"time: {generation_time:.2f}s)"
                )

                return profile

            except Exception as e:
                self._stats['generation_failures'] += 1
                self._update_generation_stats((datetime.now() - start_time).total_seconds(), success=False)

                if "service unavailable" in str(e).lower():
                    raise ServiceUnavailableError(f"Fingerprint service unavailable: {e}")
                else:
                    raise ProfileGenerationError(f"Profile generation failed: {e}")

        except Exception as e:
            if isinstance(e, (ServiceUnavailableError, ProfileGenerationError)):
                raise

            logger.error(f"Unexpected error in generate(): {e}")
            raise ProfileGenerationError(f"Unexpected error: {e}")

    async def generate_batch(
        self,
        requests: List[FingerprintRequest],
        diversity_assurance: bool = True,
        max_parallel: int = 10
    ) -> List[BrowserProfile]:
        """
        Generate multiple browser profiles in batch

        Args:
            requests: List of fingerprint requests
            diversity_assurance: Ensure diversity in generated profiles
            max_parallel: Maximum parallel requests

        Returns:
            List[BrowserProfile]: Generated profiles
        """
        if not requests:
            return []

        logger.info(f"Generating batch of {len(requests)} profiles")

        # Process requests in parallel with rate limiting
        semaphore = asyncio.Semaphore(max_parallel)

        async def generate_single(request: FingerprintRequest) -> BrowserProfile:
            async with semaphore:
                return await self.generate(
                    browser=request.browser,
                    os=request.os,
                    version=request.version,
                    region=request.region,
                    device_type=request.device_type,
                    quality_threshold=request.quality_threshold,
                    constraints=request.constraints,
                    seed=request.seed
                )

        try:
            profiles = await asyncio.gather(
                *(generate_single(request) for request in requests),
                return_exceptions=True
            )

            # Filter successful results
            successful_profiles = []
            failed_count = 0

            for i, result in enumerate(profiles):
                if isinstance(result, Exception):
                    logger.error(f"Batch request {i} failed: {result}")
                    failed_count += 1
                else:
                    successful_profiles.append(result)

            logger.info(
                f"Batch generation completed: {len(successful_profiles)} successful, "
                f"{failed_count} failed"
            )

            return successful_profiles

        except Exception as e:
            logger.error(f"Batch generation failed: {e}")
            raise ProfileGenerationError(f"Batch generation failed: {e}")

    async def validate_profile(
        self,
        profile: BrowserProfile,
        test_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Validate a browser profile against anti-bot detection

        Args:
            profile: Browser profile to validate
            test_type: Type of validation test (basic, advanced, full)

        Returns:
            Dict containing validation results
        """
        try:
            # Convert profile to request format for validation
            profile_id = f"validation_{int(datetime.now().timestamp())}"

            validation_result = await self.client.validate_profile(profile_id, test_type)

            logger.info(f"Profile validation completed: {test_type} test")
            return validation_result

        except Exception as e:
            logger.error(f"Profile validation failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'test_type': test_type,
                'timestamp': datetime.now().isoformat()
            }

    async def get_service_status(self) -> ServiceStatus:
        """
        Get the status of the fingerprint service

        Returns:
            ServiceStatus: Current service status
        """
        try:
            status = await self.client.health_check()
            return status
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return ServiceStatus(
                status="error",
                message=f"Failed to get status: {e}",
                timestamp=datetime.now()
            )

    async def wait_for_service(
        self,
        timeout_seconds: int = 60,
        check_interval: float = 2.0
    ) -> bool:
        """
        Wait for fingerprint service to become available

        Args:
            timeout_seconds: Maximum time to wait
            check_interval: Interval between status checks

        Returns:
            bool: True if service becomes available, False otherwise
        """
        return await self.client.wait_for_service(timeout_seconds, check_interval)

    def _update_generation_stats(self, generation_time: float, success: bool) -> None:
        """Update generation statistics"""
        self._stats['total_generation_time'] += generation_time

        if success:
            total_requests = self._stats['requests_made']
            if total_requests > 0:
                self._stats['average_generation_time'] = (
                    self._stats['total_generation_time'] / total_requests
                )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get generator statistics

        Returns:
            Dict containing performance and usage statistics
        """
        stats = self._stats.copy()

        # Add cache statistics if cache is enabled
        if self.cache:
            cache_stats = asyncio.run(self.cache.get_stats())
            stats.update({
                'cache_stats': cache_stats,
                'cache_hit_rate': (
                    stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses'])
                    if (stats['cache_hits'] + stats['cache_misses']) > 0 else 0.0
                )
            })

        # Add derived statistics
        stats['success_rate'] = (
            (stats['requests_made'] - stats['generation_failures']) / stats['requests_made']
            if stats['requests_made'] > 0 else 0.0
        )

        return stats

    async def clear_cache(self) -> None:
        """Clear the fingerprint cache"""
        if self.cache:
            await self.cache.clear()
            logger.info("Fingerprint cache cleared")

    async def close(self) -> None:
        """Close the fingerprint generator and clean up resources"""
        try:
            await self.client.close()
            logger.info("FingerprintGenerator closed successfully")
        except Exception as e:
            logger.error(f"Error closing FingerprintGenerator: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        # Verify service is available
        if not await self.wait_for_service(timeout_seconds=10):
            raise ServiceUnavailableError("Fingerprint service is not available")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


class ProfilePool:
    """
    Pool of pre-generated browser profiles for high-performance scenarios.

    Maintains a pool of ready-to-use profiles that can be quickly acquired
    and released, reducing API call overhead for high-frequency usage.
    """

    def __init__(
        self,
        generator: FingerprintGenerator,
        pool_size: int = 50,
        refill_threshold: float = 0.2,
        default_constraints: Optional[ProfileConstraints] = None
    ):
        self.generator = generator
        self.pool_size = pool_size
        self.refill_threshold = refill_threshold
        self.default_constraints = default_constraints

        self._pool: asyncio.Queue[BrowserProfile] = asyncio.Queue(maxsize=pool_size)
        self._lock = asyncio.Lock()
        self._refill_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start the profile pool and begin refilling"""
        async with self._lock:
            if self._running:
                return

            self._running = True

            # Initial pool fill
            await self._refill_pool()

            # Start background refill task
            self._refill_task = asyncio.create_task(self._background_refill())

            logger.info(f"ProfilePool started with size {self.pool_size}")

    async def stop(self) -> None:
        """Stop the profile pool and clean up resources"""
        async with self._lock:
            if not self._running:
                return

            self._running = False

            # Cancel background task
            if self._refill_task:
                self._refill_task.cancel()
                try:
                    await self._refill_task
                except asyncio.CancelledError:
                    pass

            # Clear pool
            while not self._pool.empty():
                try:
                    self._pool.get_nowait()
                except asyncio.QueueEmpty:
                    break

            logger.info("ProfilePool stopped")

    async def acquire(self, timeout: Optional[float] = None) -> BrowserProfile:
        """
        Acquire a profile from the pool

        Args:
            timeout: Maximum time to wait for a profile

        Returns:
            BrowserProfile: Acquired profile
        """
        if not self._running:
            raise RuntimeError("ProfilePool is not started")

        try:
            profile = await asyncio.wait_for(self._pool.get(), timeout=timeout)

            # Trigger refill if pool is getting low
            if self._pool.qsize() / self.pool_size <= self.refill_threshold:
                asyncio.create_task(self._refill_pool())

            return profile

        except asyncio.TimeoutError:
            raise RuntimeError("Timeout waiting for profile from pool")

    async def release(self, profile: BrowserProfile) -> None:
        """
        Release a profile back to the pool

        Args:
            profile: Profile to release
        """
        if not self._running:
            return

        try:
            self._pool.put_nowait(profile)
        except asyncio.QueueFull:
            # Pool is full, discard the profile
            logger.debug("ProfilePool is full, discarding released profile")

    async def _refill_pool(self) -> None:
        """Refill the pool to its target size"""
        if not self._running:
            return

        current_size = self._pool.qsize()
        needed = self.pool_size - current_size

        if needed <= 0:
            return

        logger.debug(f"Refilling ProfilePool: need {needed} profiles")

        # Generate profiles to fill the pool
        tasks = []
        for _ in range(needed):
            task = asyncio.create_task(
                self.generator.generate(constraints=self.default_constraints)
            )
            tasks.append(task)

        try:
            profiles = await asyncio.gather(*tasks, return_exceptions=True)

            for profile in profiles:
                if isinstance(profile, Exception):
                    logger.error(f"Failed to generate profile for pool: {profile}")
                    continue

                try:
                    self._pool.put_nowait(profile)
                except asyncio.QueueFull:
                    # Pool filled while generating, discard excess
                    break

            logger.debug(f"ProfilePool refill completed: {self._pool.qsize()}/{self.pool_size}")

        except Exception as e:
            logger.error(f"ProfilePool refill failed: {e}")

    async def _background_refill(self) -> None:
        """Background task to maintain pool levels"""
        while self._running:
            try:
                await asyncio.sleep(5.0)  # Check every 5 seconds

                if not self._running:
                    break

                await self._refill_pool()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background refill error: {e}")
                await asyncio.sleep(10.0)  # Wait longer on error

    def get_status(self) -> Dict[str, Any]:
        """Get pool status"""
        return {
            'running': self._running,
            'current_size': self._pool.qsize(),
            'target_size': self.pool_size,
            'utilization': self._pool.qsize() / self.pool_size if self.pool_size > 0 else 0,
            'refill_threshold': self.refill_threshold
        }