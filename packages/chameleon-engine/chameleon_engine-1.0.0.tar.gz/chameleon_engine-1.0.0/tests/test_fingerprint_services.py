"""
Tests for Fingerprint Service components.

Tests the Fingerprint Service models, API client, collectors, and validators
to ensure proper fingerprint generation, data collection, and API communication.
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

from chameleon_engine.services.fingerprint.models import (
    FingerprintRequest,
    FingerprintResponse,
    ProfileConstraints,
    ProfileMetadata,
    ValidationError,
    ServiceStatus,
    BatchFingerprintRequest,
    BatchFingerprintResponse,
    BrowserType,
    OperatingSystem
)

from chameleon_engine.services.fingerprint.client import (
    FingerprintServiceClient,
    CachingFingerprintClient,
    FingerprintServiceError,
    ServiceUnavailableError,
    ProfileGenerationError,
    ValidationError as ClientValidationError
)

from chameleon_engine.services.fingerprint.collectors import (
    RealWorldDataCollector,
    NetworkFingerprintCollector,
    DataCollectionService,
    DataSourceValidator
)

# Import test fixtures
from tests.conftest import (
    sample_browser_profile,
    sample_fingerprint_request,
    sample_fingerprint_response,
    mock_fingerprint_service,
    temp_directory,
    assert_dicts_almost_equal,
    AsyncTestCase
)


class TestFingerprintModels:
    """Test Fingerprint Service Pydantic models."""

    def test_fingerprint_request_validation(self, sample_fingerprint_request):
        """Test FingerprintRequest model validation."""
        request = FingerprintRequest(**sample_fingerprint_request)
        assert request.browser_type == BrowserType.CHROME
        assert request.operating_system == OperatingSystem.WINDOWS
        assert request.min_quality == 0.8
        assert request.max_detection_risk == 0.2

    def test_fingerprint_request_constraints(self):
        """Test FingerprintRequest with constraints."""
        constraints = ProfileConstraints(
            screen_resolution={"min_width": 1920, "min_height": 1080},
            timezone=["America/New_York", "Europe/London"],
            language=["en-US", "en-GB"],
            hardware_cores={"min": 4, "max": 16},
            memory_gb={"min": 8, "max": 32}
        )

        request = FingerprintRequest(
            browser_type="chrome",
            operating_system="windows",
            constraints=constraints
        )

        assert request.constraints.screen_resolution["min_width"] == 1920
        assert len(request.constraints.timezone) == 2
        assert request.constraints.hardware_cores["min"] == 4

    def test_fingerprint_response_validation(self, sample_browser_profile):
        """Test FingerprintResponse model validation."""
        metadata = ProfileMetadata(
            generation_time=0.5,
            coherence_score=0.95,
            uniqueness_score=0.88,
            detection_risk=0.12,
            generation_method="hybrid",
            api_version="1.0",
            quality_indicators={
                "completeness": 0.9,
                "realism": 0.92,
                "freshness": 0.85
            }
        )

        response = FingerprintResponse(
            profile=sample_browser_profile,
            metadata=metadata,
            request_id="test_req_123",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )

        assert response.profile["user_agent"] == sample_browser_profile["user_agent"]
        assert response.metadata.coherence_score == 0.95
        assert response.request_id == "test_req_123"
        assert not response.is_expired()

    def test_batch_fingerprint_request(self):
        """Test BatchFingerprintRequest model."""
        requests = [
            FingerprintRequest(
                browser_type="chrome",
                operating_system="windows",
                min_quality=0.8
            ),
            FingerprintRequest(
                browser_type="firefox",
                operating_system="linux",
                min_quality=0.7
            )
        ]

        batch_request = BatchFingerprintRequest(
            requests=requests,
            ensure_diversity=True,
            max_similarity=0.3
        )

        assert len(batch_request.requests) == 2
        assert batch_request.ensure_diversity is True
        assert batch_request.max_similarity == 0.3

    def test_service_status_model(self):
        """Test ServiceStatus model."""
        status = ServiceStatus(
            status="healthy",
            uptime=3600.0,
            version="1.0.0",
            database_status="connected",
            active_connections=10,
            performance_metrics={
                "avg_response_time": 0.5,
                "requests_per_second": 100,
                "error_rate": 0.01
            },
            last_health_check=datetime.now(timezone.utc)
        )

        assert status.status == "healthy"
        assert status.uptime == 3600.0
        assert status.database_status == "connected"
        assert status.active_connections == 10
        assert status.performance_metrics["avg_response_time"] == 0.5

    def test_validation_error_model(self):
        """Test ValidationError model."""
        validation_error = ValidationError(
            field="min_quality",
            message="Quality score must be between 0.0 and 1.0",
            value=1.5,
            allowed_range=[0.0, 1.0],
            suggestion="Use a value between 0.0 and 1.0"
        )

        assert validation_error.field == "min_quality"
        assert validation_error.message == "Quality score must be between 0.0 and 1.0"
        assert validation_error.value == 1.5
        assert validation_error.allowed_range == [0.0, 1.0]
        assert validation_error.suggestion == "Use a value between 0.0 and 1.0"


class TestFingerprintServiceClient:
    """Test FingerprintServiceClient functionality."""

    @pytest.fixture
    def client_config(self):
        """Provide client configuration for testing."""
        return {
            "base_url": "http://localhost:8000",
            "timeout": 30.0,
            "max_retries": 3,
            "retry_delay": 1.0
        }

    @pytest_asyncio.fixture
    async def mock_http_client(self):
        """Create mock HTTP client."""
        mock_client = AsyncMock()
        return mock_client

    @pytest_asyncio.fixture
    async def client(self, client_config):
        """Create FingerprintServiceClient for testing."""
        return FingerprintServiceClient(**client_config)

    async def test_client_initialization(self, client_config):
        """Test client initialization."""
        client = FingerprintServiceClient(**client_config)
        assert client.base_url == client_config["base_url"]
        assert client.timeout == client_config["timeout"]
        assert client.max_retries == client_config["max_retries"]

    async def test_get_fingerprint_success(self, client, sample_fingerprint_request, sample_fingerprint_response):
        """Test successful fingerprint generation."""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = sample_fingerprint_response

            result = await client.get_fingerprint(sample_fingerprint_request)

            assert result is not None
            assert result.profile["user_agent"] == sample_fingerprint_response["profile"]["user_agent"]
            assert result.metadata.coherence_score == sample_fingerprint_response["metadata"]["coherence_score"]
            mock_request.assert_called_once_with("POST", "/api/v1/fingerprint/generate", sample_fingerprint_request)

    async def test_get_fingerprint_service_error(self, client, sample_fingerprint_request):
        """Test fingerprint generation with service error."""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.side_effect = ServiceUnavailableError("Service down")

            with pytest.raises(ServiceUnavailableError):
                await client.get_fingerprint(sample_fingerprint_request)

    async def test_get_fingerprint_validation_error(self, client, sample_fingerprint_request):
        """Test fingerprint generation with validation error."""
        with patch.object(client, '_make_request') as mock_request:
            error_response = {
                "error": "Validation Error",
                "details": {
                    "field": "min_quality",
                    "message": "Quality score too low",
                    "value": -0.1
                }
            }
            mock_request.side_effect = ClientValidationError(error_response)

            with pytest.raises(ClientValidationError):
                await client.get_fingerprint(sample_fingerprint_request)

    async def test_batch_fingerprint_generation(self, client):
        """Test batch fingerprint generation."""
        requests = [
            FingerprintRequest(browser_type="chrome", operating_system="windows"),
            FingerprintRequest(browser_type="firefox", operating_system="linux")
        ]

        mock_responses = [
            {
                "profile": sample_browser_profile,
                "metadata": {"coherence_score": 0.9, "generation_time": 0.5},
                "request_id": "req_1"
            },
            {
                "profile": sample_browser_profile,
                "metadata": {"coherence_score": 0.85, "generation_time": 0.6},
                "request_id": "req_2"
            }
        ]

        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                "responses": mock_responses,
                "batch_id": "batch_123",
                "diversity_score": 0.7
            }

            result = await client.get_batch_fingerprints(requests)

            assert len(result.responses) == 2
            assert result.batch_id == "batch_123"
            assert result.diversity_score == 0.7

    async def test_health_check(self, client):
        """Test health check functionality."""
        mock_health_data = {
            "status": "healthy",
            "uptime": 3600.0,
            "version": "1.0.0",
            "database_status": "connected",
            "active_connections": 10
        }

        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = mock_health_data

            result = await client.health_check()

            assert result.status == "healthy"
            assert result.uptime == 3600.0
            assert result.database_status == "connected"
            mock_request.assert_called_once_with("GET", "/api/v1/health")

    async def test_validate_profile(self, client, sample_browser_profile):
        """Test profile validation."""
        validation_result = {
            "is_valid": True,
            "score": 0.92,
            "checks_performed": ["coherence", "realism", "uniqueness"],
            "issues": [],
            "suggestions": []
        }

        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = validation_result

            result = await client.validate_profile(sample_browser_profile)

            assert result.is_valid is True
            assert result.score == 0.92
            assert len(result.checks_performed) == 3

    async def test_service_statistics(self, client):
        """Test getting service statistics."""
        stats_data = {
            "total_profiles_generated": 10000,
            "active_profiles": 7500,
            "avg_generation_time": 0.8,
            "success_rate": 0.95,
            "popular_combinations": [
                {"browser": "chrome", "os": "windows", "count": 3000},
                {"browser": "firefox", "os": "linux", "count": 1500}
            ]
        }

        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = stats_data

            result = await client.get_service_statistics()

            assert result.total_profiles_generated == 10000
            assert result.active_profiles == 7500
            assert result.avg_generation_time == 0.8
            assert len(result.popular_combinations) == 2

    async def test_wait_for_service(self, client):
        """Test waiting for service availability."""
        with patch.object(client, 'health_check') as mock_health:
            # Service becomes available after 2 attempts
            mock_health.side_effect = [
                ServiceUnavailableError("Service not ready"),
                {"status": "healthy", "uptime": 100.0}
            ]

            result = await client.wait_for_service(max_wait_time=10.0, check_interval=0.1)

            assert result is True
            assert mock_health.call_count == 2

    async def test_retry_logic(self, client, sample_fingerprint_request):
        """Test retry logic on failures."""
        with patch.object(client, '_make_request') as mock_request:
            # Fail first 2 times, succeed on 3rd
            mock_request.side_effect = [
                ServiceUnavailableError("Temporary failure"),
                ServiceUnavailableError("Temporary failure"),
                sample_fingerprint_response
            ]

            result = await client.get_fingerprint(sample_fingerprint_request)

            assert result is not None
            assert mock_request.call_count == 3

    async def test_rate_limiting(self, client, sample_fingerprint_request):
        """Test rate limiting handling."""
        with patch.object(client, '_make_request') as mock_request:
            rate_limit_error = {
                "error": "Rate Limit Exceeded",
                "retry_after": 60,
                "limit": 100,
                "window": 3600
            }
            mock_request.side_effect = ClientValidationError(rate_limit_error)

            with pytest.raises(ClientValidationError) as exc_info:
                await client.get_fingerprint(sample_fingerprint_request)

            assert "Rate Limit Exceeded" in str(exc_info.value)

    async def test_connection_timeout(self, client, sample_fingerprint_request):
        """Test connection timeout handling."""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.side_effect = asyncio.TimeoutError("Connection timeout")

            with pytest.raises(ServiceUnavailableError) as exc_info:
                await client.get_fingerprint(sample_fingerprint_request)

            assert "timeout" in str(exc_info.value).lower()


class TestCachingFingerprintClient:
    """Test CachingFingerprintClient functionality."""

    @pytest_asyncio.fixture
    async def caching_client(self):
        """Create caching client for testing."""
        base_client = AsyncMock()
        cache_client = CachingFingerprintClient(
            base_client=base_client,
            cache_size=100,
            cache_ttl=3600
        )
        return cache_client, base_client

    async def test_cache_miss(self, caching_client, sample_fingerprint_request, sample_fingerprint_response):
        """Test cache miss scenario."""
        cache_client, base_client = caching_client

        # Configure mock to return response
        base_client.get_fingerprint.return_value = sample_fingerprint_response

        # First call should hit base client
        result = await cache_client.get_fingerprint(sample_fingerprint_request)

        assert result is not None
        base_client.get_fingerprint.assert_called_once_with(sample_fingerprint_request)

        # Check cache statistics
        stats = cache_client.get_cache_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 1

    async def test_cache_hit(self, caching_client, sample_fingerprint_request, sample_fingerprint_response):
        """Test cache hit scenario."""
        cache_client, base_client = caching_client

        # Configure mock to return response
        base_client.get_fingerprint.return_value = sample_fingerprint_response

        # First call (cache miss)
        result1 = await cache_client.get_fingerprint(sample_fingerprint_request)

        # Second call should hit cache
        result2 = await cache_client.get_fingerprint(sample_fingerprint_request)

        assert result1.profile["user_agent"] == result2.profile["user_agent"]
        # Base client should only be called once
        assert base_client.get_fingerprint.call_count == 1

        # Check cache statistics
        stats = cache_client.get_cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    async def test_cache_expiration(self, caching_client, sample_fingerprint_request, sample_fingerprint_response):
        """Test cache expiration."""
        cache_client, base_client = caching_client

        # Create client with short TTL
        cache_client.cache_ttl = 0.1  # 100ms

        base_client.get_fingerprint.return_value = sample_fingerprint_response

        # First call
        await cache_client.get_fingerprint(sample_fingerprint_request)

        # Wait for cache to expire
        await asyncio.sleep(0.2)

        # Second call should be cache miss
        await cache_client.get_fingerprint(sample_fingerprint_request)

        # Base client should be called twice
        assert base_client.get_fingerprint.call_count == 2

    async def test_cache_key_generation(self, caching_client):
        """Test cache key generation from requests."""
        cache_client, _ = caching_client

        request1 = FingerprintRequest(
            browser_type="chrome",
            operating_system="windows",
            min_quality=0.8
        )

        request2 = FingerprintRequest(
            browser_type="chrome",
            operating_system="windows",
            min_quality=0.8
        )

        request3 = FingerprintRequest(
            browser_type="firefox",
            operating_system="linux",
            min_quality=0.7
        )

        # Same requests should generate same keys
        key1 = cache_client._generate_cache_key(request1)
        key2 = cache_client._generate_cache_key(request2)
        key3 = cache_client._generate_cache_key(request3)

        assert key1 == key2
        assert key1 != key3

    async def test_cache_size_limit(self, caching_client):
        """Test cache size limit enforcement."""
        cache_client, base_client = caching_client

        # Set small cache size
        cache_client.cache_size = 2

        base_client.get_fingerprint.return_value = sample_fingerprint_response

        # Create different requests
        requests = []
        for i in range(4):
            request = FingerprintRequest(
                browser_type="chrome",
                operating_system="windows",
                min_quality=0.8,
                seed=f"seed_{i}"  # Different seed makes requests unique
            )
            requests.append(request)

        # Make requests to fill cache beyond limit
        for request in requests:
            await cache_client.get_fingerprint(request)

        # Cache should not exceed size limit
        stats = cache_client.get_cache_stats()
        assert stats["size"] <= cache_client.cache_size

    async def test_cache_clear(self, caching_client):
        """Test cache clearing functionality."""
        cache_client, base_client = caching_client

        base_client.get_fingerprint.return_value = sample_fingerprint_response

        # Add items to cache
        for i in range(3):
            request = FingerprintRequest(
                browser_type="chrome",
                operating_system="windows",
                seed=f"seed_{i}"
            )
            await cache_client.get_fingerprint(request)

        # Verify cache has items
        stats = cache_client.get_cache_stats()
        assert stats["size"] > 0

        # Clear cache
        cache_client.clear_cache()

        # Verify cache is empty
        stats = cache_client.get_cache_stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0


class TestRealWorldDataCollector:
    """Test RealWorldDataCollector functionality."""

    @pytest_asyncio.fixture
    async def collector(self):
        """Create data collector for testing."""
        return RealWorldDataCollector()

    async def test_user_agent_collection(self, collector):
        """Test user agent data collection."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock response with user agents
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                ]
            }
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await collector.collect_user_agents()

            assert len(result) == 3
            assert "Mozilla/5.0" in result[0]
            mock_get.assert_called()

    async def test_hardware_data_collection(self, collector):
        """Test hardware data collection."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "hardware_profiles": [
                    {
                        "screen_resolution": "1920x1080",
                        "cpu_cores": 8,
                        "memory_gb": 16,
                        "device_memory": 8
                    },
                    {
                        "screen_resolution": "1366x768",
                        "cpu_cores": 4,
                        "memory_gb": 8,
                        "device_memory": 4
                    }
                ]
            }
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await collector.collect_hardware_data()

            assert len(result) == 2
            assert result[0]["screen_resolution"] == "1920x1080"
            assert result[0]["cpu_cores"] == 8

    async def test_browser_version_collection(self, collector):
        """Test browser version data collection."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "browser_versions": {
                    "chrome": ["120.0.6099.71", "119.0.6045.123"],
                    "firefox": ["121.0", "120.0.1"],
                    "safari": ["17.2.1", "17.1.2"]
                }
            }
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await collector.collect_browser_versions()

            assert "chrome" in result
            assert "firefox" in result
            assert "safari" in result
            assert len(result["chrome"]) == 2

    async def test_data_validation(self, collector):
        """Test collected data validation."""
        # Valid user agent
        valid_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        assert collector.validate_user_agent(valid_ua) is True

        # Invalid user agent (too short)
        invalid_ua = "short"
        assert collector.validate_user_agent(invalid_ua) is False

        # Valid hardware profile
        valid_hardware = {
            "screen_resolution": "1920x1080",
            "cpu_cores": 8,
            "memory_gb": 16,
            "device_memory": 8
        }
        assert collector.validate_hardware_profile(valid_hardware) is True

        # Invalid hardware profile (negative cores)
        invalid_hardware = {
            "screen_resolution": "1920x1080",
            "cpu_cores": -4,
            "memory_gb": 16,
            "device_memory": 8
        }
        assert collector.validate_hardware_profile(invalid_hardware) is False

    async def test_collection_error_handling(self, collector):
        """Test error handling during data collection."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock network error
            mock_get.side_effect = Exception("Network error")

            result = await collector.collect_user_agents()

            # Should return empty list on error
            assert result == []

    async def test_data_deduplication(self, collector):
        """Test data deduplication functionality."""
        # Sample data with duplicates
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",  # Duplicate
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",  # Duplicate
        ]

        deduplicated = collector.deduplicate_user_agents(user_agents)

        assert len(deduplicated) == 2
        assert deduplicated[0] == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        assert deduplicated[1] == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


class TestNetworkFingerprintCollector:
    """Test NetworkFingerprintCollector functionality."""

    @pytest_asyncio.fixture
    async def network_collector(self):
        """Create network fingerprint collector for testing."""
        return NetworkFingerprintCollector()

    async def test_tls_fingerprint_collection(self, network_collector):
        """Test TLS fingerprint collection."""
        with patch('subprocess.run') as mock_run:
            # Mock openssl output
            mock_run.return_value.stdout = """
TLS Handshake Protocol
    ClientHello
        Version: TLS 1.2 (0x0303)
        Cipher Suites: TLS_AES_128_GCM_SHA256, TLS_AES_256_GCM_SHA384
        Extensions: server_name, supported_groups, signature_algorithms
"""

            result = await network_collector.collect_tls_fingerprint("https://example.com")

            assert result is not None
            assert "cipher_suites" in result
            assert "extensions" in result
            mock_run.assert_called()

    async def test_http2_settings_collection(self, network_collector):
        """Test HTTP/2 settings collection."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.headers = {
                "content-type": "application/json",
                "server": "nginx/1.18.0"
            }

            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

            result = await network_collector.collect_http2_settings("https://example.com")

            assert result is not None
            assert "headers" in result
            assert "server" in result["headers"]

    async def test_dns_pattern_collection(self, network_collector):
        """Test DNS pattern collection."""
        with patch('socket.getaddrinfo') as mock_getaddrinfo:
            # Mock DNS response
            mock_getaddrinfo.return_value = [
                (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 80)),
                (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2606:2800:220:1:248:1893:25c8:1946', 80))
            ]

            result = await network_collector.collect_dns_patterns("example.com")

            assert result is not None
            assert "ipv4_addresses" in result
            assert "ipv6_addresses" in result
            assert len(result["ipv4_addresses"]) >= 1

    async def test_ja3_hash_calculation(self, network_collector):
        """Test JA3 hash calculation."""
        sample_client_hello = {
            "version": "771",  # TLS 1.2
            "cipher_suites": ["c02b,c02f,c02c"],
            "extensions": ["0,5,10,11"],
            "elliptic_curves": ["23,24,25"],
            "elliptic_curve_point_formats": ["0"]
        }

        ja3_hash = network_collector.calculate_ja3_hash(sample_client_hello)

        assert ja3_hash is not None
        assert len(ja3_hash) == 32  # MD5 hash length

    async def test_ja4_hash_calculation(self, network_collector):
        """Test JA4 hash calculation."""
        sample_client_hello = {
            "version": "771",
            "cipher_suites": ["c02b,c02f,c02c"],
            "extensions": ["0,5,10,11"],
            "signature_algorithms": ["0403,0804,0401"],
            "supported_groups": ["23,24,25"]
        }

        ja4_hash = network_collector.calculate_ja4_hash(sample_client_hello)

        assert ja4_hash is not None
        assert len(ja4_hash) >= 50  # JA4 hashes are longer

    async def test_network_fingerprint_validation(self, network_collector):
        """Test network fingerprint validation."""
        # Valid TLS fingerprint
        valid_tls = {
            "ja3_hash": "c3b4b1f5c1234567890abcdef1234567890abcdef",
            "cipher_suites": ["TLS_AES_128_GCM_SHA256", "TLS_AES_256_GCM_SHA384"],
            "extensions": ["server_name", "supported_groups"]
        }
        assert network_collector.validate_tls_fingerprint(valid_tls) is True

        # Invalid TLS fingerprint (missing fields)
        invalid_tls = {
            "ja3_hash": "c3b4b1f5c1234567890abcdef1234567890abcdef"
        }
        assert network_collector.validate_tls_fingerprint(invalid_tls) is False

        # Valid HTTP/2 settings
        valid_http2 = {
            "header_table_size": 4096,
            "enable_push": False,
            "max_concurrent_streams": 1000
        }
        assert network_collector.validate_http2_settings(valid_http2) is True

        # Invalid HTTP/2 settings (negative values)
        invalid_http2 = {
            "header_table_size": -100,
            "enable_push": False,
            "max_concurrent_streams": 1000
        }
        assert network_collector.validate_http2_settings(invalid_http2) is False


class TestDataCollectionService:
    """Test DataCollectionService functionality."""

    @pytest_asyncio.fixture
    async def collection_service(self, temp_directory):
        """Create data collection service for testing."""
        config = {
            "data_dir": str(temp_directory),
            "collection_interval": 3600,  # 1 hour
            "max_records_per_source": 10000,
            "validation_threshold": 0.8
        }
        return DataCollectionService(config)

    async def test_service_initialization(self, collection_service):
        """Test service initialization."""
        assert collection_service.config["collection_interval"] == 3600
        assert collection_service.config["max_records_per_source"] == 10000

    async def test_collection_job_execution(self, collection_service):
        """Test collection job execution."""
        with patch.object(collection_service.real_world_collector, 'collect_user_agents') as mock_ua:
            with patch.object(collection_service.network_collector, 'collect_tls_fingerprint') as mock_tls:
                mock_ua.return_value = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                ]
                mock_tls.return_value = {
                    "ja3_hash": "c3b4b1f5c1234567890abcdef1234567890abcdef",
                    "cipher_suites": ["TLS_AES_128_GCM_SHA256"]
                }

                result = await collection_service.execute_collection_job()

                assert result["success"] is True
                assert result["user_agents_collected"] == 2
                assert result["tls_fingerprints_collected"] == 1
                assert "collection_id" in result

    async def test_scheduled_collection(self, collection_service):
        """Test scheduled data collection."""
        collection_jobs = []

        async def mock_job():
            job = await collection_service.execute_collection_job()
            collection_jobs.append(job)

        # Schedule multiple jobs
        tasks = []
        for _ in range(3):
            task = asyncio.create_task(mock_job())
            tasks.append(task)

        # Wait for all jobs to complete
        await asyncio.gather(*tasks)

        assert len(collection_jobs) == 3
        for job in collection_jobs:
            assert job["success"] is True

    async def test_collection_error_handling(self, collection_service):
        """Test error handling in collection jobs."""
        with patch.object(collection_service.real_world_collector, 'collect_user_agents') as mock_ua:
            mock_ua.side_effect = Exception("Collection failed")

            result = await collection_service.execute_collection_job()

            assert result["success"] is False
            assert "error" in result
            assert "Collection failed" in result["error"]

    async def test_data_storage(self, collection_service, temp_directory):
        """Test data storage functionality."""
        # Sample collected data
        collected_data = {
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ],
            "hardware_profiles": [
                {"screen_resolution": "1920x1080", "cpu_cores": 8}
            ],
            "tls_fingerprints": [
                {"ja3_hash": "c3b4b1f5c1234567890abcdef1234567890abcdef"}
            ]
        }

        # Store data
        collection_id = "test_collection_123"
        await collection_service.store_collected_data(collection_id, collected_data)

        # Verify storage
        stored_file = temp_directory / f"collection_{collection_id}.json"
        assert stored_file.exists()

        with open(stored_file, 'r') as f:
            stored_data = json.load(f)

        assert stored_data["collection_id"] == collection_id
        assert len(stored_data["data"]["user_agents"]) == 1
        assert stored_data["data"]["user_agents"][0] == collected_data["user_agents"][0]

    async def test_collection_statistics(self, collection_service):
        """Test collection statistics tracking."""
        # Execute some collection jobs
        for i in range(5):
            with patch.object(collection_service.real_world_collector, 'collect_user_agents') as mock_ua:
                mock_ua.return_value = [f"UA_{i}"]
                await collection_service.execute_collection_job()

        stats = collection_service.get_collection_statistics()

        assert stats["total_collections"] == 5
        assert stats["successful_collections"] == 5
        assert stats["failed_collections"] == 0
        assert stats["success_rate"] == 1.0
        assert stats["total_records_collected"] == 5

    async def test_data_cleanup(self, collection_service, temp_directory):
        """Test old data cleanup."""
        # Create old collection files
        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        for i in range(3):
            old_file = temp_directory / f"collection_old_{i}.json"
            old_data = {
                "collection_id": f"old_{i}",
                "timestamp": old_date.isoformat(),
                "data": {"user_agents": [f"old_ua_{i}"]}
            }
            with open(old_file, 'w') as f:
                json.dump(old_data, f)

        # Create recent collection files
        for i in range(2):
            recent_file = temp_directory / f"collection_recent_{i}.json"
            recent_data = {
                "collection_id": f"recent_{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {"user_agents": [f"recent_ua_{i}"]}
            }
            with open(recent_file, 'w') as f:
                json.dump(recent_data, f)

        # Run cleanup (keep data for 7 days)
        await collection_service.cleanup_old_data(days_to_keep=7)

        # Verify old files are deleted, recent files remain
        remaining_files = list(temp_directory.glob("collection_*.json"))
        assert len(remaining_files) == 2
        for file in remaining_files:
            assert "recent" in file.name


class TestDataSourceValidator:
    """Test DataSourceValidator functionality."""

    @pytest_asyncio.fixture
    async def validator(self):
        """Create data source validator for testing."""
        return DataSourceValidator()

    async def test_user_agent_validation(self, validator):
        """Test user agent validation."""
        # Valid user agents
        valid_uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]

        for ua in valid_uas:
            result = await validator.validate_user_agent(ua)
            assert result.is_valid is True
            assert result.score > 0.8

        # Invalid user agents
        invalid_uas = [
            "short",
            "Mozilla/5.0 (invalid format)",
            "",
            "bot/1.0"
        ]

        for ua in invalid_uas:
            result = await validator.validate_user_agent(ua)
            assert result.is_valid is False
            assert result.score < 0.5

    async def test_hardware_profile_validation(self, validator):
        """Test hardware profile validation."""
        # Valid hardware profiles
        valid_hardware = [
            {"screen_resolution": "1920x1080", "cpu_cores": 8, "memory_gb": 16, "device_memory": 8},
            {"screen_resolution": "1366x768", "cpu_cores": 4, "memory_gb": 8, "device_memory": 4},
            {"screen_resolution": "2560x1440", "cpu_cores": 16, "memory_gb": 32, "device_memory": 16}
        ]

        for hardware in valid_hardware:
            result = await validator.validate_hardware_profile(hardware)
            assert result.is_valid is True
            assert result.score > 0.7

        # Invalid hardware profiles
        invalid_hardware = [
            {"screen_resolution": "0x0", "cpu_cores": 8, "memory_gb": 16},  # Invalid resolution
            {"screen_resolution": "1920x1080", "cpu_cores": 0, "memory_gb": 16},  # Invalid cores
            {"screen_resolution": "1920x1080", "cpu_cores": 8, "memory_gb": -1}  # Invalid memory
        ]

        for hardware in invalid_hardware:
            result = await validator.validate_hardware_profile(hardware)
            assert result.is_valid is False
            assert result.score < 0.5

    async def test_network_fingerprint_validation(self, validator):
        """Test network fingerprint validation."""
        # Valid TLS fingerprints
        valid_tls = [
            {
                "ja3_hash": "c3b4b1f5c1234567890abcdef1234567890abcdef",
                "cipher_suites": ["TLS_AES_128_GCM_SHA256", "TLS_AES_256_GCM_SHA384"],
                "extensions": ["server_name", "supported_groups", "signature_algorithms"],
                "version": "771"
            },
            {
                "ja3_hash": "a1b2c3d4e5f6789012345678901234567890abcd",
                "cipher_suites": ["TLS_CHACHA20_POLY1305_SHA256", "TLS_AES_128_GCM_SHA256"],
                "extensions": ["server_name", "supported_groups"],
                "version": "771"
            }
        ]

        for tls in valid_tls:
            result = await validator.validate_tls_fingerprint(tls)
            assert result.is_valid is True
            assert result.score > 0.8

        # Invalid TLS fingerprints
        invalid_tls = [
            {"ja3_hash": "short"},  # Too short hash
            {"cipher_suites": ["invalid_cipher"]},  # Missing required fields
            {"ja3_hash": "invalid_hash_chars!@#", "cipher_suites": []}  # Invalid characters
        ]

        for tls in invalid_tls:
            result = await validator.validate_tls_fingerprint(tls)
            assert result.is_valid is False
            assert result.score < 0.5

    async def test_batch_validation(self, validator):
        """Test batch validation functionality."""
        # Sample batch data
        batch_data = {
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "invalid_ua",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
            ],
            "hardware_profiles": [
                {"screen_resolution": "1920x1080", "cpu_cores": 8, "memory_gb": 16},
                {"screen_resolution": "0x0", "cpu_cores": 4, "memory_gb": 8}  # Invalid
            ]
        }

        result = await validator.validate_batch(batch_data)

        assert result.total_validated == 5  # 3 UAs + 2 hardware profiles
        assert result.valid_count == 3
        assert result.invalid_count == 2
        assert result.overall_score > 0.5

        # Check detailed results
        assert len(result.user_agent_results) == 3
        assert len(result.hardware_results) == 2
        assert result.user_agent_results[1].is_valid is False  # invalid_ua
        assert result.hardware_results[1].is_valid is False  # invalid resolution

    async def test_quality_scoring(self, validator):
        """Test quality scoring algorithms."""
        # High quality data
        high_quality_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        high_quality_result = await validator.validate_user_agent(high_quality_ua)
        assert high_quality_result.score > 0.9

        # Medium quality data
        medium_quality_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        medium_quality_result = await validator.validate_user_agent(medium_quality_ua)
        assert 0.5 < medium_quality_result.score < 0.9

        # Low quality data
        low_quality_ua = "some browser"
        low_quality_result = await validator.validate_user_agent(low_quality_ua)
        assert low_quality_result.score < 0.5

    async def test_validation_rules_configuration(self, validator):
        """Test validation rules configuration."""
        # Configure strict validation
        validator.set_validation_mode("strict")

        strict_result = await validator.validate_user_agent("Mozilla/5.0 Chrome/120.0")
        assert strict_result.is_valid is False  # Should fail under strict mode

        # Configure lenient validation
        validator.set_validation_mode("lenient")

        lenient_result = await validator.validate_user_agent("Mozilla/5.0 Chrome/120.0")
        assert lenient_result.is_valid is True  # Should pass under lenient mode

        # Reset to default
        validator.set_validation_mode("default")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])