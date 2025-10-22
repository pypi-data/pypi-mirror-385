"""
Realistic Keyboard Typing Simulation

This module provides advanced keyboard typing simulation with human-like behavior patterns
including variable typing speed, errors, corrections, and natural rhythm variations.

Features:
- Variable typing speed with rhythm patterns
- Realistic error simulation and correction
- Different typing styles (hunt-and-peck, touch typing, etc.)
- Natural pause patterns and timing
- Support for special keys and combinations
- Typing statistics and performance tracking
"""

import asyncio
import random
import time
import string
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

import numpy as np


class TypingStyle(Enum):
    """Different typing styles and skill levels"""
    HUNT_AND_PECK = "hunt_and_peck"      # Slow, deliberate, many errors
    SLOW_TOUCH = "slow_touch"            # Moderate speed, some errors
    NORMAL_TOUCH = "normal_touch"        # Average speed, few errors
    FAST_TOUCH = "fast_touch"            # Fast typing, minimal errors
    PROFESSIONAL = "professional"        # Very fast, almost no errors
    NERVOUS = "nervous"                  # Erratic, variable speed
    TIRED = "tired"                      # Slow, many pauses
    EXCITED = "excited"                  # Fast, occasional errors


class KeyType(Enum):
    """Types of keys for different timing behaviors"""
    REGULAR = "regular"          # Regular letters and numbers
    SHIFTED = "shifted"          # Uppercase and shifted characters
    MODIFIER = "modifier"        # Ctrl, Alt, Shift, etc.
    SPECIAL = "special"          # Enter, Tab, Backspace, etc.
    FUNCTION = "function"        # F1-F12 keys
    NUMERIC = "numeric"          # Numpad keys


@dataclass
class TypingConfig:
    """Configuration for typing behavior"""
    base_speed: float = 0.15           # Base delay between keystrokes (seconds)
    speed_variance: float = 0.4         # Speed variation (0-1)
    error_rate: float = 0.05           # Probability of making an error
    correction_delay: Tuple[float, float] = (0.2, 0.8)  # Delay before correction
    pause_probability: float = 0.1      # Probability of pausing between words
    pause_duration: Tuple[float, float] = (0.3, 1.5)     # Pause duration range
    space_delay: float = 0.1            # Additional delay after space
    shift_delay: float = 0.05           # Additional delay for shifted keys
    rhythm_patterns: bool = True         # Enable natural rhythm patterns
    auto_correct: bool = True           # Automatically correct obvious errors


class KeyboardLayout:
    """QWERTY keyboard layout for finger-based timing"""

    # Key positions (row, column) for realistic finger movement
    KEY_POSITIONS = {
        # Home row
        'a': (2, 1), 's': (2, 2), 'd': (2, 3), 'f': (2, 4),
        'j': (2, 6), 'k': (2, 7), 'l': (2, 8), ';': (2, 9),

        # Top row
        'q': (1, 1), 'w': (1, 2), 'e': (1, 3), 'r': (1, 4),
        't': (1, 5), 'y': (1, 6), 'u': (1, 7), 'i': (1, 8),
        'o': (1, 9), 'p': (1, 10),

        # Bottom row
        'z': (3, 1), 'x': (3, 2), 'c': (3, 3), 'v': (3, 4),
        'b': (3, 5), 'n': (3, 6), 'm': (3, 7), ',': (3, 8),
        '.': (3, 9), '/': (3, 10),

        # Numbers and special keys
        '1': (0, 1), '2': (0, 2), '3': (0, 3), '4': (0, 4),
        '5': (0, 5), '6': (0, 6), '7': (0, 7), '8': (0, 8),
        '9': (0, 9), '0': (0, 10),

        # Space and enter
        ' ': (4, 5), '\n': (4, 10),
    }

    @classmethod
    def get_distance(cls, key1: str, key2: str) -> float:
        """Calculate distance between two keys based on finger movement"""
        pos1 = cls.KEY_POSITIONS.get(key1.lower(), (2, 5))
        pos2 = cls.KEY_POSITIONS.get(key2.lower(), (2, 5))

        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

    @classmethod
    def get_key_type(cls, char: str) -> KeyType:
        """Determine key type for timing adjustments"""
        if char == '\n':
            return KeyType.SPECIAL
        elif char == '\t':
            return KeyType.SPECIAL
        elif char == ' ':
            return KeyType.REGULAR
        elif char in string.ascii_uppercase:
            return KeyType.SHIFTED
        elif char in string.ascii_lowercase or char in string.digits:
            return KeyType.REGULAR
        elif char in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+']:
            return KeyType.SHIFTED
        elif char in ['ctrl', 'alt', 'shift', 'meta']:
            return KeyType.MODIFIER
        else:
            return KeyType.SPECIAL


class TypingRhythm:
    """Generate natural typing rhythm patterns"""

    def __init__(self, style: TypingStyle):
        self.style = style
        self.rhythm_cache = self._generate_rhythm_pattern()

    def _generate_rhythm_pattern(self) -> List[float]:
        """Generate rhythm pattern based on typing style"""
        patterns = {
            TypingStyle.HUNT_AND_PECK: [0.8, 1.2, 0.9, 1.1, 1.0],
            TypingStyle.SLOW_TOUCH: [0.9, 1.0, 1.1, 0.95, 1.05],
            TypingStyle.NORMAL_TOUCH: [0.95, 1.0, 1.05, 0.98, 1.02],
            TypingStyle.FAST_TOUCH: [0.9, 0.95, 1.0, 1.05, 1.1],
            TypingStyle.PROFESSIONAL: [0.95, 0.98, 1.0, 1.02, 1.05],
            TypingStyle.NERVOUS: [0.7, 1.3, 0.8, 1.2, 1.0],
            TypingStyle.TIRED: [1.2, 1.5, 1.1, 1.3, 1.4],
            TypingStyle.EXCITED: [0.8, 0.9, 1.0, 0.85, 0.95],
        }

        return patterns.get(self.style, [1.0, 1.0, 1.0, 1.0, 1.0])

    def get_timing_multiplier(self, index: int) -> float:
        """Get timing multiplier for specific keystroke"""
        return self.rhythm_cache[index % len(self.rhythm_cache)]


class ErrorSimulator:
    """Simulate typing errors and corrections"""

    def __init__(self, config: TypingConfig, style: TypingStyle):
        self.config = config
        self.style = style
        self.error_map = self._build_error_map()

    def _build_error_map(self) -> Dict[str, str]:
        """Build character substitution map for common errors"""
        # Adjacent key errors on QWERTY
        adjacent_errors = {
            'a': ['s', 'q', 'z', 'x'],
            's': ['a', 'd', 'w', 'x', 'z'],
            'd': ['s', 'f', 'e', 'x', 'c'],
            'f': ['d', 'g', 'r', 'c', 'v'],
            'g': ['f', 'h', 't', 'v', 'b'],
            'h': ['g', 'j', 'y', 'b', 'n'],
            'j': ['h', 'k', 'u', 'n', 'm'],
            'k': ['j', 'l', 'i', 'm', ','],
            'l': ['k', ';', 'o', ',', '.'],
            'q': ['w', 'a', 's', '1', '2'],
            'w': ['q', 'e', 's', 'a', '2', '3'],
            'e': ['w', 'r', 'd', 's', '3', '4'],
            'r': ['e', 't', 'f', 'd', '4', '5'],
            't': ['r', 'y', 'g', 'f', '5', '6'],
            'y': ['t', 'u', 'h', 'g', '6', '7'],
            'u': ['y', 'i', 'j', 'h', '7', '8'],
            'i': ['u', 'o', 'k', 'j', '8', '9'],
            'o': ['i', 'p', 'l', 'k', '9', '0'],
            'p': ['o', ';', 'l', '0', '-'],
            'z': ['x', 'a', 's'],
            'x': ['z', 'c', 's', 'd', 'a'],
            'c': ['x', 'v', 'd', 'f', 's'],
            'v': ['c', 'b', 'f', 'g', 'd'],
            'b': ['v', 'n', 'g', 'h', 'f'],
            'n': ['b', 'm', 'h', 'j', 'g'],
            'm': ['n', ',', 'j', 'k', 'h'],
        }

        return adjacent_errors

    def should_make_error(self, char: str, context: str) -> bool:
        """Determine if an error should be made"""
        if random.random() > self.config.error_rate:
            return False

        # Style-based error rate adjustments
        style_multipliers = {
            TypingStyle.HUNT_AND_PECK: 2.0,
            TypingStyle.SLOW_TOUCH: 1.5,
            TypingStyle.NORMAL_TOUCH: 1.0,
            TypingStyle.FAST_TOUCH: 0.8,
            TypingStyle.PROFESSIONAL: 0.3,
            TypingStyle.NERVOUS: 1.8,
            TypingStyle.TIRED: 2.5,
            TypingStyle.EXCITED: 1.2,
        }

        multiplier = style_multipliers.get(self.style, 1.0)
        return random.random() < (self.config.error_rate * multiplier)

    def generate_error(self, char: str) -> str:
        """Generate a realistic typing error"""
        char_lower = char.lower()

        # Try adjacent key error
        if char_lower in self.error_map and random.random() < 0.7:
            adjacent_chars = self.error_map[char_lower]
            if adjacent_chars:
                error_char = random.choice(adjacent_chars)
                return error_char.upper() if char.isupper() else error_char

        # Case error (wrong case)
        if char.isalpha() and random.random() < 0.5:
            return char.swapcase()

        # Skip character
        if random.random() < 0.2:
            return ''

        # Duplicate character
        if random.random() < 0.2:
            return char * 2

        # Random nearby character
        return chr(ord(char) + random.choice([-1, 1])) if char.isalnum() else char


class KeyboardTyping:
    """
    Advanced keyboard typing simulator with human-like behavior patterns.
    """

    def __init__(self, config: Optional[TypingConfig] = None):
        """
        Initialize keyboard typing simulator

        Args:
            config: Typing configuration
        """
        self.config = config or TypingConfig()
        self.typing_history: List[Dict[str, Any]] = []
        self.current_position = 0

    def _calculate_timing(self, char: str, previous_char: str, style: TypingStyle,
                         rhythm: Optional[TypingRhythm] = None) -> float:
        """Calculate realistic typing timing for a character"""
        base_delay = self.config.base_speed

        # Style-based speed adjustments
        style_multipliers = {
            TypingStyle.HUNT_AND_PECK: 2.5,
            TypingStyle.SLOW_TOUCH: 1.8,
            TypingStyle.NORMAL_TOUCH: 1.0,
            TypingStyle.FAST_TOUCH: 0.7,
            TypingStyle.PROFESSIONAL: 0.4,
            TypingStyle.NERVOUS: 1.2,  # Variable
            TypingStyle.TIRED: 2.0,
            TypingStyle.EXCITED: 0.6,
        }

        base_delay *= style_multipliers.get(style, 1.0)

        # Key type adjustments
        key_type = KeyboardLayout.get_key_type(char)
        if key_type == KeyType.SHIFTED:
            base_delay += self.config.shift_delay
        elif key_type == KeyType.SPECIAL:
            base_delay *= 1.5
        elif key_type == KeyType.REGULAR and char == ' ':
            base_delay += self.config.space_delay

        # Distance-based timing (finger movement)
        if previous_char:
            distance = KeyboardLayout.get_distance(previous_char, char)
            distance_delay = distance * 0.02  # 20ms per key distance unit
            base_delay += distance_delay

        # Rhythm pattern
        if rhythm and self.config.rhythm_patterns:
            rhythm_multiplier = rhythm.get_timing_multiplier(self.current_position)
            base_delay *= rhythm_multiplier

        # Add variance
        variance = 1.0 + random.uniform(-self.config.speed_variance, self.config.speed_variance)

        # Special case for nervous typing
        if style == TypingStyle.NERVOUS:
            if random.random() < 0.3:  # 30% chance of very fast burst
                base_delay *= 0.3
            elif random.random() < 0.2:  # 20% chance of hesitation
                base_delay *= 3.0

        return base_delay * variance

    def _should_pause(self, char: str, next_char: str) -> bool:
        """Determine if a natural pause should occur"""
        # Pause after spaces (word boundaries)
        if char == ' ' and random.random() < self.config.pause_probability * 2:
            return True

        # Pause after punctuation
        if char in '.,;:!?' and random.random() < self.config.pause_probability * 1.5:
            return True

        # Random pause
        if random.random() < self.config.pause_probability:
            return True

        return False

    async def type_text(
        self,
        text: str,
        style: TypingStyle = TypingStyle.NORMAL_TOUCH,
        page: Optional[Any] = None,
        selector: Optional[str] = None
    ) -> None:
        """
        Type text with realistic human-like behavior

        Args:
            text: Text to type
            style: Typing style
            page: Playwright page object (optional)
            selector: Element selector for typing target (optional)
        """
        if not text:
            return

        # Initialize components
        rhythm = TypingRhythm(style)
        error_simulator = ErrorSimulator(self.config, style)

        # Clear typing field if selector provided
        if selector and page:
            try:
                await page.fill(selector, "")
            except Exception:
                pass

        # Focus on element if selector provided
        if selector and page:
            try:
                await page.focus(selector)
            except Exception:
                pass

        start_time = time.time()
        typed_text = ""
        previous_char = ""

        for i, char in enumerate(text):
            self.current_position = i

            # Simulate error
            actual_char = char
            should_error = error_simulator.should_make_error(char, typed_text)

            if should_error:
                actual_char = error_simulator.generate_error(char)

                # Type the error
                if page:
                    try:
                        await page.keyboard.type(actual_char)
                    except Exception:
                        pass
                typed_text += actual_char

                # Correction delay
                if self.config.auto_correct and actual_char != char:
                    correction_delay = random.uniform(*self.config.correction_delay)
                    await asyncio.sleep(correction_delay)

                    # Backspace to correct
                    backspace_count = len(actual_char)
                    for _ in range(backspace_count):
                        if page:
                            try:
                                await page.keyboard.press("Backspace")
                            except Exception:
                                pass
                        await asyncio.sleep(0.05)  # Brief delay for backspace

                    typed_text = typed_text[:-len(actual_char)]
            else:
                # Type correct character
                if page:
                    try:
                        if char == '\n':
                            await page.keyboard.press("Enter")
                        elif char == '\t':
                            await page.keyboard.press("Tab")
                        else:
                            await page.keyboard.type(char)
                    except Exception:
                        pass
                typed_text += char

            # Calculate timing for next character
            timing = self._calculate_timing(char, previous_char, style, rhythm)
            await asyncio.sleep(timing)

            # Natural pause
            if self._should_pause(char, text[i + 1] if i + 1 < len(text) else ""):
                pause_duration = random.uniform(*self.config.pause_duration)
                await asyncio.sleep(pause_duration)

            previous_char = char

        # Record typing session
        session_record = {
            'text': text,
            'typed_text': typed_text,
            'duration': time.time() - start_time,
            'style': style.value,
            'character_count': len(text),
            'errors': len(typed_text) - len(text),
            'wpm': self._calculate_wpm(text, time.time() - start_time),
            'timestamp': time.time()
        }

        self.typing_history.append(session_record)

    async def press_key(
        self,
        key: str,
        modifiers: Optional[List[str]] = None,
        delay: Optional[float] = None,
        page: Optional[Any] = None
    ) -> None:
        """
        Press a single key with optional modifiers

        Args:
            key: Key to press
            modifiers: List of modifier keys (Ctrl, Shift, Alt, Meta)
            delay: Delay before key press (seconds)
            page: Playwright page object (optional)
        """
        if delay:
            await asyncio.sleep(delay)

        # Build key combination
        key_combo = key
        if modifiers:
            key_combo = '+'.join(modifiers + [key])

        if page:
            try:
                await page.keyboard.press(key_combo)
            except Exception:
                pass
        else:
            # Simulate key press (no actual page interaction)
            pass

        # Add brief delay after key press
        await asyncio.sleep(0.05)

    async def hotkey(
        self,
        keys: List[str],
        page: Optional[Any] = None
    ) -> None:
        """
        Press combination of keys simultaneously (hotkey)

        Args:
            keys: List of keys to press together
            page: Playwright page object (optional)
        """
        if page:
            try:
                await page.keyboard.press('+'.join(keys))
            except Exception:
                pass

        await asyncio.sleep(0.1)

    def _calculate_wpm(self, text: str, duration: float) -> float:
        """Calculate words per minute"""
        if duration <= 0:
            return 0.0

        # Standard: 5 characters = 1 word
        word_count = len(text) / 5.0
        minutes = duration / 60.0
        return word_count / minutes if minutes > 0 else 0.0

    def get_statistics(self) -> Dict[str, Any]:
        """Get typing statistics"""
        if not self.typing_history:
            return {}

        total_sessions = len(self.typing_history)
        total_chars = sum(s['character_count'] for s in self.typing_history)
        total_errors = sum(s['errors'] for s in self.typing_history)
        total_duration = sum(s['duration'] for s in self.typing_history)

        style_counts = {}
        for session in self.typing_history:
            style = session['style']
            style_counts[style] = style_counts.get(style, 0) + 1

        avg_wpm = sum(s['wpm'] for s in self.typing_history) / total_sessions

        return {
            'total_sessions': total_sessions,
            'total_characters': total_chars,
            'total_errors': total_errors,
            'total_duration': total_duration,
            'average_wpm': avg_wpm,
            'error_rate': total_errors / total_chars if total_chars > 0 else 0,
            'style_distribution': style_counts,
            'average_session_length': total_chars / total_sessions if total_sessions > 0 else 0
        }

    def reset_history(self) -> None:
        """Reset typing history"""
        self.typing_history.clear()
        self.current_position = 0


# Convenience functions for backward compatibility
async def human_type(
    page: Any,
    text: str,
    style: TypingStyle = TypingStyle.NORMAL_TOUCH,
    selector: Optional[str] = None,
    config: Optional[TypingConfig] = None
) -> None:
    """
    Type text with human-like behavior

    Args:
        page: Playwright page object
        text: Text to type
        style: Typing style
        selector: Element selector for typing target
        config: Typing configuration
    """
    keyboard = KeyboardTyping(config)
    await keyboard.type_text(text, style, page, selector)


async def realistic_key_sequence(
    page: Any,
    keys: List[str],
    delays: Optional[List[float]] = None,
    config: Optional[TypingConfig] = None
) -> None:
    """
    Type a sequence of keys with individual delays

    Args:
        page: Playwright page object
        keys: List of keys to press
        delays: List of delays for each key
        config: Typing configuration
    """
    keyboard = KeyboardTyping(config)

    for i, key in enumerate(keys):
        delay = delays[i] if delays and i < len(delays) else None
        await keyboard.press_key(key, delay=delay, page=page)