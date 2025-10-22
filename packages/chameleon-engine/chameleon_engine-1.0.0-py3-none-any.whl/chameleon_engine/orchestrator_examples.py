"""
Chameleon Engine Examples

This module demonstrates comprehensive usage examples of the ChameleonEngine
for different web scraping scenarios with advanced stealth capabilities.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List

from .orchestrator import (
    ChameleonEngine,
    ChameleonEngineConfig,
    SessionMetrics
)
from .services.fingerprint.models import BrowserType, OperatingSystem
from .behavior.mouse import MovementStyle
from .behavior.keyboard import TypingStyle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_scraping_example():
    """Example: Basic web scraping with stealth features"""
    print("=== Basic Scraping Example ===")

    # Create engine with default configuration
    engine = ChameleonEngine()

    try:
        # Start the engine
        session_id = await engine.start(
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS
        )
        print(f"Engine started with session: {session_id}")

        # Create a new page
        page_id = await engine.new_page()
        print(f"Created page: {page_id}")

        # Navigate to a website
        success = await engine.navigate(page_id, "https://httpbin.org/ip")
        print(f"Navigation successful: {success}")

        # Take a screenshot
        screenshot = await engine.take_screenshot(page_id)
        print(f"Screenshot captured: {len(screenshot)} bytes")

        # Get page content
        content = await engine.execute_script(page_id, "return document.body.innerText")
        print(f"Page content length: {len(content)} characters")

        # Show status
        status = engine.get_status()
        print(f"Engine status: {status['session_metrics']}")

    finally:
        # Stop the engine
        await engine.stop()
        print("Engine stopped")


async def advanced_stealth_example():
    """Example: Advanced stealth scraping with human behavior"""
    print("\n=== Advanced Stealth Example ===")

    # Configure engine for maximum stealth
    config = ChameleonEngineConfig(
        fingerprint_service_url="http://localhost:8000",
        headless=False,  # Show browser for demonstration
        enable_network_obfuscation=True,
        enable_custom_binary=True,
        enable_stealth_scripts=True,
        enable_human_behavior=True,
        mouse_movement_style=MovementStyle.NATURAL,
        keyboard_typing_style=TypingStyle.NORMAL_TOUCH,
        auto_rotate_profiles=False,
        enable_monitoring=True
    )

    engine = ChameleonEngine(config)

    try:
        # Start with custom profile
        session_id = await engine.start(
            browser_type=BrowserType.FIREFOX,
            operating_system=OperatingSystem.MACOS
        )
        print(f"Advanced engine started: {session_id}")

        # Create page and navigate
        page_id = await engine.new_page()
        await engine.navigate(page_id, "https://httpbin.org/forms/post")

        # Fill form with human-like behavior
        await engine.click(page_id, "input[name='custname']")
        await engine.type_text(page_id, "input[name='custname']", "John Doe", TypingStyle.NORMAL_TOUCH)

        await engine.click(page_id, "input[name='custtel']")
        await engine.type_text(page_id, "input[name='custtel']", "+1-555-123-4567", TypingStyle.SLOW_TOUCH)

        await engine.click(page_id, "input[name='custemail']")
        await engine.type_text(page_id, "input[name='custemail']", "john.doe@example.com", TypingStyle.NORMAL_TOUCH)

        # Submit form
        await engine.click(page_id, "input[type='submit']")

        # Wait for form submission
        await asyncio.sleep(2.0)

        # Take screenshot of result
        screenshot = await engine.take_screenshot(page_id, "form_result.png")
        print(f"Form result screenshot: {len(screenshot)} bytes")

        # Show detailed status
        status = engine.get_status()
        print(f"Current profile: {status['current_profile']}")
        print(f"Network obfuscation: {status['components'].get('network_obfuscator', {}).get('status', 'unknown')}")
        print(f"Session metrics: {status['session_metrics']}")

    finally:
        await engine.stop()
        print("Advanced engine stopped")


async def multi_page_scraping_example():
    """Example: Scraping multiple pages concurrently"""
    print("\n=== Multi-Page Scraping Example ===")

    config = ChameleonEngineConfig(
        max_concurrent_pages=3,
        headless=True,
        enable_human_behavior=False,  # Disable for performance
        enable_monitoring=True
    )

    engine = ChameleonEngine(config)

    try:
        session_id = await engine.start(
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS
        )
        print(f"Multi-page engine started: {session_id}")

        # URLs to scrape
        urls = [
            "https://httpbin.org/ip",
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers",
            "https://httpbin.org/uuid"
        ]

        # Create pages and navigate concurrently
        tasks = []
        for url in urls:
            page_id = await engine.new_page()
            print(f"Created page {page_id} for {url}")
            task = asyncio.create_task(scrape_page(engine, page_id, url))
            tasks.append(task)

        # Wait for all scraping to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful = sum(1 for r in results if not isinstance(r, Exception))
        print(f"Successfully scraped {successful}/{len(urls)} pages")

        # Show session metrics
        metrics = engine.get_session_metrics()
        print(f"Session metrics: {metrics}")

    finally:
        await engine.stop()
        print("Multi-page engine stopped")


async def scrape_page(engine: ChameleonEngine, page_id: str, url: str) -> Dict[str, Any]:
    """Scrape a single page and return results"""
    try:
        # Navigate
        success = await engine.navigate(page_id, url, timeout=10.0)
        if not success:
            return {'url': url, 'success': False, 'error': 'Navigation failed'}

        # Get page title
        title = await engine.execute_script(page_id, "return document.title")

        # Get page content
        content = await engine.execute_script(page_id, "return document.body.innerText")

        # Take screenshot
        screenshot = await engine.take_screenshot(page_id)

        await engine.close_page(page_id)

        return {
            'url': url,
            'success': True,
            'title': title,
            'content_length': len(content),
            'screenshot_size': len(screenshot)
        }

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return {'url': url, 'success': False, 'error': str(e)}


async def form_interaction_example():
    """Example: Complex form interaction with validation"""
    print("\n=== Form Interaction Example ===")

    config = ChameleonEngineConfig(
        headless=False,  # Show browser for demonstration
        enable_human_behavior=True,
        mouse_movement_style=MovementStyle.PRECISE,
        keyboard_typing_style=TypingStyle.SLOW_TOUCH,
        enable_monitoring=True
    )

    engine = ChameleonEngine(config)

    try:
        session_id = await engine.start(
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS
        )
        print(f"Form interaction engine started: {session_id}")

        # Create page and navigate to a complex form
        page_id = await engine.new_page()
        await engine.navigate(page_id, "https://httpbin.org/forms/post")

        # Fill a registration-like form with human behavior
        form_data = {
            "input[name='custname']": ("Alice Johnson", TypingStyle.NORMAL_TOUCH),
            "input[name='custtel']": ("(555) 123-4567", TypingStyle.SLOW_TOUCH),
            "input[name='custemail']": ("alice.johnson@email.com", TypingStyle.NORMAL_TOUCH),
            "input[name='custid']": ("ALICE123", TypingStyle.FAST_TOUCH),
            "textarea[name='comments']": (
                "I am very interested in this service. Looking forward to using it.",
                TypingStyle.FAST_TOUCH
            )
        }

        # Fill form fields with human-like timing
        for selector, (text, typing_style) in form_data.items():
            print(f"Filling {selector}")
            await engine.click(page_id, selector)
            await asyncio.sleep(0.2)  # Brief pause before typing
            await engine.type_text(page_id, selector, text, typing_style)
            await asyncio.sleep(0.3)  # Brief pause after typing

        # Take screenshot before submission
        await engine.take_screenshot(page_id, "form_filled.png")
        print("Form filled - screenshot captured")

        # Submit form with a deliberate pause
        await asyncio.sleep(1.0)
        await engine.click(page_id, "input[type='submit']")

        # Wait for response
        await asyncio.sleep(2.0)

        # Check form submission result
        result_text = await engine.execute_script(page_id, "return document.body.innerText")
        print(f"Form submission result: {result_text[:200]}...")

        # Take final screenshot
        await engine.take_screenshot(page_id, "form_result.png")

    finally:
        await engine.stop()
        print("Form interaction engine stopped")


async def profile_rotation_example():
    """Example: Automatic profile rotation for long-running sessions"""
    print("\n=== Profile Rotation Example ===")

    config = ChameleonEngineConfig(
        headless=True,
        auto_rotate_profiles=True,
        profile_rotation_interval=5.0,  # Rotate every 5 seconds for demo
        enable_monitoring=True,
        enable_analytics=True
    )

    engine = ChameleonEngine(config)

    try:
        session_id = await engine.start(
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS
        )
        print(f"Profile rotation engine started: {session_id}")

        # Simulate a long-running scraping session
        for i in range(10):
            page_id = await engine.new_page()
            await engine.navigate(page_id, f"https://httpbin.org/uuid/{i}")

            # Get current profile info
            status = engine.get_status()
            current_profile = status['current_profile']
            print(f"Request {i+1}: Using {current_profile['browser']} {current_profile['os']}")

            # Small delay between requests
            await asyncio.sleep(2.0)

            await engine.close_page(page_id)

        # Show rotation statistics
        metrics = engine.get_session_metrics()
        print(f"Profile rotations: {metrics['profile_rotations']}")
        print(f"Session duration: {metrics['duration']:.1f} seconds")

    finally:
        await engine.stop()
        print("Profile rotation engine stopped")


async def error_handling_example():
    """Example: Error handling and recovery"""
    print("\n=== Error Handling Example ===")

    engine = ChameleonEngine()

    try:
        session_id = await engine.start()
        print(f"Error handling engine started: {session_id}")

        # Test various error scenarios

        # 1. Navigate to invalid URL
        print("Testing invalid URL navigation...")
        page_id = await engine.new_page()
        success = await engine.navigate(page_id, "https://invalid-url-that-does-not-exist.com")
        print(f"Invalid URL navigation: {success}")

        # 2. Click non-existent element
        print("Testing non-existent element click...")
        click_success = await engine.click(page_id, "#non-existent-element")
        print(f"Non-existent element click: {click_success}")

        # 3. Try to navigate after page closed
        print("Testing navigation after page closure...")
        await engine.close_page(page_id)
        try:
            await engine.navigate(page_id, "https://httpbin.org/ip")
        except Exception as e:
            print(f"Expected error after page closure: {type(e).__name__}")

        # 4. Show error statistics
        status = engine.get_status()
        print(f"Errors encountered: {status['session_metrics']['errors_count']}")
        if status['session_metrics']['errors_count'] > 0:
            print("Recent errors:")
            for error in status['session_metrics']['errors'][-3:]:  # Show last 3 errors
                print(f"  - {error}")

    finally:
        await engine.stop()
        print("Error handling engine stopped")


async def performance_monitoring_example():
    """Example: Performance monitoring and optimization"""
    print("\n=== Performance Monitoring Example ===")

    config = ChameleonEngineConfig(
        headless=True,
        max_concurrent_pages=5,
        enable_monitoring=True,
        enable_analytics=True,
        session_timeout=300.0
    )

    engine = ChameleonEngine(config)

    try:
        session_id = await engine.start()
        print(f"Performance monitoring engine started: {session_id}")

        # Monitor performance over time
        start_time = time.time()

        # Perform various operations
        operations = [
            ("Page Creation", lambda: engine.new_page()),
            ("Navigation", lambda: engine.navigate("test_page", "https://httpbin.org/ip")),
            ("Script Execution", lambda: engine.execute_script("test_page", "return performance.now()")),
            ("Screenshot", lambda: engine.take_screenshot("test_page")),
        ]

        for operation_name, operation in operations:
            if operation_name == "Navigation":
                page_id = await engine.new_page()
                success = await operation(page_id, "https://httpbin.org/ip")
            elif operation_name == "Script Execution" or operation_name == "Screenshot":
                # These require an existing page
                if 'page_id' not in locals():
                    page_id = await engine.new_page()
                    await engine.navigate(page_id, "https://httpbin.org/ip")
                await operation(page_id)
            else:
                await operation()

            elapsed = time.time() - start_time
            current_metrics = engine.get_session_metrics()
            print(f"{operation_name}: {elapsed:.2f}s elapsed, {current_metrics}")

            # Brief pause between operations
            await asyncio.sleep(0.5)

        # Final performance summary
        final_metrics = engine.get_session_metrics()
        print(f"\nPerformance Summary:")
        print(f"  Total session time: {final_metrics['duration']:.2f}s")
        print(f"  Pages created: {final_metrics['pages_created']}")
        print(f"  Requests made: {final_metrics['requests_made']}")
        print(f"  Success rate: {final_metrics['success_rate']:.2%}")
        print(f"  Data downloaded: {final_metrics['total_data_size'] / 1024:.1f} KB")

    finally:
        await engine.stop()
        print("Performance monitoring engine stopped")


async def context_manager_example():
    """Example: Using context managers for automatic cleanup"""
    print("\n=== Context Manager Example ===")

    # Example 1: Basic context manager
    print("Basic context manager usage:")
    async with ChameleonEngine() as engine:
        page_id = await engine.new_page()
        await engine.navigate(page_id, "https://httpbin.org/ip")
        content = await engine.execute_script(page_id, "return document.body.innerText")
        print(f"Page content: {content[:100]}...")

    print("Engine automatically stopped")

    # Example 2: Context manager with custom configuration
    print("\nContext manager with custom configuration:")
    config = ChameleonEngineConfig(
        headless=False,
        enable_human_behavior=True,
        mouse_movement_style=MovementStyle.NERVOUS,
        keyboard_typing_style=TypingStyle.NERVOUS
    )

    async with ChameleonEngine(config) as engine:
        page_id = await engine.new_page()
        await engine.navigate(page_id, "https://httpbin.org/forms/post")

        # Use nervous behavior for form filling
        await engine.click(page_id, "input[name='custname']")
        await engine.type_text(page_id, "input[name='custname']", "Test User", TypingStyle.NERVOUS)

        screenshot = await engine.take_screenshot(page_id)
        print(f"Nervous behavior screenshot: {len(screenshot)} bytes")

    print("Custom engine automatically stopped")


async def integration_test_example():
    """Example: Full integration test with all features"""
    print("\n=== Full Integration Test ===")

    config = ChameleonEngineConfig(
        fingerprint_service_url="http://localhost:8000",
        headless=True,
        enable_network_obfuscation=True,
        enable_custom_binary=True,
        enable_stealth_scripts=True,
        enable_human_behavior=True,
        mouse_movement_style=MovementStyle.NATURAL,
        keyboard_typing_style=TypingStyle.NORMAL_TOUCH,
        max_concurrent_pages=3,
        enable_monitoring=True,
        enable_analytics=True,
        auto_rotate_profiles=False
    )

    engine = ChameleonEngine(config)

    try:
        print("Starting full integration test...")
        session_id = await engine.start(
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS
        )
        print(f"Integration test started: {session_id}")

        # Test all major features
        test_results = {}

        # Test 1: Basic navigation
        print("\nTest 1: Basic navigation")
        page_id = await engine.new_page()
        test_results['navigation'] = await engine.navigate(page_id, "https://httpbin.org/ip")

        # Test 2: Script execution
        print("Test 2: Script execution")
        test_results['script'] = await engine.execute_script(page_id, "return navigator.userAgent")

        # Test 3: Mouse interaction
        print("Test 3: Mouse interaction")
        test_results['mouse'] = await engine.click(page_id, "body")

        # Test 4: Keyboard interaction
        print("Test 4: Keyboard interaction")
        # Note: This would need an actual input field
        # test_results['keyboard'] = await engine.type_text(page_id, "input", "test")

        # Test 5: Screenshot
        print("Test 5: Screenshot capture")
        screenshot = await engine.take_screenshot(page_id)
        test_results['screenshot'] = len(screenshot) > 0

        # Test 6: Multiple pages
        print("Test 6: Multiple page management")
        page_ids = [await engine.new_page() for _ in range(2)]
        test_results['multi_page'] = len(page_ids) == 2

        # Clean up extra pages
        for pid in page_ids:
            await engine.close_page(pid)

        # Show comprehensive status
        status = engine.get_status()
        print(f"\nIntegration Test Results:")
        for test, result in test_results.items():
            print(f"  {test}: {'✓' if result else '✗'}")

        print(f"\nFinal Status:")
        print(f"  Components: {list(status['components'].keys())}")
        print(f"  Profile: {status['current_profile']}")
        print(f"  Session metrics: {status['session_metrics']}")

    finally:
        await engine.stop()
        print("Integration test completed")


async def main():
    """Run all examples"""
    print("Chameleon Engine Examples")
    print("=" * 50)

    examples = [
        basic_scraping_example,
        advanced_stealth_example,
        multi_page_scraping_example,
        form_interaction_example,
        profile_rotation_example,
        error_handling_example,
        performance_monitoring_example,
        context_manager_example,
        integration_test_example
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