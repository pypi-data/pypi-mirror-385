"""
HTTP/2 settings and header rewriting for network obfuscation.

This module provides HTTP/2 configuration management and header rewriting
capabilities for stealth network communication.
"""

import secrets
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from ..core.profiles import HTTP2Settings

logger = logging.getLogger(__name__)


class HTTP2FrameType(Enum):
    """HTTP/2 frame types."""
    DATA = "data"
    HEADERS = "headers"
    PRIORITY = "priority"
    RST_STREAM = "rst_stream"
    SETTINGS = "settings"
    PUSH_PROMISE = "push_promise"
    PING = "ping"
    GOAWAY = "goaway"
    WINDOW_UPDATE = "window_update"
    CONTINUATION = "continuation"


class HTTP2SettingsParameter(Enum):
    """HTTP/2 settings parameters."""
    HEADER_TABLE_SIZE = "header_table_size"
    ENABLE_PUSH = "enable_push"
    MAX_CONCURRENT_STREAMS = "max_concurrent_streams"
    INITIAL_WINDOW_SIZE = "initial_window_size"
    MAX_FRAME_SIZE = "max_frame_size"
    MAX_HEADER_LIST_SIZE = "max_header_list_size"


@dataclass
class HTTP2HeaderConfig:
    """Configuration for HTTP/2 header rewriting."""
    header_order: List[str]
    pseudo_headers_order: List[str]
    compression_enabled: bool = True
    huffman_encoding: bool = True
    header_table_size: int = 4096
    custom_headers: Dict[str, str] = field(default_factory=dict)
    removed_headers: List[str] = field(default_factory=list)


@dataclass
class HTTP2PriorityConfig:
    """Configuration for HTTP/2 stream priority."""
    stream_dependency: Optional[int] = None
    weight: int = 16
    exclusive: bool = False
    priority_strategy: str = "random"  # random, sequential, custom


@dataclass
class HTTP2ConnectionConfig:
    """Complete HTTP/2 connection configuration."""
    settings: HTTP2Settings
    header_config: HTTP2HeaderConfig
    priority_config: HTTP2PriorityConfig
    flow_control_enabled: bool = True
    server_push_enabled: bool = True
    multiplexing_enabled: bool = True


class HTTP2SettingsManager:
    """
    Manager for HTTP/2 settings and configurations.

    This class provides functionality to generate, manage, and customize
    HTTP/2 settings for different browsers and scenarios.
    """

    def __init__(self):
        """Initialize HTTP/2 settings manager."""
        self.browser_profiles: Dict[str, HTTP2Settings] = {}
        self._load_default_profiles()

    def _load_default_profiles(self):
        """Load default HTTP/2 settings profiles."""
        # Chrome 120
        self.browser_profiles["chrome_120"] = HTTP2Settings(
            max_concurrent_streams=1000,
            initial_window_size=65535,
            max_frame_size=16777215,
            header_table_size=4096,
            enable_push=True,
            max_header_list_size=8192
        )

        # Firefox 121
        self.browser_profiles["firefox_121"] = HTTP2Settings(
            max_concurrent_streams=100,
            initial_window_size=65536,
            max_frame_size=16384,
            header_table_size=4096,
            enable_push=True,
            max_header_list_size=65536
        )

        # Safari 17
        self.browser_profiles["safari_17"] = HTTP2Settings(
            max_concurrent_streams=100,
            initial_window_size=65535,
            max_frame_size=16777215,
            header_table_size=4096,
            enable_push=False,  # Safari disables server push
            max_header_list_size=16384
        )

        # Edge 120
        self.browser_profiles["edge_120"] = HTTP2Settings(
            max_concurrent_streams=1000,
            initial_window_size=65535,
            max_frame_size=16777215,
            header_table_size=4096,
            enable_push=True,
            max_header_list_size=8192
        )

        logger.info(f"Loaded {len(self.browser_profiles)} default HTTP/2 settings profiles")

    def get_settings(self, browser_type: str, browser_version: str) -> HTTP2Settings:
        """
        Get HTTP/2 settings for a specific browser.

        Args:
            browser_type: Browser type (chrome, firefox, safari, edge)
            browser_version: Browser version

        Returns:
            HTTP/2 settings for the browser
        """
        profile_id = f"{browser_type}_{browser_version.split('.')[0]}"
        return self.browser_profiles.get(profile_id, self.browser_profiles["chrome_120"])

    def generate_custom_settings(
        self,
        base_settings: Optional[HTTP2Settings] = None,
        randomize: bool = True,
        performance_level: str = "balanced"  # minimal, balanced, maximum
    ) -> HTTP2Settings:
        """
        Generate custom HTTP/2 settings.

        Args:
            base_settings: Base settings to customize
            randomize: Whether to randomize values
            performance_level: Performance optimization level

        Returns:
            Customized HTTP/2 settings
        """
        if not base_settings:
            base_settings = self.browser_profiles["chrome_120"]

        settings = HTTP2Settings(
            max_concurrent_streams=base_settings.max_concurrent_streams,
            initial_window_size=base_settings.initial_window_size,
            max_frame_size=base_settings.max_frame_size,
            header_table_size=base_settings.header_table_size,
            enable_push=base_settings.enable_push,
            max_header_list_size=base_settings.max_header_list_size
        )

        if randomize:
            settings = self._randomize_settings(settings, performance_level)

        return settings

    def _randomize_settings(
        self,
        settings: HTTP2Settings,
        performance_level: str
    ) -> HTTP2Settings:
        """
        Randomize HTTP/2 settings based on performance level.

        Args:
            settings: Base settings
            performance_level: Performance optimization level

        Returns:
            Randomized settings
        """
        # Performance-based ranges
        if performance_level == "minimal":
            stream_range = (50, 200)
            window_range = (16384, 32768)
            frame_range = (16384, 65536)
            header_table_range = (2048, 4096)
        elif performance_level == "maximum":
            stream_range = (500, 2000)
            window_range = (65536, 262144)
            frame_range = (1048576, 16777215)
            header_table_range = (4096, 8192)
        else:  # balanced
            stream_range = (100, 1000)
            window_range = (32768, 65536)
            frame_range = (65536, 16777215)
            header_table_range = (4096, 4096)

        # Randomize values within ranges
        settings.max_concurrent_streams = secrets.randbelow(stream_range[1] - stream_range[0]) + stream_range[0]
        settings.initial_window_size = self._align_to_window_size(
            secrets.randbelow(window_range[1] - window_range[0]) + window_range[0]
        )
        settings.max_frame_size = self._align_to_frame_size(
            secrets.randbelow(frame_range[1] - frame_range[0]) + frame_range[0]
        )
        settings.header_table_size = secrets.choice(header_table_range)
        settings.max_header_list_size = secrets.choice([4096, 8192, 16384, 32768, 65536])
        settings.enable_push = secrets.choice([True, False, False, True])  # 75% push enabled

        return settings

    def _align_to_window_size(self, value: int) -> int:
        """Align value to valid window size."""
        # HTTP/2 requires initial window size to be between 1 and 2^31-1
        # and should be a reasonable value
        valid_sizes = [16384, 32768, 65536, 131072, 262144, 524288, 1048576]
        return min(valid_sizes, key=lambda x: abs(x - value))

    def _align_to_frame_size(self, value: int) -> int:
        """Align value to valid frame size."""
        # HTTP/2 requires max frame size to be between 16384 and 16777215
        return max(16384, min(16777215, value))

    def validate_settings(self, settings: HTTP2Settings) -> List[str]:
        """
        Validate HTTP/2 settings.

        Args:
            settings: Settings to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Validate max_concurrent_streams
        if settings.max_concurrent_streams < 1 or settings.max_concurrent_streams > 4294967295:
            issues.append(f"Invalid max_concurrent_streams: {settings.max_concurrent_streams}")

        # Validate initial_window_size
        if settings.initial_window_size < 1 or settings.initial_window_size > 4294967295:
            issues.append(f"Invalid initial_window_size: {settings.initial_window_size}")

        # Validate max_frame_size
        if settings.max_frame_size < 16384 or settings.max_frame_size > 16777215:
            issues.append(f"Invalid max_frame_size: {settings.max_frame_size}")

        # Validate header_table_size
        if settings.header_table_size < 0 or settings.header_table_size > 4294967295:
            issues.append(f"Invalid header_table_size: {settings.header_table_size}")

        # Validate max_header_list_size
        if settings.max_header_list_size < 0 or settings.max_header_list_size > 4294967295:
            issues.append(f"Invalid max_header_list_size: {settings.max_header_list_size}")

        return issues

    def to_dict(self, settings: HTTP2Settings) -> Dict[str, Any]:
        """Convert HTTP/2 settings to dictionary."""
        return {
            "max_concurrent_streams": settings.max_concurrent_streams,
            "initial_window_size": settings.initial_window_size,
            "max_frame_size": settings.max_frame_size,
            "header_table_size": settings.header_table_size,
            "enable_push": settings.enable_push,
            "max_header_list_size": settings.max_header_list_size
        }

    def from_dict(self, data: Dict[str, Any]) -> HTTP2Settings:
        """Create HTTP/2 settings from dictionary."""
        return HTTP2Settings(
            max_concurrent_streams=data.get("max_concurrent_streams", 1000),
            initial_window_size=data.get("initial_window_size", 65535),
            max_frame_size=data.get("max_frame_size", 16777215),
            header_table_size=data.get("header_table_size", 4096),
            enable_push=data.get("enable_push", True),
            max_header_list_size=data.get("max_header_list_size", 8192)
        )


class HTTP2HeaderRewriter:
    """
    Rewriter for HTTP/2 headers and pseudo-headers.

    This class provides functionality to rewrite and customize HTTP/2 headers
    for stealth communication.
    """

    def __init__(self, settings_manager: HTTP2SettingsManager):
        """
        Initialize header rewriter.

        Args:
            settings_manager: HTTP/2 settings manager
        """
        self.settings_manager = settings_manager

    def create_header_config(
        self,
        browser_type: str,
        browser_version: str,
        custom_headers: Optional[Dict[str, str]] = None
    ) -> HTTP2HeaderConfig:
        """
        Create HTTP/2 header configuration.

        Args:
            browser_type: Browser type
            browser_version: Browser version
            custom_headers: Custom headers to include

        Returns:
            HTTP/2 header configuration
        """
        # Browser-specific header orders
        if browser_type == "chrome":
            pseudo_order = [":method", ":path", ":scheme", ":authority"]
            header_order = [
                "user-agent",
                "accept",
                "accept-language",
                "accept-encoding",
                "sec-ch-ua",
                "sec-ch-ua-mobile",
                "sec-ch-ua-platform",
                "dnt",
                "connection",
                "upgrade-insecure-requests"
            ]
        elif browser_type == "firefox":
            pseudo_order = [":method", ":path", ":scheme", ":authority"]
            header_order = [
                "user-agent",
                "accept",
                "accept-language",
                "accept-encoding",
                "dnt",
                "connection",
                "upgrade-insecure-requests"
            ]
        elif browser_type == "safari":
            pseudo_order = [":method", ":path", ":scheme", ":authority"]
            header_order = [
                "user-agent",
                "accept",
                "accept-language",
                "accept-encoding",
                "dnt",
                "connection"
            ]
        else:  # Default to Chrome
            pseudo_order = [":method", ":path", ":scheme", ":authority"]
            header_order = [
                "user-agent",
                "accept",
                "accept-language",
                "accept-encoding",
                "dnt",
                "connection"
            ]

        # Add custom headers
        if custom_headers:
            header_order.extend(custom_headers.keys())

        return HTTP2HeaderConfig(
            header_order=header_order,
            pseudo_headers_order=pseudo_order,
            custom_headers=custom_headers or {},
            compression_enabled=True,
            huffman_encoding=True,
            header_table_size=4096
        )

    def rewrite_headers(
        self,
        original_headers: Dict[str, str],
        config: HTTP2HeaderConfig,
        randomize_order: bool = True
    ) -> List[Tuple[str, str]]:
        """
        Rewrite headers according to configuration.

        Args:
            original_headers: Original headers
            config: Header configuration
            randomize_order: Whether to randomize header order

        Returns:
            Rewritten headers as list of (name, value) tuples
        """
        # Separate pseudo-headers and regular headers
        pseudo_headers = {}
        regular_headers = {}

        for name, value in original_headers.items():
            if name.startswith(':'):
                pseudo_headers[name] = value
            else:
                regular_headers[name] = value

        # Add custom headers
        regular_headers.update(config.custom_headers)

        # Remove specified headers
        for header in config.removed_headers:
            regular_headers.pop(header, None)

        # Order headers
        ordered_pseudo_headers = []
        for pseudo_name in config.pseudo_headers_order:
            if pseudo_name in pseudo_headers:
                ordered_pseudo_headers.append((pseudo_name, pseudo_headers[pseudo_name]))

        ordered_regular_headers = []
        header_order = config.header_order.copy()
        if randomize_order:
            # Randomize non-critical headers
            critical_headers = ["user-agent", "host", "connection"]
            non_critical = [h for h in header_order if h.lower() not in critical_headers]
            secrets.SystemRandom().shuffle(non_critical)
            header_order = [h for h in header_order if h.lower() in critical_headers] + non_critical

        for header_name in header_order:
            if header_name in regular_headers:
                ordered_regular_headers.append((header_name, regular_headers[header_name]))

        # Add any remaining headers not in order list
        for header_name, value in regular_headers.items():
            if header_name not in header_order:
                ordered_regular_headers.append((header_name, value))

        return ordered_pseudo_headers + ordered_regular_headers

    def generate_priority_config(
        self,
        stream_id: int,
        parent_stream_id: Optional[int] = None,
        strategy: str = "random"
    ) -> HTTP2PriorityConfig:
        """
        Generate HTTP/2 stream priority configuration.

        Args:
            stream_id: Stream ID
            parent_stream_id: Parent stream ID
            strategy: Priority strategy

        Returns:
            Priority configuration
        """
        if strategy == "random":
            weight = secrets.randbelow(255) + 1  # 1-256
            exclusive = secrets.choice([True, False])
        elif strategy == "sequential":
            weight = 128 + (stream_id % 128)  # Deterministic based on stream ID
            exclusive = False
        else:  # custom
            weight = 128
            exclusive = False

        return HTTP2PriorityConfig(
            stream_dependency=parent_stream_id,
            weight=weight,
            exclusive=exclusive,
            priority_strategy=strategy
        )

    def optimize_for_stealth(
        self,
        base_config: HTTP2HeaderConfig,
        target_site: Optional[str] = None
    ) -> HTTP2HeaderConfig:
        """
        Optimize header configuration for stealth.

        Args:
            base_config: Base header configuration
            target_site: Target website for specialized optimization

        Returns:
            Optimized header configuration
        """
        # Create a copy of the base config
        optimized_config = HTTP2HeaderConfig(
            header_order=base_config.header_order.copy(),
            pseudo_headers_order=base_config.pseudo_headers_order.copy(),
            compression_enabled=base_config.compression_enabled,
            huffman_encoding=base_config.huffman_encoding,
            header_table_size=base_config.header_table_size,
            custom_headers=base_config.custom_headers.copy(),
            removed_headers=base_config.removed_headers.copy()
        )

        # Site-specific optimizations
        if target_site:
            if "google.com" in target_site:
                # Remove headers that Google might flag
                optimized_config.removed_headers.extend(["sec-ch-ua", "sec-ch-ua-mobile"])
            elif "facebook.com" in target_site:
                # Facebook is more sensitive to automation
                optimized_config.removed_headers.extend(["connection", "upgrade-insecure-requests"])
                optimized_config.custom_headers["sec-fetch-dest"] = "document"
                optimized_config.custom_headers["sec-fetch-mode"] = "navigate"
                optimized_config.custom_headers["sec-fetch-site"] = "none"
                optimized_config.custom_headers["sec-fetch-user"] = "?1"

        # General stealth optimizations
        # Occasionally disable compression for variety
        if secrets.randbelow(10) == 0:  # 10% chance
            optimized_config.compression_enabled = False

        # Occasionally vary header table size
        if secrets.randbelow(5) == 0:  # 20% chance
            optimized_config.header_table_size = secrets.choice([2048, 4096, 8192])

        return optimized_config