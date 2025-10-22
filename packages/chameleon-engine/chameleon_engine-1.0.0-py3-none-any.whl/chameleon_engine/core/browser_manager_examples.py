"""
Examples of using the Advanced Browser Manager.

This module provides example code demonstrating how to use the BrowserManager
for stealth web browsing with network obfuscation.
"""

import asyncio
import logging
from typing import List

from .browser_manager import BrowserManager, BrowserLaunchConfig, BrowserManagerStatus
from .profiles import BrowserProfile, BrowserType, OperatingSystem, ScreenResolution, NavigatorProperties, HTTPHeaders, TLSFingerprint, HTTP2Settings

logger = logging.getLogger(__name__)


async def basic_browser_manager_example():
    """Example: Basic Browser Manager usage."""

    print("=== Basic Browser Manager Example ===\n")

    # Create a simple browser profile
    profile = BrowserProfile(
        profile_id="basic_example",
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
            accept_language="en-US,en;q=0.9"
        ),
        tls_fingerprint=TLSFingerprint(id="chrome_120_windows"),
        http2_settings=HTTP2Settings()
    )

    # Create browser manager
    manager = BrowserManager(profile=profile)

    # Add status callback
    def status_callback(status: BrowserManagerStatus):
        print(f"   Status: {status.value}")

    manager.add_status_callback(status_callback)

    try:
        print("1. Starting browser manager...")
        context_id = await manager.start()
        print(f"   Browser started with context: {context_id}")

        # Get status
        status = await manager.get_status()
        print(f"   Status: {status['status']}")
        print(f"   Browser Type: {status['browser_type']}")
        print(f"   Proxy URL: {status['proxy_url']}")
        print(f"   Binary Path: {status['binary_path']}")

        print("\n2. Creating new page...")
        page_id = await manager.new_page()
        print(f"   Created page: {page_id}")

        print("\n3. Navigating to example.com...")
        success = await manager.navigate(page_id, "https://example.com")
        print(f"   Navigation successful: {success}")

        # Take screenshot
        print("\n4. Taking screenshot...")
        screenshot = await manager.take_screenshot(page_id, "example.png")
        print(f"   Screenshot taken: {len(screenshot)} bytes")

        # Execute JavaScript
        print("\n5. Executing JavaScript...")
        title = await manager.execute_script(page_id, "return document.title;")
        print(f"   Page title: {title}")

        return manager

    finally:
        print("\n6. Stopping browser manager...")
        await manager.stop()
        print("   Browser manager stopped")


async def advanced_configuration_example():
    """Example: Advanced Browser Manager configuration."""

    print("=== Advanced Configuration Example ===\n")

    # Create advanced browser profile
    profile = BrowserProfile(
        profile_id="advanced_example",
        browser_type=BrowserType.FIREFOX,
        operating_system=OperatingSystem.WINDOWS,
        version="121.0.0.0",
        screen=ScreenResolution(width=1366, height=768),
        navigator=NavigatorProperties(
            hardware_concurrency=4,
            device_memory=4.0,
            platform="Win32",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            languages=["en-US", "en"]
        ),
        headers=HTTPHeaders(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            accept_language="en-US,en;q=0.5",
            accept_encoding="gzip, deflate, br"
        ),
        tls_fingerprint=TLSFingerprint(id="firefox_121_windows"),
        http2_settings=HTTP2Settings(max_concurrent_streams=100)
    )

    # Create advanced launch configuration
    launch_config = BrowserLaunchConfig(
        headless=True,
        devtools=False,
        slow_mo=0,
        timeout=60000,
        ignore_https_errors=True,
        bypass_csp=True,
        java_script_enabled=True,
        hide_captcha=True,
        hide_webgl=False,
        randomize_canvas=True,
        randomize_audio_context=False,
        randomize_timezone=True,
        randomize_language=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--disable-default-browser-check"
        ]
    )

    print("1. Advanced Configuration:")
    print(f"   Browser: {profile.browser_type.value} {profile.version}")
    print(f"   Screen: {profile.screen.width}x{profile.screen.height}")
    print(f"   Hardware: {profile.navigator.hardware_concurrency} cores, {profile.navigator.device_memory}GB RAM")
    print(f"   Headless: {launch_config.headless}")
    print(f"   Randomize Canvas: {launch_config.randomize_canvas}")
    print(f"   Randomize Timezone: {launch_config.randomize_timezone}")

    manager = BrowserManager(profile=profile, launch_config=launch_config)

    # Add monitoring callbacks
    def status_monitor(status: BrowserManagerStatus):
        print(f"   [MONITOR] Status: {status.value}")

    def error_monitor(error: Exception):
        print(f"   [MONITOR] Error: {str(error)}")

    def page_monitor(page, event: str, data=None):
        print(f"   [MONITOR] Page {event}: {data.get('url', 'N/A') if data else 'N/A'}")

    manager.add_status_callback(status_monitor)
    manager.add_error_callback(error_monitor)
    manager.add_page_callback(page_monitor)

    try:
        print("\n2. Starting with advanced configuration...")
        context_id = await manager.start()
        print(f"   Started with context: {context_id}")

        # Create multiple pages
        print("\n3. Creating multiple pages...")
        pages = []
        for i in range(3):
            page_id = await manager.new_page()
            pages.append(page_id)
            print(f"   Created page {i+1}: {page_id}")

        # Navigate each page to different sites
        sites = [
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers",
            "https://httpbin.org/ip"
        ]

        for i, (page_id, site) in enumerate(zip(pages, sites)):
            print(f"\n4. Navigating page {i+1} to {site}...")
            success = await manager.navigate(page_id, site)
            print(f"   Navigation successful: {success}")

            # Wait for page to load
            await asyncio.sleep(2)

            # Check page content
            content = await manager.execute_script(page_id, "return document.body.innerText;")
            print(f"   Content length: {len(content)} characters")

        # Get final status
        final_status = await manager.get_status()
        print(f"\n5. Final Status:")
        print(f"   Total Pages: {final_status['metrics']['total_pages']}")
        print(f"   Active Pages: {final_status['metrics']['active_pages']}")
        print(f"   Success Rate: {final_status['metrics']['success_rate']:.1f}%")
        print(f"   Average Load Time: {final_status['metrics']['average_page_load_time']:.3f}s")

        return manager

    finally:
        print("\n6. Stopping advanced browser manager...")
        await manager.stop()
        print("   Advanced browser manager stopped")


async def stealth_browsing_example():
    """Example: Stealth browsing with advanced anti-detection."""

    print("=== Stealth Browsing Example ===\n")

    # Create stealth profile
    profile = BrowserProfile(
        profile_id="stealth_example",
        browser_type=BrowserType.CHROME,
        operating_system=OperatingSystem.WINDOWS,
        version="120.0.0.0",
        screen=ScreenResolution(width=1920, height=1080),
        viewport=ScreenResolution(width=1366, height=768),  # Different viewport
        navigator=NavigatorProperties(
            hardware_concurrency=6,
            device_memory=6.0,
            platform="Win32",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            languages=["en-US", "en"],
            do_not_track="1",
            cookie_enabled=True,
            on_line=True
        ),
        headers=HTTPHeaders(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            accept_language="en-US,en;q=0.9",
            accept_encoding="gzip, deflate, br, zstd",
            sec_ch_ua='"Google Chrome";v="120", "Chromium";v="120", "Not=A?Brand";v="99"',
            sec_ch_ua_mobile="?0",
            sec_ch_ua_platform='"Windows"',
            dnt="1",
            upgrade_insecure_requests="1",
            connection="keep-alive"
        ),
        tls_fingerprint=TLSFingerprint(
            id="chrome_120_windows",
            utls_config={
                "client": "chrome",
                "version": "120",
                "platform": "windows"
            }
        ),
        http2_settings=HTTP2Settings(
            max_concurrent_streams=1000,
            initial_window_size=65535,
            enable_push=True
        )
    )

    # Create stealth launch configuration
    launch_config = BrowserLaunchConfig(
        headless=True,
        devtools=False,
        slow_mo=100,  # Small delay for human-like behavior
        timeout=60000,
        ignore_https_errors=True,
        bypass_csp=True,
        java_script_enabled=True,
        hide_captcha=True,
        hide_webgl=False,
        randomize_canvas=True,
        randomize_audio_context=True,
        randomize_timezone=True,
        randomize_language=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows"
        ]
    )

    print("1. Stealth Configuration:")
    print(f"   Profile ID: {profile.profile_id}")
    print(f"   Browser: {profile.browser_type.value} {profile.version}")
    print(f"   Screen vs Viewport: {profile.screen.width}x{profile.screen.height} vs {profile.viewport.width}x{profile.viewport.height}")
    print(f"   Do Not Track: {profile.navigator.do_not_track}")
    print(f"   Canvas Randomization: {launch_config.randomize_canvas}")
    print(f"   Audio Context Randomization: {launch_config.randomize_audio_context}")
    print(f"   Custom Arguments: {len(launch_config.args)}")

    manager = BrowserManager(profile=profile, launch_config=launch_config)

    # Add stealth monitoring
    def stealth_status_callback(status: BrowserManagerStatus):
        stealth_indicators = ["✓" if status == BrowserManagerStatus.RUNNING else "⏸"]
        print(f"   [STEALTH] Browser {stealth_indicators[0]} - {status.value}")

    def stealth_error_callback(error: Exception):
        print(f"   [STEALTH] ⚠️ Error: {str(error)}")

    manager.add_status_callback(stealth_status_callback)
    manager.add_error_callback(stealth_error_callback)

    try:
        print("\n2. Starting stealth browser...")
        context_id = await manager.start()
        print(f"   Stealth browser started: {context_id}")

        # Get detailed status
        status = await manager.get_status()
        print(f"\n3. Stealth Status:")
        print(f"   Network Obfuscation: {'✓' if status.get('obfuscation_status') else '✗'}")
        print(f"   Custom Binary: {'✓' if status['binary_path'] else '✗'}")
        print(f"   Proxy Integration: {'✓' if status['proxy_url'] else '✗'}")

        print("\n4. Testing stealth capabilities...")
        page_id = await manager.new_page()

        # Test 1: Fingerprint detection
        print("   Test 1: Checking navigator properties...")
        navigator_info = await manager.execute_script(page_id, """
            return {
                webdriver: navigator.webdriver,
                hardwareConcurrency: navigator.hardwareConcurrency,
                deviceMemory: navigator.deviceMemory,
                platform: navigator.platform,
                languages: navigator.languages,
                plugins: navigator.plugins.length
            };
        """)

        print(f"     WebDriver: {navigator_info['webdriver']} (should be undefined/false)")
        print(f"     Hardware Concurrency: {navigator_info['hardwareConcurrency']} cores")
        print(f"     Device Memory: {navigator_info['deviceMemory']} GB")
        print(f"     Platform: {navigator_info['platform']}")
        print(f"     Languages: {navigator_info['languages']}")
        print(f"     Plugins: {navigator_info['plugins']} (should be > 0)")

        # Test 2: Canvas fingerprinting
        print("\n   Test 2: Canvas fingerprint randomization...")
        canvas_hash_1 = await manager.execute_script(page_id, """
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillText('Browser fingerprint test', 2, 2);
            return canvas.toDataURL().slice(-50);
        """)

        await asyncio.sleep(0.1)  # Small delay

        canvas_hash_2 = await manager.execute_script(page_id, """
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillText('Browser fingerprint test', 2, 2);
            return canvas.toDataURL().slice(-50);
        """)

        canvas_different = canvas_hash_1 != canvas_hash_2
        print(f"     Canvas randomization: {'✓' if canvas_different else '✗'} (hashes should differ)")

        # Test 3: WebGL fingerprinting
        print("\n   Test 3: WebGL fingerprint consistency...")
        webgl_info = await manager.execute_script(page_id, """
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (!gl) return null;

            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            return {
                vendor: gl.getParameter(gl.VENDOR),
                renderer: gl.getParameter(gl.RENDERER),
                version: gl.getParameter(gl.VERSION)
            };
        """)

        if webgl_info:
            print(f"     WebGL Vendor: {webgl_info['vendor']}")
            print(f"     WebGL Renderer: {webgl_info['renderer']}")
            print(f"     WebGL Version: {webgl_info['version']}")

        # Test 4: Anti-bot detection
        print("\n   Test 4: Anti-bot detection bypass...")
        await manager.navigate(page_id, "https://bot.sannysoft.com/")
        await asyncio.sleep(3)

        # Check for bot detection indicators
        bot_detected = await manager.execute_script(page_id, """
            // Check for common bot detection indicators
            const indicators = {
                hasPhantom: !!window.callPhantom,
                hasWebdriver: !!window.webdriver,
                hasChromeRuntime: !!window.chrome && !!window.chrome.runtime,
                navigatorPermissions: 'permissions' in navigator,
                pluginsLength: navigator.plugins.length,
                languagesLength: navigator.languages.length
            };
            return indicators;
        """)

        print(f"     PhantomJS detected: {bot_detected['hasPhantom']} (should be false)")
        print(f"     WebDriver property: {bot_detected['hasWebdriver']} (should be false)")
        print(f"     Chrome runtime: {bot_detected['hasChromeRuntime']} (should be true)")
        print(f"     Permissions API: {bot_detected['navigatorPermissions']} (should be true)")
        print(f"     Plugins count: {bot_detected['pluginsLength']} (should be > 0)")
        print(f"     Languages count: {bot_detected['languagesLength']} (should be > 0)")

        # Calculate stealth score
        stealth_score = 0
        max_score = 7

        if not bot_detected['hasPhantom']:
            stealth_score += 1
        if not bot_detected['hasWebdriver']:
            stealth_score += 1
        if bot_detected['hasChromeRuntime']:
            stealth_score += 1
        if bot_detected['navigatorPermissions']:
            stealth_score += 1
        if bot_detected['pluginsLength'] > 0:
            stealth_score += 1
        if bot_detected['languagesLength'] > 0:
            stealth_score += 1
        if canvas_different:
            stealth_score += 1

        stealth_percentage = (stealth_score / max_score) * 100
        print(f"\n   Stealth Score: {stealth_score}/{max_score} ({stealth_percentage:.1f}%)")

        return manager

    finally:
        print("\n5. Stopping stealth browser...")
        await manager.stop()
        print("   Stealth browser stopped")


async def multi_browser_comparison_example():
    """Example: Comparing different browsers side by side."""

    print("=== Multi-Browser Comparison Example ===\n")

    # Define configurations for different browsers
    browser_configs = [
        {
            "name": "Chrome 120",
            "profile": BrowserProfile(
                profile_id="chrome_comparison",
                browser_type=BrowserType.CHROME,
                operating_system=OperatingSystem.WINDOWS,
                version="120.0.0.0",
                screen=ScreenResolution(width=1920, height=1080),
                navigator=NavigatorProperties(
                    hardware_concurrency=8,
                    device_memory=8.0,
                    platform="Win32",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            )
        },
        {
            "name": "Firefox 121",
            "profile": BrowserProfile(
                profile_id="firefox_comparison",
                browser_type=BrowserType.FIREFOX,
                operating_system=OperatingSystem.WINDOWS,
                version="121.0.0.0",
                screen=ScreenResolution(width=1920, height=1080),
                navigator=NavigatorProperties(
                    hardware_concurrency=8,
                    device_memory=8.0,
                    platform="Win32",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
                )
            )
        }
    ]

    managers = []
    pages = []

    try:
        print("1. Starting multiple browsers...")

        for i, config in enumerate(browser_configs):
            print(f"   Starting {config['name']}...")
            manager = BrowserManager(profile=config['profile'])

            # Add callback for this browser
            def create_callback(browser_name):
                def callback(status: BrowserManagerStatus):
                    print(f"     {browser_name}: {status.value}")
                return callback

            manager.add_status_callback(create_callback(config['name']))

            await manager.start()
            managers.append(manager)

            # Create page for each browser
            page_id = await manager.new_page()
            pages.append((manager, page_id, config['name']))

            print(f"     {config['name']} started with page: {page_id}")

        print(f"\n2. Created {len(managers)} browsers successfully")

        # Test each browser with the same site
        test_url = "https://httpbin.org/headers"
        print(f"\n3. Navigating all browsers to {test_url}...")

        results = []
        for manager, page_id, browser_name in pages:
            print(f"   Testing {browser_name}...")
            start_time = asyncio.get_event_loop().time()

            success = await manager.navigate(page_id, test_url)
            navigation_time = asyncio.get_event_loop().time() - start_time

            if success:
                # Get headers from the page
                headers = await manager.execute_script(page_id, """
                    return document.body.innerText;
                """)

                # Extract user agent from response
                user_agent = "Unknown"
                if "User-Agent" in headers:
                    for line in headers.split('\n'):
                        if 'User-Agent' in line:
                            user_agent = line.split(':', 1)[-1].strip().strip('"')
                            break

                results.append({
                    "browser": browser_name,
                    "navigation_time": navigation_time,
                    "user_agent": user_agent,
                    "success": True
                })

                print(f"     Navigation time: {navigation_time:.3f}s")
                print(f"     User-Agent: {user_agent[:50]}...")

            else:
                results.append({
                    "browser": browser_name,
                    "navigation_time": 0,
                    "user_agent": "Failed",
                    "success": False
                })
                print(f"     Navigation failed")

        print("\n4. Comparison Results:")
        print(f"{'Browser':<15} {'Time (s)':<10} {'User-Agent':<50}")
        print("-" * 80)

        for result in results:
            time_str = f"{result['navigation_time']:.3f}" if result['success'] else "Failed"
            ua_str = result['user_agent'][:47] + "..." if len(result['user_agent']) > 50 else result['user_agent']
            print(f"{result['browser']:<15} {time_str:<10} {ua_str:<50}")

        # Performance comparison
        successful_results = [r for r in results if r['success']]
        if successful_results:
            avg_time = sum(r['navigation_time'] for r in successful_results) / len(successful_results)
            fastest = min(successful_results, key=lambda x: x['navigation_time'])
            slowest = max(successful_results, key=lambda x: x['navigation_time'])

            print(f"\n5. Performance Analysis:")
            print(f"   Average navigation time: {avg_time:.3f}s")
            print(f"   Fastest browser: {fastest['browser']} ({fastest['navigation_time']:.3f}s)")
            print(f"   Slowest browser: {slowest['browser']} ({slowest['navigation_time']:.3f}s)")

        # Get status from all managers
        print(f"\n6. Final Status Summary:")
        total_pages = 0
        total_requests = 0

        for i, manager in enumerate(managers):
            status = await manager.get_status()
            browser_name = browser_configs[i]['name']
            print(f"   {browser_name}:")
            print(f"     Status: {status['status']}")
            print(f"     Pages: {status['metrics']['total_pages']}")
            print(f"     Success Rate: {status['metrics']['success_rate']:.1f}%")
            print(f"     Active Pages: {status['metrics']['active_pages']}")

            total_pages += status['metrics']['total_pages']

        print(f"\n7. Summary:")
        print(f"   Total browsers: {len(managers)}")
        print(f"   Total pages created: {total_pages}")
        print(f"   Successful navigations: {len(successful_results)}/{len(results)}")

        return managers

    finally:
        print("\n8. Stopping all browsers...")
        for i, manager in enumerate(managers):
            try:
                await manager.stop()
                print(f"   {browser_configs[i]['name']} stopped")
            except Exception as e:
                print(f"   Error stopping {browser_configs[i]['name']}: {str(e)}")


async def page_management_example():
    """Example: Advanced page management and monitoring."""

    print("=== Page Management Example ===\n")

    # Create browser profile
    profile = BrowserProfile(
        profile_id="page_management_example",
        browser_type=BrowserType.CHROME,
        operating_system=OperatingSystem.WINDOWS
    )

    manager = BrowserManager(profile=profile)

    # Add comprehensive monitoring
    def page_monitor(page, event: str, data=None):
        if event == "created":
            print(f"   Page created: {data or 'Unknown'}")
        elif event == "closed":
            print(f"   Page closed")
        elif event == "navigated":
            print(f"   Navigated to: {data.get('url', 'Unknown') if data else 'Unknown'} "
                  f"({data.get('response_status', 'N/A') if data else 'N/A'}) "
                  f"in {data.get('navigation_time', 0):.3f}s")
        elif event == "navigation_failed":
            print(f"   Navigation failed: {data.get('url', 'Unknown') if data else 'Unknown'} "
                  f"- {data.get('error', 'Unknown error') if data else 'Unknown error'}")

    def status_monitor(status: BrowserManagerStatus):
        print(f"   Status: {status.value}")

    manager.add_page_callback(page_monitor)
    manager.add_status_callback(status_monitor)

    try:
        print("1. Starting browser for page management...")
        context_id = await manager.start()
        print(f"   Browser started: {context_id}")

        print("\n2. Creating multiple pages...")
        pages = []

        # Create 5 pages
        for i in range(5):
            page_id = await manager.new_page()
            pages.append(page_id)
            print(f"   Created page {i+1}: {page_id}")
            await asyncio.sleep(0.5)  # Small delay between page creation

        print(f"\n3. Created {len(pages)} pages")

        # Different sites to navigate to
        sites = [
            "https://example.com",
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers",
            "https://httpbin.org/ip",
            "https://jsonplaceholder.typicode.com/posts/1"
        ]

        print("\n4. Navigating pages to different sites...")
        navigation_tasks = []

        for page_id, site in zip(pages, sites):
            task = asyncio.create_task(manager.navigate(page_id, site))
            navigation_tasks.append((page_id, site, task))

        # Wait for all navigations to complete
        for page_id, site, task in navigation_tasks:
            try:
                success = await task
                print(f"   {page_id} -> {site}: {'✓' if success else '✗'}")
            except Exception as e:
                print(f"   {page_id} -> {site}: ✗ ({str(e)[:50]}...)")

        print("\n5. Testing concurrent operations...")

        # Take screenshots of all pages concurrently
        print("   Taking screenshots...")
        screenshot_tasks = []
        for i, page_id in enumerate(pages):
            task = asyncio.create_task(manager.take_screenshot(page_id, f"screenshot_{i}.png"))
            screenshot_tasks.append((page_id, task))

        for page_id, task in screenshot_tasks:
            try:
                screenshot = await task
                print(f"   Screenshot taken for {page_id}: {len(screenshot)} bytes")
            except Exception as e:
                print(f"   Screenshot failed for {page_id}: {str(e)}")

        # Execute JavaScript on all pages
        print("\n   Executing JavaScript...")
        js_tasks = []
        for page_id in pages:
            task = asyncio.create_task(manager.execute_script(page_id, "return [document.title, document.URL];"))
            js_tasks.append((page_id, task))

        for page_id, task in js_tasks:
            try:
                title, url = await task
                print(f"   {page_id}: {title[:30]}... ({url})")
            except Exception as e:
                print(f"   JavaScript failed for {page_id}: {str(e)}")

        print("\n6. Managing page lifecycle...")

        # Close some pages
        pages_to_close = pages[:2]
        for page_id in pages_to_close:
            success = await manager.close_page(page_id)
            print(f"   Closed page {page_id}: {'✓' if success else '✗'}")
            if success:
                pages.remove(page_id)

        print(f"\n7. Remaining pages: {len(pages)}")

        # Create new pages to replace closed ones
        for _ in range(2):
            new_page_id = await manager.new_page()
            pages.append(new_page_id)
            print(f"   Created new page: {new_page_id}")

        # Get final status
        final_status = await manager.get_status()
        print(f"\n8. Final Page Management Status:")
        print(f"   Total Pages Created: {final_status['metrics']['total_pages']}")
        print(f"   Active Pages: {final_status['metrics']['active_pages']}")
        print(f"   Successful Navigations: {final_status['metrics']['successful_navigations']}")
        print(f"   Failed Navigations: {final_status['metrics']['failed_navigations']}")
        print(f"   Success Rate: {final_status['metrics']['success_rate']:.1f}%")
        print(f"   Average Load Time: {final_status['metrics']['average_page_load_time']:.3f}s")

        return manager

    finally:
        print("\n9. Stopping browser manager...")
        await manager.stop()
        print("   Browser manager stopped")


async def main():
    """Run all examples."""

    print("=== Advanced Browser Manager Examples ===\n")

    examples = [
        ("Basic Browser Manager", basic_browser_manager_example),
        ("Advanced Configuration", advanced_configuration_example),
        ("Stealth Browsing", stealth_browsing_example),
        ("Multi-Browser Comparison", multi_browser_comparison_example),
        ("Page Management", page_management_example)
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