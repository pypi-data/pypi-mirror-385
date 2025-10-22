"""
Core components for browser management and profile handling.

This module contains the fundamental building blocks for browser lifecycle
management and browser profile configuration.
"""

from .browser_manager import BrowserManager
from .profiles import (
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
    ProfileGenerationResult
)

__all__ = [
    "BrowserManager",
    "BrowserProfile",
    "BrowserType",
    "OperatingSystem",
    "ScreenResolution",
    "NavigatorProperties",
    "HTTPHeaders",
    "TLSFingerprint",
    "HTTP2Settings",
    "CanvasFingerprint",
    "AudioFingerprint",
    "ProfileRequest",
    "ProfileGenerationResult"
]