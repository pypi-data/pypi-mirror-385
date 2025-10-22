"""
Custom binary management service.

This module provides functionality for downloading, managing, and maintaining
custom browser binaries (Chromium, Firefox) for anti-detection purposes.
"""

from .manager import CustomBinaryManager, BinaryInfo, BinaryType
from .downloader import BinaryDownloader, DownloadProgress
from .validator import BinaryValidator, ValidationResult
from .config import BinaryConfig, BinaryConfigManager

__all__ = [
    "CustomBinaryManager",
    "BinaryInfo",
    "BinaryType",
    "BinaryDownloader",
    "DownloadProgress",
    "BinaryValidator",
    "ValidationResult",
    "BinaryConfig",
    "BinaryConfigManager"
]