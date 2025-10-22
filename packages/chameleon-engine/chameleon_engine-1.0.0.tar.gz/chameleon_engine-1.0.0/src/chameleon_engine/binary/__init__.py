"""
Custom Chromium binary management.

This module provides utilities for downloading, caching, and managing
custom-built Chromium binaries that have headless detection traces removed.
"""

from .manager import BinaryManager

__all__ = ["BinaryManager"]