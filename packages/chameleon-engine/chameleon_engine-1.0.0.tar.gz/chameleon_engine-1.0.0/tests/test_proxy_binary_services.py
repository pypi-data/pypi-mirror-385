"""
Tests for Proxy and Binary Service components.

Tests the Go Proxy Manager, Custom Binary Manager, and related functionality
to ensure proper proxy lifecycle management, binary handling, and integration.
"""

import pytest
import asyncio
import json
import tempfile
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List, Optional

from chameleon_engine.services.proxy.manager import (
    GoProxyManager,
    ProxyConfig,
    ProxyManagerPool,
    ProxyStatus,
    ProxyHealthInfo
)

from chameleon_engine.services.binary.manager import (
    CustomBinaryManager,
    BinaryDownloader,
    BinaryValidator,
    BinaryConfig,
    BinaryInfo,
    BinaryType,
    BinaryStatus,
    BinaryValidationError
)

# Import test fixtures
from tests.conftest import (
    sample_browser_profile,
    proxy_config,
    binary_config,
    temp_directory,
    assert_dicts_almost_equal,
    AsyncTestCase
)


class TestProxyConfig:
    """Test ProxyConfig model validation and functionality."""

    def test_proxy_config_creation(self, proxy_config):
        """Test creating proxy configuration."""
        config = ProxyConfig(**proxy_config)
        assert config.host == proxy_config["host"]
        assert config.port == proxy_config["port"]
        assert config.proxy_type == proxy_config["proxy_type"]
        assert config.timeout == proxy_config["timeout"]

    def test_proxy_config_validation(self):
        """Test proxy configuration validation."""
        # Valid configurations
        valid_configs = [
            {"host": "127.0.0.1", "port": 8080, "proxy_type": "http"},
            {"host": "localhost", "port": 3128, "proxy_type": "socks5"},
            {"host": "192.168.1.100", "port": 8888, "proxy_type": "https", "username": "user", "password": "pass"}
        ]

        for config_data in valid_configs:
            config = ProxyConfig(**config_data)
            assert config.host == config_data["host"]
            assert config.port == config_data["port"]
            assert config.proxy_type == config_data["proxy_type"]

        # Invalid configurations
        invalid_configs = [
            {"host": "", "port": 8080, "proxy_type": "http"},  # Empty host
            {"host": "127.0.0.1", "port": 0, "proxy_type": "http"},  # Invalid port
            {"host": "127.0.0.1", "port": 70000, "proxy_type": "http"},  # Port too high
            {"host": "127.0.0.1", "port": 8080, "proxy_type": "invalid"}  # Invalid proxy type
        ]

        for config_data in invalid_configs:
            with pytest.raises(Exception):
                ProxyConfig(**config_data)

    def test_proxy_config_authentication(self):
        """Test proxy configuration with authentication."""
        # With authentication
        auth_config = ProxyConfig(
            host="127.0.0.1",
            port=8080,
            username="testuser",
            password="testpass"
        )
        assert auth_config.username == "testuser"
        assert auth_config.password == "testpass"
        assert auth_config.has_auth() is True

        # Without authentication
        no_auth_config = ProxyConfig(host="127.0.0.1", port=8080)
        assert no_auth_config.username is None
        assert no_auth_config.password is None
        assert no_auth_config.has_auth() is False

    def test_proxy_config_url_generation(self):
        """Test proxy URL generation."""
        # HTTP proxy without auth
        config = ProxyConfig(host="127.0.0.1", port=8080, proxy_type="http")
        assert config.get_url() == "http://127.0.0.1:8080"

        # SOCKS5 proxy with auth
        config = ProxyConfig(
            host="127.0.0.1",
            port=1080,
            proxy_type="socks5",
            username="user",
            password="pass"
        )
        assert config.get_url() == "socks5://user:pass@127.0.0.1:1080"

    def test_proxy_config_optimization_presets(self):
        """Test proxy configuration optimization presets."""
        # High performance preset
        high_perf = ProxyConfig.optimization_preset("high_performance")
        assert high_perf.timeout == 10.0
        assert high_perf.max_connections == 1000

        # Stealth preset
        stealth = ProxyConfig.optimization_preset("stealth")
        assert stealth.timeout == 30.0
        assert stealth.rotate_tls is True
        assert stealth.rewrite_headers is True

        # Testing preset
        testing = ProxyConfig.optimization_preset("testing")
        assert testing.timeout == 5.0
        assert testing.validate_certificates is False


class TestGoProxyManager:
    """Test GoProxyManager functionality."""

    @pytest_asyncio.fixture
    async def proxy_manager(self, temp_directory):
        """Create GoProxyManager for testing."""
        config = ProxyConfig(
            host="127.0.0.1",
            port=8080,
            data_dir=str(temp_directory),
            binary_path="/mock/go-proxy-binary"
        )
        return GoProxyManager(config)

    async def test_proxy_initialization(self, proxy_manager):
        """Test proxy manager initialization."""
        assert proxy_manager.config.host == "127.0.0.1"
        assert proxy_manager.config.port == 8080
        assert proxy_manager.status == ProxyStatus.STOPPED
        assert proxy_manager.process is None

    async def test_proxy_start_success(self, proxy_manager):
        """Test successful proxy start."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.pid = 12345
            mock_process.returncode = None
            mock_subprocess.return_value = mock_process

            # Mock health check to succeed
            with patch.object(proxy_manager, '_wait_for_ready') as mock_ready:
                mock_ready.return_value = True

                result = await proxy_manager.start()

                assert result is True
                assert proxy_manager.status == ProxyStatus.RUNNING
                assert proxy_manager.process == mock_process
                mock_subprocess.assert_called_once()

    async def test_proxy_start_failure(self, proxy_manager):
        """Test proxy start failure."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.side_effect = Exception("Failed to start proxy")

            with pytest.raises(Exception) as exc_info:
                await proxy_manager.start()

            assert "Failed to start proxy" in str(exc_info.value)
            assert proxy_manager.status == ProxyStatus.ERROR

    async def test_proxy_stop(self, proxy_manager):
        """Test proxy stop functionality."""
        # First start the proxy
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.pid = 12345
            mock_process.returncode = None
            mock_subprocess.return_value = mock_process

            with patch.object(proxy_manager, '_wait_for_ready') as mock_ready:
                mock_ready.return_value = True
                await proxy_manager.start()

        # Now stop it
        mock_process.terminate = AsyncMock()
        mock_process.wait = AsyncMock()

        result = await proxy_manager.stop()

        assert result is True
        assert proxy_manager.status == ProxyStatus.STOPPED
        mock_process.terminate.assert_called_once()

    async def test_proxy_set_profile(self, proxy_manager, sample_browser_profile):
        """Test setting browser profile in proxy."""
        # Mock successful profile setting
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"success": True}
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await proxy_manager.set_profile(sample_browser_profile)

            assert result is True
            mock_post.assert_called_once()

            # Verify the profile data was sent correctly
            call_args = mock_post.call_args
            assert "json" in call_args.kwargs
            sent_profile = call_args.kwargs["json"]
            assert sent_profile["user_agent"] == sample_browser_profile["user_agent"]

    async def test_proxy_set_profile_failure(self, proxy_manager, sample_browser_profile):
        """Test profile setting failure."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_response.json.return_value = {"error": "Invalid profile"}
            mock_post.return_value.__aenter__.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await proxy_manager.set_profile(sample_browser_profile)

            assert "Invalid profile" in str(exc_info.value)

    async def test_proxy_health_check(self, proxy_manager):
        """Test proxy health check."""
        mock_health_data = {
            "status": "healthy",
            "uptime": 1800.0,
            "connections": 10,
            "memory_usage": 50.0,
            "cpu_usage": 5.0,
            "last_request": datetime.now(timezone.utc).isoformat()
        }

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_health_data
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await proxy_manager.health_check()

            assert result.status == "healthy"
            assert result.uptime == 1800.0
            assert result.connections == 10
            assert result.memory_usage == 50.0

    async def test_proxy_connection_stats(self, proxy_manager):
        """Test getting proxy connection statistics."""
        mock_stats = {
            "total_connections": 1000,
            "active_connections": 25,
            "failed_connections": 5,
            "avg_response_time": 0.15,
            "data_transferred": 1048576,  # 1MB
            "connection_types": {
                "http": 800,
                "https": 200
            }
        }

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_stats
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await proxy_manager.get_connection_stats()

            assert result.total_connections == 1000
            assert result.active_connections == 25
            assert result.failed_connections == 5
            assert result.avg_response_time == 0.15
            assert result.data_transferred == 1048576

    async def test_proxy_wait_for_ready(self, proxy_manager):
        """Test waiting for proxy to be ready."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # First few calls fail, then succeed
            responses = [
                AsyncMock(status=503),  # Service unavailable
                AsyncMock(status=503),  # Service unavailable
                AsyncMock(status=200, json=AsyncMock(return_value={"status": "ready"}))
            ]
            mock_get.return_value.__aenter__.side_effect = responses

            result = await proxy_manager._wait_for_ready(max_wait_time=1.0, check_interval=0.1)

            assert result is True
            assert mock_get.call_count == 3

    async def test_proxy_configuration_update(self, proxy_manager):
        """Test updating proxy configuration."""
        new_config = {
            "timeout": 60.0,
            "max_connections": 2000,
            "enable_logging": True
        }

        with patch('aiohttp.ClientSession.put') as mock_put:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"success": True}
            mock_put.return_value.__aenter__.return_value = mock_response

            result = await proxy_manager.update_configuration(new_config)

            assert result is True
            mock_put.assert_called_once()

            # Verify configuration was sent
            call_args = mock_put.call_args
            assert "json" in call_args.kwargs
            sent_config = call_args.kwargs["json"]
            assert sent_config["timeout"] == 60.0

    async def test_proxy_logs_retrieval(self, proxy_manager):
        """Test retrieving proxy logs."""
        mock_logs = [
            {
                "timestamp": "2024-01-01T12:00:00Z",
                "level": "INFO",
                "message": "Proxy started successfully",
                "connection_id": "conn_123"
            },
            {
                "timestamp": "2024-01-01T12:01:00Z",
                "level": "DEBUG",
                "message": "Processing request to https://example.com",
                "connection_id": "conn_124"
            }
        ]

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"logs": mock_logs}
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await proxy_manager.get_logs(level="DEBUG", limit=100)

            assert len(result) == 2
            assert result[0]["level"] == "INFO"
            assert result[1]["level"] == "DEBUG"
            assert "connection_id" in result[0]

    async def test_proxy_error_recovery(self, proxy_manager):
        """Test proxy error recovery mechanisms."""
        # Start proxy
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.pid = 12345
            mock_process.returncode = None
            mock_subprocess.return_value = mock_process

            with patch.object(proxy_manager, '_wait_for_ready') as mock_ready:
                mock_ready.return_value = True
                await proxy_manager.start()

        # Simulate proxy crash
        mock_process.returncode = 1

        # Health check should detect failure
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            health = await proxy_manager.health_check()
            assert proxy_manager.status == ProxyStatus.ERROR

        # Test auto-recovery
        with patch.object(proxy_manager, 'stop') as mock_stop:
            with patch.object(proxy_manager, 'start') as mock_start:
                mock_start.return_value = True

                recovered = await proxy_manager.attempt_recovery()

                assert recovered is True
                mock_stop.assert_called_once()
                mock_start.assert_called_once()


class TestProxyManagerPool:
    """Test ProxyManagerPool functionality."""

    @pytest_asyncio.fixture
    async def proxy_pool(self, temp_directory):
        """Create proxy manager pool for testing."""
        configs = [
            ProxyConfig(host="127.0.0.1", port=8080, data_dir=str(temp_directory / "proxy1")),
            ProxyConfig(host="127.0.0.1", port=8081, data_dir=str(temp_directory / "proxy2")),
            ProxyConfig(host="127.0.0.1", port=8082, data_dir=str(temp_directory / "proxy3"))
        ]
        return ProxyManagerPool(configs)

    async def test_pool_initialization(self, proxy_pool):
        """Test proxy pool initialization."""
        assert len(proxy_pool.managers) == 3
        assert proxy_pool.current_index == 0
        assert proxy_pool.strategy == "round_robin"

    async def test_pool_start_all(self, proxy_pool):
        """Test starting all proxy managers in pool."""
        with patch('chameleon_engine.services.proxy.manager.GoProxyManager.start') as mock_start:
            mock_start.return_value = True

            result = await proxy_pool.start_all()

            assert result is True
            assert mock_start.call_count == 3

    async def test_pool_stop_all(self, proxy_pool):
        """Test stopping all proxy managers in pool."""
        with patch('chameleon_engine.services.proxy.manager.GoProxyManager.stop') as mock_stop:
            mock_stop.return_value = True

            result = await proxy_pool.stop_all()

            assert result is True
            assert mock_stop.call_count == 3

    async def test_round_robin_selection(self, proxy_pool):
        """Test round-robin proxy selection."""
        # Mock all managers as healthy
        for manager in proxy_pool.managers:
            manager.status = ProxyStatus.RUNNING

        # Get next manager multiple times
        selected_managers = []
        for _ in range(6):  # 2 cycles through 3 managers
            manager = proxy_pool.get_next_manager()
            selected_managers.append(manager)

        # Should cycle through all managers
        assert len(set(selected_managers)) == 3
        assert selected_managers[0] == selected_managers[3]
        assert selected_managers[1] == selected_managers[4]
        assert selected_managers[2] == selected_managers[5]

    async def test_healthy_manager_selection(self, proxy_pool):
        """Test selecting only healthy proxy managers."""
        # Set different health statuses
        proxy_pool.managers[0].status = ProxyStatus.RUNNING
        proxy_pool.managers[1].status = ProxyStatus.ERROR
        proxy_pool.managers[2].status = ProxyStatus.RUNNING

        # Get healthy manager
        manager = proxy_pool.get_healthy_manager()

        # Should return one of the healthy managers
        assert manager in [proxy_pool.managers[0], proxy_pool.managers[2]]
        assert manager != proxy_pool.managers[1]

    async def test_pool_health_check(self, proxy_pool):
        """Test pool-wide health check."""
        mock_health_info = ProxyHealthInfo(
            status="healthy",
            uptime=1800.0,
            connections=10,
            memory_usage=50.0
        )

        with patch('chameleon_engine.services.proxy.manager.GoProxyManager.health_check') as mock_health:
            mock_health.return_value = mock_health_info

            results = await proxy_pool.health_check_all()

            assert len(results) == 3
            for result in results:
                assert result.status == "healthy"

    async def test_pool_failover(self, proxy_pool):
        """Test proxy pool failover functionality."""
        # Mock first manager as unhealthy
        proxy_pool.managers[0].status = ProxyStatus.ERROR
        proxy_pool.managers[1].status = ProxyStatus.RUNNING
        proxy_pool.managers[2].status = ProxyStatus.RUNNING

        # Get manager should skip unhealthy one
        manager = proxy_pool.get_next_manager()

        assert manager != proxy_pool.managers[0]
        assert manager in [proxy_pool.managers[1], proxy_pool.managers[2]]

    async def test_pool_load_balancing_strategies(self, proxy_pool):
        """Test different load balancing strategies."""
        # Test least connections strategy
        proxy_pool.strategy = "least_connections"

        # Mock different connection counts
        proxy_pool.managers[0].connection_count = 50
        proxy_pool.managers[1].connection_count = 10
        proxy_pool.managers[2].connection_count = 25

        manager = proxy_pool.get_next_manager()

        # Should select manager with least connections
        assert manager == proxy_pool.managers[1]

        # Test weighted strategy
        proxy_pool.strategy = "weighted"
        proxy_pool.weights = [0.5, 0.3, 0.2]  # Prefer first manager

        # Run selection multiple times to see distribution
        selections = {}
        for _ in range(100):
            manager = proxy_pool.get_next_manager()
            manager_index = proxy_pool.managers.index(manager)
            selections[manager_index] = selections.get(manager_index, 0) + 1

        # First manager should be selected more often
        assert selections[0] > selections[1]
        assert selections[0] > selections[2]

    async def test_pool_statistics(self, proxy_pool):
        """Test pool statistics collection."""
        # Mock some statistics
        for i, manager in enumerate(proxy_pool.managers):
            manager.connection_count = 10 + i * 5
            manager.total_requests = 100 + i * 50

        stats = proxy_pool.get_pool_statistics()

        assert stats["total_managers"] == 3
        assert stats["healthy_managers"] == 3
        assert stats["total_connections"] == 45  # 10 + 15 + 20
        assert stats["total_requests"] == 300   # 100 + 150 + 200


class TestBinaryConfig:
    """Test BinaryConfig model validation and functionality."""

    def test_binary_config_creation(self, binary_config):
        """Test creating binary configuration."""
        config = BinaryConfig(**binary_config)
        assert config.browser_type == binary_config["browser_type"]
        assert config.version == binary_config["version"]
        assert config.platform == binary_config["platform"]
        assert config.architecture == binary_config["architecture"]

    def test_binary_config_validation(self):
        """Test binary configuration validation."""
        # Valid configurations
        valid_configs = [
            {
                "browser_type": "chromium",
                "version": "latest",
                "platform": "linux",
                "architecture": "x64"
            },
            {
                "browser_type": "chrome",
                "version": "120.0.6099.71",
                "platform": "windows",
                "architecture": "x86"
            },
            {
                "browser_type": "firefox",
                "version": "121.0",
                "platform": "macos",
                "architecture": "arm64"
            }
        ]

        for config_data in valid_configs:
            config = BinaryConfig(**config_data)
            assert config.browser_type == config_data["browser_type"]
            assert config.platform == config_data["platform"]

        # Invalid configurations
        invalid_configs = [
            {"browser_type": "invalid_browser", "version": "latest", "platform": "linux"},  # Invalid browser
            {"browser_type": "chrome", "version": "", "platform": "linux"},  # Empty version
            {"browser_type": "chrome", "version": "latest", "platform": "invalid_platform"}  # Invalid platform
        ]

        for config_data in invalid_configs:
            with pytest.raises(Exception):
                BinaryConfig(**config_data)

    def test_binary_config_platform_detection(self):
        """Test automatic platform detection."""
        config = BinaryConfig.with_autodetection(
            browser_type="chrome",
            version="latest"
        )

        assert config.browser_type == "chrome"
        assert config.version == "latest"
        assert config.platform is not None
        assert config.architecture is not None

    def test_binary_config_download_url_generation(self):
        """Test download URL generation."""
        config = BinaryConfig(
            browser_type="chromium",
            version="120.0.6099.71",
            platform="linux",
            architecture="x64"
        )

        url = config.get_download_url()
        assert "chromium" in url
        assert "120.0.6099.71" in url
        assert "linux" in url

    def test_binary_config_file_paths(self, temp_directory):
        """Test binary file path generation."""
        config = BinaryConfig(
            browser_type="chrome",
            version="120.0.6099.71",
            platform="linux",
            architecture="x64"
        )

        config.set_installation_dir(str(temp_directory))

        binary_path = config.get_binary_path()
        assert temp_directory.name in binary_path
        assert "chrome" in binary_path
        assert "120.0.6099.71" in binary_path

    def test_binary_config_optimization_presets(self):
        """Test binary configuration optimization presets."""
        # Development preset
        dev_config = BinaryConfig.optimization_preset("development")
        assert dev_config.enable_debugging is True
        assert dev_config.enable_logging is True
        assert "debug" in dev_config.args

        # Production preset
        prod_config = BinaryConfig.optimization_preset("production")
        assert prod_config.enable_debugging is False
        assert prod_config.enable_headless is True
        assert "--no-sandbox" in prod_config.args

        # Testing preset
        test_config = BinaryConfig.optimization_preset("testing")
        assert test_config.enable_headless is True
        assert "--disable-dev-shm-usage" in test_config.args


class TestBinaryDownloader:
    """Test BinaryDownloader functionality."""

    @pytest_asyncio.fixture
    async def downloader(self, temp_directory):
        """Create BinaryDownloader for testing."""
        return BinaryDownloader(str(temp_directory))

    async def test_download_success(self, downloader, temp_directory):
        """Test successful binary download."""
        # Create a mock file to download
        test_content = b"mock binary content"
        test_file = temp_directory / "mock_binary.zip"
        test_file.write_bytes(test_content)

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content.read = AsyncMock(return_value=test_content)
            mock_get.return_value.__aenter__.return_value = mock_response

            config = BinaryConfig(
                browser_type="chrome",
                version="120.0.6099.71",
                platform="linux",
                architecture="x64",
                download_url="http://example.com/chrome.zip"
            )

            result = await downloader.download_binary(config)

            assert result is True
            assert (temp_directory / "chrome-120.0.6099.71-linux-x64.zip").exists()

    async def test_download_with_resume(self, downloader, temp_directory):
        """Test download with resume capability."""
        # Create partially downloaded file
        partial_file = temp_directory / "chrome-120.0.6099.71-linux-x64.zip.part"
        partial_file.write_bytes(b"partial content")

        full_content = b"partial content" + b" remaining content"

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 206  # Partial content
            mock_response.headers = {"Content-Range": "bytes 15-31/32"}
            mock_response.content.read = AsyncMock(return_value=b" remaining content")
            mock_get.return_value.__aenter__.return_value = mock_response

            config = BinaryConfig(
                browser_type="chrome",
                version="120.0.6099.71",
                platform="linux",
                architecture="x64",
                download_url="http://example.com/chrome.zip"
            )

            result = await downloader.download_binary(config, resume=True)

            assert result is True
            final_file = temp_directory / "chrome-120.0.6099.71-linux-x64.zip"
            assert final_file.exists()
            assert final_file.read_bytes() == full_content

    async def test_download_checksum_validation(self, downloader):
        """Test download checksum validation."""
        test_content = b"test binary content"
        expected_checksum = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"  # SHA256 of "test"

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content.read = AsyncMock(return_value=test_content)
            mock_get.return_value.__aenter__.return_value = mock_response

            config = BinaryConfig(
                browser_type="chrome",
                version="120.0.6099.71",
                platform="linux",
                architecture="x64",
                download_url="http://example.com/chrome.zip",
                checksum=f"sha256:{expected_checksum}"
            )

            result = await downloader.download_binary(config)

            assert result is True

    async def test_download_checksum_failure(self, downloader):
        """Test download checksum validation failure."""
        test_content = b"test binary content"
        wrong_checksum = "wrong_checksum_value"

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content.read = AsyncMock(return_value=test_content)
            mock_get.return_value.__aenter__.return_value = mock_response

            config = BinaryConfig(
                browser_type="chrome",
                version="120.0.6099.71",
                platform="linux",
                architecture="x64",
                download_url="http://example.com/chrome.zip",
                checksum=f"sha256:{wrong_checksum}"
            )

            with pytest.raises(BinaryValidationError) as exc_info:
                await downloader.download_binary(config)

            assert "checksum" in str(exc_info.value).lower()

    async def test_download_progress_tracking(self, downloader):
        """Test download progress tracking."""
        progress_updates = []

        def progress_callback(progress):
            progress_updates.append(progress)

        test_content = b"x" * 1000  # 1KB of content

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content.iter_chunked = AsyncMock(
                return_value=iter([b"x" * 100 for _ in range(10)])
            )
            mock_get.return_value.__aenter__.return_value = mock_response

            config = BinaryConfig(
                browser_type="chrome",
                version="120.0.6099.71",
                platform="linux",
                architecture="x64",
                download_url="http://example.com/chrome.zip"
            )

            await downloader.download_binary(config, progress_callback=progress_callback)

            assert len(progress_updates) > 0
            assert progress_updates[0]["downloaded"] > 0
            assert progress_updates[-1]["percent"] == 100.0

    async def test_batch_download(self, downloader):
        """Test batch download of multiple binaries."""
        configs = [
            BinaryConfig(
                browser_type="chrome",
                version="120.0.6099.71",
                platform="linux",
                architecture="x64",
                download_url="http://example.com/chrome.zip"
            ),
            BinaryConfig(
                browser_type="firefox",
                version="121.0",
                platform="linux",
                architecture="x64",
                download_url="http://example.com/firefox.tar.gz"
            )
        ]

        test_content = b"binary content"

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content.read = AsyncMock(return_value=test_content)
            mock_get.return_value.__aenter__.return_value = mock_response

            results = await downloader.download_batch(configs, max_concurrent=2)

            assert len(results) == 2
            assert all(result["success"] for result in results)

    async def test_download_retry_logic(self, downloader):
        """Test download retry logic."""
        attempt_count = 0

        async def failing_download(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Network error")
            return AsyncMock(status=200, content.read=AsyncMock(return_value=b"success"))

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.side_effect = failing_download

            config = BinaryConfig(
                browser_type="chrome",
                version="120.0.6099.71",
                platform="linux",
                architecture="x64",
                download_url="http://example.com/chrome.zip"
            )

            result = await downloader.download_binary(config, max_retries=3)

            assert result is True
            assert attempt_count == 3


class TestBinaryValidator:
    """Test BinaryValidator functionality."""

    @pytest_asyncio.fixture
    async def validator(self):
        """Create BinaryValidator for testing."""
        return BinaryValidator()

    async def test_checksum_validation(self, validator):
        """Test checksum validation."""
        test_content = b"test binary content"
        expected_checksum = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"  # SHA256

        result = await validator.validate_checksum(test_content, f"sha256:{expected_checksum}")

        assert result.is_valid is True
        assert result.algorithm == "sha256"
        assert result.calculated_checksum == expected_checksum

    async def test_checksum_validation_failure(self, validator):
        """Test checksum validation failure."""
        test_content = b"test binary content"
        wrong_checksum = "wrong_checksum_value"

        result = await validator.validate_checksum(test_content, f"sha256:{wrong_checksum}")

        assert result.is_valid is False
        assert result.error_message is not None

    async def test_signature_validation(self, validator, temp_directory):
        """Test digital signature validation."""
        # Create test files
        binary_file = temp_directory / "test_binary"
        signature_file = temp_directory / "test_binary.sig"
        public_key_file = temp_directory / "public_key.pem"

        binary_file.write_bytes(b"test binary content")
        signature_file.write_bytes(b"mock signature")
        public_key_file.write_text(b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----""")

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Good signature"

            result = await validator.validate_signature(
                binary_path=str(binary_file),
                signature_path=str(signature_file),
                public_key_path=str(public_key_file)
            )

            assert result.is_valid is True
            assert "Good signature" in result.verification_message

    async def test_malware_scan(self, validator, temp_directory):
        """Test malware scanning functionality."""
        binary_file = temp_directory / "test_binary"
        binary_file.write_bytes(b"test binary content")

        with patch('subprocess.run') as mock_run:
            # Mock clamscan output
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "test_binary: OK"

            result = await validator.scan_for_malware(str(binary_file))

            assert result.is_safe is True
            assert result.scan_result == "OK"

    async def test_executable_validation(self, validator, temp_directory):
        """Test executable validation."""
        # Create a mock executable
        exe_file = temp_directory / "test_binary"
        exe_file.write_bytes(b"\x7fELF")  # ELF header

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "ELF 64-bit LSB executable"

            result = await validator.validate_executable(str(exe_file))

            assert result.is_executable is True
            assert "ELF" in result.file_type
            assert result.architecture == "64-bit"

    async def test_comprehensive_validation(self, validator, temp_directory):
        """Test comprehensive binary validation."""
        binary_file = temp_directory / "test_binary"
        binary_file.write_bytes(b"test binary content")

        config = BinaryConfig(
            browser_type="chrome",
            version="120.0.6099.71",
            platform="linux",
            architecture="x64",
            checksum="sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )

        with patch.object(validator, 'validate_checksum') as mock_checksum:
            with patch.object(validator, 'validate_signature') as mock_signature:
                with patch.object(validator, 'scan_for_malware') as mock_malware:
                    with patch.object(validator, 'validate_executable') as mock_executable:

                        # Mock all validations to pass
                        mock_checksum.return_value = AsyncMock(is_valid=True)
                        mock_signature.return_value = AsyncMock(is_valid=True)
                        mock_malware.return_value = AsyncMock(is_safe=True)
                        mock_executable.return_value = AsyncMock(is_executable=True)

                        result = await validator.validate_comprehensive(str(binary_file), config)

                        assert result.overall_valid is True
                        assert result.checksum_valid is True
                        assert result.signature_valid is True
                        assert result.malware_scan_passed is True
                        assert result.is_executable is True

    async def test_validation_error_handling(self, validator, temp_directory):
        """Test validation error handling."""
        # Non-existent file
        with pytest.raises(BinaryValidationError):
            await validator.validate_checksum("/non/existent/file", "sha256:checksum")

        # Invalid checksum format
        binary_file = temp_directory / "test_binary"
        binary_file.write_bytes(b"content")

        with pytest.raises(BinaryValidationError):
            await validator.validate_checksum(b"content", "invalid_format")


class TestCustomBinaryManager:
    """Test CustomBinaryManager functionality."""

    @pytest_asyncio.fixture
    async def binary_manager(self, temp_directory):
        """Create CustomBinaryManager for testing."""
        return CustomBinaryManager(
            installation_dir=str(temp_directory),
            max_cached_binaries=5
        )

    async def test_binary_installation(self, binary_manager, binary_config):
        """Test binary installation."""
        with patch.object(binary_manager.downloader, 'download_binary') as mock_download:
            with patch.object(binary_manager.validator, 'validate_comprehensive') as mock_validate:
                with patch('zipfile.ZipFile') as mock_zipfile:

                    # Mock successful download
                    mock_download.return_value = True

                    # Mock successful validation
                    mock_validation = AsyncMock()
                    mock_validation.overall_valid = True
                    mock_validate.return_value = mock_validation

                    # Mock zip extraction
                    mock_zip = AsyncMock()
                    mock_zipfile.return_value.__enter__.return_value = mock_zip

                    result = await binary_manager.install_binary(binary_config)

                    assert result is not None
                    assert result.endswith("/browser")
                    mock_download.assert_called_once_with(binary_config)
                    mock_validate.assert_called_once()

    async def test_binary_retrieval(self, binary_manager, binary_config):
        """Test binary retrieval."""
        # Mock an already installed binary
        binary_path = binary_manager._get_binary_path(binary_config)
        binary_path.parent.mkdir(parents=True, exist_ok=True)
        binary_path.write_bytes(b"mock binary")

        result = await binary_manager.get_binary(binary_config)

        assert result == str(binary_path)

    async def test_binary_auto_installation(self, binary_manager, binary_config):
        """Test automatic binary installation when not found."""
        with patch.object(binary_manager, 'install_binary') as mock_install:
            mock_install.return_value = "/path/to/installed/binary"

            result = await binary_manager.get_binary(binary_config, auto_install=True)

            assert result == "/path/to/installed/binary"
            mock_install.assert_called_once_with(binary_config)

    async def test_binary_update(self, binary_manager, binary_config):
        """Test binary update functionality."""
        # Mock existing binary with older version
        old_config = BinaryConfig(
            browser_type="chrome",
            version="119.0.6045.123",
            platform="linux",
            architecture="x64"
        )

        with patch.object(binary_manager, 'install_binary') as mock_install:
            with patch.object(binary_manager, 'uninstall_binary') as mock_uninstall:

                mock_install.return_value = "/path/to/new/binary"

                result = await binary_manager.update_binary(old_config, binary_config)

                assert result is True
                mock_uninstall.assert_called_once_with(old_config)
                mock_install.assert_called_once_with(binary_config)

    async def test_binary_uninstallation(self, binary_manager, binary_config):
        """Test binary uninstallation."""
        # Create mock binary files
        binary_path = binary_manager._get_binary_path(binary_config)
        binary_path.parent.mkdir(parents=True, exist_ok=True)
        binary_path.write_bytes(b"mock binary")

        result = await binary_manager.uninstall_binary(binary_config)

        assert result is True
        assert not binary_path.exists()

    async def test_binary_listing(self, binary_manager, temp_directory):
        """Test listing installed binaries."""
        # Create mock binary installations
        for i, browser in enumerate(["chrome", "firefox", "chromium"]):
            config = BinaryConfig(
                browser_type=browser,
                version=f"120.{i}.0",
                platform="linux",
                architecture="x64"
            )
            binary_path = binary_manager._get_binary_path(config)
            binary_path.parent.mkdir(parents=True, exist_ok=True)
            binary_path.write_bytes(f"mock {browser} binary".encode())

        # Create metadata files
        for i, browser in enumerate(["chrome", "firefox", "chromium"]):
            config = BinaryConfig(
                browser_type=browser,
                version=f"120.{i}.0",
                platform="linux",
                architecture="x64"
            )
            metadata_path = binary_manager._get_metadata_path(config)
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            metadata = {
                "config": config.model_dump(),
                "installed_at": datetime.now(timezone.utc).isoformat(),
                "size": 1000000 + i * 100000,
                "usage_count": i + 1
            }
            metadata_path.write_text(json.dumps(metadata))

        binaries = await binary_manager.list_binaries()

        assert len(binaries) == 3
        browser_names = [b.config.browser_type for b in binaries]
        assert "chrome" in browser_names
        assert "firefox" in browser_names
        assert "chromium" in browser_names

    async def test_binary_cleanup(self, binary_manager, temp_directory):
        """Test old binary cleanup."""
        # Create old and new binaries
        old_config = BinaryConfig(
            browser_type="chrome",
            version="119.0.6045.123",
            platform="linux",
            architecture="x64"
        )
        new_config = BinaryConfig(
            browser_type="chrome",
            version="120.0.6099.71",
            platform="linux",
            architecture="x64"
        )

        for config in [old_config, new_config]:
            binary_path = binary_manager._get_binary_path(config)
            binary_path.parent.mkdir(parents=True, exist_ok=True)
            binary_path.write_bytes(f"mock {config.version}".encode())

            metadata_path = binary_manager._get_metadata_path(config)
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            if config == old_config:
                installed_at = datetime.now(timezone.utc) - timedelta(days=10)
            else:
                installed_at = datetime.now(timezone.utc)

            metadata = {
                "config": config.model_dump(),
                "installed_at": installed_at.isoformat(),
                "size": 1000000,
                "usage_count": 1
            }
            metadata_path.write_text(json.dumps(metadata))

        # Clean up binaries older than 7 days, keeping latest 2 versions
        cleaned = await binary_manager.cleanup_old_binary_versions(days_to_keep=7, keep_latest=2)

        assert cleaned == 1  # Should have cleaned 1 old binary
        new_binary_path = binary_manager._get_binary_path(new_config)
        assert new_binary_path.exists()
        old_binary_path = binary_manager._get_binary_path(old_config)
        assert not old_binary_path.exists()

    async def test_binary_usage_tracking(self, binary_manager, binary_config):
        """Test binary usage tracking."""
        # Install binary first
        binary_path = binary_manager._get_binary_path(binary_config)
        binary_path.parent.mkdir(parents=True, exist_ok=True)
        binary_path.write_bytes(b"mock binary")

        # Create metadata
        metadata_path = binary_manager._get_metadata_path(binary_config)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "config": binary_config.model_dump(),
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "size": 1000000,
            "usage_count": 5
        }
        metadata_path.write_text(json.dumps(metadata))

        # Track usage
        await binary_manager.track_usage(binary_config)

        # Verify usage count increased
        updated_metadata = json.loads(metadata_path.read_text())
        assert updated_metadata["usage_count"] == 6
        assert updated_metadata["last_used"] is not None

    async def test_binary_health_check(self, binary_manager, binary_config):
        """Test binary health check."""
        # Install binary
        binary_path = binary_manager._get_binary_path(binary_config)
        binary_path.parent.mkdir(parents=True, exist_ok=True)
        binary_path.write_bytes(b"mock binary")

        with patch.object(binary_manager.validator, 'validate_comprehensive') as mock_validate:
            mock_validation = AsyncMock()
            mock_validation.overall_valid = True
            mock_validation.is_executable = True
            mock_validate.return_value = mock_validation

            health = await binary_manager.health_check(binary_config)

            assert health.is_healthy is True
            assert health.exists is True
            assert health.is_executable is True

    async def test_binary_manager_statistics(self, binary_manager, temp_directory):
        """Test binary manager statistics."""
        # Create multiple binary installations
        browsers = ["chrome", "firefox", "chromium", "edge"]
        for browser in browsers:
            config = BinaryConfig(
                browser_type=browser,
                version="120.0.0",
                platform="linux",
                architecture="x64"
            )
            binary_path = binary_manager._get_binary_path(config)
            binary_path.parent.mkdir(parents=True, exist_ok=True)
            binary_path.write_bytes(f"mock {browser} binary".encode())

            metadata_path = binary_manager._get_metadata_path(config)
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            metadata = {
                "config": config.model_dump(),
                "installed_at": datetime.now(timezone.utc).isoformat(),
                "size": 1000000,
                "usage_count": 10
            }
            metadata_path.write_text(json.dumps(metadata))

        stats = await binary_manager.get_statistics()

        assert stats["total_binaries"] == 4
        assert stats["total_size"] == 4000000
        assert stats["total_usage"] == 40
        assert len(stats["by_browser"]) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])