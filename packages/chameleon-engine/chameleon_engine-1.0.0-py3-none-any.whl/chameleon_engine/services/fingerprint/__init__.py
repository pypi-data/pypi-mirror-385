"""
Fingerprint service client for API-based fingerprint generation.

This module provides a client for communicating with the FastAPI fingerprint service
that generates realistic browser profiles with network-level fingerprints.
"""

from .models import (
    FingerprintRequest,
    FingerprintResponse,
    FingerprintError,
    ServiceStatus,
    ProfileConstraints,
    ProfileMetadata,
    BatchFingerprintRequest,
    BatchFingerprintResponse,
    BrowserType,
    OperatingSystem,
    ValidationError
)
from .collectors import (
    RealWorldDataCollector,
    DataSourceValidator,
    NetworkFingerprintCollector,
    DataCollectionService
)
from .client import (
    FingerprintServiceClient,
    FingerprintServiceClientError,
    FingerprintServiceUnavailableError,
    CachingFingerprintClient
)

__all__ = [
    "FingerprintRequest",
    "FingerprintResponse",
    "FingerprintError",
    "ServiceStatus",
    "ProfileConstraints",
    "ProfileMetadata",
    "BatchFingerprintRequest",
    "BatchFingerprintResponse",
    "BrowserType",
    "OperatingSystem",
    "ValidationError",
    "RealWorldDataCollector",
    "DataSourceValidator",
    "NetworkFingerprintCollector",
    "DataCollectionService",
    "FingerprintServiceClient",
    "FingerprintServiceClientError",
    "FingerprintServiceUnavailableError",
    "CachingFingerprintClient"
]