"""
Chameleon Engine: A modular stealth browser automation library.

Chameleon Engine generates highly realistic, dynamic browser identities and
simulates human behavior to bypass modern anti-bot systems.
"""

import logging

# Initialize binary installer on import
try:
    from .binaries import install_on_import
    install_on_import()
except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to initialize binary installer: {e}")

# Main orchestrator
from .orchestrator import (
    ChameleonEngine,
    ChameleonEngineConfig,
    SessionMetrics,
    ChameleonEngineError,
    EngineNotStartedError,
    ComponentInitializationError
)

# Core components
from .core.profiles import (
    BrowserProfile,
    BrowserType,
    OperatingSystem,
    ScreenResolution,
    NavigatorProperties,
    HTTPHeaders,
    TLSFingerprint,
    HTTP2Settings,
    CanvasFingerprint,
    AudioFingerprint
)

# Services
from .services.fingerprint import (
    FingerprintServiceClient,
    FingerprintGenerator,
    FingerprintCache,
    ProfilePool
)

from .services.proxy import (
    GoProxyManager,
    ProxyConfig,
    ProxyManagerPool
)

from .services.binary import (
    CustomBinaryManager,
    BinaryInfo,
    BinaryType,
    BinaryConfig
)

# Network components
from .network.obfuscator import (
    NetworkObfuscator,
    TLSFingerprintManager,
    HTTP2SettingsManager,
    ProxyIntegrationManager
)

# Browser management
from .core.browser_manager import (
    BrowserManager,
    BrowserLaunchConfig,
    BrowserMetrics
)

# Behavior simulation
from .behavior import (
    MouseMovement,
    MovementStyle,
    MouseConfig,
    KeyboardTyping,
    TypingStyle,
    TypingConfig,
    KeyType
)

# Convenience functions
from .behavior.mouse import (
    realistic_move,
    realistic_click,
    realistic_drag_and_drop
)

from .behavior.keyboard import (
    human_type,
    realistic_key_sequence
)

__version__ = "1.0.0"

__all__ = [
    # Main orchestrator
    "ChameleonEngine",
    "ChameleonEngineConfig",
    "SessionMetrics",
    "ChameleonEngineError",
    "EngineNotStartedError",
    "ComponentInitializationError",

    # Core components
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

    # Services
    "FingerprintServiceClient",
    "FingerprintGenerator",
    "FingerprintCache",
    "ProfilePool",
    "GoProxyManager",
    "ProxyConfig",
    "ProxyManagerPool",
    "CustomBinaryManager",
    "BinaryInfo",
    "BinaryType",
    "BinaryConfig",

    # Network components
    "NetworkObfuscator",
    "TLSFingerprintManager",
    "HTTP2SettingsManager",
    "ProxyIntegrationManager",

    # Browser management
    "BrowserManager",
    "BrowserLaunchConfig",
    "BrowserMetrics",

    # Behavior simulation
    "MouseMovement",
    "MovementStyle",
    "MouseConfig",
    "KeyboardTyping",
    "TypingStyle",
    "TypingConfig",
    "KeyType",

    # Convenience functions
    "realistic_move",
    "realistic_click",
    "realistic_drag_and_drop",
    "human_type",
    "realistic_key_sequence"
]