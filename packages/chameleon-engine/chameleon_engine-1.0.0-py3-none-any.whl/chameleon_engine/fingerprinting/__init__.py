"""
Fingerprinting Module

Advanced browser fingerprinting generation and management for Chameleon Engine.

This module provides comprehensive fingerprint generation capabilities with:
- API-based profile generation with intelligent caching
- High-performance profile pooling for batch operations
- Advanced error handling and service monitoring
- Integration with the Fingerprint Service microservice

Key Components:
- FingerprintGenerator: Main class for generating browser profiles
- ProfilePool: High-performance pool management for batch scenarios
- FingerprintCache: LRU caching with TTL and statistics
"""

from .generator import (
    FingerprintGenerator,
    ProfilePool,
    FingerprintCache,
    FingerprintGeneratorError,
    ServiceUnavailableError,
    ProfileGenerationError
)

__all__ = [
    "FingerprintGenerator",
    "ProfilePool",
    "FingerprintCache",
    "FingerprintGeneratorError",
    "ServiceUnavailableError",
    "ProfileGenerationError"
]

__version__ = "1.0.0"