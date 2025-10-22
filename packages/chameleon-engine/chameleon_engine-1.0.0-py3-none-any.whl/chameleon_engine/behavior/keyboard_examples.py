"""
Keyboard Typing Examples

This module demonstrates various keyboard typing patterns and behaviors
for different use cases in web automation and bot detection avoidance.
"""

import asyncio
import time
from typing import List, Dict, Any

from .keyboard import (
    KeyboardTyping,
    TypingStyle,
    TypingConfig,
    human_type,
    realistic_key_sequence
)


async def basic_typing_example():
    """Example: Basic typing with different styles"""
    print("=== Basic Typing Example ===")

    sample_text = "The quick brown fox jumps over the lazy dog."

    keyboard = KeyboardTyping()

    styles = [
        TypingStyle.HUNT_AND_PECK,
        TypingStyle.SLOW_TOUCH,
        TypingStyle.NORMAL_TOUCH,
        TypingStyle.FAST_TOUCH,
        TypingStyle.PROFESSIONAL
    ]

    for style in styles:
        print(f"\nTyping with {style.value} style:")
        print(f"Text: '{sample_text}'")

        start_time = time.time()
        await keyboard.type_text(sample_text, style)
        duration = time.time() - start_time

        # Get latest session stats
        latest_session = keyboard.typing_history[-1]
        print(f"Duration: {duration:.2f}s")
        print(f"WPM: {latest_session['wpm']:.1f}")
        print(f"Errors: {latest_session['errors']}")

        await asyncio.sleep(1)  # Brief pause between styles

    # Show overall statistics
    stats = keyboard.get_statistics()
    print(f"\nOverall Statistics:")
    print(f"  Total sessions: {stats['total_sessions']}")
    print(f"  Average WPM: {stats['average_wpm']:.1f}")
    print(f"  Error rate: {stats['error_rate']:.2%}")
    print(f"  Style distribution: {stats['style_distribution']}")


async def custom_configuration_example():
    """Example: Using custom typing configuration"""
    print("\n=== Custom Configuration Example ===")

    # Create configuration for nervous typing
    nervous_config = TypingConfig(
        base_speed=0.08,
        speed_variance=0.6,
        error_rate=0.12,
        correction_delay=(0.1, 0.3),
        pause_probability=0.2,
        pause_duration=(0.1, 0.8),
        rhythm_patterns=True,
        auto_correct=True
    )

    keyboard = KeyboardTyping(nervous_config)

    test_texts = [
        "This is a test of nervous typing behavior.",
        "The user might be anxious or in a hurry.",
        "Notice the variable speed and occasional errors."
    ]

    for i, text in enumerate(test_texts):
        print(f"Text {i+1}: '{text}'")
        start_time = time.time()
        await keyboard.type_text(text, TypingStyle.NERVOUS)
        duration = time.time() - start_time

        latest_session = keyboard.typing_history[-1]
        print(f"Duration: {duration:.2f}s, WPM: {latest_session['wpm']:.1f}")
        await asyncio.sleep(0.5)

    print("Nervous typing demonstration completed")


async def error_simulation_example():
    """Example: Error simulation and correction"""
    print("\n=== Error Simulation Example ===")

    # High error rate configuration
    error_config = TypingConfig(
        base_speed=0.2,
        error_rate=0.15,  # 15% error rate
        correction_delay=(0.2, 0.5),
        auto_correct=True
    )

    keyboard = KeyboardTyping(error_config)

    test_text = "This text will have several typing errors that get corrected automatically."

    print(f"Original text: '{test_text}'")
    print("Simulating typing with high error rate...")

    start_time = time.time()
    await keyboard.type_text(test_text, TypingStyle.HUNT_AND_PECK)
    duration = time.time() - start_time

    latest_session = keyboard.typing_history[-1]
    print(f"Typed text: '{latest_session['typed_text']}'")
    print(f"Duration: {duration:.2f}s")
    print(f"Errors made: {latest_session['errors']}")
    print(f"Final length: {len(latest_session['typed_text'])} characters")


async def key_combinations_example():
    """Example: Key combinations and hotkeys"""
    print("\n=== Key Combinations Example ===")

    keyboard = KeyboardTyping()

    # Simulate common key combinations
    key_combinations = [
        (["Ctrl", "c"], "Copy"),
        (["Ctrl", "v"], "Paste"),
        (["Ctrl", "a"], "Select All"),
        (["Ctrl", "z"], "Undo"),
        (["Alt", "Tab"], "Switch Window"),
        (["Ctrl", "Shift", "t"], "Reopen Tab"),
    ]

    for keys, description in key_combinations:
        print(f"Pressing: {' + '.join(keys)} ({description})")
        await keyboard.hotkey(keys)
        await asyncio.sleep(0.3)

    # Individual key presses with delays
    print("\nIndividual key sequence:")
    keys = ["Tab", "Tab", "Enter", "Arrow Down", "Enter"]
    delays = [0.2, 0.15, 0.3, 0.1, 0.25]

    for key, delay in zip(keys, delays):
        print(f"Press {key} after {delay}s delay")
        await keyboard.press_key(key, delay=delay)

    print("Key combinations demonstration completed")


async def typing_rhythm_example():
    """Example: Different typing rhythms and patterns"""
    print("\n=== Typing Rhythm Example ===")

    keyboard = KeyboardTyping()
    text = "Natural typing rhythm varies based on the user's skill and mood."

    rhythms = [
        TypingStyle.TIRED,
        TypingStyle.EXCITED,
        TypingStyle.NERVOUS,
        TypingStyle.PROFESSIONAL
    ]

    for rhythm in rhythms:
        print(f"\nDemonstrating {rhythm.value} rhythm:")
        start_time = time.time()
        await keyboard.type_text(text, rhythm)
        duration = time.time() - start_time

        latest_session = keyboard.typing_history[-1]
        print(f"Duration: {duration:.2f}s")
        print(f"WPM: {latest_session['wpm']:.1f}")

        await asyncio.sleep(0.5)


async def form_filling_example():
    """Example: Realistic form filling"""
    print("\n=== Form Filling Example ===")

    keyboard = KeyboardTyping()

    # Simulate filling out a registration form
    form_data = {
        "First Name": ("John", TypingStyle.NORMAL_TOUCH),
        "Last Name": ("Doe", TypingStyle.NORMAL_TOUCH),
        "Email": ("john.doe@example.com", TypingStyle.SLOW_TOUCH),  # More careful with email
        "Password": ("SecurePassword123!", TypingStyle.HUNT_AND_PECK),  # Hunt and peck for password
        "Address": ("123 Main Street, Anytown, USA", TypingStyle.NORMAL_TOUCH),
        "Phone": ("555-123-4567", TypingStyle.SLOW_TOUCH),
        "Comments": ("I am very interested in this service and look forward to using it.",
                    TypingStyle.FAST_TOUCH)  # Faster for free text
    }

    for field_name, (text, style) in form_data.items():
        print(f"Filling {field_name}:")
        print(f"  Text: '{text}'")
        print(f"  Style: {style.value}")

        start_time = time.time()
        await keyboard.type_text(text, style)
        duration = time.time() - start_time

        latest_session = keyboard.typing_history[-1]
        print(f"  Duration: {duration:.2f}s")

        # Simulate tabbing to next field
        await asyncio.sleep(0.3)
        print("  [Tab to next field]")

    print("\nForm filling completed")

    # Show form statistics
    stats = keyboard.get_statistics()
    print(f"Form Statistics:")
    print(f"  Total characters typed: {stats['total_characters']}")
    print(f"  Total time: {stats['total_duration']:.2f}s")
    print(f"  Average WPM: {stats['average_wpm']:.1f}")
    print(f"  Error rate: {stats['error_rate']:.2%}")


async def complex_text_example():
    """Example: Typing complex text with punctuation and numbers"""
    print("\n=== Complex Text Example ===")

    keyboard = KeyboardTyping()

    complex_texts = [
        "The invoice #12345 costs $1,234.56 (including 20% VAT).",
        "Email: contact@example.com | Phone: +1 (555) 123-4567",
        "Website: https://www.example.com/path?query=value&param=data",
        "Date: 12/31/2024, Time: 23:59:59, Reference: ABC-XYZ-789"
    ]

    for i, text in enumerate(complex_texts):
        print(f"Complex text {i+1}: '{text}'")

        start_time = time.time()
        await keyboard.type_text(text, TypingStyle.NORMAL_TOUCH)
        duration = time.time() - start_time

        latest_session = keyboard.typing_history[-1]
        print(f"Duration: {duration:.2f}s, WPM: {latest_session['wpm']:.1f}")
        await asyncio.sleep(0.5)


async def performance_test():
    """Example: Performance testing with different text lengths"""
    print("\n=== Performance Test ===")

    keyboard = KeyboardTyping()

    # Generate texts of different lengths
    text_lengths = [50, 100, 200, 500]
    base_text = "The quick brown fox jumps over the lazy dog. "

    for length in text_lengths:
        text = (base_text * ((length // len(base_text)) + 1))[:length]

        print(f"Typing {length} characters...")

        start_time = time.time()
        await keyboard.type_text(text, TypingStyle.FAST_TOUCH)
        duration = time.time() - start_time

        latest_session = keyboard.typing_history[-1]
        print(f"  Duration: {duration:.2f}s")
        print(f"  WPM: {latest_session['wpm']:.1f}")
        print(f"  Characters/second: {length/duration:.1f}")

    # Overall performance statistics
    stats = keyboard.get_statistics()
    print(f"\nPerformance Results:")
    print(f"  Average WPM across all tests: {stats['average_wpm']:.1f}")
    print(f"  Total characters typed: {stats['total_characters']}")
    print(f"  Total time: {stats['total_duration']:.2f}s")


async def comparison_example():
    """Example: Compare different typing styles on the same text"""
    print("\n=== Typing Style Comparison ===")

    keyboard = KeyboardTyping()
    test_text = "This sample text will be typed using different styles to compare their characteristics."

    styles = list(TypingStyle)
    results = {}

    for style in styles:
        print(f"Testing {style.value} style...")

        keyboard.reset_history()  # Clear history for clean measurement

        start_time = time.time()
        await keyboard.type_text(test_text, style)
        duration = time.time() - start_time

        stats = keyboard.get_statistics()
        results[style.value] = {
            'duration': duration,
            'wpm': stats['average_wpm'],
            'errors': stats.get('total_errors', 0),
            'error_rate': stats['error_rate']
        }

        print(f"  Duration: {duration:.2f}s, WPM: {stats['average_wpm']:.1f}")

    print(f"\nComparison Results:")
    print(f"{'Style':<15} | {'Time':<6} | {'WPM':<6} | {'Errors':<7} | {'Error Rate':<10}")
    print("-" * 55)

    for style, data in results.items():
        print(f"{style:<15} | {data['duration']:>5.2f}s | {data['wpm']:>5.1f} | "
              f"{data['errors']:>6d} | {data['error_rate']:>8.2%}")


async def integration_example():
    """Example: Integration with page object (simulated)"""
    print("\n=== Integration Example ===")

    # Simulate page object
    class MockPage:
        def __init__(self):
            self.typed_text = ""
            self.focused_element = None
            self.events = []

        async def fill(self, selector, text):
            self.typed_text = text
            self.events.append(f"fill '{selector}' with '{text}'")

        async def focus(self, selector):
            self.focused_element = selector
            self.events.append(f"focus on '{selector}'")

        async def keyboard_type(self, text):
            self.typed_text += text
            self.events.append(f"type '{text}'")

        async def keyboard_press(self, key):
            self.events.append(f"press '{key}'")

    # Create mock page with patched methods
    page = MockPage()
    page.keyboard = MockPage()
    page.keyboard.type = page.keyboard_type
    page.keyboard.press = page.keyboard_press

    # Use human_type function
    await human_type(
        page,
        "This is a test of the integration with page objects.",
        TypingStyle.NORMAL_TOUCH,
        selector="#search-input"
    )

    print("Page events recorded:")
    for event in page.events:
        print(f"  {event}")

    print(f"Final typed text: '{page.typed_text}'")
    print(f"Focused element: '{page.focused_element}'")


async def main():
    """Run all examples"""
    print("Keyboard Typing Examples")
    print("=" * 50)

    examples = [
        basic_typing_example,
        custom_configuration_example,
        error_simulation_example,
        key_combinations_example,
        typing_rhythm_example,
        form_filling_example,
        complex_text_example,
        performance_test,
        comparison_example,
        integration_example
    ]

    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}")

        print("\n" + "-" * 50)

    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())