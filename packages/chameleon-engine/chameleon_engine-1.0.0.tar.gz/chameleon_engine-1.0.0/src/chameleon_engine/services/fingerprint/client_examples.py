"""
Examples of using the Fingerprint Service Client.

This module provides example code demonstrating how to use the fingerprint service
client for various use cases.
"""

import asyncio
import logging
from typing import List

from .client import FingerprintServiceClient, CachingFingerprintClient
from .models import FingerprintRequest, BrowserType, OperatingSystem, ProfileConstraints

logger = logging.getLogger(__name__)


async def basic_fingerprint_request():
    """Example: Basic fingerprint request."""

    async with FingerprintServiceClient("http://localhost:8000") as client:
        # Create a basic request
        request = FingerprintRequest(
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS,
            locale="en-US",
            mobile=False
        )

        # Get fingerprint
        fingerprint = await client.get_fingerprint(request)

        print(f"Generated fingerprint: {fingerprint.profile_id}")
        print(f"Browser: {fingerprint.browser_profile.browser_type}")
        print(f"Coherence score: {fingerprint.metadata.coherence_score}")

        return fingerprint


async def constrained_fingerprint_request():
    """Example: Fingerprint request with constraints."""

    async with FingerprintServiceClient("http://localhost:8000") as client:
        # Create constraints
        constraints = ProfileConstraints(
            browser_types=[BrowserType.CHROME, BrowserType.FIREFOX],
            operating_systems=[OperatingSystem.WINDOWS, OperatingSystem.MACOS],
            min_screen_width=1920,
            max_screen_width=2560,
            min_screen_height=1080,
            max_screen_height=1440,
            locales=["en-US", "en-GB"],
            coherence_threshold=0.9
        )

        # Create request with constraints
        request = FingerprintRequest(
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS,
            constraints=constraints,
            include_advanced_fingerprinting=True,
            coherence_threshold=0.85
        )

        # Get fingerprint
        fingerprint = await client.get_fingerprint(request)

        print(f"Constrained fingerprint: {fingerprint.profile_id}")
        print(f"Screen: {fingerprint.browser_profile.screen.width}x{fingerprint.browser_profile.screen.height}")

        return fingerprint


async def batch_fingerprint_request():
    """Example: Batch fingerprint generation."""

    async with FingerprintServiceClient("http://localhost:8000") as client:
        # Create multiple requests
        requests = [
            FingerprintRequest(
                browser_type=BrowserType.CHROME,
                operating_system=OperatingSystem.WINDOWS,
                locale="en-US"
            ),
            FingerprintRequest(
                browser_type=BrowserType.FIREFOX,
                operating_system=OperatingSystem.WINDOWS,
                locale="en-US"
            ),
            FingerprintRequest(
                browser_type=BrowserType.SAFARI,
                operating_system=OperatingSystem.MACOS,
                locale="en-US"
            ),
            FingerprintRequest(
                browser_type=BrowserType.CHROME,
                operating_system=OperatingSystem.ANDROID,
                locale="en-US",
                mobile=True
            )
        ]

        # Get batch fingerprints
        batch_response = await client.get_batch_fingerprints(requests, ensure_diversity=True)

        print(f"Batch generation completed:")
        print(f"  Successful: {batch_response.total_successful}")
        print(f"  Failed: {batch_response.total_failed}")
        print(f"  Average time: {batch_response.avg_generation_time_ms:.2f}ms")

        # Process successful fingerprints
        for i, fingerprint in enumerate(batch_response.successful_profiles):
            print(f"  Profile {i+1}: {fingerprint.profile_id} ({fingerprint.browser_profile.browser_type}/{fingerprint.browser_profile.operating_system})")

        return batch_response


async def health_check_example():
    """Example: Service health check."""

    async with FingerprintServiceClient("http://localhost:8000") as client:
        # Check service health
        health = await client.health_check()

        print(f"Service Status: {health.status}")
        print(f"Uptime: {health.uptime_seconds}s")
        print(f"Total Profiles: {health.total_profiles}")
        print(f"Active Profiles: {health.active_profiles}")
        print(f"API Version: {health.api_version}")

        if health.last_data_update:
            print(f"Last Data Update: {health.last_data_update}")

        return health


async def service_statistics_example():
    """Example: Get service statistics."""

    async with FingerprintServiceClient("http://localhost:8000") as client:
        # Get statistics
        stats = await client.get_service_statistics()

        print("Service Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        return stats


async def usage_reporting_example():
    """Example: Report fingerprint usage."""

    async with FingerprintServiceClient("http://localhost:8000") as client:
        # First get a fingerprint
        request = FingerprintRequest(
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS
        )

        fingerprint = await client.get_fingerprint(request)

        # Simulate successful usage
        success = await client.report_usage(
            profile_id=fingerprint.profile_id,
            success=True,
            target_domain="example.com",
            response_time_ms=1250,
            detected_as_bot=False
        )

        print(f"Usage reported successfully: {success}")

        # Simulate failed usage
        failure = await client.report_usage(
            profile_id=fingerprint.profile_id,
            success=False,
            target_domain="bot-detection-site.com",
            response_time_ms=500,
            detected_as_bot=True,
            error_message="Detected as automated bot"
        )

        print(f"Failure reported successfully: {failure}")


async def validation_example():
    """Example: Profile validation."""

    async with FingerprintServiceClient("http://localhost:8000") as client:
        # Get a fingerprint
        request = FingerprintRequest(
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS
        )

        fingerprint = await client.get_fingerprint(request)

        # Validate the profile
        validation_result = await client.validate_profile(
            profile_id=fingerprint.profile_id,
            test_type="synthetic"
        )

        print(f"Validation Result: {validation_result.get('result')}")
        print(f"Validation Score: {validation_result.get('score')}")

        if validation_result.get('details'):
            print("Validation Details:")
            for key, value in validation_result['details'].items():
                print(f"  {key}: {value}")


async def caching_client_example():
    """Example: Using caching client."""

    # Create base client
    base_client = FingerprintServiceClient("http://localhost:8000")

    # Wrap with caching client
    async with CachingFingerprintClient(
        base_client=base_client,
        cache_ttl_seconds=1800,  # 30 minutes
        max_cache_size=500
    ) as caching_client:

        # Make multiple similar requests
        request = FingerprintRequest(
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS
        )

        # First request (cache miss)
        print("First request (cache miss):")
        fingerprint1 = await caching_client.get_fingerprint(request)
        print(f"Profile ID: {fingerprint1.profile_id}")

        # Second request (cache hit)
        print("Second request (cache hit):")
        fingerprint2 = await caching_client.get_fingerprint(request)
        print(f"Profile ID: {fingerprint2.profile_id}")

        # Get cache statistics
        cache_stats = caching_client.get_cache_stats()
        print("\nCache Statistics:")
        print(f"  Cache Size: {cache_stats['cache_size']}/{cache_stats['max_cache_size']}")
        print(f"  Hit Rate: {cache_stats['hit_rate']:.2%}")
        print(f"  Cache Hits: {cache_stats['cache_hits']}")
        print(f"  Cache Misses: {cache_stats['cache_misses']}")


async def connection_test_example():
    """Example: Connection testing."""

    client = FingerprintServiceClient("http://localhost:8000")

    try:
        # Test connection
        test_result = await client.test_connection()

        print("Connection Test Results:")
        for key, value in test_result.items():
            print(f"  {key}: {value}")

        if test_result.get('connection_status') == 'success':
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed!")

    except Exception as e:
        print(f"Connection test failed: {e}")

    finally:
        await client.close()


async def wait_for_service_example():
    """Example: Wait for service to be ready."""

    client = FingerprintServiceClient("http://localhost:8000")

    try:
        print("Waiting for fingerprint service to be ready...")
        ready = await client.wait_for_service(max_wait_seconds=30)

        if ready:
            print("✅ Service is ready!")

            # Service is ready - make a test request
            request = FingerprintRequest(
                browser_type=BrowserType.CHROME,
                operating_system=OperatingSystem.WINDOWS
            )

            fingerprint = await client.get_fingerprint(request)
            print(f"Test fingerprint generated: {fingerprint.profile_id}")

        else:
            print("❌ Service did not become ready in time")

    except Exception as e:
        print(f"Error waiting for service: {e}")

    finally:
        await client.close()


async def error_handling_example():
    """Example: Error handling and recovery."""

    async with FingerprintServiceClient("http://localhost:8000") as client:
        try:
            # Try to get a fingerprint
            request = FingerprintRequest(
                browser_type=BrowserType.CHROME,
                operating_system=OperatingSystem.WINDOWS,
                coherence_threshold=0.99  # Very high threshold
            )

            fingerprint = await client.get_fingerprint(request)
            print(f"Success: {fingerprint.profile_id}")

        except Exception as e:
            print(f"Error occurred: {str(e)}")

            # Try with lower requirements
            print("Retrying with lower requirements...")
            request.coherence_threshold = 0.7

            fingerprint = await client.get_fingerprint(request)
            print(f"Retry successful: {fingerprint.profile_id}")


async def advanced_usage_example():
    """Example: Advanced usage with multiple features."""

    async with FingerprintServiceClient("http://localhost:8000") as client:

        # Check service health first
        health = await client.health_check()
        if health.status != "healthy":
            print(f"Service not healthy: {health.status}")
            return

        print("Service is healthy, proceeding with advanced operations...")

        # Create constraints for high-quality profiles
        constraints = ProfileConstraints(
            browser_types=[BrowserType.CHROME, BrowserType.FIREFOX],
            operating_systems=[OperatingSystem.WINDOWS, OperatingSystem.MACOS],
            min_screen_width=1920,
            locales=["en-US", "en-GB"],
            coherence_threshold=0.9
        )

        # Generate multiple high-quality profiles
        requests = [
            FingerprintRequest(
                browser_type=BrowserType.CHROME,
                operating_system=OperatingSystem.WINDOWS,
                constraints=constraints,
                include_advanced_fingerprinting=True,
                coherence_threshold=0.85
            ),
            FingerprintRequest(
                browser_type=BrowserType.FIREFOX,
                operating_system=OperatingSystem.MACOS,
                constraints=constraints,
                include_advanced_fingerprinting=True,
                coherence_threshold=0.85
            )
        ]

        batch_response = await client.get_batch_fingerprints(requests)

        # Process and validate each profile
        for fingerprint in batch_response.successful_profiles:
            print(f"\nProcessing profile: {fingerprint.profile_id}")

            # Validate the profile
            validation = await client.validate_profile(fingerprint.profile_id)
            print(f"  Validation: {validation.get('result')} (score: {validation.get('score', 0):.2f})")

            # Simulate usage
            await client.report_usage(
                profile_id=fingerprint.profile_id,
                success=True,
                target_domain="test-site.com",
                response_time_ms=1000
            )

            print(f"  Quality metrics:")
            print(f"    Coherence: {fingerprint.metadata.coherence_score:.2f}")
            print(f"    Uniqueness: {fingerprint.metadata.uniqueness_score:.2f}")
            print(f"    Detection Risk: {fingerprint.metadata.detection_risk_score:.2f}")


async def main():
    """Run all examples."""

    print("=== Fingerprint Service Client Examples ===\n")

    examples = [
        ("Basic Request", basic_fingerprint_request),
        ("Constrained Request", constrained_fingerprint_request),
        ("Batch Request", batch_fingerprint_request),
        ("Health Check", health_check_example),
        ("Usage Reporting", usage_reporting_example),
        ("Caching Client", caching_client_example),
        ("Connection Test", connection_test_example)
    ]

    for name, example_func in examples:
        print(f"\n--- {name} ---")
        try:
            await example_func()
        except Exception as e:
            print(f"Example failed: {str(e)}")

        print("-" * 50)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run examples
    asyncio.run(main())