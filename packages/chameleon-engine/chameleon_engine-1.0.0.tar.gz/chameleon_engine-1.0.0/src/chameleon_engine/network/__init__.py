"""
Network-level obfuscation and stealth functionality.

This module provides network-level obfuscation capabilities including
TLS fingerprinting, HTTP/2 rewriting, and proxy management.
"""

from .obfuscator import NetworkObfuscator, ObfuscationConfig, ObfuscationStatus
from .tls_fingerprint import TLSFingerprintManager, TLSClientHelloBuilder
from .http2_rewriter import HTTP2SettingsManager, HTTP2HeaderRewriter
from .proxy_integration import ProxyIntegrationManager

__all__ = [
    "NetworkObfuscator",
    "ObfuscationConfig",
    "ObfuscationStatus",
    "TLSFingerprintManager",
    "TLSClientHelloBuilder",
    "HTTP2SettingsManager",
    "HTTP2HeaderRewriter",
    "ProxyIntegrationManager"
]