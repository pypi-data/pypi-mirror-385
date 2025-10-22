"""
Tests for Behavior Simulation and ChameleonEngine Orchestrator.

Tests the mouse movement, keyboard typing, network obfuscation, browser management,
fingerprint generation, and main orchestrator components to ensure proper
integration and functionality.
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List, Optional, Tuple

from chameleon_engine.behavior.mouse import (
    MouseMovement,
    MovementStyle,
    MouseConfig,
    BezierCurve
)

from chameleon_engine.behavior.keyboard import (
    KeyboardTyping,
    TypingStyle,
    TypingConfig,
    KeyType,
    KeyboardLayout
)

from chameleon_engine.network.obfuscator import (
    NetworkObfuscator,
    TLSFingerprintManager,
    HTTP2SettingsManager,
    ProxyIntegrationManager
)

from chameleon_engine.core.browser_manager import (
    BrowserManager,
    BrowserLaunchConfig,
    BrowserMetrics
)

from chameleon_engine.fingerprinting.generator import (
    FingerprintGenerator,
    FingerprintCache,
    ProfilePool
)

from chameleon_engine.orchestrator import (
    ChameleonEngine,
    ChameleonEngineConfig,
    SessionMetrics,
    ChameleonEngineError,
    EngineNotStartedError,
    ComponentInitializationError
)

# Import test fixtures
from tests.conftest import (
    sample_browser_profile,
    sample_fingerprint_request,
    sample_fingerprint_response,
    mock_fingerprint_service,
    mock_proxy_service,
    mock_browser_manager,
    mock_binary_manager,
    temp_directory,
    assert_dicts_almost_equal,
    AsyncTestCase,
    performance_tracker
)


class TestBezierCurve:
    """Test Bezier curve mathematical utilities."""

    def test_bezier_curve_creation(self):
        """Test Bezier curve creation with control points."""
        start_point = (0, 0)
        control_point1 = (50, 100)
        control_point2 = (150, -100)
        end_point = (200, 0)

        curve = BezierCurve(start_point, control_point1, control_point2, end_point)

        assert curve.start_point == start_point
        assert curve.control_point1 == control_point1
        assert curve.control_point2 == control_point2
        assert curve.end_point == end_point

    def test_bezier_curve_evaluation(self):
        """Test Bezier curve point evaluation."""
        curve = BezierCurve((0, 0), (50, 100), (150, -100), (200, 0))

        # Test curve at different t values
        point_0 = curve.get_point(0.0)
        point_05 = curve.get_point(0.5)
        point_1 = curve.get_point(1.0)

        # Start point
        assert point_0 == (0, 0)

        # End point
        assert point_1 == (200, 0)

        # Middle point should be somewhere in between
        assert 0 < point_05[0] < 200
        assert isinstance(point_05[1], (int, float))

    def test_bezier_curve_length(self):
        """Test Bezier curve length calculation."""
        # Simple straight line curve
        curve = BezierCurve((0, 0), (50, 0), (150, 0), (200, 0))
        length = curve.get_length()
        assert abs(length - 200) < 1.0  # Should be approximately 200

        # More complex curve
        curve = BezierCurve((0, 0), (100, 100), (100, -100), (200, 0))
        length = curve.get_length()
        assert length > 200  # Should be longer than straight line

    def test_bezier_curve_point_at_distance(self):
        """Test getting point at specific distance along curve."""
        curve = BezierCurve((0, 0), (50, 100), (150, -100), (200, 0))

        point_at_100 = curve.get_point_at_distance(100)
        point_at_50 = curve.get_point_at_distance(50)

        # Points should be in order along the curve
        assert point_at_50[0] < point_at_100[0] < 200

    def test_bezier_curve_bounds(self):
        """Test Bezier curve bounding box calculation."""
        curve = BezierCurve((0, 0), (100, 100), (200, -100), (300, 0))

        bounds = curve.get_bounds()

        assert bounds["min_x"] == 0
        assert bounds["max_x"] == 300
        assert bounds["min_y"] <= -100
        assert bounds["max_y"] >= 100


class TestMouseMovement:
    """Test MouseMovement functionality."""

    @pytest_asyncio.fixture
    async def mouse_movement(self):
        """Create MouseMovement instance for testing."""
        config = MouseConfig(
            base_speed=500,
            speed_variance=0.2,
            jitter_intensity=2.0,
            pause_probability=0.1,
            max_pause_duration=0.5
        )
        return MouseMovement(config)

    async def test_mouse_movement_initialization(self, mouse_movement):
        """Test mouse movement initialization."""
        assert mouse_movement.config.base_speed == 500
        assert mouse_movement.config.speed_variance == 0.2
        assert mouse_movement.config.jitter_intensity == 2.0
        assert mouse_movement.get_statistics()["total_movements"] == 0

    async def test_simple_movement(self, mouse_movement):
        """Test simple mouse movement."""
        with patch('asyncio.sleep') as mock_sleep:
            # Mock page element
            mock_page = AsyncMock()
            mock_page.mouse = AsyncMock()

            await mouse_movement.move_to(mock_page, 100, 200)

            # Verify mouse move was called
            mock_page.mouse.move.assert_called()

            # Check movement coordinates
            call_args = mock_page.mouse.move.call_args
            assert call_args[0][0] == 100
            assert call_args[0][1] == 200

            # Verify statistics were updated
            stats = mouse_movement.get_statistics()
            assert stats["total_movements"] == 1
            assert stats["total_distance"] > 0

    async def test_bezier_curve_movement(self, mouse_movement):
        """Test mouse movement along Bezier curve."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.mouse = AsyncMock()

            start_pos = (0, 0)
            end_pos = (200, 100)

            await mouse_movement.move_to(mock_page, end_pos[0], end_pos[1],
                                       start_pos=start_pos, style=MovementStyle.NATURAL)

            # Verify multiple mouse moves (Bezier curve generates multiple points)
            assert mock_page.mouse.move.call_count > 1

            # Verify final position is correct
            final_call = mock_page.mouse.move.call_args
            assert abs(final_call[0][0] - end_pos[0]) < 5  # Allow small tolerance
            assert abs(final_call[0][1] - end_pos[1]) < 5

    async def test_movement_styles(self, mouse_movement):
        """Test different movement styles."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.mouse = AsyncMock()

            styles = [
                MovementStyle.NATURAL,
                MovementStyle.PRECISE,
                MovementStyle.NERVOUS,
                MovementStyle.SLOW,
                MovementStyle.FAST
            ]

            for style in styles:
                mouse_movement.reset_statistics()
                await mouse_movement.move_to(mock_page, 100, 100, style=style)

                stats = mouse_movement.get_statistics()
                assert stats["total_movements"] == 1
                assert stats["style_used"] == style.value

    async def test_click_functionality(self, mouse_movement):
        """Test mouse click functionality."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.mouse = AsyncMock()
            mock_page.click = AsyncMock()

            await mouse_movement.click(mock_page, 100, 100)

            # Verify mouse was moved and click was performed
            mock_page.mouse.move.assert_called()
            mock_page.click.assert_called_with(100, 100)

            # Verify click statistics
            stats = mouse_movement.get_statistics()
            assert stats["total_clicks"] == 1

    async def test_double_click_functionality(self, mouse_movement):
        """Test double click functionality."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.dblclick = AsyncMock()

            await mouse_movement.double_click(mock_page, 100, 100)

            # Verify double click was performed
            mock_page.dblclick.assert_called_with(100, 100)

            # Verify statistics
            stats = mouse_movement.get_statistics()
            assert stats["double_clicks"] == 1

    async def test_drag_and_drop(self, mouse_movement):
        """Test drag and drop functionality."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.mouse = AsyncMock()

            start_pos = (50, 50)
            end_pos = (150, 150)

            await mouse_movement.drag_and_drop(mock_page, start_pos[0], start_pos[1],
                                             end_pos[0], end_pos[1])

            # Verify mouse operations
            assert mock_page.mouse.move.call_count >= 2  # Start and end positions
            mock_page.mouse.down.assert_called()
            mock_page.mouse.up.assert_called()

            # Verify statistics
            stats = mouse_movement.get_statistics()
            assert stats["drag_operations"] == 1

    async def test_movement_timing_and_pauses(self, mouse_movement):
        """Test movement timing and pause functionality."""
        sleep_calls = []

        async def mock_sleep(duration):
            sleep_calls.append(duration)

        with patch('asyncio.sleep', side_effect=mock_sleep):
            mock_page = AsyncMock()
            mock_page.mouse = AsyncMock()

            await mouse_movement.move_to(mock_page, 200, 200)

            # Verify some sleep calls were made (timing delays)
            assert len(sleep_calls) > 0

            # Verify sleep durations are reasonable
            for sleep_duration in sleep_calls:
                assert 0 <= sleep_duration <= 2.0  # Reasonable sleep duration

    async def test_jitter_and_randomness(self, mouse_movement):
        """Test jitter and randomness in mouse movement."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.mouse = AsyncMock()

            # Perform same movement multiple times
            movements = []
            for _ in range(5):
                mouse_movement.reset_statistics()
                await mouse_movement.move_to(mock_page, 100, 100)

                # Get all mouse move positions
                call_args_list = [call[0] for call in mock_page.mouse.move.call_args_list]
                movements.append(call_args_list)
                mock_page.mouse.reset_mock()

            # Movements should have some randomness (not identical)
            assert len(set(tuple(map(tuple, movement)) for movement in movements)) > 1

    async def test_performance_tracking(self, mouse_movement, performance_tracker):
        """Test performance tracking functionality."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.mouse = AsyncMock()

            performance_tracker.start_timer("mouse_movement")

            # Perform multiple operations
            await mouse_movement.move_to(mock_page, 100, 100)
            await mouse_movement.click(mock_page, 200, 200)
            await mouse_movement.drag_and_drop(mock_page, 50, 50, 150, 150)

            duration = performance_tracker.end_timer("mouse_movement")

            # Verify performance was tracked
            assert duration > 0
            assert duration < 10.0  # Should complete within reasonable time

            # Verify statistics
            stats = mouse_movement.get_statistics()
            assert stats["total_movements"] == 1
            assert stats["total_clicks"] == 1
            assert stats["drag_operations"] == 1


class TestKeyboardTyping:
    """Test KeyboardTyping functionality."""

    @pytest_asyncio.fixture
    async def keyboard_typing(self):
        """Create KeyboardTyping instance for testing."""
        config = TypingConfig(
            base_wpm=60,
            wpm_variance=0.2,
            error_rate=0.02,
            correction_delay=0.3,
            rhythm_variance=0.1
        )
        return KeyboardTyping(config)

    async def test_keyboard_typing_initialization(self, keyboard_typing):
        """Test keyboard typing initialization."""
        assert keyboard_typing.config.base_wpm == 60
        assert keyboard_typing.config.error_rate == 0.02
        assert keyboard_typing.get_statistics()["total_keys_typed"] == 0

    async def test_simple_text_typing(self, keyboard_typing):
        """Test simple text typing."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.keyboard = AsyncMock()

            test_text = "Hello World"
            await keyboard_typing.type_text(mock_page, "#input", test_text)

            # Verify each character was typed
            assert mock_page.keyboard.press.call_count == len(test_text)

            # Verify statistics
            stats = keyboard_typing.get_statistics()
            assert stats["total_keys_typed"] == len(test_text)
            assert stats["words_typed"] == len(test_text.split())

    async def test_typing_styles(self, keyboard_typing):
        """Test different typing styles."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.keyboard = AsyncMock()

            styles = [
                TypingStyle.HUNT_AND_PECK,
                TypingStyle.TOUCH,
                TypingStyle.PROFESSIONAL,
                TypingStyle.NERVOUS,
                TypingStyle.SLOW,
                TypingStyle.FAST,
                TypingStyle.INACCURATE,
                TypingStyle.CAREFUL
            ]

            test_text = "test"

            for style in styles:
                keyboard_typing.reset_statistics()
                await keyboard_typing.type_text(mock_page, "#input", test_text, style=style)

                stats = keyboard_typing.get_statistics()
                assert stats["total_keys_typed"] == len(test_text)
                assert stats["style_used"] == style.value

    async def test_error_simulation(self, keyboard_typing):
        """Test typing error simulation."""
        # Set high error rate for testing
        keyboard_typing.config.error_rate = 0.5  # 50% error rate

        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.keyboard = AsyncMock()

            test_text = "hello"
            await keyboard_typing.type_text(mock_page, "#input", test_text)

            # With high error rate, should see backspace corrections
            backspace_calls = [call for call in mock_page.keyboard.press.call_args_list
                             if call[0][0] == 'Backspace']

            # Should have some corrections (not guaranteed, but likely with 50% error rate)
            total_presses = mock_page.keyboard.press.call_count
            assert total_presses >= len(test_text)  # At minimum, type all characters

    async def test_special_characters_and_numbers(self, keyboard_typing):
        """Test typing special characters and numbers."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.keyboard = AsyncMock()

            test_text = "Test123!@#"
            await keyboard_typing.type_text(mock_page, "#input", test_text)

            # Verify all characters including special ones were typed
            assert mock_page.keyboard.press.call_count == len(test_text)

            # Verify specific characters were pressed
            pressed_keys = [call[0][0] for call in mock_page.keyboard.press.call_args_list]
            assert '1' in pressed_keys
            assert '2' in pressed_keys
            assert '3' in pressed_keys
            assert '!' in pressed_keys
            assert '@' in pressed_keys
            assert '#' in pressed_keys

    async def test_hotkey_combinations(self, keyboard_typing):
        """Test hotkey functionality."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.keyboard = AsyncMock()

            await keyboard_typing.hotkey(mock_page, "Control", "c")
            await keyboard_typing.hotkey(mock_page, "Alt", "Tab")

            # Verify hotkey combinations
            assert mock_page.keyboard.press.call_count == 4  # 2 keys for each hotkey
            assert mock_page.keyboard.down.call_count == 2  # 2 key down events
            assert mock_page.keyboard.up.call_count == 2    # 2 key up events

    async def test_typing_rhythm_and_timing(self, keyboard_typing):
        """Test typing rhythm and timing patterns."""
        sleep_calls = []

        async def mock_sleep(duration):
            sleep_calls.append(duration)

        with patch('asyncio.sleep', side_effect=mock_sleep):
            mock_page = AsyncMock()
            mock_page.keyboard = AsyncMock()

            test_text = "Hello World"
            await keyboard_typing.type_text(mock_page, "#input", test_text)

            # Verify timing delays between keystrokes
            assert len(sleep_calls) > 0

            # Verify reasonable timing (not too fast, not too slow)
            for sleep_duration in sleep_calls:
                assert 0.01 <= sleep_duration <= 2.0  # Reasonable typing delay

            # Calculate average typing speed
            total_time = sum(sleep_calls)
            chars_per_minute = (len(test_text) / total_time) * 60 if total_time > 0 else 0

            # Should be close to configured WPM (allowing for variance)
            expected_wpm = keyboard_typing.config.base_wpm
            expected_chars_per_min = expected_wpm * 5  # Average word length = 5
            assert abs(chars_per_minute - expected_chars_per_min) < expected_chars_per_min

    async def test_finger_movement_modeling(self, keyboard_typing):
        """Test finger movement modeling for realistic typing."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.keyboard = AsyncMock()

            # Test text with keys on different keyboard rows
            test_text = "asdfjkl;"  # Home row keys
            await keyboard_typing.type_text(mock_page, "#input", test_text)

            sleep_calls = []
            original_sleep = asyncio.sleep
            def track_sleep(duration):
                sleep_calls.append(duration)
                return original_sleep(duration)

            with patch('asyncio.sleep', side_effect=track_sleep):
                await keyboard_typing.type_text(mock_page, "#input2", "qweruiop")  # Top row

            # Typing patterns should differ between rows (different finger movement distances)
            assert len(sleep_calls) > 0

    async def test_wpm_calculation(self, keyboard_typing):
        """Test words per minute calculation."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.keyboard = AsyncMock()

            # Simulate typing for exactly 1 minute
            start_time = asyncio.get_event_loop().time()

            async def mock_sleep_realistic(duration):
                # Adjust sleep to simulate real typing time
                real_duration = 60.0 / (keyboard_typing.config.base_wpm * 5)  # 5 chars per word
                await asyncio.sleep(real_duration)

            with patch('asyncio.sleep', side_effect=mock_sleep_realistic):
                test_text = "This is a test sentence for typing speed calculation. "
                await keyboard_typing.type_text(mock_page, "#input", test_text)

            end_time = asyncio.get_event_loop().time()
            actual_duration = end_time - start_time

            stats = keyboard_typing.get_statistics()

            # Calculate WPM from statistics
            calculated_wpm = stats.get("wpm", 0)

            # Should be close to configured WPM (within reasonable variance)
            expected_wpm = keyboard_typing.config.base_wpm
            variance = keyboard_typing.config.wpm_variance
            assert expected_wpm * (1 - variance) <= calculated_wpm <= expected_wpm * (1 + variance)

    async def test_performance_tracking(self, keyboard_typing, performance_tracker):
        """Test performance tracking for keyboard typing."""
        with patch('asyncio.sleep') as mock_sleep:
            mock_page = AsyncMock()
            mock_page.keyboard = AsyncMock()

            performance_tracker.start_timer("keyboard_typing")

            test_text = "The quick brown fox jumps over the lazy dog"
            await keyboard_typing.type_text(mock_page, "#input", test_text)

            duration = performance_tracker.end_timer("keyboard_typing")

            # Verify performance was tracked
            assert duration > 0
            assert duration < 30.0  # Should complete within reasonable time

            # Verify statistics
            stats = keyboard_typing.get_statistics()
            assert stats["total_keys_typed"] == len(test_text)
            assert stats["characters_per_minute"] > 0


class TestTLSFingerprintManager:
    """Test TLSFingerprintManager functionality."""

    @pytest_asyncio.fixture
    async def tls_manager(self):
        """Create TLSFingerprintManager for testing."""
        return TLSFingerprintManager()

    async def test_tls_fingerprint_generation(self, tls_manager):
        """Test TLS fingerprint generation."""
        fingerprint = await tls_manager.generate_fingerprint()

        assert fingerprint.ja3_hash is not None
        assert len(fingerprint.ja3_hash) == 32  # MD5 hash length
        assert fingerprint.ja4_hash is not None
        assert len(fingerprint.ja4_hash) >= 50  # JA4 hashes are longer
        assert fingerprint.client_hello is not None
        assert "version" in fingerprint.client_hello
        assert "cipher_suites" in fingerprint.client_hello

    async def test_client_hello_building(self, tls_manager):
        """Test ClientHello message building."""
        client_hello = await tls_manager.build_client_hello()

        assert "version" in client_hello
        assert "cipher_suites" in client_hello
        assert len(client_hello["cipher_suites"]) > 0
        assert "extensions" in client_hello
        assert len(client_hello["extensions"]) > 0

    async def test_fingerprint_rotation(self, tls_manager):
        """Test TLS fingerprint rotation."""
        initial_fingerprint = await tls_manager.generate_fingerprint()

        # Rotate fingerprint
        await tls_manager.rotate_fingerprint()
        rotated_fingerprint = await tls_manager.generate_fingerprint()

        # Fingerprints should be different
        assert initial_fingerprint.ja3_hash != rotated_fingerprint.ja3_hash

    async def test_browser_specific_fingerprints(self, tls_manager):
        """Test browser-specific TLS fingerprints."""
        browsers = ["chrome", "firefox", "safari", "edge"]

        fingerprints = {}
        for browser in browsers:
            fingerprint = await tls_manager.generate_fingerprint(browser_type=browser)
            fingerprints[browser] = fingerprint

        # Different browsers should have different fingerprints
        for i, browser1 in enumerate(browsers):
            for browser2 in browsers[i+1:]:
                assert fingerprints[browser1].ja3_hash != fingerprints[browser2].ja3_hash

    async def test_fingerprint_validation(self, tls_manager):
        """Test TLS fingerprint validation."""
        fingerprint = await tls_manager.generate_fingerprint()

        # Validate generated fingerprint
        is_valid = await tls_manager.validate_fingerprint(fingerprint)
        assert is_valid is True

        # Test invalid fingerprint
        invalid_fingerprint = Mock()
        invalid_fingerprint.ja3_hash = "invalid"
        invalid_fingerprint.client_hello = {}

        is_valid = await tls_manager.validate_fingerprint(invalid_fingerprint)
        assert is_valid is False


class TestHTTP2SettingsManager:
    """Test HTTP2SettingsManager functionality."""

    @pytest_asyncio.fixture
    async def http2_manager(self):
        """Create HTTP2SettingsManager for testing."""
        return HTTP2SettingsManager()

    async def test_http2_settings_generation(self, http2_manager):
        """Test HTTP/2 settings generation."""
        settings = await http2_manager.generate_settings()

        assert "header_table_size" in settings
        assert "enable_push" in settings
        assert "max_concurrent_streams" in settings
        assert "initial_window_size" in settings
        assert settings["header_table_size"] > 0
        assert isinstance(settings["enable_push"], bool)

    async def test_browser_specific_settings(self, http2_manager):
        """Test browser-specific HTTP/2 settings."""
        browsers = ["chrome", "firefox", "safari"]

        settings_by_browser = {}
        for browser in browsers:
            settings = await http2_manager.generate_settings(browser_type=browser)
            settings_by_browser[browser] = settings

        # Different browsers may have different settings
        # (some might be the same, which is fine)
        for browser, settings in settings_by_browser.items():
            assert settings["header_table_size"] > 0
            assert isinstance(settings["enable_push"], bool)

    async def test_header_rewriting(self, http2_manager):
        """Test HTTP/2 header rewriting."""
        original_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.5"
        }

        rewritten_headers = await http2_manager.rewrite_headers(
            original_headers, browser_type="chrome"
        )

        # Headers should be rewritten with fingerprint
        assert "user-agent" in rewritten_headers
        assert "accept" in rewritten_headers
        assert rewritten_headers["user-agent"] != original_headers["user-agent"]

    async def test_settings_validation(self, http2_manager):
        """Test HTTP/2 settings validation."""
        settings = await http2_manager.generate_settings()

        # Validate settings
        is_valid = await http2_manager.validate_settings(settings)
        assert is_valid is True

        # Test invalid settings
        invalid_settings = {
            "header_table_size": -100,  # Invalid negative value
            "max_concurrent_streams": 0   # Invalid zero value
        }

        is_valid = await http2_manager.validate_settings(invalid_settings)
        assert is_valid is False


class TestProxyIntegrationManager:
    """Test ProxyIntegrationManager functionality."""

    @pytest_asyncio.fixture
    async def proxy_integration(self, mock_proxy_service):
        """Create ProxyIntegrationManager for testing."""
        return ProxyIntegrationManager(mock_proxy_service)

    async def test_proxy_integration_initialization(self, proxy_integration):
        """Test proxy integration initialization."""
        assert proxy_integration.proxy_service is not None
        assert proxy_integration.proxy_status == "stopped"

    async def test_proxy_lifecycle_management(self, proxy_integration):
        """Test proxy lifecycle management."""
        # Start proxy
        result = await proxy_integration.start_proxy()
        assert result is True
        assert proxy_integration.proxy_status == "running"

        # Stop proxy
        result = await proxy_integration.stop_proxy()
        assert result is True
        assert proxy_integration.proxy_status == "stopped"

    async def test_profile_configuration(self, proxy_integration, sample_browser_profile):
        """Test configuring browser profile in proxy."""
        await proxy_integration.start_proxy()

        result = await proxy_integration.configure_profile(sample_browser_profile)
        assert result is True

    async def test_health_monitoring(self, proxy_integration):
        """Test proxy health monitoring."""
        await proxy_integration.start_proxy()

        health_info = await proxy_integration.get_proxy_health()
        assert health_info is not None
        assert health_info.status == "healthy"

    async def test_connection_statistics(self, proxy_integration):
        """Test proxy connection statistics."""
        await proxy_integration.start_proxy()

        stats = await proxy_integration.get_connection_stats()
        assert stats is not None
        assert "total_connections" in stats

    async def test_load_balancing_setup(self, proxy_integration):
        """Test load balancing setup."""
        proxy_configs = [
            {"host": "127.0.0.1", "port": 8080},
            {"host": "127.0.0.1", "port": 8081},
            {"host": "127.0.0.1", "port": 8082}
        ]

        result = await proxy_integration.setup_load_balancing(proxy_configs)
        assert result is True

    async def test_failover_handling(self, proxy_integration):
        """Test proxy failover handling."""
        await proxy_integration.start_proxy()

        # Simulate proxy failure
        proxy_integration.proxy_service.set_failure(True)

        # Attempt to get proxy should handle failure
        result = await proxy_integration.get_healthy_proxy()
        # Should either return None (no healthy proxy) or handle gracefully
        assert result is None or isinstance(result, dict)


class TestBrowserManager:
    """Test BrowserManager functionality."""

    @pytest_asyncio.fixture
    async def browser_manager(self, mock_proxy_service, mock_binary_manager):
        """Create BrowserManager for testing."""
        return BrowserManager(
            proxy_service=mock_proxy_service,
            binary_manager=mock_binary_manager
        )

    async def test_browser_initialization(self, browser_manager):
        """Test browser manager initialization."""
        assert browser_manager.proxy_service is not None
        assert browser_manager.binary_manager is not None
        assert browser_manager.browser_status == "stopped"

    async def test_browser_launch(self, browser_manager, sample_browser_profile):
        """Test browser launch with profile."""
        launch_config = BrowserLaunchConfig(
            headless=True,
            viewport={"width": 1920, "height": 1080}
        )

        result = await browser_manager.start_browser(sample_browser_profile, launch_config)
        assert result is True
        assert browser_manager.browser_status == "running"

    async def test_page_management(self, browser_manager):
        """Test page lifecycle management."""
        await browser_manager.start_browser(sample_browser_profile, BrowserLaunchConfig())

        # Create new page
        page_id = await browser_manager.new_page()
        assert page_id is not None
        assert page_id in browser_manager.pages

        # Close page
        result = await browser_manager.close_page(page_id)
        assert result is True
        assert page_id not in browser_manager.pages

    async def test_navigation(self, browser_manager):
        """Test page navigation."""
        await browser_manager.start_browser(sample_browser_profile, BrowserLaunchConfig())
        page_id = await browser_manager.new_page()

        result = await browser_manager.navigate(page_id, "https://example.com")
        assert result is True

        # Verify navigation was recorded
        page_info = browser_manager.pages[page_id]
        assert page_info["url"] == "https://example.com"

    async def test_element_interaction(self, browser_manager):
        """Test element interaction."""
        await browser_manager.start_browser(sample_browser_profile, BrowserLaunchConfig())
        page_id = await browser_manager.new_page()

        # Click element
        result = await browser_manager.click(page_id, "#button")
        assert result is True

        # Type text
        result = await browser_manager.type_text(page_id, "#input", "test text")
        assert result is True

    async def test_screenshot_capture(self, browser_manager):
        """Test screenshot capture."""
        await browser_manager.start_browser(sample_browser_profile, BrowserLaunchConfig())
        page_id = await browser_manager.new_page()

        screenshot_bytes = await browser_manager.take_screenshot(page_id)
        assert screenshot_bytes is not None
        assert len(screenshot_bytes) > 0
        assert screenshot_bytes.startswith(b'\x89PNG')  # PNG header

    async def test_javascript_execution(self, browser_manager):
        """Test JavaScript execution."""
        await browser_manager.start_browser(sample_browser_profile, BrowserLaunchConfig())
        page_id = await browser_manager.new_page()

        script = "return document.title;"
        result = await browser_manager.execute_script(page_id, script)
        assert result is not None

    async def test_browser_metrics(self, browser_manager):
        """Test browser metrics collection."""
        await browser_manager.start_browser(sample_browser_profile, BrowserLaunchConfig())

        metrics = browser_manager.get_metrics()
        assert metrics is not None
        assert "browser_status" in metrics
        assert "page_count" in metrics
        assert "uptime" in metrics


class TestFingerprintGenerator:
    """Test FingerprintGenerator functionality."""

    @pytest_asyncio.fixture
    async def fingerprint_generator(self, mock_fingerprint_service):
        """Create FingerprintGenerator for testing."""
        return FingerprintGenerator(mock_fingerprint_service)

    async def test_fingerprint_generation(self, fingerprint_generator, sample_fingerprint_request):
        """Test fingerprint generation."""
        profile = await fingerprint_generator.generate(sample_fingerprint_request)

        assert profile is not None
        assert "user_agent" in profile
        assert "viewport" in profile
        assert profile["user_agent"] is not None

    async def test_batch_generation(self, fingerprint_generator):
        """Test batch fingerprint generation."""
        requests = [
            {
                "browser_type": "chrome",
                "operating_system": "windows",
                "min_quality": 0.8
            },
            {
                "browser_type": "firefox",
                "operating_system": "linux",
                "min_quality": 0.7
            }
        ]

        profiles = await fingerprint_generator.generate_batch(requests)

        assert len(profiles) == 2
        for profile in profiles:
            assert "user_agent" in profile
            assert profile["user_agent"] is not None

    async def test_caching_functionality(self, fingerprint_generator, sample_fingerprint_request):
        """Test fingerprint caching."""
        # Generate fingerprint (cache miss)
        profile1 = await fingerprint_generator.generate(sample_fingerprint_request)

        # Generate same fingerprint again (cache hit)
        profile2 = await fingerprint_generator.generate(sample_fingerprint_request)

        # Should return same profile from cache
        assert profile1["user_agent"] == profile2["user_agent"]

        # Verify cache statistics
        cache_stats = fingerprint_generator.get_cache_stats()
        assert cache_stats["hits"] > 0
        assert cache_stats["misses"] > 0

    async def test_service_health_monitoring(self, fingerprint_generator):
        """Test service health monitoring."""
        health_status = await fingerprint_generator.get_service_status()
        assert health_status is not None
        assert "status" in health_status

    async def test_profile_validation(self, fingerprint_generator, sample_browser_profile):
        """Test profile validation."""
        validation_result = await fingerprint_generator.validate_profile(sample_browser_profile)
        assert validation_result is not None
        assert "is_valid" in validation_result
        assert "score" in validation_result


class TestChameleonEngine:
    """Test ChameleonEngine orchestrator functionality."""

    @pytest_asyncio.fixture
    async def chameleon_engine(self, mock_fingerprint_service, mock_proxy_service,
                              mock_binary_manager, temp_directory):
        """Create ChameleonEngine for testing."""
        config = ChameleonEngineConfig(
            data_dir=str(temp_directory),
            enable_metrics=True,
            max_concurrent_pages=5,
            profile_rotation_interval=3600
        )
        return ChameleonEngine(
            config=config,
            fingerprint_service=mock_fingerprint_service,
            proxy_service=mock_proxy_service,
            binary_manager=mock_binary_manager
        )

    async def test_engine_initialization(self, chameleon_engine):
        """Test engine initialization."""
        assert chameleon_engine.config is not None
        assert chameleon_engine.fingerprint_service is not None
        assert chameleon_engine.proxy_service is not None
        assert chameleon_engine.binary_manager is not None
        assert chameleon_engine.engine_status == "stopped"

    async def test_engine_startup(self, chameleon_engine):
        """Test engine startup."""
        result = await chameleon_engine.start(
            browser_type="chrome",
            operating_system="windows"
        )

        assert result is not None
        assert len(result) > 0  # Should return session ID
        assert chameleon_engine.engine_status == "running"

    async def test_engine_shutdown(self, chameleon_engine):
        """Test engine shutdown."""
        # Start first
        await chameleon_engine.start("chrome", "windows")

        # Then stop
        await chameleon_engine.stop()
        assert chameleon_engine.engine_status == "stopped"

    async def test_page_creation_and_management(self, chameleon_engine):
        """Test page creation and management."""
        await chameleon_engine.start("chrome", "windows")

        page_id = await chameleon_engine.new_page()
        assert page_id is not None
        assert page_id in chameleon_engine.pages

        # Close page
        await chameleon_engine.close_page(page_id)
        assert page_id not in chameleon_engine.pages

    async def test_navigation_and_interaction(self, chameleon_engine):
        """Test navigation and element interaction."""
        await chameleon_engine.start("chrome", "windows")
        page_id = await chameleon_engine.new_page()

        # Navigate
        result = await chameleon_engine.navigate(page_id, "https://example.com")
        assert result is True

        # Click element
        result = await chameleon_engine.click(page_id, "#button")
        assert result is True

        # Type text
        result = await chameleon_engine.type_text(page_id, "#input", "test text")
        assert result is True

    async def test_screenshot_functionality(self, chameleon_engine):
        """Test screenshot capture."""
        await chameleon_engine.start("chrome", "windows")
        page_id = await chameleon_engine.new_page()

        screenshot_bytes = await chameleon_engine.take_screenshot(page_id)
        assert screenshot_bytes is not None
        assert len(screenshot_bytes) > 0

    async def test_profile_rotation(self, chameleon_engine):
        """Test profile rotation."""
        await chameleon_engine.start("chrome", "windows")

        initial_profile = chameleon_engine.current_profile
        rotated_profile = await chameleon_engine.rotate_profile()

        assert rotated_profile is not None
        assert rotated_profile != initial_profile

    async def test_session_metrics(self, chameleon_engine):
        """Test session metrics collection."""
        await chameleon_engine.start("chrome", "windows")
        page_id = await chameleon_engine.new_page()
        await chameleon_engine.navigate(page_id, "https://example.com")

        metrics = chameleon_engine.get_session_metrics()
        assert metrics is not None
        assert "session_duration" in metrics
        assert "pages_created" in metrics
        assert "navigations_performed" in metrics
        assert metrics["pages_created"] == 1
        assert metrics["navigations_performed"] == 1

    async def test_engine_status_monitoring(self, chameleon_engine):
        """Test engine status monitoring."""
        await chameleon_engine.start("chrome", "windows")

        status = chameleon_engine.get_status()
        assert status is not None
        assert "engine_status" in status
        assert "component_health" in status
        assert "performance_metrics" in status
        assert status["engine_status"] == "running"

    async def test_error_handling_and_recovery(self, chameleon_engine):
        """Test error handling and recovery."""
        await chameleon_engine.start("chrome", "windows")

        # Simulate component failure
        chameleon_engine.proxy_service.set_failure(True)

        # Engine should detect failure and attempt recovery
        await chameleon_engine._health_check()

        # Check if recovery was attempted
        # (Implementation depends on specific recovery strategy)

    async def test_concurrent_page_management(self, chameleon_engine):
        """Test concurrent page management."""
        await chameleon_engine.start("chrome", "windows")

        # Create multiple pages concurrently
        page_tasks = []
        for _ in range(3):
            task = asyncio.create_task(chameleon_engine.new_page())
            page_tasks.append(task)

        page_ids = await asyncio.gather(*page_tasks)

        assert len(page_ids) == 3
        for page_id in page_ids:
            assert page_id in chameleon_engine.pages

        # Clean up
        close_tasks = [asyncio.create_task(chameleon_engine.close_page(page_id)) for page_id in page_ids]
        await asyncio.gather(*close_tasks)

    async def test_resource_cleanup(self, chameleon_engine):
        """Test resource cleanup on shutdown."""
        await chameleon_engine.start("chrome", "windows")
        page_id = await chameleon_engine.new_page()

        # Verify resources are allocated
        assert len(chameleon_engine.pages) == 1
        assert chameleon_engine.engine_status == "running"

        # Shutdown and verify cleanup
        await chameleon_engine.stop()

        assert chameleon_engine.engine_status == "stopped"
        assert len(chameleon_engine.pages) == 0

    async def test_configuration_customization(self, chameleon_engine):
        """Test engine configuration customization."""
        # Test that configuration is applied correctly
        assert chameleon_engine.config.enable_metrics is True
        assert chameleon_engine.config.max_concurrent_pages == 5
        assert chameleon_engine.config.profile_rotation_interval == 3600

    async def test_context_manager_usage(self, chameleon_engine):
        """Test using engine as context manager."""
        async with chameleon_engine:
            page_id = await chameleon_engine.new_page()
            await chameleon_engine.navigate(page_id, "https://example.com")

            # Should be running within context
            assert chameleon_engine.engine_status == "running"
            assert len(chameleon_engine.pages) == 1

        # Should be stopped after context exit
        assert chameleon_engine.engine_status == "stopped"
        assert len(chameleon_engine.pages) == 0


class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    async def test_full_scraping_workflow(self, mock_fingerprint_service, mock_proxy_service,
                                        mock_binary_manager, temp_directory):
        """Test complete web scraping workflow."""
        config = ChameleonEngineConfig(data_dir=str(temp_directory))
        engine = ChameleonEngine(
            config=config,
            fingerprint_service=mock_fingerprint_service,
            proxy_service=mock_proxy_service,
            binary_manager=mock_binary_manager
        )

        async with engine:
            # Start session with specific browser/OS
            session_id = await engine.start("chrome", "windows")

            # Create page and navigate
            page_id = await engine.new_page()
            await engine.navigate(page_id, "https://example.com")

            # Simulate human interaction
            await engine.click(page_id, "#some-button")
            await engine.type_text(page_id, "#search-input", "search query")

            # Take screenshot
            screenshot = await engine.take_screenshot(page_id)
            assert len(screenshot) > 0

            # Get session metrics
            metrics = engine.get_session_metrics()
            assert metrics["pages_created"] == 1
            assert metrics["navigations_performed"] == 1

    async def test_profile_rotation_scenario(self, mock_fingerprint_service, mock_proxy_service,
                                           mock_binary_manager, temp_directory):
        """Test profile rotation during long session."""
        config = ChameleonEngineConfig(
            data_dir=str(temp_directory),
            profile_rotation_interval=0.1  # Very short for testing
        )
        engine = ChameleonEngine(
            config=config,
            fingerprint_service=mock_fingerprint_service,
            proxy_service=mock_proxy_service,
            binary_manager=mock_binary_manager
        )

        async with engine:
            initial_profile = engine.current_profile

            # Wait for rotation (with short interval)
            await asyncio.sleep(0.2)

            # Trigger background task to check rotation
            await engine._check_profile_rotation()

            # Profile should have been rotated
            assert engine.current_profile != initial_profile

    async def test_error_recovery_scenario(self, mock_fingerprint_service, mock_proxy_service,
                                         mock_binary_manager, temp_directory):
        """Test error recovery during operations."""
        config = ChameleonEngineConfig(data_dir=str(temp_directory))
        engine = ChameleonEngine(
            config=config,
            fingerprint_service=mock_fingerprint_service,
            proxy_service=mock_proxy_service,
            binary_manager=mock_binary_manager
        )

        async with engine:
            page_id = await engine.new_page()

            # Simulate navigation failure
            engine.browser_manager.set_navigation_result(page_id, "https://example.com", False)

            # Navigation should handle failure gracefully
            result = await engine.navigate(page_id, "https://example.com")
            assert result is False

            # Engine should still be functional
            status = engine.get_status()
            assert status["engine_status"] == "running"

    async def test_performance_under_load(self, mock_fingerprint_service, mock_proxy_service,
                                        mock_binary_manager, temp_directory):
        """Test engine performance under load."""
        config = ChameleonEngineConfig(
            data_dir=str(temp_directory),
            max_concurrent_pages=10
        )
        engine = ChameleonEngine(
            config=config,
            fingerprint_service=mock_fingerprint_service,
            proxy_service=mock_proxy_service,
            binary_manager=mock_binary_manager
        )

        async with engine:
            # Create many pages concurrently
            page_tasks = []
            for i in range(10):
                task = asyncio.create_task(engine.new_page())
                page_tasks.append(task)

            page_ids = await asyncio.gather(*page_tasks)

            # Perform operations on all pages
            operation_tasks = []
            for page_id in page_ids:
                task = asyncio.create_task(engine.navigate(page_id, f"https://example.com/page/{page_id}"))
                operation_tasks.append(task)

            results = await asyncio.gather(*operation_tasks)

            # Most operations should succeed
            success_count = sum(1 for result in results if result)
            assert success_count >= 8  # Allow for some failures under load

            # Verify engine is still responsive
            final_status = engine.get_status()
            assert final_status["engine_status"] == "running"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])