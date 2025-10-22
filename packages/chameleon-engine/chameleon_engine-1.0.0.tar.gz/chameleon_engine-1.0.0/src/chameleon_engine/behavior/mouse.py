"""
Realistic Mouse Movement Simulation

This module provides advanced mouse movement simulation using Bezier curves
and human-like behavior patterns to avoid bot detection.

Features:
- Bezier curve-based movement paths
- Variable speed and acceleration
- Random micro-movements and jitter
- Human-like pause patterns
- Multiple movement styles (natural, precise, nervous)
"""

import asyncio
import random
import math
import time
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

import numpy as np


class MovementStyle(Enum):
    """Different mouse movement styles"""
    NATURAL = "natural"        # Smooth, curved movements
    PRECISE = "precise"        # Direct, slightly jittery movements
    NERVOUS = "nervous"        # Quick, slightly erratic movements
    SLOW = "slow"             # Deliberate, careful movements
    FAST = "fast"             # Quick, confident movements


@dataclass
class MouseConfig:
    """Configuration for mouse movement behavior"""
    base_speed: float = 300.0          # Base pixels per second
    speed_variance: float = 0.3         # Speed variation (0-1)
    jitter_frequency: float = 0.1       # How often to add jitter (0-1)
    jitter_magnitude: float = 2.0       # Maximum jitter in pixels
    pause_probability: float = 0.15     # Probability of pausing mid-movement
    pause_duration: Tuple[float, float] = (0.1, 0.5)  # Min/max pause duration
    micro_movement_prob: float = 0.3    # Probability of micro-movements
    curve_complexity: int = 3           # Number of control points for curves


class BezierCurve:
    """Bezier curve calculation utilities"""

    @staticmethod
    def calculate_point(t: float, control_points: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Calculate point on Bezier curve at parameter t (0-1)

        Args:
            t: Parameter value (0-1)
            control_points: List of control points

        Returns:
            Tuple of (x, y) coordinates
        """
        n = len(control_points) - 1
        x, y = 0.0, 0.0

        for i, (px, py) in enumerate(control_points):
            # Bernstein polynomial
            coefficient = (math.comb(n, i) *
                          (t ** i) *
                          ((1 - t) ** (n - i)))
            x += coefficient * px
            y += coefficient * py

        return x, y

    @staticmethod
    def generate_curve(
        start: Tuple[float, float],
        end: Tuple[float, float],
        complexity: int = 3,
        max_deviation: float = 100.0
    ) -> List[Tuple[float, float]]:
        """
        Generate Bezier curve control points

        Args:
            start: Starting point (x, y)
            end: Ending point (x, y)
            complexity: Number of control points
            max_deviation: Maximum deviation from straight line

        Returns:
            List of control points including start and end
        """
        if complexity < 2:
            return [start, end]

        # Start and end points
        control_points = [start, end]

        # Generate intermediate control points
        for i in range(1, complexity):
            # Position along the line (0-1)
            t = i / complexity

            # Base point on the line
            base_x = start[0] + t * (end[0] - start[0])
            base_y = start[1] + t * (end[1] - start[1])

            # Add perpendicular deviation
            line_angle = math.atan2(end[1] - start[1], end[0] - start[0])
            perp_angle = line_angle + math.pi / 2

            deviation = random.uniform(-max_deviation, max_deviation)

            control_x = base_x + deviation * math.cos(perp_angle)
            control_y = base_y + deviation * math.sin(perp_angle)

            # Insert control point
            control_points.insert(i, (control_x, control_y))

        return control_points


class MouseMovement:
    """
    Advanced mouse movement simulator with human-like behavior patterns.
    """

    def __init__(self, config: Optional[MouseConfig] = None):
        """
        Initialize mouse movement simulator

        Args:
            config: Mouse movement configuration
        """
        self.config = config or MouseConfig()
        self.current_position = (0.0, 0.0)
        self.movement_history: List[Dict[str, Any]] = []

    def _apply_jitter(self, x: float, y: float) -> Tuple[float, float]:
        """Apply random jitter to position"""
        if random.random() < self.config.jitter_frequency:
            jitter_x = random.uniform(-self.config.jitter_magnitude, self.config.jitter_magnitude)
            jitter_y = random.uniform(-self.config.jitter_magnitude, self.config.jitter_magnitude)
            return x + jitter_x, y + jitter_y
        return x, y

    def _calculate_speed(self, distance: float, style: MovementStyle) -> float:
        """Calculate movement speed based on distance and style"""
        base_speed = self.config.base_speed

        # Style-based speed modification
        style_multipliers = {
            MovementStyle.NATURAL: 1.0,
            MovementStyle.PRECISE: 0.7,
            MovementStyle.NERVOUS: 1.5,
            MovementStyle.SLOW: 0.4,
            MovementStyle.FAST: 1.8
        }

        base_speed *= style_multipliers[style]

        # Distance-based speed adjustment (shorter distances = slower speeds)
        if distance < 50:
            base_speed *= 0.5
        elif distance > 300:
            base_speed *= 1.2

        # Add variance
        variance = 1.0 + random.uniform(-self.config.speed_variance, self.config.speed_variance)

        return base_speed * variance

    def _generate_movement_path(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        style: MovementStyle
    ) -> List[Tuple[float, float]]:
        """Generate movement path using Bezier curves"""

        # Adjust curve complexity based on style
        complexity = self.config.curve_complexity
        if style == MovementStyle.PRECISE:
            complexity = max(2, complexity - 1)
        elif style == MovementStyle.NERVOUS:
            complexity = min(5, complexity + 1)

        # Generate Bezier curve
        control_points = BezierCurve.generate_curve(
            start, end,
            complexity=complexity,
            max_deviation=min(100, math.dist(start, end) * 0.3)
        )

        # Sample points along the curve
        num_points = max(10, int(math.dist(start, end) / 5))
        path_points = []

        for i in range(num_points + 1):
            t = i / num_points
            point = BezierCurve.calculate_point(t, control_points)

            # Apply jitter
            point = self._apply_jitter(*point)
            path_points.append(point)

        return path_points

    def _add_micro_movements(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Add small micro-movements to simulate human hand tremor"""
        enhanced_points = []

        for point in points:
            enhanced_points.append(point)

            # Randomly add micro-movements
            if random.random() < self.config.micro_movement_prob:
                # Small circular or elliptical micro-movement
                micro_offset_x = random.uniform(-3, 3)
                micro_offset_y = random.uniform(-3, 3)

                enhanced_point = (
                    point[0] + micro_offset_x,
                    point[1] + micro_offset_y
                )
                enhanced_points.append(enhanced_point)

        return enhanced_points

    async def move_to(
        self,
        target_x: float,
        target_y: float,
        style: MovementStyle = MovementStyle.NATURAL,
        page: Optional[Any] = None
    ) -> None:
        """
        Move mouse to target position with realistic behavior

        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            style: Movement style
            page: Playwright page object (optional)
        """
        start_pos = self.current_position
        end_pos = (target_x, target_y)

        # Generate movement path
        path_points = self._generate_movement_path(start_pos, end_pos, style)
        path_points = self._add_micro_movements(path_points)

        # Calculate movement parameters
        total_distance = sum(
            math.dist(path_points[i], path_points[i + 1])
            for i in range(len(path_points) - 1)
        )

        speed = self._calculate_speed(total_distance, style)
        total_duration = total_distance / speed if speed > 0 else 0.1

        # Execute movement
        start_time = time.time()

        for i in range(len(path_points) - 1):
            current_point = path_points[i]
            next_point = path_points[i + 1]

            # Calculate segment parameters
            segment_distance = math.dist(current_point, next_point)
            segment_duration = (segment_distance / total_distance) * total_duration

            # Move to current point
            self.current_position = current_point

            if page:
                try:
                    await page.mouse.move(current_point[0], current_point[1])
                except Exception as e:
                    # Continue even if mouse movement fails
                    pass

            # Random pause
            if random.random() < self.config.pause_probability:
                pause_duration = random.uniform(*self.config.pause_duration)
                await asyncio.sleep(pause_duration)

            # Wait for next segment
            await asyncio.sleep(segment_duration)

        # Ensure final position is reached
        self.current_position = end_pos
        if page:
            try:
                await page.mouse.move(target_x, target_y)
            except Exception:
                pass

        # Record movement
        movement_record = {
            'start_pos': start_pos,
            'end_pos': end_pos,
            'duration': time.time() - start_time,
            'style': style.value,
            'distance': total_distance,
            'speed': speed,
            'timestamp': time.time()
        }

        self.movement_history.append(movement_record)

    async def click(
        self,
        button: str = "left",
        click_delay: Tuple[float, float] = (0.05, 0.15),
        hold_duration: Tuple[float, float] = (0.1, 0.3),
        page: Optional[Any] = None
    ) -> None:
        """
        Perform realistic mouse click

        Args:
            button: Mouse button ('left', 'right', 'middle')
            click_delay: Delay before and after click (min, max) in seconds
            hold_duration: Button hold duration (min, max) in seconds
            page: Playwright page object (optional)
        """
        # Pre-click delay
        delay = random.uniform(*click_delay)
        await asyncio.sleep(delay)

        # Click down
        if page:
            try:
                await page.mouse.down(button=button)
            except Exception:
                pass

        # Hold duration
        hold = random.uniform(*hold_duration)
        await asyncio.sleep(hold)

        # Click up
        if page:
            try:
                await page.mouse.up(button=button)
            except Exception:
                pass

        # Post-click delay
        delay = random.uniform(*click_delay)
        await asyncio.sleep(delay)

    async def double_click(
        self,
        button: str = "left",
        interval: Tuple[float, float] = (0.05, 0.15),
        page: Optional[Any] = None
    ) -> None:
        """
        Perform realistic double click

        Args:
            button: Mouse button
            interval: Time between clicks (min, max) in seconds
            page: Playwright page object (optional)
        """
        await self.click(button=button, page=page)

        interval_time = random.uniform(*interval)
        await asyncio.sleep(interval_time)

        await self.click(button=button, page=page)

    async def drag_and_drop(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        style: MovementStyle = MovementStyle.NATURAL,
        page: Optional[Any] = None
    ) -> None:
        """
        Perform realistic drag and drop operation

        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            style: Movement style
            page: Playwright page object (optional)
        """
        # Move to start position
        await self.move_to(start_x, start_y, style, page)

        # Mouse down
        if page:
            try:
                await page.mouse.down()
            except Exception:
                pass

        # Small delay to simulate grabbing
        await asyncio.sleep(random.uniform(0.1, 0.2))

        # Move to end position while dragging
        await self.move_to(end_x, end_y, style, page)

        # Mouse up
        if page:
            try:
                await page.mouse.up()
            except Exception:
                pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get movement statistics"""
        if not self.movement_history:
            return {}

        total_movements = len(self.movement_history)
        total_distance = sum(m['distance'] for m in self.movement_history)
        total_duration = sum(m['duration'] for m in self.movement_history)

        style_counts = {}
        for movement in self.movement_history:
            style = movement['style']
            style_counts[style] = style_counts.get(style, 0) + 1

        return {
            'total_movements': total_movements,
            'total_distance': total_distance,
            'total_duration': total_duration,
            'average_speed': total_distance / total_duration if total_duration > 0 else 0,
            'average_distance': total_distance / total_movements if total_movements > 0 else 0,
            'style_distribution': style_counts,
            'current_position': self.current_position
        }

    def reset_history(self) -> None:
        """Reset movement history"""
        self.movement_history.clear()

    def set_position(self, x: float, y: float) -> None:
        """Set current mouse position without movement"""
        self.current_position = (x, y)


# Convenience functions for backward compatibility
async def realistic_move(
    page: Any,
    target_x: float,
    target_y: float,
    style: MovementStyle = MovementStyle.NATURAL,
    config: Optional[MouseConfig] = None
) -> None:
    """
    Move mouse realistically to target position

    Args:
        page: Playwright page object
        target_x: Target X coordinate
        target_y: Target Y coordinate
        style: Movement style
        config: Mouse movement configuration
    """
    mouse = MouseMovement(config)
    await mouse.move_to(target_x, target_y, style, page)


async def realistic_click(
    page: Any,
    button: str = "left",
    click_delay: Tuple[float, float] = (0.05, 0.15),
    hold_duration: Tuple[float, float] = (0.1, 0.3),
    config: Optional[MouseConfig] = None
) -> None:
    """
    Perform realistic mouse click

    Args:
        page: Playwright page object
        button: Mouse button
        click_delay: Delay before/after click
        hold_duration: Button hold duration
        config: Mouse movement configuration
    """
    mouse = MouseMovement(config)
    await mouse.click(button, click_delay, hold_duration, page)


async def realistic_drag_and_drop(
    page: Any,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    style: MovementStyle = MovementStyle.NATURAL,
    config: Optional[MouseConfig] = None
) -> None:
    """
    Perform realistic drag and drop

    Args:
        page: Playwright page object
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        style: Movement style
        config: Mouse movement configuration
    """
    mouse = MouseMovement(config)
    await mouse.drag_and_drop(start_x, start_y, end_x, end_y, style, page)