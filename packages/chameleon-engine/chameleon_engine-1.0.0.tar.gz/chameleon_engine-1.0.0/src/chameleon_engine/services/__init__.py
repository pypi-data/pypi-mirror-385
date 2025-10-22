"""
Service clients and external service integrations.

This package contains clients for communicating with external microservices
that provide fingerprinting, database, and network obfuscation capabilities.
"""

from .fingerprint import FingerprintServiceClient
from .proxy import GoProxyManager

__all__ = ["FingerprintServiceClient", "GoProxyManager"]