"""
Examples of using the Advanced Network Obfuscator.

This module provides example code demonstrating how to use the NetworkObfuscator
and its components for comprehensive network-level stealth.
"""

import asyncio
import logging
from typing import List

from .obfuscator import NetworkObfuscator, ObfuscationConfig, ObfuscationStatus
from .tls_fingerprint import TLSFingerprintManager, TLSClientHelloBuilder
from .http2_rewriter import HTTP2SettingsManager, HTTP2HeaderRewriter
from .proxy_integration import ProxyIntegrationManager, ProxyIntegrationConfig
from ..core.profiles import BrowserProfile, BrowserType, OperatingSystem

logger = logging.getLogger(__name__)


async def basic_network_obfuscator_example():
    """Example: Basic Network Obfuscator usage."""

    print("=== Basic Network Obfuscator Example ===\n")

    # Create obfuscator with default configuration
    config = ObfuscationConfig(
        proxy_enabled=True,
        proxy_port=8080,
        tls_obfuscation_enabled=True,
        http2_obfuscation_enabled=True,
        fingerprint_service_url="http://localhost:8000"
    )

    obfuscator = NetworkObfuscator(config)

    try:
        print("1. Starting network obfuscation...")

        # Create a sample browser profile
        profile = BrowserProfile(
            profile_id="example_profile",
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS,
            version="120.0.0.0"
        )

        # Start obfuscation
        proxy_url = await obfuscator.start(profile)
        print(f"   Network obfuscation started at: {proxy_url}")

        # Get status
        status = await obfuscator.get_status()
        print(f"   Status: {status['status']}")
        print(f"   Uptime: {status['uptime_seconds']:.1f}s")
        print(f"   Profile ID: {status['profile_id']}")

        # Rotate TLS fingerprint
        print("\n2. Rotating TLS fingerprint...")
        rotation_success = await obfuscator.rotate_tls_fingerprint()
        print(f"   TLS fingerprint rotated: {rotation_success}")
        print(f"   Total TLS fingerprints rotated: {status['metrics']['tls_fingerprints_rotated']}")

        return obfuscator

    finally:
        print("\n3. Stopping network obfuscation...")
        await obfuscator.stop()
        print("   Network obfuscation stopped")


async def advanced_configuration_example():
    """Example: Advanced configuration with custom settings."""

    print("=== Advanced Configuration Example ===\n")

    # Create advanced configuration
    config = ObfuscationConfig(
        proxy_enabled=True,
        proxy_port=8081,
        proxy_host="127.0.0.1",
        proxy_startup_timeout=20,
        proxy_health_check_interval=3.0,

        tls_obfuscation_enabled=True,
        tls_fingerprint_rotation_enabled=True,
        tls_fingerprint_rotation_interval=30,  # 30 seconds for demo

        http2_obfuscation_enabled=True,
        http2_settings_randomization=True,

        fingerprint_service_url="http://localhost:8000",
        fingerprint_cache_enabled=True,
        fingerprint_cache_ttl=600,  # 10 minutes

        connection_pool_size=50,
        max_concurrent_requests=25,
        request_timeout=15,

        metrics_enabled=True,
        health_check_enabled=True
    )

    print("1. Advanced Configuration:")
    print(f"   Proxy Port: {config.proxy_port}")
    print(f"   TLS Rotation Interval: {config.tls_fingerprint_rotation_interval}s")
    print(f"   Connection Pool Size: {config.connection_pool_size}")
    print(f"   Max Concurrent Requests: {config.max_concurrent_requests}")
    print(f"   Health Check Interval: {config.proxy_health_check_interval}s")

    obfuscator = NetworkObfuscator(config)

    # Add status callback
    def status_callback(status: ObfuscationStatus):
        print(f"   Status changed: {status.value}")

    def error_callback(error: Exception):
        print(f"   Error occurred: {str(error)}")

    obfuscator.add_status_callback(status_callback)
    obfuscator.add_error_callback(error_callback)

    try:
        print("\n2. Starting with advanced configuration...")
        profile = BrowserProfile(
            profile_id="advanced_example",
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS
        )

        proxy_url = await obfuscator.start(profile)
        print(f"   Started at: {proxy_url}")

        # Monitor for a short period to see callbacks
        print("\n3. Monitoring for 15 seconds...")
        await asyncio.sleep(15)

        # Get detailed status
        status = await obfuscator.get_status()
        print(f"\n4. Final Status:")
        print(f"   Status: {status['status']}")
        print(f"   Uptime: {status['uptime_seconds']:.1f}s")
        print(f"   Total Requests: {status['metrics']['total_requests']}")
        print(f"   Success Rate: {status['metrics']['success_rate']:.1f}%")

        return obfuscator

    finally:
        await obfuscator.stop()


async def tls_fingerprint_management_example():
    """Example: TLS fingerprint management and generation."""

    print("=== TLS Fingerprint Management Example ===\n")

    # Initialize TLS fingerprint manager
    tls_manager = TLSFingerprintManager()

    print("1. Available TLS Fingerprint Profiles:")
    profiles = tls_manager.list_profiles()
    for profile_id in profiles:
        profile = tls_manager.get_profile(profile_id)
        print(f"   - {profile.name} ({profile.browser_type} {profile.browser_version} on {profile.operating_system})")

    print("\n2. Generating Custom TLS Fingerprints:")

    # Generate fingerprints for different browsers
    browsers = [
        ("chrome", "120.0.0.0", "windows"),
        ("firefox", "121.0.0.0", "windows"),
        ("safari", "17.0.0.0", "macos")
    ]

    for browser_type, version, os in browsers:
        fingerprint = tls_manager.generate_fingerprint(
            browser_type=browser_type,
            browser_version=version,
            operating_system=os,
            randomize=True
        )
        print(f"   {browser_type.title()} {version} on {os.title()}:")
        print(f"     Fingerprint ID: {fingerprint.id}")
        print(f"     JA3 Hash: {fingerprint.ja3_hash}")
        print(f"     Cipher Suites: {len(fingerprint.cipher_suites)}")
        print(f"     Extensions: {len(fingerprint.extensions)}")

    print("\n3. TLS ClientHello Builder:")
    client_hello_builder = TLSClientHelloBuilder(tls_manager)

    # Build ClientHello for Chrome
    chrome_fingerprint = tls_manager.generate_fingerprint("chrome", "120.0.0.0", "windows")
    client_hello = client_hello_builder.build_client_hello(chrome_fingerprint)

    print("   Chrome ClientHello Configuration:")
    print(f"     TLS Version: {client_hello['version']}")
    print(f"     Cipher Suites: {client_hello['cipher_suites'][:3]}...")  # Show first 3
    print(f"     ALPN Protocols: {client_hello['alpn_protocols']}")
    print(f"     Key Share Groups: {client_hello['key_share_groups']}")

    print("\n4. Generating ClientHello Variants:")
    variants = client_hello_builder.generate_client_hello_variants(chrome_fingerprint, count=3)
    print(f"   Generated {len(variants)} ClientHello variants")
    for i, variant in enumerate(variants):
        print(f"     Variant {i+1}: {len(variant['cipher_suites'])} cipher suites, "
              f"{len(variant['extensions'])} extensions")


async def http2_settings_management_example():
    """Example: HTTP/2 settings management and header rewriting."""

    print("=== HTTP/2 Settings Management Example ===\n")

    # Initialize HTTP/2 settings manager
    http2_manager = HTTP2SettingsManager()

    print("1. Browser-specific HTTP/2 Settings:")
    browsers = ["chrome_120", "firefox_121", "safari_17", "edge_120"]

    for browser_id in browsers:
        settings = http2_manager.get_settings(
            browser_type=browser_id.split('_')[0],
            browser_version=browser_id.split('_')[1]
        )
        print(f"   {browser_id}:")
        print(f"     Max Concurrent Streams: {settings.max_concurrent_streams}")
        print(f"     Initial Window Size: {settings.initial_window_size}")
        print(f"     Max Frame Size: {settings.max_frame_size}")
        print(f"     Enable Push: {settings.enable_push}")

    print("\n2. Custom HTTP/2 Settings Generation:")

    # Generate custom settings for different performance levels
    performance_levels = ["minimal", "balanced", "maximum"]

    for level in performance_levels:
        custom_settings = http2_manager.generate_custom_settings(
            performance_level=level,
            randomize=True
        )
        print(f"   {level.title()} Performance:")
        print(f"     Max Concurrent Streams: {custom_settings.max_concurrent_streams}")
        print(f"     Initial Window Size: {custom_settings.initial_window_size}")
        print(f"     Header Table Size: {custom_settings.header_table_size}")
        print(f"     Enable Push: {custom_settings.enable_push}")

    print("\n3. HTTP/2 Header Rewriting:")
    header_rewriter = HTTP2HeaderRewriter(http2_manager)

    # Create header configuration for Chrome
    header_config = header_rewriter.create_header_config(
        browser_type="chrome",
        browser_version="120",
        custom_headers={
            "x-custom-header": "test-value",
            "x-automation-test": "true"
        }
    )

    # Original headers
    original_headers = {
        ":method": "GET",
        ":path": "/",
        ":scheme": "https",
        ":authority": "example.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "connection": "keep-alive",
        "upgrade-insecure-requests": "1"
    }

    # Rewrite headers
    rewritten_headers = header_rewriter.rewrite_headers(
        original_headers=original_headers,
        config=header_config,
        randomize_order=True
    )

    print("   Header Configuration:")
    print(f"     Compression Enabled: {header_config.compression_enabled}")
    print(f"     Huffman Encoding: {header_config.huffman_encoding}")
    print(f"     Custom Headers: {list(header_config.custom_headers.keys())}")

    print("\n   Rewritten Headers:")
    for name, value in rewritten_headers[:10]:  # Show first 10
        print(f"     {name}: {value}")
    if len(rewritten_headers) > 10:
        print(f"     ... and {len(rewritten_headers) - 10} more headers")

    print("\n4. Stealth Optimization:")
    stealth_config = header_rewriter.optimize_for_stealth(
        base_config=header_config,
        target_site="google.com"
    )

    print("   Optimized for Google:")
    print(f"     Removed Headers: {stealth_config.removed_headers}")
    print(f"     Custom Headers: {list(stealth_config.custom_headers.keys())}")
    print(f"     Compression Enabled: {stealth_config.compression_enabled}")


async def proxy_integration_example():
    """Example: Advanced proxy integration with load balancing."""

    print("=== Proxy Integration Example ===\n")

    # Create proxy integration configuration
    config = ProxyIntegrationConfig(
        max_connections_per_proxy=50,
        connection_timeout=30,
        health_check_interval=10.0,
        load_balancing_strategy="least_connections",
        enable_failover=True,
        enable_metrics=True
    )

    proxy_integration = ProxyIntegrationManager(config)

    print("1. Proxy Integration Configuration:")
    print(f"   Max Connections per Proxy: {config.max_connections_per_proxy}")
    print(f"   Load Balancing Strategy: {config.load_balancing_strategy}")
    print(f"   Failover Enabled: {config.enable_failover}")
    print(f"   Health Check Interval: {config.health_check_interval}s")

    # Add callbacks
    def health_callback(proxy_id: str, status):
        print(f"   Proxy {proxy_id} health: {status.value}")

    def request_callback(request_info):
        print(f"   Request via {request_info['proxy_id']}: "
              f"{'Success' if request_info['success'] else 'Failed'} "
              f"({request_info['duration']:.3f}s)")

    proxy_integration.add_proxy_health_callback(health_callback)
    proxy_integration.add_request_callback(request_callback)

    print("\n2. Simulating Proxy Management:")

    # Note: This is a simulation since we don't have actual proxy binaries
    print("   (Note: This is a simulation - actual proxy binaries would be required)")

    # Simulate adding proxies
    proxy_configs = [
        ("proxy_1", 8080, "Chrome on Windows"),
        ("proxy_2", 8081, "Firefox on Windows"),
        ("proxy_3", 8082, "Chrome on macOS")
    ]

    simulated_proxies = []
    for proxy_id, port, description in proxy_configs:
        print(f"   Simulating addition of {proxy_id} at port {port} ({description})")
        # In real implementation:
        # proxy_id = await proxy_integration.add_proxy(proxy_config, profile)
        simulated_proxies.append(proxy_id)

    print("\n3. Starting Health Monitoring:")
    await proxy_integration.start_health_monitoring()

    # Simulate health checks
    print("   Simulating health checks...")
    await asyncio.sleep(2)

    # Get status
    status = await proxy_integration.get_status()
    print(f"\n4. Integration Status:")
    print(f"   Total Proxies: {status['total_proxies']}")
    print(f"   Healthy Proxies: {status['healthy_proxies']}")
    print(f"   Degraded Proxies: {status['degraded_proxies']}")
    print(f"   Load Balancing Strategy: {status['load_balancing_strategy']}")
    print(f"   Health Monitoring Active: {status['health_monitoring_active']}")

    print("\n5. Load Balancing Demo:")

    # Simulate request distribution
    for i in range(5):
        # In real implementation:
        # proxy_id = await proxy_integration.get_proxy_for_request(profile)
        proxy_id = simulated_proxies[i % len(simulated_proxies)]
        print(f"   Request {i+1} -> {proxy_id}")

        # Simulate request execution
        # result = await proxy_integration.execute_request(proxy_id, request_func)
        await asyncio.sleep(0.1)

    # Final metrics
    final_status = await proxy_integration.get_status()
    print(f"\n6. Final Metrics:")
    print(f"   Total Requests: {final_status['metrics']['total_requests']}")
    print(f"   Proxy Switches: {final_status['metrics']['proxy_switches']}")
    print(f"   Health Checks: {final_status['metrics']['health_checks']}")

    # Cleanup
    await proxy_integration.cleanup()
    print("\n7. Proxy integration cleaned up")


async def comprehensive_obfuscation_example():
    """Example: Comprehensive network obfuscation with all components."""

    print("=== Comprehensive Network Obfuscation Example ===\n")

    # Create comprehensive configuration
    config = ObfuscationConfig(
        proxy_enabled=True,
        proxy_port=8080,
        tls_obfuscation_enabled=True,
        tls_fingerprint_rotation_enabled=True,
        tls_fingerprint_rotation_interval=10,  # Short for demo
        http2_obfuscation_enabled=True,
        fingerprint_service_url="http://localhost:8000",
        metrics_enabled=True,
        health_check_enabled=True
    )

    obfuscator = NetworkObfuscator(config)

    # Add comprehensive monitoring
    def status_monitor(status: ObfuscationStatus):
        print(f"[MONITOR] Status: {status.value}")

    def error_monitor(error: Exception):
        print(f"[MONITOR] Error: {str(error)}")

    obfuscator.add_status_callback(status_monitor)
    obfuscator.add_error_callback(error_monitor)

    try:
        print("1. Creating comprehensive browser profile...")

        # Create detailed browser profile
        from ..core.profiles import ScreenResolution, NavigatorProperties, HTTPHeaders, TLSFingerprint, HTTP2Settings

        profile = BrowserProfile(
            profile_id="comprehensive_example",
            browser_type=BrowserType.CHROME,
            operating_system=OperatingSystem.WINDOWS,
            version="120.0.0.0",
            screen=ScreenResolution(width=1920, height=1080),
            navigator=NavigatorProperties(
                hardware_concurrency=8,
                device_memory=8.0,
                platform="Win32",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ),
            headers=HTTPHeaders(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                accept_language="en-US,en;q=0.9",
                accept_encoding="gzip, deflate, br"
            ),
            tls_fingerprint=TLSFingerprint(
                id="chrome_120_windows",
                utls_config={"client": "chrome", "version": "120", "platform": "windows"}
            ),
            http2_settings=HTTP2Settings(
                max_concurrent_streams=1000,
                initial_window_size=65535
            )
        )

        print(f"   Profile ID: {profile.profile_id}")
        print(f"   Browser: {profile.browser_type} {profile.version}")
        print(f"   OS: {profile.operating_system}")
        print(f"   Screen: {profile.screen.width}x{profile.screen.height}")

        print("\n2. Starting comprehensive obfuscation...")
        proxy_url = await obfuscator.start(profile)
        print(f"   Started successfully at: {proxy_url}")

        print("\n3. Demonstrating automatic TLS rotation...")

        # Monitor TLS rotation for 25 seconds (rotation interval = 10s)
        start_time = asyncio.get_event_loop().time()
        initial_rotations = 0

        while (asyncio.get_event_loop().time() - start_time) < 25:
            await asyncio.sleep(2)
            current_status = await obfuscator.get_status()
            current_rotations = current_status['metrics']['tls_fingerprints_rotated']

            if current_rotations > initial_rotations:
                print(f"   TLS rotation detected! Total rotations: {current_rotations}")
                initial_rotations = current_rotations

        print("\n4. Manual profile reconfiguration...")

        # Create new profile for reconfiguration
        new_profile = BrowserProfile(
            profile_id="reconfigured_profile",
            browser_type=BrowserType.FIREFOX,
            operating_system=OperatingSystem.WINDOWS,
            version="121.0.0.0",
            screen=profile.screen,  # Keep same screen
            navigator=profile.navigator,  # Keep same navigator
            headers=profile.headers,  # Keep same headers
            tls_fingerprint=TLSFingerprint(
                id="firefox_121_windows",
                utls_config={"client": "firefox", "version": "121", "platform": "windows"}
            ),
            http2_settings=HTTP2Settings(
                max_concurrent_streams=100,  # Firefox typically uses fewer streams
                initial_window_size=65536
            )
        )

        new_proxy_url = await obfuscator.reconfigure(new_profile)
        print(f"   Reconfigured with Firefox profile")
        print(f"   New proxy URL: {new_proxy_url}")

        print("\n5. Final comprehensive status...")
        final_status = await obfuscator.get_status()

        print(f"   Status: {final_status['status']}")
        print(f"   Uptime: {final_status['uptime_seconds']:.1f}s")
        print(f"   Current Profile: {final_status['profile_id']}")
        print(f"   Total Requests: {final_status['metrics']['total_requests']}")
        print(f"   Success Rate: {final_status['metrics']['success_rate']:.1f}%")
        print(f"   TLS Fingerprints Rotated: {final_status['metrics']['tls_fingerprints_rotated']}")
        print(f"   Average Response Time: {final_status['metrics']['average_response_time']:.3f}s")

        # Component status
        print("\n6. Component Status:")
        components = final_status['components']
        print(f"   Proxy Manager: {'✓' if components['proxy_manager'] else '✗'}")
        print(f"   Fingerprint Client: {'✓' if components['fingerprint_client'] else '✗'}")
        print(f"   Binary Manager: {'✓' if components['binary_manager'] else '✗'}")

        if 'proxy_status' in final_status:
            proxy_status = final_status['proxy_status']
            print(f"   Proxy Process Status: {proxy_status.get('status', 'unknown')}")
            print(f"   Proxy Uptime: {proxy_status.get('uptime_seconds', 0):.1f}s")

        return obfuscator

    finally:
        print("\n7. Stopping comprehensive obfuscation...")
        await obfuscator.stop()
        print("   Comprehensive obfuscation stopped successfully")


async def main():
    """Run all examples."""

    print("=== Advanced Network Obfuscator Examples ===\n")

    examples = [
        ("Basic Network Obfuscator", basic_network_obfuscator_example),
        ("Advanced Configuration", advanced_configuration_example),
        ("TLS Fingerprint Management", tls_fingerprint_management_example),
        ("HTTP/2 Settings Management", http2_settings_management_example),
        ("Proxy Integration", proxy_integration_example),
        ("Comprehensive Obfuscation", comprehensive_obfuscation_example)
    ]

    for name, example_func in examples:
        print(f"\n{'='*60}")
        print(f"{name}")
        print('='*60)

        try:
            await example_func()
        except Exception as e:
            print(f"Example failed: {str(e)}")
            logger.exception(f"Example {name} failed")

        print(f"\n{'='*60}")
        print(f"Completed: {name}")
        print('='*60)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run examples
    asyncio.run(main())