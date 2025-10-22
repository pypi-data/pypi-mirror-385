"""
Tests for Browser Profile models and validation.

Tests the core BrowserProfile, BrowserType, OperatingSystem, and related models
to ensure they properly validate data, maintain consistency, and support serialization.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
import json

from chameleon_engine.core.profiles import (
    BrowserProfile,
    BrowserType,
    OperatingSystem,
    ScreenResolution,
    NavigatorProperties,
    HTTPHeaders,
    TLSFingerprint,
    HTTP2Settings,
    CanvasFingerprint,
    AudioFingerprint,
    ProfileRequest,
    ProfileResult,
    ProfileGenerationOptions
)

# Import test fixtures
from tests.conftest import (
    sample_browser_profile,
    sample_navigator_properties,
    sample_tls_fingerprint,
    sample_http2_settings,
    assert_dicts_almost_equal
)


class TestBrowserType:
    """Test BrowserType enum and validation."""

    def test_browser_type_values(self):
        """Test browser type enum values."""
        assert BrowserType.CHROME.value == "chrome"
        assert BrowserType.FIREFOX.value == "firefox"
        assert BrowserType.SAFARI.value == "safari"
        assert BrowserType.EDGE.value == "edge"
        assert BrowserType.OPERA.value == "opera"

    def test_browser_type_from_string(self):
        """Test creating browser type from string."""
        assert BrowserType("chrome") == BrowserType.CHROME
        assert BrowserType("firefox") == BrowserType.FIREFOX

    def test_browser_type_invalid(self):
        """Test invalid browser type raises error."""
        with pytest.raises(ValueError):
            BrowserType("invalid_browser")


class TestOperatingSystem:
    """Test OperatingSystem enum and validation."""

    def test_os_values(self):
        """Test operating system enum values."""
        assert OperatingSystem.WINDOWS.value == "windows"
        assert OperatingSystem.MACOS.value == "macos"
        assert OperatingSystem.LINUX.value == "linux"
        assert OperatingSystem.ANDROID.value == "android"
        assert OperatingSystem.IOS.value == "ios"

    def test_os_from_string(self):
        """Test creating OS from string."""
        assert OperatingSystem("windows") == OperatingSystem.WINDOWS
        assert OperatingSystem("linux") == OperatingSystem.LINUX


class TestScreenResolution:
    """Test ScreenResolution model validation."""

    def test_valid_screen_resolution(self):
        """Test creating valid screen resolution."""
        resolution = ScreenResolution(width=1920, height=1080)
        assert resolution.width == 1920
        assert resolution.height == 1080
        assert resolution.aspect_ratio == pytest.approx(16.0/9.0, rel=1e-2)

    def test_screen_resolution_validation(self):
        """Test screen resolution validation."""
        # Valid resolutions
        valid_resolutions = [
            (1920, 1080),
            (1366, 768),
            (1440, 900),
            (2560, 1440)
        ]

        for width, height in valid_resolutions:
            resolution = ScreenResolution(width=width, height=height)
            assert resolution.width == width
            assert resolution.height == height
            assert resolution.aspect_ratio > 0

        # Invalid resolutions
        with pytest.raises(ValidationError):
            ScreenResolution(width=0, height=1080)  # Width too small

        with pytest.raises(ValidationError):
            ScreenResolution(width=1920, height=0)  # Height too small

        with pytest.raises(ValidationError):
            ScreenResolution(width=-100, height=1080)  # Negative width

    def test_common_resolutions(self):
        """Test common resolution factory methods."""
        fhd = ScreenResolution.fhd()
        assert fhd.width == 1920 and fhd.height == 1080

        hd = ScreenResolution.hd()
        assert hd.width == 1366 and hd.height == 768

        qhd = ScreenResolution.qhd()
        assert qhd.width == 2560 and qhd.height == 1440

        uhd = ScreenResolution.uhd()
        assert uhd.width == 3840 and uhd.height == 2160

    def test_screen_resolution_serialization(self):
        """Test screen resolution serialization."""
        resolution = ScreenResolution(width=1920, height=1080)
        data = resolution.model_dump()
        assert data["width"] == 1920
        assert data["height"] == 1080
        assert "aspect_ratio" in data

        # Test round-trip
        new_resolution = ScreenResolution(**data)
        assert new_resolution.width == resolution.width
        assert new_resolution.height == resolution.height


class TestNavigatorProperties:
    """Test NavigatorProperties model validation."""

    def test_valid_navigator_properties(self, sample_navigator_properties):
        """Test creating valid navigator properties."""
        nav = NavigatorProperties(**sample_navigator_properties)
        assert nav.user_agent == sample_navigator_properties["user_agent"]
        assert nav.platform == sample_navigator_properties["platform"]
        assert nav.language == sample_navigator_properties["language"]
        assert nav.hardware_concurrency == sample_navigator_properties["hardware_concurrency"]
        assert nav.device_memory == sample_navigator_properties["device_memory"]

    def test_navigator_properties_validation(self):
        """Test navigator properties validation."""
        # Test valid user agent
        valid_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        nav = NavigatorProperties(user_agent=valid_ua, platform="Win32", language="en-US")
        assert nav.user_agent == valid_ua

        # Test invalid user agent (too short)
        with pytest.raises(ValidationError):
            NavigatorProperties(user_agent="short", platform="Win32", language="en-US")

        # Test invalid language format
        with pytest.raises(ValidationError):
            NavigatorProperties(
                user_agent=valid_ua,
                platform="Win32",
                language="invalid_format"
            )

        # Test invalid hardware concurrency
        with pytest.raises(ValidationError):
            NavigatorProperties(
                user_agent=valid_ua,
                platform="Win32",
                language="en-US",
                hardware_concurrency=0
            )

        # Test invalid device memory
        with pytest.raises(ValidationError):
            NavigatorProperties(
                user_agent=valid_ua,
                platform="Win32",
                language="en-US",
                device_memory=0.1  # Too low
            )

    def test_navigator_properties_browser_detection(self, sample_navigator_properties):
        """Test browser type detection from user agent."""
        nav = NavigatorProperties(**sample_navigator_properties)
        assert nav.get_browser_type() == BrowserType.CHROME

        # Test Firefox detection
        firefox_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        nav_firefox = NavigatorProperties(user_agent=firefox_ua, platform="Win32", language="en-US")
        assert nav_firefox.get_browser_type() == BrowserType.FIREFOX

        # Test Safari detection
        safari_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
        nav_safari = NavigatorProperties(user_agent=safari_ua, platform="MacIntel", language="en-US")
        assert nav_safari.get_browser_type() == BrowserType.SAFARI

    def test_navigator_properties_os_detection(self, sample_navigator_properties):
        """Test OS detection from user agent and platform."""
        nav = NavigatorProperties(**sample_navigator_properties)
        assert nav.get_operating_system() == OperatingSystem.WINDOWS

        # Test macOS detection
        mac_nav = NavigatorProperties(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            platform="MacIntel",
            language="en-US"
        )
        assert mac_nav.get_operating_system() == OperatingSystem.MACOS

        # Test Linux detection
        linux_nav = NavigatorProperties(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            platform="Linux x86_64",
            language="en-US"
        )
        assert linux_nav.get_operating_system() == OperatingSystem.LINUX


class TestHTTPHeaders:
    """Test HTTPHeaders model validation."""

    def test_valid_headers(self):
        """Test creating valid HTTP headers."""
        headers_data = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.5",
            "accept-encoding": "gzip, deflate, br",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "upgrade-insecure-requests": "1"
        }

        headers = HTTPHeaders(**headers_data)
        assert headers.accept == headers_data["accept"]
        assert headers.accept_language == headers_data["accept-language"]
        assert headers.user_agent == headers_data["user-agent"]

    def test_header_validation(self):
        """Test header validation rules."""
        # Test valid accept header
        valid_accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        headers = HTTPHeaders(accept=valid_accept)
        assert headers.accept == valid_accept

        # Test invalid accept header (empty)
        with pytest.raises(ValidationError):
            HTTPHeaders(accept="")

        # Test invalid user agent (too short)
        with pytest.raises(ValidationError):
            HTTPHeaders(user_agent="short")

    def test_header_case_insensitivity(self):
        """Test that header names are case insensitive."""
        headers_data = {
            "Accept": "text/html,application/xhtml+xml",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Content-Type": "application/json"
        }

        headers = HTTPHeaders(**headers_data)
        assert headers.accept == headers_data["Accept"]
        assert headers.user_agent == headers_data["User-Agent"]
        assert headers.content_type == headers_data["Content-Type"]

    def test_header_serialization(self):
        """Test header serialization to dict."""
        headers_data = {
            "accept": "text/html,application/xhtml+xml",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        headers = HTTPHeaders(**headers_data)
        serialized = headers.model_dump()

        assert serialized["accept"] == headers_data["accept"]
        assert serialized["user-agent"] == headers_data["user-agent"]


class TestTLSFingerprint:
    """Test TLSFingerprint model validation."""

    def test_valid_tls_fingerprint(self, sample_tls_fingerprint):
        """Test creating valid TLS fingerprint."""
        tls = TLSFingerprint(**sample_tls_fingerprint)
        assert tls.ja3_hash == sample_tls_fingerprint["ja3_hash"]
        assert tls.ja4_hash == sample_tls_fingerprint["ja4_hash"]
        assert tls.client_hello["version"] == sample_tls_fingerprint["client_hello"]["version"]

    def test_tls_fingerprint_validation(self):
        """Test TLS fingerprint validation."""
        # Test valid JA3 hash
        valid_ja3 = "c3b4b1f5c1234567890abcdef1234567890abcdef"
        tls = TLSFingerprint(ja3_hash=valid_ja3)
        assert tls.ja3_hash == valid_ja3

        # Test invalid JA3 hash (wrong length)
        with pytest.raises(ValidationError):
            TLSFingerprint(ja3_hash="short")

        # Test invalid JA3 hash (invalid characters)
        with pytest.raises(ValidationError):
            TLSFingerprint(ja3_hash="invalid_hash_chars!@#")

    def test_client_hello_validation(self):
        """Test ClientHello structure validation."""
        valid_client_hello = {
            "version": "TLSv1.3",
            "cipher_suites": [
                "TLS_AES_128_GCM_SHA256",
                "TLS_AES_256_GCM_SHA384"
            ],
            "extensions": [
                "server_name",
                "supported_groups"
            ],
            "signature_algorithms": [
                "ecdsa_secp256r1_sha256"
            ],
            "supported_groups": [
                "x25519",
                "secp256r1"
            ]
        }

        tls = TLSFingerprint(
            ja3_hash="c3b4b1f5c1234567890abcdef1234567890abcdef",
            client_hello=valid_client_hello
        )
        assert tls.client_hello["version"] == "TLSv1.3"
        assert len(tls.client_hello["cipher_suites"]) == 2

        # Test invalid ClientHello (missing required fields)
        with pytest.raises(ValidationError):
            TLSFingerprint(
                ja3_hash="c3b4b1f5c1234567890abcdef1234567890abcdef",
                client_hello={"version": "TLSv1.3"}  # Missing cipher_suites
            )


class TestHTTP2Settings:
    """Test HTTP2Settings model validation."""

    def test_valid_http2_settings(self, sample_http2_settings):
        """Test creating valid HTTP/2 settings."""
        http2 = HTTP2Settings(**sample_http2_settings)
        assert http2.header_table_size == sample_http2_settings["header_table_size"]
        assert http2.enable_push == sample_http2_settings["enable_push"]
        assert http2.max_concurrent_streams == sample_http2_settings["max_concurrent_streams"]

    def test_http2_settings_validation(self):
        """Test HTTP/2 settings validation."""
        # Test valid settings
        settings = HTTP2Settings(
            header_table_size=4096,
            enable_push=False,
            max_concurrent_streams=1000
        )
        assert settings.header_table_size == 4096
        assert settings.enable_push is False

        # Test invalid header_table_size (too small)
        with pytest.raises(ValidationError):
            HTTP2Settings(header_table_size=0)

        # Test invalid max_concurrent_streams (too small)
        with pytest.raises(ValidationError):
            HTTP2Settings(max_concurrent_streams=0)

        # Test invalid initial_window_size (out of range)
        with pytest.raises(ValidationError):
            HTTP2Settings(initial_window_size=2**33)  # Too large

    def test_default_settings(self):
        """Test default HTTP/2 settings."""
        settings = HTTP2Settings()
        assert settings.header_table_size == 4096
        assert settings.enable_push is False
        assert settings.max_concurrent_streams == 1000
        assert settings.initial_window_size == 65535
        assert settings.max_frame_size == 16384
        assert settings.max_header_list_size == 8192


class TestCanvasFingerprint:
    """Test CanvasFingerprint model validation."""

    def test_valid_canvas_fingerprint(self):
        """Test creating valid canvas fingerprint."""
        canvas = CanvasFingerprint(
            fingerprint="canvas_fingerprint_hash_12345",
            noise_level=0.1,
            width=1920,
            height=1080
        )
        assert canvas.fingerprint == "canvas_fingerprint_hash_12345"
        assert canvas.noise_level == 0.1
        assert canvas.width == 1920
        assert canvas.height == 1080

    def test_canvas_fingerprint_validation(self):
        """Test canvas fingerprint validation."""
        # Test valid values
        canvas = CanvasFingerprint(
            fingerprint="valid_hash_12345",
            noise_level=0.05
        )
        assert canvas.noise_level == 0.05

        # Test invalid fingerprint (too short)
        with pytest.raises(ValidationError):
            CanvasFingerprint(fingerprint="short")

        # Test invalid noise_level (negative)
        with pytest.raises(ValidationError):
            CanvasFingerprint(
                fingerprint="valid_hash_12345",
                noise_level=-0.1
            )

        # Test invalid noise_level (too high)
        with pytest.raises(ValidationError):
            CanvasFingerprint(
                fingerprint="valid_hash_12345",
                noise_level=1.5
            )


class TestAudioFingerprint:
    """Test AudioFingerprint model validation."""

    def test_valid_audio_fingerprint(self):
        """Test creating valid audio fingerprint."""
        audio = AudioFingerprint(
            fingerprint="audio_fingerprint_hash_12345",
            noise_level=0.05,
            sample_rate=44100
        )
        assert audio.fingerprint == "audio_fingerprint_hash_12345"
        assert audio.noise_level == 0.05
        assert audio.sample_rate == 44100

    def test_audio_fingerprint_validation(self):
        """Test audio fingerprint validation."""
        # Test valid values
        audio = AudioFingerprint(
            fingerprint="valid_hash_12345",
            noise_level=0.1,
            sample_rate=48000
        )
        assert audio.noise_level == 0.1
        assert audio.sample_rate == 48000

        # Test invalid sample_rate (too low)
        with pytest.raises(ValidationError):
            AudioFingerprint(
                fingerprint="valid_hash_12345",
                sample_rate=1000  # Too low
            )

        # Test invalid sample_rate (not a common rate)
        with pytest.raises(ValidationError):
            AudioFingerprint(
                fingerprint="valid_hash_12345",
                sample_rate=12345  # Not a standard rate
            )


class TestBrowserProfile:
    """Test BrowserProfile model validation and operations."""

    def test_valid_browser_profile(self, sample_browser_profile):
        """Test creating valid browser profile."""
        profile = BrowserProfile(**sample_browser_profile)
        assert profile.user_agent == sample_browser_profile["user_agent"]
        assert profile.viewport["width"] == sample_browser_profile["viewport"]["width"]
        assert profile.timezone == sample_browser_profile["timezone"]
        assert profile.language == sample_browser_profile["language"]

    def test_browser_profile_validation(self):
        """Test browser profile validation."""
        # Test minimal valid profile
        minimal_profile = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "viewport": {"width": 1920, "height": 1080},
            "screen": {"width": 1920, "height": 1080, "color_depth": 24, "pixel_depth": 24},
            "timezone": "America/New_York",
            "language": "en-US"
        }

        profile = BrowserProfile(**minimal_profile)
        assert profile.user_agent == minimal_profile["user_agent"]
        assert profile.viewport["width"] == 1920

        # Test invalid user agent (too short)
        with pytest.raises(ValidationError):
            BrowserProfile(
                user_agent="short",
                viewport={"width": 1920, "height": 1080},
                screen={"width": 1920, "height": 1080, "color_depth": 24, "pixel_depth": 24},
                timezone="America/New_York",
                language="en-US"
            )

        # Test invalid viewport dimensions
        with pytest.raises(ValidationError):
            BrowserProfile(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                viewport={"width": 0, "height": 1080},  # Invalid width
                screen={"width": 1920, "height": 1080, "color_depth": 24, "pixel_depth": 24},
                timezone="America/New_York",
                language="en-US"
            )

    def test_browser_profile_consistency_validation(self, sample_browser_profile):
        """Test browser profile consistency validation."""
        # Test consistent profile
        profile = BrowserProfile(**sample_browser_profile)
        consistency_score = profile.calculate_consistency_score()
        assert consistency_score >= 0.0
        assert consistency_score <= 1.0

        # Test inconsistent profile (Windows timezone but macOS user agent)
        inconsistent_profile = sample_browser_profile.copy()
        inconsistent_profile["user_agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        inconsistent_profile["platform"] = "MacIntel"

        with pytest.raises(ValidationError):
            BrowserProfile(**inconsistent_profile)

    def test_browser_profile_serialization(self, sample_browser_profile):
        """Test browser profile serialization."""
        profile = BrowserProfile(**sample_browser_profile)

        # Test dict serialization
        profile_dict = profile.model_dump()
        assert profile_dict["user_agent"] == sample_browser_profile["user_agent"]
        assert profile_dict["viewport"]["width"] == sample_browser_profile["viewport"]["width"]

        # Test JSON serialization
        profile_json = profile.model_dump_json()
        parsed = json.loads(profile_json)
        assert parsed["user_agent"] == sample_browser_profile["user_agent"]

        # Test round-trip
        new_profile = BrowserProfile(**profile_dict)
        assert new_profile.user_agent == profile.user_agent
        assert new_profile.viewport == profile.viewport

    def test_browser_profile_fingerprint_extraction(self, sample_browser_profile):
        """Test fingerprint extraction from profile."""
        profile = BrowserProfile(**sample_browser_profile)

        # Test browser type detection
        assert profile.get_browser_type() == BrowserType.CHROME

        # Test OS detection
        assert profile.get_operating_system() == OperatingSystem.WINDOWS

        # Test screen resolution detection
        resolution = profile.get_screen_resolution()
        assert resolution.width == sample_browser_profile["viewport"]["width"]
        assert resolution.height == sample_browser_profile["viewport"]["height"]

    def test_browser_profile_expiration(self, sample_browser_profile):
        """Test browser profile expiration handling."""
        profile = BrowserProfile(**sample_browser_profile)

        # Test non-expired profile
        assert not profile.is_expired()

        # Test expired profile
        import datetime
        expired_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        profile.expires_at = expired_time
        assert profile.is_expired()

    def test_browser_profile_usage_tracking(self, sample_browser_profile):
        """Test usage tracking functionality."""
        profile = BrowserProfile(**sample_browser_profile)

        # Test initial usage
        assert profile.usage_count == 0
        assert profile.last_used_at is None

        # Test usage increment
        profile.increment_usage()
        assert profile.usage_count == 1
        assert profile.last_used_at is not None

        # Test multiple usage increments
        for _ in range(5):
            profile.increment_usage()
        assert profile.usage_count == 6

    def test_browser_profile_copy_and_modify(self, sample_browser_profile):
        """Test profile copying and modification."""
        profile = BrowserProfile(**sample_browser_profile)

        # Test profile copy
        copied_profile = profile.copy()
        assert copied_profile.user_agent == profile.user_agent
        assert copied_profile is not profile  # Different objects

        # Test profile modification
        modified_profile = profile.copy()
        modified_profile.language = "fr-FR"
        assert modified_profile.language == "fr-FR"
        assert profile.language == sample_browser_profile["language"]  # Original unchanged

    def test_browser_profile_quality_score(self, sample_browser_profile):
        """Test profile quality scoring."""
        profile = BrowserProfile(**sample_browser_profile)

        # Test quality score calculation
        quality_score = profile.calculate_quality_score()
        assert 0.0 <= quality_score <= 1.0

        # Test complete profile (should have high score)
        complete_profile_data = sample_browser_profile.copy()
        complete_profile_data.update({
            "webgl": {
                "vendor": "Google Inc.",
                "renderer": "ANGLE (Intel(R) HD Graphics 630)",
                "version": "WebGL 2.0"
            },
            "canvas": {
                "fingerprint": "sample_canvas_fingerprint_hash",
                "noise": 0.1
            },
            "audio": {
                "fingerprint": "sample_audio_fingerprint_hash",
                "noise": 0.05
            }
        })

        complete_profile = BrowserProfile(**complete_profile_data)
        complete_score = complete_profile.calculate_quality_score()
        assert complete_score >= quality_score  # More complete profile should have higher score


class TestProfileRequest:
    """Test ProfileRequest model validation."""

    def test_valid_profile_request(self, sample_fingerprint_request):
        """Test creating valid profile request."""
        request = ProfileRequest(**sample_fingerprint_request)
        assert request.browser_type == BrowserType.CHROME
        assert request.operating_system == OperatingSystem.WINDOWS
        assert request.min_quality == 0.8
        assert request.max_detection_risk == 0.2

    def test_profile_request_validation(self):
        """Test profile request validation."""
        # Test valid request
        request_data = {
            "browser_type": "chrome",
            "operating_system": "windows",
            "min_quality": 0.7,
            "max_detection_risk": 0.3
        }

        request = ProfileRequest(**request_data)
        assert request.browser_type == BrowserType.CHROME
        assert request.operating_system == OperatingSystem.WINDOWS

        # Test invalid quality bounds
        with pytest.raises(ValidationError):
            ProfileRequest(
                browser_type="chrome",
                operating_system="windows",
                min_quality=-0.1  # Negative quality
            )

        with pytest.raises(ValidationError):
            ProfileRequest(
                browser_type="chrome",
                operating_system="windows",
                min_quality=1.1  # Quality > 1.0
            )

        # Test inconsistent constraints (min_quality > max_quality)
        with pytest.raises(ValidationError):
            ProfileRequest(
                browser_type="chrome",
                operating_system="windows",
                min_quality=0.9,
                max_quality=0.8  # Lower than min_quality
            )

    def test_profile_request_constraints(self):
        """Test profile request constraints."""
        # Test with constraints
        constraints = {
            "screen_resolution": {"min_width": 1920, "min_height": 1080},
            "timezone": ["America/New_York", "Europe/London"],
            "language": ["en-US", "en-GB"]
        }

        request = ProfileRequest(
            browser_type="chrome",
            operating_system="windows",
            constraints=constraints
        )

        assert request.constraints["screen_resolution"]["min_width"] == 1920
        assert len(request.constraints["timezone"]) == 2
        assert len(request.constraints["language"]) == 2


class TestProfileResult:
    """Test ProfileResult model validation."""

    def test_valid_profile_result(self, sample_browser_profile):
        """Test creating valid profile result."""
        result = ProfileResult(
            profile=sample_browser_profile,
            generation_time=0.5,
            coherence_score=0.95,
            uniqueness_score=0.88,
            detection_risk=0.12
        )

        assert result.profile["user_agent"] == sample_browser_profile["user_agent"]
        assert result.generation_time == 0.5
        assert result.coherence_score == 0.95
        assert result.uniqueness_score == 0.88
        assert result.detection_risk == 0.12

    def test_profile_result_validation(self, sample_browser_profile):
        """Test profile result validation."""
        # Test valid scores
        result = ProfileResult(
            profile=sample_browser_profile,
            generation_time=1.0,
            coherence_score=0.8,
            uniqueness_score=0.7,
            detection_risk=0.2
        )
        assert result.coherence_score == 0.8
        assert result.uniqueness_score == 0.7
        assert result.detection_risk == 0.2

        # Test invalid scores (out of range)
        with pytest.raises(ValidationError):
            ProfileResult(
                profile=sample_browser_profile,
                generation_time=1.0,
                coherence_score=1.5  # > 1.0
            )

        with pytest.raises(ValidationError):
            ProfileResult(
                profile=sample_browser_profile,
                generation_time=1.0,
                coherence_score=-0.1  # < 0.0
            )

        # Test invalid generation time
        with pytest.raises(ValidationError):
            ProfileResult(
                profile=sample_browser_profile,
                generation_time=-1.0,  # Negative time
                coherence_score=0.8,
                uniqueness_score=0.7,
                detection_risk=0.2
            )

    def test_profile_result_quality_assessment(self, sample_browser_profile):
        """Test profile result quality assessment."""
        # High quality result
        high_quality_result = ProfileResult(
            profile=sample_browser_profile,
            generation_time=0.3,
            coherence_score=0.95,
            uniqueness_score=0.9,
            detection_risk=0.05
        )

        assert high_quality_result.is_high_quality()
        assert not high_quality_result.is_high_risk()

        # Low quality result
        low_quality_result = ProfileResult(
            profile=sample_browser_profile,
            generation_time=2.0,
            coherence_score=0.6,
            uniqueness_score=0.5,
            detection_risk=0.4
        )

        assert not low_quality_result.is_high_quality()
        assert low_quality_result.is_high_risk()


class TestProfileGenerationOptions:
    """Test ProfileGenerationOptions model validation."""

    def test_valid_options(self):
        """Test creating valid generation options."""
        options = ProfileGenerationOptions(
            seed="test_seed_123",
            ttl=3600,
            cache_enabled=True,
            max_retry_attempts=3
        )

        assert options.seed == "test_seed_123"
        assert options.ttl == 3600
        assert options.cache_enabled is True
        assert options.max_retry_attempts == 3

    def test_options_validation(self):
        """Test generation options validation."""
        # Test valid TTL
        options = ProfileGenerationOptions(ttl=7200)
        assert options.ttl == 7200

        # Test invalid TTL (negative)
        with pytest.raises(ValidationError):
            ProfileGenerationOptions(ttl=-100)

        # Test invalid retry attempts (negative)
        with pytest.raises(ValidationError):
            ProfileGenerationOptions(max_retry_attempts=-1)

        # Test invalid retry attempts (too many)
        with pytest.raises(ValidationError):
            ProfileGenerationOptions(max_retry_attempts=20)  # > 10


class TestPerformanceValidation:
    """Test performance aspects of profile validation."""

    def test_large_profile_validation_performance(self, sample_browser_profile):
        """Test validation performance with large profiles."""
        import time

        # Create a large profile with many properties
        large_profile = sample_browser_profile.copy()
        large_profile.update({
            "webgl": {
                "vendor": "Google Inc.",
                "renderer": "ANGLE (Intel(R) HD Graphics 630)",
                "version": "WebGL 2.0",
                "extensions": [f"ext_{i}" for i in range(100)]
            },
            "plugins": [f"Plugin {i}" for i in range(50)],
            "mime_types": [f"application/x-type-{i}" for i in range(30)]
        })

        # Measure validation time
        start_time = time.time()
        profile = BrowserProfile(**large_profile)
        validation_time = time.time() - start_time

        # Validation should be fast (< 100ms for large profile)
        assert validation_time < 0.1
        assert profile.webgl["extensions"] == large_profile["webgl"]["extensions"]
        assert len(profile.plugins) == 50
        assert len(profile.mime_types) == 30

    def test_serialization_performance(self, sample_browser_profile):
        """Test serialization performance."""
        import time
        import json

        profile = BrowserProfile(**sample_browser_profile)

        # Measure serialization time
        start_time = time.time()
        serialized = profile.model_dump_json()
        serialization_time = time.time() - start_time

        # Serialization should be fast (< 50ms)
        assert serialization_time < 0.05

        # Measure deserialization time
        start_time = time.time()
        parsed_data = json.loads(serialized)
        restored_profile = BrowserProfile(**parsed_data)
        deserialization_time = time.time() - start_time

        # Deserialization should be fast (< 50ms)
        assert deserialization_time < 0.05
        assert restored_profile.user_agent == profile.user_agent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])