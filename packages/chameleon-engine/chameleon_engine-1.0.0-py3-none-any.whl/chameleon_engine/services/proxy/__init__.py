"""
Go proxy service manager for network-level obfuscation.

This module provides a Python client for managing the Go-based network
obfuscation proxy that handles TLS fingerprinting and HTTP/2 rewriting.
"""

from .manager import GoProxyManager, ProxyManagerPool
from .config import ProxyConfig, ProxyConfigManager

__all__ = [
    "GoProxyManager",
    "ProxyManagerPool",
    "ProxyConfig",
    "ProxyConfigManager"
]