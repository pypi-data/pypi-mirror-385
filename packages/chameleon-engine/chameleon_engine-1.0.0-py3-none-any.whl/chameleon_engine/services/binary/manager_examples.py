"""
Examples of using the Custom Binary Manager.

This module provides example code demonstrating how to use the custom binary
manager for downloading and managing browser binaries.
"""

import asyncio
import logging
from typing import List

from .manager import CustomBinaryManager, BinaryInfo, BinaryType, BinaryStatus
from .config import BinaryConfig, BinaryConfigManager, get_optimized_config_for_use_case
from .downloader import DownloadProgress
from .validator import ValidationResult

logger = logging.getLogger(__name__)


async def basic_binary_manager_example():
    """Example: Basic binary manager usage."""

    # Create manager with default configuration
    manager = CustomBinaryManager()

    try:
        await manager.start()

        print(f"Binary manager started")
        print(f"Platform: {manager.current_platform.value}")
        print(f"Architecture: {manager.current_arch.value}")

        # Get manager status
        status = await manager.get_status()
        print(f"Total binaries: {status['total_binaries']}")
        print(f"Storage used: {status['total_size_mb']:.1f} MB")

        # Try to get a Chromium binary (auto-install if not available)
        try:
            chromium_binary = await manager.get_binary(
                binary_type=BinaryType.CHROMIUM,
                auto_install=True
            )

            print(f"Chromium binary available: {chromium_binary.executable_path}")
            print(f"Version: {chromium_binary.version}")
            print(f"Status: {chromium_binary.status.value}")
            print(f"Size: {chromium_binary.size / (1024*1024):.1f} MB")
            print(f"Usage count: {chromium_binary.usage_count}")

        except Exception as e:
            print(f"Failed to get Chromium binary: {str(e)}")

        return manager

    finally:
        await manager.stop()


async def configuration_management_example():
    """Example: Using different configurations."""

    # Create configuration manager
    config_manager = BinaryConfigManager()

    # Show available configurations
    all_configs = config_manager.get_all_configs()
    print(f"Available configurations: {list(all_configs.keys())}")

    # Create custom configuration
    custom_config = BinaryConfig(
        storage_directory="./custom_binaries",
        cache_directory="./custom_cache",
        temp_directory="./custom_temp",
        max_concurrent_downloads=2,
        download_timeout=180,
        verify_checksums=True,
        auto_cleanup=True,
        max_storage_gb=5,
        keep_versions=2
    )

    config_manager.add_config("custom", custom_config)

    # Use custom configuration
    manager = CustomBinaryManager(config_name="custom")

    try:
        await manager.start()

        print(f"Using custom configuration")
        print(f"Storage directory: {manager.config.storage_directory}")
        print(f"Max storage: {manager.config.max_storage_gb} GB")

        # Show platform info
        platform, arch = config_manager.get_platform_info()
        print(f"Detected platform: {platform.value}_{arch.value}")

        # List available sources
        sources = config_manager.get_all_sources()
        print(f"Available binary sources: {list(sources.keys())}")

        return manager

    finally:
        await manager.stop()


async def multi_binary_installation_example():
    """Example: Installing multiple browser binaries."""

    manager = CustomBinaryManager()

    def progress_callback(progress: DownloadProgress):
        print(f"Download progress: {progress.progress_percentage:.1f}% - "
              f"{progress.downloaded_mb:.1f}/{progress.total_mb:.1f} MB - "
              f"{progress.speed_mb_per_sec:.1f} MB/s")

    try:
        await manager.start()

        # List of binaries to install
        binaries_to_install = [
            (BinaryType.CHROMIUM, "latest"),
            (BinaryType.FIREFOX, "latest"),
        ]

        installed_binaries = []

        for binary_type, version in binaries_to_install:
            try:
                print(f"\nInstalling {binary_type.value} {version}...")

                binary_info = await manager.install_binary(
                    binary_type=binary_type,
                    version=version,
                    progress_callback=progress_callback
                )

                installed_binaries.append(binary_info)
                print(f"✓ Installed {binary_type.value}: {binary_info.executable_path}")

            except Exception as e:
                print(f"✗ Failed to install {binary_type.value}: {str(e)}")

        # List all installed binaries
        print(f"\nInstalled binaries:")
        all_binaries = await manager.list_binaries(status=BinaryStatus.INSTALLED)

        for binary in all_binaries:
            print(f"  - {binary.binary_type.value} {binary.version} "
                  f"({binary.platform.value}_{binary.architecture.value})")
            print(f"    Path: {binary.executable_path}")
            print(f"    Size: {binary.size / (1024*1024):.1f} MB")
            print(f"    Installed: {binary.install_date}")

        return manager

    finally:
        await manager.stop()


async def binary_validation_example():
    """Example: Binary validation and verification."""

    manager = CustomBinaryManager()

    try:
        await manager.start()

        # Install a binary first
        chromium_binary = await manager.install_binary(
            binary_type=BinaryType.CHROMIUM,
            version="latest"
        )

        print(f"Installed binary: {chromium_binary.executable_path}")

        # Validate the binary
        validation_result = await manager.validator.validate_binary(
            chromium_binary.executable_path
        )

        print(f"\nValidation Results:")
        print(f"Status: {validation_result.status.value}")
        print(f"Message: {validation_result.message}")
        print(f"Checksum verified: {validation_result.checksum_verified}")
        print(f"Signature verified: {validation_result.signature_verified}")
        print(f"Malware scan passed: {validation_result.malware_scan_passed}")
        print(f"Execution test passed: {validation_result.execution_test_passed}")

        if validation_result.details:
            print(f"\nValidation Details:")
            for key, value in validation_result.details.items():
                print(f"  {key}: {value}")

        return manager

    finally:
        await manager.stop()


async def binary_update_and_cleanup_example():
    """Example: Updating binaries and cleanup operations."""

    manager = CustomBinaryManager()

    try:
        await manager.start()

        # Install an older version first
        print("Installing initial binary...")
        binary_info = await manager.install_binary(
            binary_type=BinaryType.CHROMIUM,
            version="latest"
        )

        print(f"Initial binary: {binary_info.version}")

        # List binaries before update
        binaries_before = await manager.list_binaries()
        print(f"Binaries before update: {len(binaries_before)}")

        # Update to latest version
        try:
            print("\nUpdating to latest version...")
            updated_binary = await manager.update_binary(
                binary_type=BinaryType.CHROMIUM,
                current_version=binary_info.version
            )

            print(f"Updated binary: {updated_binary.version}")

        except Exception as e:
            print(f"Update failed: {str(e)}")

        # List binaries after update
        binaries_after = await manager.list_binaries()
        print(f"Binaries after update: {len(binaries_after)}")

        # Perform cleanup
        print("\nPerforming cleanup...")
        cleaned_count = await manager.cleanup_old_versions(keep_count=1)
        print(f"Cleaned up {cleaned_count} old versions")

        # Final status
        final_status = await manager.get_status()
        print(f"Final storage usage: {final_status['total_size_mb']:.1f} MB")

        return manager

    finally:
        await manager.stop()


async def optimized_configurations_example():
    """Example: Using optimized configurations for different use cases."""

    use_cases = ['development', 'testing', 'production', 'minimal']

    for use_case in use_cases:
        print(f"\n=== {use_case.upper()} Configuration ===")

        # Get optimized configuration
        config = get_optimized_config_for_use_case(use_case)

        print(f"Storage directory: {config.storage_directory}")
        print(f"Max concurrent downloads: {config.max_concurrent_downloads}")
        print(f"Download timeout: {config.download_timeout}s")
        print(f"Verify checksums: {config.verify_checksums}")
        print(f"Auto cleanup: {config.auto_cleanup}")
        print(f"Max storage: {config.max_storage_gb} GB")
        print(f"Keep versions: {config.keep_versions}")

        # Create manager with this configuration
        manager = CustomBinaryManager(config=config)

        try:
            await manager.start()

            # Try to install a binary
            try:
                binary = await manager.get_binary(
                    binary_type=BinaryType.CHROMIUM,
                    auto_install=True
                )

                print(f"✓ Binary installed: {binary.executable_path}")
                print(f"  Version: {binary.version}")
                print(f"  Size: {binary.size / (1024*1024):.1f} MB")

            except Exception as e:
                print(f"✗ Failed to install binary: {str(e)}")

        finally:
            await manager.stop()


async def batch_operations_example():
    """Example: Batch operations with multiple binaries."""

    manager = CustomBinaryManager()

    def batch_progress_callback(progress: DownloadProgress):
        print(f"[{progress.url.split('/')[-1]}] "
              f"{progress.progress_percentage:.1f}% - "
              f"{progress.speed_mb_per_sec:.1f} MB/s")

    try:
        await manager.start()

        # Prepare batch installation
        binary_types = [BinaryType.CHROMIUM, BinaryType.FIREFOX]

        print("Starting batch installation...")

        # Install binaries concurrently
        install_tasks = []
        for binary_type in binary_types:
            task = asyncio.create_task(
                manager.install_binary(
                    binary_type=binary_type,
                    version="latest",
                    progress_callback=batch_progress_callback
                )
            )
            install_tasks.append(task)

        # Wait for all installations to complete
        results = await asyncio.gather(*install_tasks, return_exceptions=True)

        # Process results
        successful_installations = []
        failed_installations = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"✗ {binary_types[i].value} failed: {str(result)}")
                failed_installations.append(binary_types[i])
            else:
                print(f"✓ {result.binary_type.value} installed successfully")
                successful_installations.append(result)

        # Summary
        print(f"\nBatch Installation Summary:")
        print(f"Successful: {len(successful_installations)}")
        print(f"Failed: {len(failed_installations)}")

        # List all installed binaries
        all_binaries = await manager.list_binaries(status=BinaryStatus.INSTALLED)
        print(f"Total installed binaries: {len(all_binaries)}")

        return manager

    finally:
        await manager.stop()


async def error_handling_and_recovery_example():
    """Example: Error handling and recovery mechanisms."""

    manager = CustomBinaryManager()

    try:
        await manager.start()

        # Try to install a binary with invalid version
        print("Testing error handling with invalid version...")
        try:
            binary = await manager.install_binary(
                binary_type=BinaryType.CHROMIUM,
                version="invalid.version.number.12345"
            )
            print("This should not succeed")
        except Exception as e:
            print(f"✓ Expected error caught: {str(e)}")

        # Try to get non-existent binary without auto-install
        print("\nTesting non-existent binary access...")
        try:
            binary = await manager.get_binary(
                binary_type=BinaryType.CHROME,
                version="non.existent.version",
                auto_install=False
            )
            print("This should not succeed")
        except ValueError as e:
            print(f"✓ Expected error caught: {str(e)}")

        # Test recovery with valid installation
        print("\nTesting recovery with valid installation...")
        try:
            binary = await manager.get_binary(
                binary_type=BinaryType.CHROMIUM,
                auto_install=True
            )
            print(f"✓ Recovery successful: {binary.executable_path}")
        except Exception as e:
            print(f"✗ Recovery failed: {str(e)}")

        # Test status checking
        print("\nTesting status reporting...")
        status = await manager.get_status()
        print(f"Manager running: {status['running']}")
        print(f"Total binaries: {status['total_binaries']}")
        print(f"Status breakdown: {status['status_counts']}")

        return manager

    finally:
        await manager.stop()


async def monitor_and_maintenance_example():
    """Example: Monitoring and maintenance operations."""

    manager = CustomBinaryManager()

    try:
        await manager.start()

        # Install a few binaries for monitoring
        print("Installing binaries for monitoring demo...")

        binary_types = [BinaryType.CHROMIUM, BinaryType.FIREFOX]

        for binary_type in binary_types:
            try:
                await manager.install_binary(binary_type=binary_type, version="latest")
                print(f"✓ Installed {binary_type.value}")
            except Exception as e:
                print(f"✗ Failed to install {binary_type.value}: {str(e)}")

        # Monitor usage over time
        print("\nSimulating usage...")
        binaries = await manager.list_binaries(status=BinaryStatus.INSTALLED)

        for i in range(3):
            for binary in binaries:
                # Simulate usage by getting the binary
                await manager.get_binary(
                    binary_type=binary.binary_type,
                    version=binary.version,
                    auto_install=False
                )

            print(f"Usage cycle {i+1} completed")
            await asyncio.sleep(1)  # Small delay

        # Show usage statistics
        print("\nUsage Statistics:")
        for binary in binaries:
            info = await manager.get_binary_info(
                f"{binary.binary_type.value}_{binary.version}_{binary.platform.value}_{binary.architecture.value}"
            )
            if info:
                print(f"  {binary.binary_type.value}: Used {info.usage_count} times, "
                      f"last used: {info.last_used}")

        # Perform maintenance
        print("\nPerforming maintenance tasks...")

        # Check for corrupted binaries
        all_binaries = await manager.list_binaries()
        corrupted_count = 0

        for binary in all_binaries:
            if binary.status == BinaryStatus.CORRUPTED:
                print(f"Found corrupted binary: {binary.binary_type.value}")
                corrupted_count += 1

        if corrupted_count == 0:
            print("✓ No corrupted binaries found")

        # Perform cleanup if needed
        cleaned_count = await manager.cleanup_old_versions()
        print(f"✓ Cleaned up {cleaned_count} old versions")

        # Final status report
        final_status = await manager.get_status()
        print(f"\nFinal Status Report:")
        print(f"  Total binaries: {final_status['total_binaries']}")
        print(f"  Storage used: {final_status['total_size_mb']:.1f} MB")
        print(f"  Status breakdown: {final_status['status_counts']}")

        return manager

    finally:
        await manager.stop()


async def main():
    """Run all examples."""

    print("=== Custom Binary Manager Examples ===\n")

    examples = [
        ("Basic Manager Usage", basic_binary_manager_example),
        ("Configuration Management", configuration_management_example),
        ("Multi-Binary Installation", multi_binary_installation_example),
        ("Binary Validation", binary_validation_example),
        ("Update and Cleanup", binary_update_and_cleanup_example),
        ("Optimized Configurations", optimized_configurations_example),
        ("Batch Operations", batch_operations_example),
        ("Error Handling", error_handling_and_recovery_example),
        ("Monitor and Maintenance", monitor_and_maintenance_example)
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