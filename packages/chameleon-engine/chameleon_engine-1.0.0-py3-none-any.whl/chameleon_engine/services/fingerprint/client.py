"""
Fingerprint Service API client.

This module provides a Python client for communicating with the FastAPI fingerprint
service that generates realistic browser profiles with network-level fingerprints.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .models import (
    FingerprintRequest,
    FingerprintResponse,
    FingerprintError,
    ServiceStatus,
    BatchFingerprintRequest,
    BatchFingerprintResponse
)
from ...core.profiles import BrowserProfile

logger = logging.getLogger(__name__)


class FingerprintServiceClientError(Exception):
    """Base exception for fingerprint service client errors."""
    pass


class FingerprintServiceUnavailableError(FingerprintServiceClientError):
    """Exception raised when the fingerprint service is unavailable."""
    pass


class FingerprintServiceClient:
    """
    Client for communicating with the Fingerprint Service API.

    This client handles all communication with the FastAPI fingerprint service,
    including error handling, retries, and response parsing.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        max_retries: int = 3,
        api_key: Optional[str] = None
    ):
        """
        Initialize the fingerprint service client.

        Args:
            base_url: Base URL of the fingerprint service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.api_key = api_key

        # Configure HTTP client
        self.client_config = {
            'timeout': httpx.Timeout(timeout),
            'headers': {
                'User-Agent': 'ChameleonEngine/1.0 FingerprintClient',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }

        if api_key:
            self.client_config['headers']['Authorization'] = f'Bearer {api_key}'

        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(**self.client_config)
            logger.info(f"Fingerprint service client started for {self.base_url}")

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Fingerprint service client closed")

    def _ensure_client(self):
        """Ensure the HTTP client is initialized."""
        if self._client is None:
            raise FingerprintServiceClientError(
                "Client not started. Call await client.start() or use async context manager."
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    async def get_fingerprint(self, request: FingerprintRequest) -> FingerprintResponse:
        """
        Fetch a fresh fingerprint from the service.

        Args:
            request: Fingerprint request with specifications

        Returns:
            FingerprintResponse with generated profile

        Raises:
            FingerprintServiceClientError: If the request fails
        """
        self._ensure_client()

        try:
            logger.info(f"Requesting fingerprint: {request.browser_type}/{request.operating_system}")

            response = await self._client.post(
                f"{self.base_url}/api/v1/fingerprint",
                json=request.model_dump(exclude_none=True)
            )
            response.raise_for_status()

            data = response.json()
            fingerprint_response = FingerprintResponse.model_validate(data)

            logger.info(f"Successfully generated fingerprint: {fingerprint_response.profile_id}")
            return fingerprint_response

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Fingerprint service error ({e.response.status_code}): {error_data.get('error_message', 'Unknown error')}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

        except httpx.RequestError as e:
            error_msg = f"Failed to connect to fingerprint service: {str(e)}"
            logger.error(error_msg)
            raise FingerprintServiceUnavailableError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error requesting fingerprint: {str(e)}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

    async def get_batch_fingerprints(
        self,
        requests: List[FingerprintRequest],
        ensure_diversity: bool = True
    ) -> BatchFingerprintResponse:
        """
        Generate multiple fingerprints in a single request.

        Args:
            requests: List of fingerprint requests
            ensure_diversity: Whether to ensure generated profiles are diverse

        Returns:
            BatchFingerprintResponse with results

        Raises:
            FingerprintServiceClientError: If the request fails
        """
        self._ensure_client()

        try:
            batch_request = BatchFingerprintRequest(
                requests=requests,
                ensure_diversity=ensure_diversity
            )

            logger.info(f"Requesting batch of {len(requests)} fingerprints")

            response = await self._client.post(
                f"{self.base_url}/api/v1/fingerprint/batch",
                json=batch_request.model_dump(exclude_none=True)
            )
            response.raise_for_status()

            data = response.json()
            batch_response = BatchFingerprintResponse.model_validate(data)

            logger.info(f"Batch request completed: {batch_response.total_successful}/{batch_response.total_requested} successful")
            return batch_response

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Batch fingerprint service error ({e.response.status_code}): {error_data.get('error_message', 'Unknown error')}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error requesting batch fingerprints: {str(e)}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

    async def health_check(self) -> ServiceStatus:
        """
        Check if the fingerprint service is healthy.

        Returns:
            ServiceStatus with health information

        Raises:
            FingerprintServiceClientError: If the health check fails
        """
        self._ensure_client()

        try:
            response = await self._client.get(f"{self.base_url}/health")
            response.raise_for_status()

            data = response.json()
            status = ServiceStatus.model_validate(data)

            logger.info(f"Service health check: {status.status} (uptime: {status.uptime_seconds}s)")
            return status

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Health check failed ({e.response.status_code}): {error_data.get('error_message', 'Unknown error')}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error during health check: {str(e)}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

    async def get_profile_by_id(self, profile_id: str) -> Optional[FingerprintResponse]:
        """
        Retrieve a specific profile by ID.

        Args:
            profile_id: Unique profile identifier

        Returns:
            FingerprintResponse if found, None otherwise

        Raises:
            FingerprintServiceClientError: If the request fails
        """
        self._ensure_client()

        try:
            response = await self._client.get(f"{self.base_url}/api/v1/fingerprint/{profile_id}")

            if response.status_code == 404:
                logger.warning(f"Profile not found: {profile_id}")
                return None

            response.raise_for_status()

            data = response.json()
            fingerprint_response = FingerprintResponse.model_validate(data)

            logger.info(f"Retrieved profile: {profile_id}")
            return fingerprint_response

        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                error_data = self._extract_error_data(e.response)
                error_msg = f"Failed to retrieve profile ({e.response.status_code}): {error_data.get('error_message', 'Unknown error')}"
                logger.error(error_msg)
                raise FingerprintServiceClientError(error_msg) from e
            return None

        except Exception as e:
            error_msg = f"Unexpected error retrieving profile: {str(e)}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

    async def validate_profile(self, profile_id: str, test_type: str = "synthetic") -> Dict[str, Any]:
        """
        Validate a profile against anti-bot detection.

        Args:
            profile_id: Profile identifier to validate
            test_type: Type of validation test to perform

        Returns:
            Validation results

        Raises:
            FingerprintServiceClientError: If validation fails
        """
        self._ensure_client()

        try:
            response = await self._client.post(
                f"{self.base_url}/api/v1/fingerprint/{profile_id}/validate",
                json={"test_type": test_type}
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Profile validation completed for {profile_id}: {data.get('result', 'unknown')}")
            return data

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Profile validation failed ({e.response.status_code}): {error_data.get('error_message', 'Unknown error')}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error during profile validation: {str(e)}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

    async def get_service_statistics(self) -> Dict[str, Any]:
        """
        Get service statistics and metrics.

        Returns:
            Service statistics

        Raises:
            FingerprintServiceClientError: If the request fails
        """
        self._ensure_client()

        try:
            response = await self._client.get(f"{self.base_url}/api/v1/statistics")
            response.raise_for_status()

            data = response.json()
            logger.info("Retrieved service statistics")
            return data

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Failed to get statistics ({e.response.status_code}): {error_data.get('error_message', 'Unknown error')}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error getting statistics: {str(e)}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

    async def report_usage(
        self,
        profile_id: str,
        success: bool,
        target_domain: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        detected_as_bot: Optional[bool] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Report usage of a profile for analytics.

        Args:
            profile_id: Profile identifier
            success: Whether the usage was successful
            target_domain: Target domain if applicable
            response_time_ms: Response time in milliseconds
            detected_as_bot: Whether the profile was detected as a bot
            error_message: Error message if usage failed

        Returns:
            True if reported successfully

        Raises:
            FingerprintServiceClientError: If reporting fails
        """
        self._ensure_client()

        try:
            usage_data = {
                "success": success,
                "usage_timestamp": datetime.utcnow().isoformat()
            }

            if target_domain:
                usage_data["target_domain"] = target_domain
            if response_time_ms is not None:
                usage_data["response_time_ms"] = response_time_ms
            if detected_as_bot is not None:
                usage_data["detected_as_bot"] = detected_as_bot
            if error_message:
                usage_data["error_message"] = error_message

            response = await self._client.post(
                f"{self.base_url}/api/v1/fingerprint/{profile_id}/usage",
                json=usage_data
            )
            response.raise_for_status()

            logger.debug(f"Usage reported for profile {profile_id}: success={success}")
            return True

        except httpx.HTTPStatusError as e:
            error_data = self._extract_error_data(e.response)
            error_msg = f"Failed to report usage ({e.response.status_code}): {error_data.get('error_message', 'Unknown error')}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error reporting usage: {str(e)}"
            logger.error(error_msg)
            raise FingerprintServiceClientError(error_msg) from e

    def _extract_error_data(self, response: httpx.Response) -> Dict[str, Any]:
        """Extract error data from HTTP response."""
        try:
            return response.json()
        except Exception:
            return {
                "error_code": f"HTTP_{response.status_code}",
                "error_message": response.text or f"HTTP {response.status_code} error"
            }

    async def wait_for_service(self, max_wait_seconds: int = 60) -> bool:
        """
        Wait for the fingerprint service to become available.

        Args:
            max_wait_seconds: Maximum time to wait in seconds

        Returns:
            True if service becomes available, False otherwise
        """
        logger.info(f"Waiting for fingerprint service at {self.base_url} (max {max_wait_seconds}s)")

        start_time = datetime.utcnow()
        wait_interval = 2.0  # Start with 2 seconds

        while True:
            try:
                await self.start()
                status = await self.health_check()

                if status.status == "healthy":
                    logger.info("Fingerprint service is healthy and ready")
                    return True
                else:
                    logger.warning(f"Service status: {status.status}, waiting...")

            except Exception as e:
                logger.debug(f"Service not ready yet: {str(e)}")

            # Check timeout
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed >= max_wait_seconds:
                logger.error(f"Timeout waiting for service after {max_wait_seconds}s")
                return False

            # Wait with exponential backoff
            await asyncio.sleep(min(wait_interval, max_wait_seconds - elapsed))
            wait_interval *= 1.5  # Exponential backoff

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the fingerprint service.

        Returns:
            Test results with connection information

        Raises:
            FingerprintServiceClientError: If connection test fails
        """
        try:
            await self.start()

            # Test basic connectivity
            health = await self.health_check()

            # Test fingerprint generation
            test_request = FingerprintRequest(
                browser_type="chrome",
                operating_system="windows",
                include_advanced_fingerprinting=False
            )

            start_time = datetime.utcnow()
            test_fingerprint = await self.get_fingerprint(test_request)
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                "connection_status": "success",
                "service_status": health.status,
                "response_time_ms": response_time,
                "test_profile_id": test_fingerprint.profile_id,
                "api_version": health.api_version,
                "uptime_seconds": health.uptime_seconds
            }

        except Exception as e:
            return {
                "connection_status": "failed",
                "error": str(e),
                "service_url": self.base_url
            }

        finally:
            await self.close()


class CachingFingerprintClient:
    """
    Fingerprint service client with local caching capabilities.

    This client extends the base client with caching functionality to improve
    performance and reduce load on the fingerprint service.
    """

    def __init__(
        self,
        base_client: FingerprintServiceClient,
        cache_ttl_seconds: int = 3600,  # 1 hour default
        max_cache_size: int = 1000
    ):
        """
        Initialize the caching fingerprint client.

        Args:
            base_client: Base fingerprint service client
            cache_ttl_seconds: Time to live for cached profiles
            max_cache_size: Maximum number of cached profiles
        """
        self.client = base_client
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_cache_size = max_cache_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    async def get_fingerprint(self, request: FingerprintRequest) -> FingerprintResponse:
        """
        Get fingerprint with caching.

        Args:
            request: Fingerprint request

        Returns:
            Fingerprint response from cache or service
        """
        cache_key = self._generate_cache_key(request)
        cached = self._get_from_cache(cache_key)

        if cached:
            self._cache_hits += 1
            logger.debug(f"Cache hit for fingerprint: {cache_key}")
            return FingerprintResponse.model_validate(cached['data'])

        # Cache miss - fetch from service
        self._cache_misses += 1
        response = await self.client.get_fingerprint(request)

        # Store in cache
        self._store_in_cache(cache_key, response)

        return response

    def _generate_cache_key(self, request: FingerprintRequest) -> str:
        """Generate cache key from request."""
        key_parts = [
            request.browser_type or "chrome",
            request.operating_system or "windows",
            request.version or "latest",
            str(request.mobile or False),
            request.locale or "en-US"
        ]

        # Add constraints if present
        if request.constraints:
            constraints = request.constraints
            if constraints.browser_types:
                key_parts.append(f"browsers:{','.join(constraints.browser_types)}")
            if constraints.operating_systems:
                key_parts.append(f"os:{','.join(constraints.operating_systems)}")
            if constraints.min_browser_version:
                key_parts.append(f"min_ver:{constraints.min_browser_version}")

        return "|".join(key_parts)

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get item from cache if valid."""
        if cache_key not in self._cache:
            return None

        cached_item = self._cache[cache_key]
        age = (datetime.utcnow() - cached_item['timestamp']).total_seconds()

        if age > self.cache_ttl_seconds:
            # Expired - remove from cache
            del self._cache[cache_key]
            return None

        return cached_item

    def _store_in_cache(self, cache_key: str, response: FingerprintResponse):
        """Store item in cache."""
        # Implement LRU eviction if cache is full
        if len(self._cache) >= self.max_cache_size:
            # Remove oldest item (simple LRU)
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]['timestamp'])
            del self._cache[oldest_key]

        self._cache[cache_key] = {
            'data': response.model_dump(),
            'timestamp': datetime.utcnow()
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0

        return {
            'cache_size': len(self._cache),
            'max_cache_size': self.max_cache_size,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate': hit_rate,
            'ttl_seconds': self.cache_ttl_seconds
        }

    def clear_cache(self):
        """Clear all cached items."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Fingerprint cache cleared")