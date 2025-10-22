"""
Mouse Movement Examples

This module demonstrates various mouse movement patterns and behaviors
for different use cases in web automation and bot detection avoidance.
"""

import asyncio
import time
from typing import List, Dict, Any

from .mouse import (
    MouseMovement,
    MovementStyle,
    MouseConfig,
    realistic_move,
    realistic_click,
    realistic_drag_and_drop
)


async def basic_movement_example():
    """Example: Basic mouse movement to different positions"""
    print("=== Basic Mouse Movement Example ===")

    # Create mouse movement simulator
    mouse = MouseMovement()

    # Test different movement styles
    styles = [
        MovementStyle.NATURAL,
        MovementStyle.PRECISE,
        MovementStyle.NERVOUS,
        MovementStyle.SLOW,
        MovementStyle.FAST
    ]

    target_positions = [
        (100, 100),
        (300, 200),
        (500, 150),
        (200, 300),
        (400, 400)
    ]

    for i, (style, target) in enumerate(zip(styles, target_positions)):
        print(f"Moving to {target} using {style.value} style")

        # Simulate movement (without actual page)
        start_time = time.time()
        await mouse.move_to(target[0], target[1], style)
        duration = time.time() - start_time

        print(f"  Movement completed in {duration:.2f}s")
        print(f"  Current position: {mouse.current_position}")

    # Show statistics
    stats = mouse.get_statistics()
    print(f"\nMovement Statistics:")
    print(f"  Total movements: {stats['total_movements']}")
    print(f"  Total distance: {stats['total_distance']:.1f} pixels")
    print(f"  Average speed: {stats['average_speed']:.1f} pixels/sec")
    print(f"  Style distribution: {stats['style_distribution']}")


async def custom_configuration_example():
    """Example: Using custom mouse configuration"""
    print("\n=== Custom Configuration Example ===")

    # Create custom configuration for nervous movement
    nervous_config = MouseConfig(
        base_speed=400.0,
        speed_variance=0.5,
        jitter_frequency=0.3,
        jitter_magnitude=4.0,
        pause_probability=0.25,
        pause_duration=(0.05, 0.2),
        micro_movement_prob=0.5,
        curve_complexity=4
    )

    mouse = MouseMovement(nervous_config)

    # Test nervous movement pattern
    positions = [(150, 150), (250, 100), (350, 200), (300, 300), (200, 250)]

    for target in positions:
        print(f"Nervous movement to {target}")
        await mouse.move_to(target[0], target[1], MovementStyle.NERVOUS)
        await asyncio.sleep(0.2)  # Brief pause between movements

    print("Nervous movement pattern completed")


async def click_patterns_example():
    """Example: Different click patterns"""
    print("\n=== Click Patterns Example ===")

    mouse = MouseMovement()

    # Single clicks with different delays
    print("Single clicks:")
    for i in range(3):
        print(f"  Click {i+1}")
        await mouse.click(click_delay=(0.1, 0.2), hold_duration=(0.05, 0.15))
        await asyncio.sleep(0.5)

    # Double click
    print("\nDouble click:")
    await mouse.double_click(interval=(0.08, 0.12))

    # Right click
    print("\nRight click:")
    await mouse.click(button="right", click_delay=(0.1, 0.2))


async def drag_and_drop_example():
    """Example: Drag and drop operations"""
    print("\n=== Drag and Drop Example ===")

    mouse = MouseMovement()

    # Simulate dragging elements
    drag_operations = [
        (100, 100, 300, 300),  # Diagonal drag
        (200, 150, 200, 350),  # Vertical drag
        (50, 200, 350, 200),   # Horizontal drag
        (150, 150, 250, 250),  # Short diagonal drag
    ]

    for i, (start_x, start_y, end_x, end_y) in enumerate(drag_operations):
        style = [MovementStyle.NATURAL, MovementStyle.PRECISE][i % 2]
        print(f"Drag {i+1}: ({start_x}, {start_y}) → ({end_x}, {end_y}) using {style.value} style")

        await mouse.drag_and_drop(start_x, start_y, end_x, end_y, style)
        await asyncio.sleep(0.5)

    print("Drag and drop operations completed")


async def complex_movement_sequence():
    """Example: Complex movement sequence simulating real user behavior"""
    print("\n=== Complex Movement Sequence ===")

    mouse = MouseMovement()

    # Simulate user browsing behavior
    print("Simulating user browsing pattern...")

    # Move to navigation menu
    await mouse.move_to(50, 50, MovementStyle.NATURAL)
    await asyncio.sleep(0.3)

    # Click on menu item
    await mouse.click()
    await asyncio.sleep(0.5)

    # Scroll down (simulated with movement)
    scroll_positions = [(400, 200), (400, 300), (400, 400), (400, 500)]
    for pos in scroll_positions:
        await mouse.move_to(pos[0], pos[1], MovementStyle.NATURAL)
        await asyncio.sleep(0.2)

    # Click on a link
    await mouse.move_to(200, 350, MovementStyle.PRECISE)
    await mouse.click()
    await asyncio.sleep(0.8)

    # Fill form (simulated)
    form_fields = [(150, 200), (150, 250), (150, 300), (150, 350)]
    for field_pos in form_fields:
        await mouse.move_to(field_pos[0], field_pos[1], MovementStyle.PRECISE)
        await mouse.click()
        await asyncio.sleep(0.3)

    # Submit button with nervous movement (user uncertainty)
    await mouse.move_to(200, 450, MovementStyle.NERVOUS)
    await mouse.click(click_delay=(0.2, 0.4))

    print("Complex sequence completed")

    # Show final statistics
    stats = mouse.get_statistics()
    print(f"\nFinal Statistics:")
    print(f"  Total movements: {stats['total_movements']}")
    print(f"  Total duration: {stats['total_duration']:.2f}s")
    print(f"  Average speed: {stats['average_speed']:.1f} pixels/sec")


async def performance_test():
    """Example: Performance testing with many movements"""
    print("\n=== Performance Test ===")

    mouse = MouseMovement()

    # Generate random target positions
    import random
    movements = 50

    print(f"Performing {movements} random movements...")

    start_time = time.time()

    for i in range(movements):
        target_x = random.randint(50, 800)
        target_y = random.randint(50, 600)
        style = random.choice(list(MovementStyle))

        await mouse.move_to(target_x, target_y, style)

        if i % 10 == 0:
            print(f"  Completed {i}/{movements} movements")

    total_time = time.time() - start_time
    stats = mouse.get_statistics()

    print(f"\nPerformance Results:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average time per movement: {total_time/movements:.3f}s")
    print(f"  Total distance: {stats['total_distance']:.1f} pixels")
    print(f"  Average speed: {stats['average_speed']:.1f} pixels/sec")


async def comparison_example():
    """Example: Compare different movement styles"""
    print("\n=== Movement Style Comparison ===")

    styles = list(MovementStyle)
    target = (400, 300)
    start_pos = (100, 100)

    results = {}

    for style in styles:
        print(f"Testing {style.value} style...")

        mouse = MouseMovement()
        mouse.set_position(*start_pos)

        # Perform movement
        start_time = time.time()
        await mouse.move_to(target[0], target[1], style)
        duration = time.time() - start_time

        # Get statistics
        stats = mouse.get_statistics()

        results[style.value] = {
            'duration': duration,
            'distance': stats['total_distance'],
            'speed': stats['average_speed'],
            'path_complexity': len(mouse.movement_history)
        }

        print(f"  Duration: {duration:.2f}s")
        print(f"  Distance: {stats['total_distance']:.1f} pixels")
        print(f"  Speed: {stats['average_speed']:.1f} pixels/sec")

    print(f"\nComparison Results:")
    for style, data in results.items():
        print(f"{style:12} | Time: {data['duration']:5.2f}s | "
              f"Dist: {data['distance']:6.1f}px | Speed: {data['speed']:6.1f}px/s")


async def integration_example():
    """Example: Integration with page object (simulated)"""
    print("\n=== Integration Example ===")

    # Simulate page object
    class MockPage:
        def __init__(self):
            self.mouse = MockMouse()
            self.events = []

        async def wait_for_timeout(self, timeout):
            await asyncio.sleep(timeout / 1000)

    class MockMouse:
        def __init__(self):
            self.position = (0, 0)
            self.events = []

        async def move(self, x, y):
            self.position = (x, y)
            self.events.append(f"move to ({x}, {y})")

        async def down(self, button="left"):
            self.events.append(f"mouse down ({button})")

        async def up(self, button="left"):
            self.events.append(f"mouse up ({button})")

    # Create mock page
    page = MockPage()

    # Use realistic movement functions
    await realistic_move(page, 200, 200, MovementStyle.NATURAL)
    await asyncio.sleep(0.5)
    await realistic_click(page)
    await asyncio.sleep(0.3)
    await realistic_drag_and_drop(page, 200, 200, 400, 300, MovementStyle.PRECISE)

    print("Mouse events recorded:")
    for event in page.mouse.events:
        print(f"  {event}")


async def main():
    """Run all examples"""
    print("Mouse Movement Examples")
    print("=" * 50)

    examples = [
        basic_movement_example,
        custom_configuration_example,
        click_patterns_example,
        drag_and_drop_example,
        complex_movement_sequence,
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