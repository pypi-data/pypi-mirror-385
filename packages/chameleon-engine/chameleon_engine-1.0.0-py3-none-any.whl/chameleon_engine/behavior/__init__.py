"""
Human behavior simulation components.

This module provides realistic mouse movement and keyboard interaction
patterns to mimic human user behavior and avoid detection.
"""

from .mouse import (
    realistic_move,
    realistic_click,
    realistic_drag_and_drop,
    MouseMovement,
    MovementStyle,
    MouseConfig
)
from .keyboard import (
    human_type,
    realistic_key_sequence,
    KeyboardTyping,
    TypingStyle,
    TypingConfig,
    KeyType
)

__all__ = [
    # Mouse movement
    "realistic_move",
    "realistic_click",
    "realistic_drag_and_drop",
    "MouseMovement",
    "MovementStyle",
    "MouseConfig",
    # Keyboard typing
    "human_type",
    "realistic_key_sequence",
    "KeyboardTyping",
    "TypingStyle",
    "TypingConfig",
    "KeyType"
]