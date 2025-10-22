"""
Comprehensive integration tests for Chameleon Engine.

Tests complete workflows and component integration to ensure all parts
work together correctly in realistic scenarios.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from chameleon_engine.orchestrator import (
    ChameleonEngine,
    ChameleonEngineConfig
)

from chameleon_engine.core.profiles import (
    BrowserProfile,
    BrowserType,
    OperatingSystem
)

# Import test fixtures
from tests.conftest import (
    mock_fingerprint_service,
    mock_proxy_service,
    mock_browser_manager,
    mock_binary_manager,
    sample_browser_profile,
    temp_directory
)


@pytest.mark.integration
class TestChameleonEngineIntegration:
    """Comprehensive integration tests for ChameleonEngine."""

    @pytest_asyncio.fixture
    async def integration_engine(self, mock_fingerprint_service, mock_proxy_service,
                               mock_binary_manager, temp_directory):
        """Create ChameleonEngine with mocked dependencies for integration testing."""
        config = ChameleonEngineConfig(
            data_dir=str(temp_directory),
            enable_metrics=True,
            max_concurrent_pages=3,
            profile_rotation_interval=3600
        )
        return ChameleonEngine(
            config=config,
            fingerprint_service=mock_fingerprint_service,
            proxy_service=mock_proxy_service,
            binary_manager=mock_binary_manager
        )

    async def test_complete_scraping_workflow(self, integration_engine):
        """Test complete web scraping workflow from start to finish."""
        # 1. Start engine with specific browser configuration
        session_id = await integration_engine.start(
            browser_type="chrome",
            operating_system="windows"
        )
        assert session_id is not None
        assert integration_engine.engine_status == "running"

        # 2. Create and configure page
        page_id = await integration_engine.new_page(
            viewport={"width": 1920, "height": 1080}
        )
        assert page_id is not None
        assert page_id in integration_engine.pages

        # 3. Navigate to target page
        nav_result = await integration_engine.navigate(
            page_id,
            "https://example.com",
            wait_until="domcontentloaded"
        )
        assert nav_result is True

        # 4. Perform human-like interactions
        # Click on element with realistic mouse movement
        click_result = await integration_engine.click(
            page_id,
            "#example-button",
            position={"x": 100, "y": 200}
        )
        assert click_result is True

        # Type text with realistic typing patterns
        type_result = await integration_engine.type_text(
            page_id,
            "#search-input",
            "search query with realistic typing",
            style="natural"
        )
        assert type_result is True

        # 5. Extract data/content
        content = await integration_engine.get_page_content(page_id)
        assert content is not None
        assert len(content) > 0

        # 6. Take screenshot for verification
        screenshot = await integration_engine.take_screenshot(page_id, full_page=True)
        assert screenshot is not None
        assert len(screenshot) > 0

        # 7. Get session metrics
        metrics = integration_engine.get_session_metrics()
        assert metrics is not None
        assert metrics["pages_created"] == 1
        assert metrics["navigations_performed"] == 1
        assert metrics["total_interactions"] >= 2  # click + type

        # 8. Cleanup
        await integration_engine.close_page(page_id)
        assert page_id not in integration_engine.pages

    async def test_profile_rotation_during_session(self, integration_engine):
        """Test profile rotation during active session."""
        # Start session
        await integration_engine.start("chrome", "windows")
        initial_profile = integration_engine.current_profile

        # Create page and perform some actions
        page_id = await integration_engine.new_page()
        await integration_engine.navigate(page_id, "https://example.com")

        # Rotate profile
        new_profile = await integration_engine.rotate_profile()
        assert new_profile is not None
        assert new_profile != initial_profile

        # Verify new profile is being used
        assert integration_engine.current_profile == new_profile

        # Continue operations with new profile
        await integration_engine.navigate(page_id, "https://another-site.com")

        # Verify functionality continues working
        content = await integration_engine.get_page_content(page_id)
        assert content is not None

        # Cleanup
        await integration_engine.close_page(page_id)

    async def test_error_recovery_and_resilience(self, integration_engine):
        """Test error handling and recovery mechanisms."""
        await integration_engine.start("chrome", "windows")
        page_id = await integration_engine.new_page()

        # Simulate navigation failure
        integration_engine.browser_manager.set_navigation_result(
            page_id, "https://failing-site.com", False
        )

        # Navigation should handle failure gracefully
        result = await integration_engine.navigate(page_id, "https://failing-site.com")
        assert result is False  # Should report failure

        # Engine should still be functional
        assert integration_engine.engine_status == "running"

        # Subsequent successful navigation should work
        integration_engine.browser_manager.set_navigation_result(
            page_id, "https://working-site.com", True
        )
        result = await integration_engine.navigate(page_id, "https://working-site.com")
        assert result is True

        # Cleanup
        await integration_engine.close_page(page_id)

    async def test_concurrent_page_management(self, integration_engine):
        """Test managing multiple pages concurrently."""
        await integration_engine.start("chrome", "windows")

        # Create multiple pages concurrently
        page_tasks = []
        for i in range(3):
            task = asyncio.create_task(integration_engine.new_page())
            page_tasks.append(task)

        page_ids = await asyncio.gather(*page_tasks)
        assert len(page_ids) == 3
        assert len(integration_engine.pages) == 3

        # Perform operations on all pages concurrently
        navigation_tasks = []
        for i, page_id in enumerate(page_ids):
            task = asyncio.create_task(
                integration_engine.navigate(page_id, f"https://example.com/page/{i}")
            )
            navigation_tasks.append(task)

        nav_results = await asyncio.gather(*navigation_tasks)
        assert all(nav_results)  # All navigations should succeed

        # Take screenshots from all pages
        screenshot_tasks = []
        for page_id in page_ids:
            task = asyncio.create_task(integration_engine.take_screenshot(page_id))
            screenshot_tasks.append(task)

        screenshots = await asyncio.gather(*screenshot_tasks)
        assert all(len(screenshot) > 0 for screenshot in screenshots)

        # Cleanup all pages
        close_tasks = []
        for page_id in page_ids:
            task = asyncio.create_task(integration_engine.close_page(page_id))
            close_tasks.append(task)

        await asyncio.gather(*close_tasks)
        assert len(integration_engine.pages) == 0

    async def test_component_health_monitoring(self, integration_engine):
        """Test health monitoring of all components."""
        await integration_engine.start("chrome", "windows")

        # Get overall engine status
        status = integration_engine.get_status()
        assert status["engine_status"] == "running"
        assert "component_health" in status

        # Check individual component health
        component_health = status["component_health"]
        assert "fingerprint_service" in component_health
        assert "proxy_service" in component_health
        assert "binary_manager" in component_health
        assert "browser_manager" in component_health

        # All components should be healthy
        for component, health in component_health.items():
            assert health["status"] == "healthy"

        # Simulate component failure and test detection
        integration_engine.proxy_service.set_failure(True)

        # Force health check
        await integration_engine._health_check()

        # Should detect proxy service failure
        updated_status = integration_engine.get_status()
        proxy_health = updated_status["component_health"]["proxy_service"]
        assert proxy_health["status"] != "healthy"

    async def test_performance_under_load(self, integration_engine):
        """Test engine performance under realistic load."""
        await integration_engine.start("chrome", "windows")

        # Simulate realistic usage pattern
        operations = []
        start_time = asyncio.get_event_loop().time()

        # Create pages and perform operations
        for i in range(5):
            # Create page
            page_id = await integration_engine.new_page()

            # Navigate
            await integration_engine.navigate(page_id, f"https://example.com/page/{i}")

            # Perform interactions
            await integration_engine.click(page_id, "#button")
            await integration_engine.type_text(page_id, "#input", f"test text {i}")

            # Take screenshot
            await integration_engine.take_screenshot(page_id)

            # Close page
            await integration_engine.close_page(page_id)

        end_time = asyncio.get_event_loop().time()
        total_duration = end_time - start_time

        # Performance should be reasonable
        assert total_duration < 30.0  # Should complete within 30 seconds

        # Check metrics
        metrics = integration_engine.get_session_metrics()
        assert metrics["pages_created"] == 5
        assert metrics["navigations_performed"] == 5

    async def test_context_manager_usage(self, integration_engine):
        """Test using engine as context manager."""
        async with integration_engine:
            # Engine should be started
            assert integration_engine.engine_status == "running"

            # Perform operations
            page_id = await integration_engine.new_page()
            await integration_engine.navigate(page_id, "https://example.com")
            await integration_engine.click(page_id, "#test")
            await integration_engine.close_page(page_id)

        # Engine should be stopped after context exit
        assert integration_engine.engine_status == "stopped"
        assert len(integration_engine.pages) == 0

    async def test_configuration_customization(self, temp_directory):
        """Test engine configuration customization."""
        custom_config = ChameleonEngineConfig(
            data_dir=str(temp_directory),
            enable_metrics=True,
            max_concurrent_pages=2,
            profile_rotation_interval=1800,  # 30 minutes
            auto_cleanup_enabled=True,
            performance_monitoring=True
        )

        # Create mocks
        mock_fp = Mock()
        mock_proxy = Mock()
        mock_binary = Mock()

        engine = ChameleonEngine(
            config=custom_config,
            fingerprint_service=mock_fp,
            proxy_service=mock_proxy,
            binary_manager=mock_binary
        )

        # Verify configuration was applied
        assert engine.config.max_concurrent_pages == 2
        assert engine.config.profile_rotation_interval == 1800
        assert engine.config.auto_cleanup_enabled is True
        assert engine.config.performance_monitoring is True

    async def test_data_persistence_and_recovery(self, integration_engine, temp_directory):
        """Test data persistence and recovery capabilities."""
        # Start engine and perform operations
        await integration_engine.start("chrome", "windows")
        page_id = await integration_engine.new_page()
        await integration_engine.navigate(page_id, "https://example.com")

        # Get session data
        session_data = integration_engine.get_session_data()
        assert session_data is not None
        assert "session_id" in session_data
        assert "start_time" in session_data
        assert "current_profile" in session_data

        # Simulate shutdown and restart
        await integration_engine.stop()

        # Verify data directory exists and contains data
        data_dir = Path(integration_engine.config.data_dir)
        assert data_dir.exists()

        # Restart engine
        await integration_engine.start("chrome", "windows")

        # Engine should be functional after restart
        assert integration_engine.engine_status == "running"

        # Should be able to create new pages and navigate
        new_page_id = await integration_engine.new_page()
        await integration_engine.navigate(new_page_id, "https://recovered-site.com")

        # Cleanup
        await integration_engine.close_page(new_page_id)

    async def test_network_obfuscation_integration(self, integration_engine):
        """Test network obfuscation integration."""
        await integration_engine.start("chrome", "windows")

        # Verify network obfuscator is initialized
        assert integration_engine.network_obfuscator is not None

        # Get network status
        network_status = integration_engine.get_network_status()
        assert network_status is not None
        assert "tls_fingerprint" in network_status
        assert "http2_settings" in network_status
        assert "proxy_status" in network_status

        # Rotate TLS fingerprint
        await integration_engine.rotate_tls_fingerprint()
        updated_status = integration_engine.get_network_status()
        assert updated_status["tls_fingerprint"]["last_rotated"] is not None

    async def test_fingerprint_integration(self, integration_engine):
        """Test fingerprint service integration."""
        await integration_engine.start("chrome", "windows")

        # Test fingerprint generation
        fingerprint_request = {
            "browser_type": "chrome",
            "operating_system": "windows",
            "min_quality": 0.8,
            "max_detection_risk": 0.2
        }

        profile = await integration_engine.generate_fingerprint(fingerprint_request)
        assert profile is not None
        assert "user_agent" in profile
        assert "viewport" in profile

        # Test profile validation
        validation_result = await integration_engine.validate_profile(profile)
        assert validation_result is not None
        assert "is_valid" in validation_result
        assert "score" in validation_result

    async def test_browser_profile_integration(self, integration_engine):
        """Test browser profile integration and application."""
        await integration_engine.start("chrome", "windows")

        # Create custom profile
        custom_profile = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "viewport": {"width": 1366, "height": 768},
            "timezone": "Europe/London",
            "language": "en-GB",
            "platform": "Win32"
        }

        # Apply custom profile
        result = await integration_engine.apply_profile(custom_profile)
        assert result is True

        # Create page with custom profile
        page_id = await integration_engine.new_page(profile=custom_profile)
        assert page_id is not None

        # Verify profile was applied
        applied_profile = integration_engine.pages[page_id].get("profile")
        assert applied_profile is not None
        assert applied_profile["user_agent"] == custom_profile["user_agent"]

        # Cleanup
        await integration_engine.close_page(page_id)


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndScenarios:
    """End-to-end testing scenarios."""

    async def test_ecommerce_scraping_scenario(self, integration_engine):
        """Test complete e-commerce scraping scenario."""
        await integration_engine.start("chrome", "windows")

        # 1. Navigate to product page
        page_id = await integration_engine.new_page()
        await integration_engine.navigate(page_id, "https://example-ecommerce.com/product/123")

        # 2. Human-like browsing behavior
        # Scroll down to read description
        await integration_engine.scroll(page_id, "down", 500)
        await asyncio.sleep(1)  # Human reading time

        # Scroll back up
        await integration_engine.scroll(page_id, "up", 300)

        # 3. Interact with product options
        await integration_engine.click(page_id, "#color-option-blue")
        await integration_engine.click(page_id, "#size-medium")

        # 4. Add to cart with realistic mouse movement
        await integration_engine.click(page_id, "#add-to-cart")

        # 5. Check cart
        await integration_engine.click(page_id, "#cart-icon")

        # 6. Extract product and pricing information
        product_info = await integration_engine.extract_text(page_id, ".product-title")
        price_info = await integration_engine.extract_text(page_id, ".price")
        cart_count = await integration_engine.extract_text(page_id, ".cart-count")

        # Verify data extraction
        assert product_info is not None
        assert price_info is not None

        # 7. Take screenshot for verification
        screenshot = await integration_engine.take_screenshot(page_id)
        assert len(screenshot) > 0

        # 8. Get performance metrics
        metrics = integration_engine.get_session_metrics()
        assert metrics["pages_created"] == 1
        assert metrics["total_interactions"] >= 5

        # Cleanup
        await integration_engine.close_page(page_id)

    async def test_form_submission_scenario(self, integration_engine):
        """Test form filling and submission scenario."""
        await integration_engine.start("chrome", "windows")

        page_id = await integration_engine.new_page()
        await integration_engine.navigate(page_id, "https://example-form.com/contact")

        # Fill form with realistic typing
        await integration_engine.type_text(
            page_id, "#name", "John Doe", style="natural"
        )
        await integration_engine.type_text(
            page_id, "#email", "john.doe@example.com", style="professional"
        )
        await integration_engine.type_text(
            page_id, "#message", "This is a test message from Chameleon Engine.",
            style="careful"
        )

        # Select dropdown
        await integration_engine.select_option(page_id, "#topic", "Technical Support")

        # Check checkbox
        await integration_engine.click(page_id, "#subscribe-newsletter")

        # Submit form
        await integration_engine.click(page_id, "#submit-button")

        # Wait for response
        await asyncio.sleep(2)

        # Verify submission success
        success_message = await integration_engine.extract_text(page_id, ".success-message")
        assert success_message is not None

        # Cleanup
        await integration_engine.close_page(page_id)

    async def test_multi_page_navigation_scenario(self, integration_engine):
        """Test multi-page navigation and data extraction scenario."""
        await integration_engine.start("chrome", "windows")

        # Start at homepage
        page_id = await integration_engine.new_page()
        await integration_engine.navigate(page_id, "https://example-news.com")

        # Click on article link
        await integration_engine.click(page_id, "#article-link-1")

        # Wait for page load
        await asyncio.sleep(1)

        # Extract article content
        article_title = await integration_engine.extract_text(page_id, "h1")
        article_content = await integration_engine.extract_text(page_id, ".article-content")

        # Navigate to related articles
        await integration_engine.click(page_id, ".related-article:first-child")

        # Extract related article info
        related_title = await integration_engine.extract_text(page_id, "h1")

        # Go back to homepage
        await integration_engine.navigate(page_id, "https://example-news.com")

        # Search for topics
        await integration_engine.type_text(page_id, "#search-box", "technology news")
        await integration_engine.click(page_id, "#search-button")

        # Extract search results
        search_results = await integration_engine.extract_multiple_texts(page_id, ".search-result-title")

        # Verify data extraction
        assert article_title is not None
        assert len(search_results) > 0

        # Cleanup
        await integration_engine.close_page(page_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])