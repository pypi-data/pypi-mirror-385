"""
Fingerprint Generator Examples

This module contains comprehensive examples demonstrating how to use the FingerprintGenerator
and related components for various use cases in Chameleon Engine.
"""

import asyncio
import logging
from typing import List, Dict, Any

from .generator import (
    FingerprintGenerator,
    ProfilePool,
    FingerprintCache,
    ServiceUnavailableError,
    ProfileGenerationError
)
from ..services.fingerprint.models import (
    BrowserType,
    OperatingSystem,
    ProfileConstraints,
    DeviceType
)
from ..core.profiles import BrowserProfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_fingerprint_generation():
    """Example: Basic fingerprint generation"""
    print("=== Basic Fingerprint Generation ===")

    async with FingerprintGenerator() as generator:
        # Generate a basic Chrome profile for Windows
        profile = await generator.generate(
            browser=BrowserType.CHROME,
            os=OperatingSystem.WINDOWS
        )

        print(f"Generated profile:")
        print(f"  Browser: {profile.browser_type.value}")
        print(f"  OS: {profile.operating_system.value}")
        print(f"  User Agent: {profile.navigator.user_agent[:100]}...")
        print(f"  Screen: {profile.screen.width}x{profile.screen.height}")
        print(f"  Canvas Fingerprint: {len(profile.canvas.fingerprint)} chars")

        return profile


async def advanced_fingerprint_generation():
    """Example: Advanced fingerprint generation with constraints"""
    print("\n=== Advanced Fingerprint Generation ===")

    generator = FingerprintGenerator(
        service_url="http://localhost:8000",
        cache_size=100,
        cache_ttl=1800  # 30 minutes
    )

    try:
        # Define specific constraints
        constraints = ProfileConstraints(
            browser_types=[BrowserType.CHROME, BrowserType.FIREFOX],
            operating_systems=[OperatingSystem.WINDOWS, OperatingSystem.MACOS],
            screen_resolutions=["1920x1080", "1366x768"],
            regions=["us", "uk", "de"],
            exclude_mobile=True,
            quality_threshold=0.8
        )

        # Generate profile with constraints
        profile = await generator.generate(
            browser=BrowserType.FIREFOX,
            os=OperatingSystem.MACOS,
            version="120.0",
            region="us",
            device_type="desktop",
            quality_threshold=0.85,
            constraints=constraints,
            seed="deterministic-seed-123"
        )

        print(f"Advanced profile generated:")
        print(f"  Browser: {profile.browser_type.value} {profile.browser_version}")
        print(f"  OS: {profile.operating_system.value}")
        print(f"  Region: {profile.headers.accept_language}")
        print(f"  TLS Fingerprint: {profile.tls_fingerprint.ja3_hash}")
        print(f"  HTTP2 Settings: {len(profile.http2_settings.settings_pairs)} settings")

        # Validate the profile
        validation_result = await generator.validate_profile(profile, test_type="basic")
        print(f"  Validation status: {validation_result.get('status', 'unknown')}")

        return profile

    finally:
        await generator.close()


async def batch_fingerprint_generation():
    """Example: Batch fingerprint generation for multiple profiles"""
    print("\n=== Batch Fingerprint Generation ===")

    async with FingerprintGenerator() as generator:
        # Create multiple requests
        requests = [
            {
                'browser': BrowserType.CHROME,
                'os': OperatingSystem.WINDOWS,
                'region': 'us'
            },
            {
                'browser': BrowserType.FIREFOX,
                'os': OperatingSystem.MACOS,
                'region': 'uk'
            },
            {
                'browser': BrowserType.SAFARI,
                'os': OperatingSystem.MACOS,
                'region': 'de'
            },
            {
                'browser': BrowserType.EDGE,
                'os': OperatingSystem.WINDOWS,
                'region': 'fr'
            },
            {
                'browser': BrowserType.CHROME,
                'os': OperatingSystem.LINUX,
                'region': 'jp'
            }
        ]

        # Generate profiles in batch
        profiles = []
        for request in requests:
            try:
                profile = await generator.generate(**request)
                profiles.append(profile)
                print(f"Generated: {request['browser'].value}/{request['os'].value} for {request['region']}")
            except Exception as e:
                print(f"Failed to generate {request['browser'].value}/{request['os'].value}: {e}")

        print(f"Successfully generated {len(profiles)} profiles")

        # Show statistics
        stats = generator.get_statistics()
        print(f"Generator statistics:")
        print(f"  Total requests: {stats['requests_made']}")
        print(f"  Cache hits: {stats['cache_hits']}")
        print(f"  Success rate: {stats['success_rate']:.2%}")
        print(f"  Average generation time: {stats['average_generation_time']:.2f}s")

        return profiles


async def profile_pool_usage():
    """Example: Using ProfilePool for high-performance scenarios"""
    print("\n=== Profile Pool Usage ===")

    generator = FingerprintGenerator()
    pool = ProfilePool(
        generator=generator,
        pool_size=10,
        refill_threshold=0.3,
        default_constraints=ProfileConstraints(
            quality_threshold=0.7,
            browser_types=[BrowserType.CHROME, BrowserType.FIREFOX]
        )
    )

    try:
        # Start the pool
        await pool.start()
        print("Profile pool started")

        # Acquire and use profiles
        profiles = []
        for i in range(5):
            try:
                # Acquire profile from pool
                profile = await pool.acquire(timeout=5.0)
                profiles.append(profile)

                print(f"Acquired profile {i+1}: {profile.browser_type.value}/{profile.operating_system.value}")

                # Simulate using the profile
                await asyncio.sleep(0.1)

                # Release profile back to pool
                await pool.release(profile)
                print(f"Released profile {i+1}")

            except Exception as e:
                print(f"Error acquiring/releasing profile {i+1}: {e}")

        # Show pool status
        status = pool.get_status()
        print(f"Pool status:")
        print(f"  Current size: {status['current_size']}")
        print(f"  Target size: {status['target_size']}")
        print(f"  Utilization: {status['utilization']:.2%}")

    finally:
        await pool.stop()
        await generator.close()
        print("Profile pool stopped")


async def service_monitoring():
    """Example: Service monitoring and health checks"""
    print("\n=== Service Monitoring ===")

    generator = FingerprintGenerator(
        service_url="http://localhost:8000",
        timeout=10.0,
        max_retries=2
    )

    try:
        # Check service status
        print("Checking service status...")
        status = await generator.get_service_status()

        print(f"Service status:")
        print(f"  Status: {status.status}")
        print(f"  Message: {status.message}")
        print(f"  Timestamp: {status.timestamp}")

        if hasattr(status, 'database_status'):
            print(f"  Database: {status.database_status}")

        if hasattr(status, 'uptime_seconds'):
            print(f"  Uptime: {status.uptime_seconds}s")

        # Wait for service if needed
        if status.status != "healthy":
            print("Service not healthy, waiting for recovery...")
            is_available = await generator.wait_for_service(timeout_seconds=30)
            print(f"Service available: {is_available}")

        # Generate a test profile
        try:
            profile = await generator.generate(
                browser=BrowserType.CHROME,
                os=OperatingSystem.WINDOWS,
                quality_threshold=0.6
            )
            print("Test profile generated successfully")
        except ServiceUnavailableError as e:
            print(f"Service unavailable: {e}")
        except ProfileGenerationError as e:
            print(f"Profile generation failed: {e}")

    finally:
        await generator.close()


async def caching_performance_demo():
    """Example: Demonstrating caching performance benefits"""
    print("\n=== Caching Performance Demo ===")

    # Test with caching enabled
    print("Testing with caching enabled...")
    generator_with_cache = FingerprintGenerator(
        cache_size=50,
        cache_ttl=300  # 5 minutes
    )

    try:
        start_time = asyncio.get_event_loop().time()

        # Generate same profile multiple times
        profiles = []
        for i in range(5):
            profile = await generator_with_cache.generate(
                browser=BrowserType.CHROME,
                os=OperatingSystem.WINDOWS,
                region="us"
            )
            profiles.append(profile)
            print(f"Request {i+1}: Generated profile")

        cached_time = asyncio.get_event_loop().time() - start_time

        # Get statistics
        stats = generator_with_cache.get_statistics()
        print(f"With cache:")
        print(f"  Total time: {cached_time:.2f}s")
        print(f"  Cache hits: {stats['cache_hits']}")
        print(f"  Cache misses: {stats['cache_misses']}")
        print(f"  Hit rate: {stats.get('cache_hit_rate', 0):.2%}")
        print(f"  Average time: {stats['average_generation_time']:.2f}s")

    finally:
        await generator_with_cache.close()

    # Test without caching
    print("\nTesting without caching...")
    generator_no_cache = FingerprintGenerator(use_cache=False)

    try:
        start_time = asyncio.get_event_loop().time()

        # Generate same profile multiple times
        profiles = []
        for i in range(5):
            profile = await generator_no_cache.generate(
                browser=BrowserType.CHROME,
                os=OperatingSystem.WINDOWS,
                region="us"
            )
            profiles.append(profile)
            print(f"Request {i+1}: Generated profile")

        no_cache_time = asyncio.get_event_loop().time() - start_time

        # Get statistics
        stats = generator_no_cache.get_statistics()
        print(f"Without cache:")
        print(f"  Total time: {no_cache_time:.2f}s")
        print(f"  Average time: {stats['average_generation_time']:.2f}s")

        # Performance comparison
        if cached_time > 0:
            speedup = no_cache_time / cached_time
            print(f"\nPerformance improvement: {speedup:.2f}x faster with caching")

    finally:
        await generator_no_cache.close()


async def error_handling_examples():
    """Example: Comprehensive error handling"""
    print("\n=== Error Handling Examples ===")

    # Test with invalid service URL
    print("Testing with invalid service URL...")
    generator = FingerprintGenerator(service_url="http://invalid:8000")

    try:
        await generator.wait_for_service(timeout_seconds=5)
    except ServiceUnavailableError as e:
        print(f"Expected service unavailable error: {e}")
    finally:
        await generator.close()

    # Test with very high quality requirements
    print("\nTesting with very high quality requirements...")
    generator = FingerprintGenerator(service_url="http://localhost:8000")

    try:
        profile = await generator.generate(
            browser=BrowserType.CHROME,
            os=OperatingSystem.WINDOWS,
            quality_threshold=0.999  # Almost impossible
        )
        print("Generated profile with high quality (unexpected)")
    except ProfileGenerationError as e:
        print(f"Expected profile generation error: {e}")
    except Exception as e:
        print(f"Other error (service may be unavailable): {e}")
    finally:
        await generator.close()


async def main():
    """Run all examples"""
    print("Fingerprint Generator Examples")
    print("=" * 50)

    examples = [
        basic_fingerprint_generation,
        advanced_fingerprint_generation,
        batch_fingerprint_generation,
        profile_pool_usage,
        service_monitoring,
        caching_performance_demo,
        error_handling_examples
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