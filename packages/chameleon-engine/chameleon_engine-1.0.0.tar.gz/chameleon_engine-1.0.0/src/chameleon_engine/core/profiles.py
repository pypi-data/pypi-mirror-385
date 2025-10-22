"""
Advanced browser profile models for stealth web scraping.

This module contains Pydantic models that define the structure of browser
fingerprints including network-level properties like TLS fingerprints and HTTP/2 settings,
which are essential for bypassing modern anti-bot detection systems.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class BrowserType(str, Enum):
    """Supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"


class OperatingSystem(str, Enum):
    """Supported operating systems."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    ANDROID = "android"
    IOS = "ios"


class ScreenResolution(BaseModel):
    """Screen resolution configuration."""
    width: int = Field(..., ge=320, le=7680, description="Screen width in pixels")
    height: int = Field(..., ge=240, le=4320, description="Screen height in pixels")

    @property
    def aspect_ratio(self) -> float:
        """Calculate screen aspect ratio."""
        return self.width / self.height


class WebGLParameters(BaseModel):
    """WebGL rendering parameters."""
    vendor: Optional[str] = Field(None, description="WebGL vendor string")
    renderer: Optional[str] = Field(None, description="WebGL renderer string")
    version: Optional[str] = Field(None, description="WebGL version string")
    max_texture_size: Optional[int] = Field(None, ge=0, description="Maximum texture size")
    max_viewport_dims: Optional[List[int]] = Field(None, description="Maximum viewport dimensions")


class NavigatorProperties(BaseModel):
    """Browser navigator properties for fingerprinting."""
    hardware_concurrency: int = Field(..., ge=1, le=32, description="Number of CPU cores")
    device_memory: Optional[float] = Field(None, ge=0.25, le=32.0, description="Device memory in GB")
    platform: str = Field(..., description="Platform string")
    user_agent: str = Field(..., description="User agent string")
    webdriver: bool = Field(False, description="Whether navigator.webdriver is present")
    languages: List[str] = Field(default_factory=lambda: ["en-US", "en"], description="Browser languages")
    do_not_track: Optional[str] = Field(None, description="Do Not Track header value")
    cookie_enabled: bool = Field(True, description="Whether cookies are enabled")
    on_line: bool = Field(True, description="Whether browser is online")

    # WebGL properties
    webgl: Optional[WebGLParameters] = Field(None, description="WebGL parameters")

    # Additional navigator properties
    max_touch_points: Optional[int] = Field(None, ge=0, description="Maximum touch points")
    vendor: Optional[str] = Field(None, description="Navigator vendor")
    vendor_sub: Optional[str] = Field(None, description="Navigator vendor sub")

    model_config = ConfigDict(validate_assignment=True)


class HTTPHeaders(BaseModel):
    """HTTP headers for browser fingerprinting."""
    sec_ch_ua: Optional[str] = Field(None, description="Sec-CH-UA header")
    sec_ch_ua_platform: Optional[str] = Field(None, description="Sec-CH-UA-Platform header")
    sec_ch_ua_mobile: Optional[str] = Field(None, description="Sec-CH-UA-Mobile header")
    sec_ch_ua_full_version_list: Optional[str] = Field(None, description="Sec-CH-UA-Full-Version-List header")
    accept_language: str = Field("en-US,en;q=0.9", description="Accept-Language header")
    accept_encoding: Optional[str] = Field("gzip, deflate, br", description="Accept-Encoding header")
    user_agent: str = Field(..., description="User-Agent header")
    dnt: Optional[str] = Field(None, description="DNT header")
    upgrade_insecure_requests: Optional[str] = Field("1", description="Upgrade-Insecure-Requests header")

    model_config = ConfigDict(validate_assignment=True)


class TLSFingerprint(BaseModel):
    """TLS fingerprint configuration for network-level stealth."""
    id: str = Field(..., description="TLS fingerprint identifier")
    utls_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="uTLS configuration for ClientHello fingerprint"
    )
    ja3_hash: Optional[str] = Field(None, description="JA3 hash for TLS fingerprint")
    cipher_suites: Optional[List[str]] = Field(None, description="Cipher suites")
    extensions: Optional[List[str]] = Field(None, description="TLS extensions")
    version: Optional[str] = Field(None, description="TLS version")

    model_config = ConfigDict(validate_assignment=True)


class HTTP2Settings(BaseModel):
    """HTTP/2 settings for protocol-level fingerprinting."""
    max_concurrent_streams: int = Field(1000, ge=1, le=4294967295, description="Max concurrent streams")
    initial_window_size: int = Field(65535, ge=1, le=4294967295, description="Initial window size")
    max_frame_size: int = Field(16777215, ge=1, le=4294967295, description="Maximum frame size")
    header_table_size: int = Field(4096, ge=1, le=4294967295, description="Header table size")
    enable_push: bool = Field(True, description="Whether server push is enabled")
    max_header_list_size: int = Field(8192, ge=1, le=4294967295, description="Maximum header list size")

    model_config = ConfigDict(validate_assignment=True)


class CanvasFingerprint(BaseModel):
    """Canvas fingerprint parameters."""
    text_rendering: Optional[str] = Field(None, description="Canvas text rendering hash")
    fingerprint_hash: Optional[str] = Field(None, description="Canvas fingerprint hash")
    webgl_fingerprint: Optional[str] = Field(None, description="WebGL canvas fingerprint")

    model_config = ConfigDict(validate_assignment=True)


class AudioFingerprint(BaseModel):
    """Audio context fingerprint parameters."""
    context_fingerprint: Optional[str] = Field(None, description="Audio context fingerprint")
    oscillator_types: Optional[List[str]] = Field(None, description="Available oscillator types")

    model_config = ConfigDict(validate_assignment=True)


class BrowserProfile(BaseModel):
    """
    Complete browser profile for stealth web scraping.

    This model contains all the properties needed to create a realistic browser
    fingerprint including network-level configurations like TLS and HTTP/2 settings.
    """

    # Basic browser information
    browser_type: BrowserType = Field(..., description="Browser type")
    operating_system: OperatingSystem = Field(..., description="Operating system")
    version: str = Field("latest", description="Browser version")

    # Screen and viewport
    screen: ScreenResolution = Field(..., description="Screen resolution")
    viewport: Optional[ScreenResolution] = Field(None, description="Viewport resolution")

    # Navigator properties
    navigator: NavigatorProperties = Field(..., description="Navigator properties")

    # HTTP headers
    headers: HTTPHeaders = Field(..., description="HTTP headers")

    # Network-level properties
    tls_fingerprint: TLSFingerprint = Field(..., description="TLS fingerprint configuration")
    http2_settings: HTTP2Settings = Field(..., description="HTTP/2 settings")

    # Advanced fingerprinting
    canvas_fingerprint: Optional[CanvasFingerprint] = Field(None, description="Canvas fingerprint")
    audio_fingerprint: Optional[AudioFingerprint] = Field(None, description="Audio fingerprint")

    # Metadata
    profile_id: str = Field(..., description="Unique profile identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Profile creation time")
    expires_at: Optional[datetime] = Field(None, description="Profile expiration time")
    coherence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Profile coherence score")
    is_active: bool = Field(True, description="Whether profile is active")

    # Usage tracking
    usage_count: int = Field(default=0, ge=0, description="Number of times this profile was used")
    last_used: Optional[datetime] = Field(None, description="Last time this profile was used")

    # Proxy configuration
    proxy_config: Optional[Dict[str, Any]] = Field(None, description="Proxy configuration")

    @field_validator('viewport')
    @classmethod
    def validate_viewport(cls, v, info):
        """Validate viewport is not larger than screen."""
        if v and (v.width > info.data['screen'].width or v.height > info.data['screen'].height):
            raise ValueError("Viewport cannot be larger than screen resolution")
        return v

    @field_validator('navigator')
    @classmethod
    def validate_hardware_concurrency(cls, v, info):
        """Validate hardware concurrency makes sense for OS/browser combination."""
        # Add logic here to validate realistic combinations
        return v

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",  # Prevent extra fields
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        },
        json_decoders={
            datetime: lambda v: datetime.fromisoformat(v) if isinstance(v, str) else v,
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for JSON serialization."""
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrowserProfile":
        """Create profile from dictionary."""
        return cls.model_validate(data)


class ProfileRequest(BaseModel):
    """Request model for generating browser profiles."""

    browser_type: BrowserType = Field(BrowserType.CHROME, description="Preferred browser type")
    operating_system: OperatingSystem = Field(OperatingSystem.WINDOWS, description="Preferred operating system")
    version: str = Field("latest", description="Browser version")
    locale: Optional[str] = Field("en-US", description="Locale preference")
    mobile: bool = Field(False, description="Mobile browser preference")
    seed: Optional[str] = Field(None, description="Seed for reproducible profiles")

    # Advanced options
    include_advanced_fingerprinting: bool = Field(True, description="Include canvas/audio fingerprinting")
    coherence_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Minimum coherence score")

    model_config = ConfigDict(validate_assignment=True)


class ProfileGenerationResult(BaseModel):
    """Result of profile generation process."""

    success: bool = Field(..., description="Whether generation was successful")
    profile: Optional[BrowserProfile] = Field(None, description="Generated profile")
    error_message: Optional[str] = Field(None, description="Error message if generation failed")
    generation_time_ms: Optional[int] = Field(None, description="Generation time in milliseconds")

    model_config = ConfigDict(validate_assignment=True)