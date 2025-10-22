"""
Fingerprint Service API models.

This module contains Pydantic models for the Fingerprint Service API,
including request/response models for browser profile generation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from ...core.profiles import BrowserProfile


class BrowserType(str, Enum):
    """Supported browser types for fingerprint requests."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    OPERA = "opera"


class OperatingSystem(str, Enum):
    """Supported operating systems for fingerprint requests."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    ANDROID = "android"
    IOS = "ios"


class ProfileConstraints(BaseModel):
    """Constraints for fingerprint generation."""

    # Browser constraints
    browser_types: Optional[List[BrowserType]] = Field(
        None, description="Allowed browser types"
    )
    min_browser_version: Optional[str] = Field(
        None, description="Minimum browser version"
    )
    max_browser_version: Optional[str] = Field(
        None, description="Maximum browser version"
    )

    # OS constraints
    operating_systems: Optional[List[OperatingSystem]] = Field(
        None, description="Allowed operating systems"
    )

    # Device constraints
    mobile_only: Optional[bool] = Field(
        None, description="Generate only mobile profiles"
    )
    desktop_only: Optional[bool] = Field(
        None, description="Generate only desktop profiles"
    )

    # Hardware constraints
    min_screen_width: Optional[int] = Field(
        None, ge=320, le=7680, description="Minimum screen width"
    )
    max_screen_width: Optional[int] = Field(
        None, ge=320, le=7680, description="Maximum screen width"
    )
    min_screen_height: Optional[int] = Field(
        None, ge=240, le=4320, description="Minimum screen height"
    )
    max_screen_height: Optional[int] = Field(
        None, ge=240, le=4320, description="Maximum screen height"
    )

    # Regional constraints
    locales: Optional[List[str]] = Field(
        None, description="Allowed locales (e.g., en-US, en-GB)"
    )

    # Network constraints
    require_ipv6: Optional[bool] = Field(
        None, description="Require IPv6 connectivity"
    )

    model_config = ConfigDict(validate_assignment=True)


class FingerprintRequest(BaseModel):
    """Request model for generating browser fingerprints."""

    # Basic requirements
    browser_type: Optional[BrowserType] = Field(
        BrowserType.CHROME, description="Preferred browser type"
    )
    operating_system: Optional[OperatingSystem] = Field(
        OperatingSystem.WINDOWS, description="Preferred operating system"
    )
    version: Optional[str] = Field(
        "latest", description="Browser version (latest or specific version)"
    )

    # Regional and device preferences
    locale: Optional[str] = Field(
        "en-US", description="Locale preference (e.g., en-US, en-GB, it-IT)"
    )
    mobile: Optional[bool] = Field(
        False, description="Mobile browser preference"
    )

    # Advanced options
    constraints: Optional[ProfileConstraints] = Field(
        None, description="Generation constraints"
    )
    seed: Optional[str] = Field(
        None, description="Seed for reproducible profiles"
    )

    # Feature toggles
    include_advanced_fingerprinting: Optional[bool] = Field(
        True, description="Include canvas/audio fingerprinting"
    )
    include_network_fingerprinting: Optional[bool] = Field(
        True, description="Include TLS/HTTP2 fingerprinting"
    )

    # Quality requirements
    coherence_threshold: Optional[float] = Field(
        0.8, ge=0.0, le=1.0, description="Minimum coherence score"
    )
    max_usage_count: Optional[int] = Field(
        None, ge=0, description="Maximum usage count for profile"
    )

    # TTL
    expires_in_hours: Optional[int] = Field(
        None, ge=1, le=168, description="Profile expiration in hours"
    )

    model_config = ConfigDict(validate_assignment=True)


class ProfileMetadata(BaseModel):
    """Metadata about the generated fingerprint."""

    # Generation info
    generation_method: str = Field(
        ..., description="How the profile was generated (real_world, synthetic, hybrid)"
    )
    data_source_version: str = Field(
        ..., description="Version of the data source used"
    )
    generation_time_ms: Optional[int] = Field(
        None, description="Profile generation time in milliseconds"
    )

    # Quality metrics
    coherence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Profile coherence score"
    )
    uniqueness_score: float = Field(
        ..., ge=0.0, le=1.0, description="Profile uniqueness score"
    )
    detection_risk_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Detection risk score"
    )

    # Usage tracking
    usage_count: int = Field(
        0, ge=0, description="Number of times this profile was used"
    )
    last_used: Optional[datetime] = Field(
        None, description="Last time this profile was used"
    )

    # Freshness
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Profile creation time"
    )
    expires_at: Optional[datetime] = Field(
        None, description="Profile expiration time"
    )

    model_config = ConfigDict(validate_assignment=True)


class FingerprintResponse(BaseModel):
    """Response model for fingerprint generation requests."""

    # Profile data
    profile_id: str = Field(
        ..., description="Unique profile identifier"
    )
    browser_profile: BrowserProfile = Field(
        ..., description="Generated browser profile"
    )

    # Metadata
    metadata: ProfileMetadata = Field(
        ..., description="Profile metadata and quality metrics"
    )

    # Service info
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    api_version: str = Field(
        "v1", description="API version used"
    )

    model_config = ConfigDict(validate_assignment=True)


class ValidationError(BaseModel):
    """Detailed validation error information."""

    field: str = Field(..., description="Field that failed validation")
    error_type: str = Field(..., description="Type of validation error")
    message: str = Field(..., description="Human-readable error message")
    severity: str = Field(
        "error", description="Error severity (warning, error, critical)"
    )
    suggestion: Optional[str] = Field(
        None, description="Suggested fix for the error"
    )


class FingerprintError(BaseModel):
    """Error response for fingerprint generation failures."""

    error_code: str = Field(..., description="Machine-readable error code")
    error_message: str = Field(..., description="Human-readable error message")

    # Detailed information
    validation_errors: Optional[List[ValidationError]] = Field(
        None, description="Detailed validation errors"
    )

    # Service info
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )
    request_id: Optional[str] = Field(
        None, description="Request ID for tracing"
    )

    model_config = ConfigDict(validate_assignment=True)


class ServiceStatus(BaseModel):
    """Service health and status information."""

    # Basic status
    status: str = Field(..., description="Service status (healthy, degraded, down)")
    uptime_seconds: int = Field(..., description="Service uptime in seconds")

    # Database status
    database_status: str = Field(..., description="Database connection status")
    total_profiles: int = Field(..., description="Total profiles in database")
    active_profiles: int = Field(..., description="Active profiles in database")

    # Data freshness
    last_data_update: Optional[datetime] = Field(
        None, description="Last time data was updated"
    )
    data_age_hours: Optional[float] = Field(
        None, description="Age of data in hours"
    )

    # Performance metrics
    avg_generation_time_ms: Optional[float] = Field(
        None, description="Average profile generation time"
    )
    requests_per_minute: Optional[float] = Field(
        None, description="Current request rate"
    )

    # Service info
    version: str = Field(..., description="Service version")
    api_version: str = Field("v1", description="API version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Status timestamp"
    )

    model_config = ConfigDict(validate_assignment=True)


class BatchFingerprintRequest(BaseModel):
    """Request for generating multiple fingerprints."""

    requests: List[FingerprintRequest] = Field(
        ..., min_items=1, max_items=100, description="List of fingerprint requests"
    )

    # Batch options
    ensure_diversity: Optional[bool] = Field(
        True, description="Ensure generated profiles are diverse"
    )
    max_retry_attempts: Optional[int] = Field(
        3, ge=1, le=10, description="Maximum retry attempts per failed request"
    )

    model_config = ConfigDict(validate_assignment=True)


class BatchFingerprintResponse(BaseModel):
    """Response for batch fingerprint generation."""

    # Results
    successful_profiles: List[FingerprintResponse] = Field(
        ..., description="Successfully generated profiles"
    )
    failed_requests: List[FingerprintError] = Field(
        ..., description="Failed requests with error details"
    )

    # Summary
    total_requested: int = Field(..., description="Total number of requests")
    total_successful: int = Field(..., description="Number of successful generations")
    total_failed: int = Field(..., description="Number of failed generations")

    # Performance
    total_generation_time_ms: int = Field(
        ..., description="Total generation time for all profiles"
    )
    avg_generation_time_ms: float = Field(
        ..., description="Average generation time per profile"
    )

    # Service info
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    api_version: str = Field("v1", description="API version")

    model_config = ConfigDict(validate_assignment=True)