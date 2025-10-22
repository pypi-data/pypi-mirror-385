"""
Data collection modules for fingerprint generation.

This package provides collectors that gather real-world browser fingerprint data
from various sources including device libraries, analytics sites, and browser
detection websites.
"""

from .real_world import RealWorldDataCollector, DataSourceValidator
from .network import NetworkFingerprintCollector
from .service import DataCollectionService

__all__ = [
    "RealWorldDataCollector",
    "DataSourceValidator",
    "NetworkFingerprintCollector",
    "DataCollectionService"
]