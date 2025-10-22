"""
Advanced Browser Manager for Chameleon Engine.

This module provides comprehensive browser management capabilities integrating
Playwright automation with network obfuscation and custom binary management.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path

from playwright.async_api import (
    async_playwright, Browser, BrowserContext, Page, BrowserType as PlaywrightBrowserType,
    Playwright, Error as PlaywrightError
)

from .profiles import BrowserProfile, BrowserType, OperatingSystem
from ..network.obfuscator import NetworkObfuscator, ObfuscationConfig, ObfuscationStatus
from ..services.binary.manager import CustomBinaryManager, BinaryType
from ..services.fingerprint.client import FingerprintServiceClient

logger = logging.getLogger(__name__)


class BrowserManagerStatus(Enum):
    """Browser manager status values."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    RECONFIGURING = "reconfiguring"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class BrowserLaunchConfig:
    """Configuration for browser launch."""
    headless: bool = True
    devtools: bool = False
    slow_mo: int = 0
    timeout: int = 30000
    ignore_https_errors: bool = True
    bypass_csp: bool = True

    # Advanced options
    ignore_default_args: List[str] = field(default_factory=list)
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    java_script_enabled: bool = True

    # Stealth options
    hide_captcha: bool = True
    hide_webgl: bool = False
    randomize_canvas: bool = False
    randomize_audio_context: bool = False
    randomize_timezone: bool = True
    randomize_language: bool = True


@dataclass
class BrowserMetrics:
    """Browser performance and usage metrics."""
    start_time: Optional[datetime] = None
    total_pages: int = 0
    successful_navigations: int = 0
    failed_navigations: int = 0
    total_requests: int = 0
    blocked_requests: int = 0
    average_page_load_time: float = 0.0
    active_pages: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate navigation success rate."""
        if self.total_pages == 0:
            return 0.0
        return (self.successful_navigations / self.total_pages) * 100

    @property
    def uptime_seconds(self) -> float:
        """Calculate uptime in seconds."""
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()


class BrowserManager:
    """
    Advanced Browser Manager for Chameleon Engine.

    This class provides comprehensive browser management integrating Playwright
    automation with network obfuscation, custom binaries, and stealth features.
    """

    def __init__(
        self,
        profile: Optional[BrowserProfile] = None,
        launch_config: Optional[BrowserLaunchConfig] = None,
        obfuscation_config: Optional[ObfuscationConfig] = None
    ):
        """
        Initialize the Browser Manager.

        Args:
            profile: Browser profile to use
            launch_config: Browser launch configuration
            obfuscation_config: Network obfuscation configuration
        """
        self.profile = profile
        self.launch_config = launch_config or BrowserLaunchConfig()
        self.obfuscation_config = obfuscation_config or ObfuscationConfig()

        # Status and state
        self.status = BrowserManagerStatus.STOPPED
        self.metrics = BrowserMetrics()

        # Playwright components
        self.playwright: Optional[Playwright] = None
        self.browser_type: Optional[PlaywrightBrowserType] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

        # Service managers
        self.binary_manager: Optional[CustomBinaryManager] = None
        self.network_obfuscator: Optional[NetworkObfuscator] = None
        self.fingerprint_client: Optional[FingerprintServiceClient] = None

        # Page management
        self.pages: Dict[str, Page] = {}
        self.page_callbacks: Dict[str, List[Callable]] = {}

        # Event callbacks
        self._status_callbacks: List[Callable[[BrowserManagerStatus], None]] = []
        self._error_callbacks: List[Callable[[Exception], None]] = []
        self._page_callbacks: List[Callable[[Page, str], None]] = {}

        # Current configuration
        self.current_proxy_url: Optional[str] = None
        self.current_binary_path: Optional[str] = None

        logger.info("Browser Manager initialized")

    async def start(
        self,
        profile: Optional[BrowserProfile] = None,
        launch_config: Optional[BrowserLaunchConfig] = None
    ) -> str:
        """
        Start the browser with network obfuscation.

        Args:
            profile: Browser profile (overrides instance profile)
            launch_config: Launch configuration (overrides instance config)

        Returns:
            Browser context ID

        Raises:
            RuntimeError: If browser is already running
            Exception: If startup fails
        """
        if self.status in [BrowserManagerStatus.STARTING, BrowserManagerStatus.RUNNING]:
            raise RuntimeError(f"Browser manager is already {self.status.value}")

        try:
            await self._set_status(BrowserManagerStatus.STARTING)
            self.metrics.start_time = datetime.now()

            # Update configurations
            if profile:
                self.profile = profile
            if launch_config:
                self.launch_config = launch_config

            if not self.profile:
                raise ValueError("Browser profile is required")

            # Initialize service managers
            await self._initialize_services()

            # Start network obfuscation
            await self._start_network_obfuscation()

            # Initialize Playwright
            await self._initialize_playwright()

            # Launch browser with custom binary and proxy
            await self._launch_browser()

            # Create browser context with profile
            await self._create_browser_context()

            # Inject stealth scripts
            await self._inject_stealth_scripts()

            await self._set_status(BrowserManagerStatus.RUNNING)

            context_id = f"context_{int(time.time())}"
            logger.info(f"Browser started successfully with context ID: {context_id}")
            return context_id

        except Exception as e:
            await self._set_status(BrowserManagerStatus.ERROR)
            await self._notify_error(e)
            logger.error(f"Failed to start browser: {str(e)}")
            await self.stop()
            raise

    async def stop(self):
        """Stop the browser and cleanup resources."""
        if self.status == BrowserManagerStatus.STOPPED:
            return

        try:
            await self._set_status(BrowserManagerStatus.STOPPING)

            # Close all pages
            for page_id in list(self.pages.keys()):
                await self.close_page(page_id)

            # Close browser context
            if self.context:
                await self.context.close()
                self.context = None

            # Close browser
            if self.browser:
                await self.browser.close()
                self.browser = None

            # Stop Playwright
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

            # Stop network obfuscation
            if self.network_obfuscator:
                await self.network_obfuscator.stop()
                self.network_obfuscator = None

            # Stop service managers
            if self.binary_manager:
                await self.binary_manager.stop()
                self.binary_manager = None

            if self.fingerprint_client:
                await self.fingerprint_client.close()
                self.fingerprint_client = None

            # Reset state
            self.current_proxy_url = None
            self.current_binary_path = None

            await self._set_status(BrowserManagerStatus.STOPPED)
            logger.info("Browser stopped successfully")

        except Exception as e:
            await self._set_status(BrowserManagerStatus.ERROR)
            await self._notify_error(e)
            logger.error(f"Error stopping browser: {str(e)}")

    async def new_page(
        self,
        page_id: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Create a new browser page.

        Args:
            page_id: Optional page identifier
            viewport: Viewport size (width, height)
            user_agent: Custom user agent

        Returns:
            Page ID
        """
        if self.status != BrowserManagerStatus.RUNNING:
            raise RuntimeError(f"Cannot create page in {self.status.value} state")

        if not self.context:
            raise RuntimeError("Browser context not available")

        try:
            # Generate page ID if not provided
            if not page_id:
                page_id = f"page_{int(time.time() * 1000)}"

            # Check if page ID already exists
            if page_id in self.pages:
                raise ValueError(f"Page ID {page_id} already exists")

            # Create page options
            page_options = {}

            if viewport:
                page_options["viewport"] = viewport
            elif self.profile and self.profile.viewport:
                page_options["viewport"] = {
                    "width": self.profile.viewport.width,
                    "height": self.profile.viewport.height
                }

            if user_agent:
                page_options["user_agent"] = user_agent
            elif self.profile and self.profile.navigator.user_agent:
                page_options["user_agent"] = self.profile.navigator.user_agent

            # Create page
            page = await self.context.new_page()

            # Setup page event handlers
            await self._setup_page_handlers(page, page_id)

            # Store page
            self.pages[page_id] = page
            self.metrics.active_pages += 1
            self.metrics.total_pages += 1

            # Notify callbacks
            await self._notify_page_callbacks(page, "created")

            logger.info(f"Created new page: {page_id}")
            return page_id

        except Exception as e:
            logger.error(f"Failed to create page: {str(e)}")
            raise

    async def close_page(self, page_id: str) -> bool:
        """
        Close a browser page.

        Args:
            page_id: Page ID to close

        Returns:
            True if closed successfully
        """
        if page_id not in self.pages:
            return False

        try:
            page = self.pages[page_id]
            await page.close()
            del self.pages[page_id]
            self.metrics.active_pages -= 1

            # Notify callbacks
            await self._notify_page_callbacks(page, "closed")

            logger.info(f"Closed page: {page_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to close page {page_id}: {str(e)}")
            return False

    async def get_page(self, page_id: str) -> Optional[Page]:
        """
        Get a page by ID.

        Args:
            page_id: Page ID

        Returns:
            Page object if found
        """
        return self.pages.get(page_id)

    async def navigate(
        self,
        page_id: str,
        url: str,
        wait_until: str = "domcontentloaded",
        timeout: Optional[int] = None
    ) -> bool:
        """
        Navigate to a URL.

        Args:
            page_id: Page ID to navigate
            url: Target URL
            wait_until: When to consider navigation successful
            timeout: Navigation timeout

        Returns:
            True if navigation successful
        """
        page = await self.get_page(page_id)
        if not page:
            raise ValueError(f"Page {page_id} not found")

        start_time = time.time()
        try:
            # Navigate to URL
            response = await page.goto(
                url,
                wait_until=wait_until,
                timeout=timeout or self.launch_config.timeout
            )

            navigation_time = time.time() - start_time
            self._update_navigation_metrics(navigation_time, True)

            # Notify callbacks
            await self._notify_page_callbacks(page, "navigated", {
                "url": url,
                "response_status": response.status if response else None,
                "navigation_time": navigation_time
            })

            logger.info(f"Page {page_id} navigated to {url} in {navigation_time:.3f}s")
            return True

        except Exception as e:
            navigation_time = time.time() - start_time
            self._update_navigation_metrics(navigation_time, False)

            # Notify callbacks
            await self._notify_page_callbacks(page, "navigation_failed", {
                "url": url,
                "error": str(e),
                "navigation_time": navigation_time
            })

            logger.error(f"Page {page_id} failed to navigate to {url}: {str(e)}")
            raise

    async def execute_script(
        self,
        page_id: str,
        script: str,
        *args
    ) -> Any:
        """
        Execute JavaScript in a page.

        Args:
            page_id: Page ID
            script: JavaScript code to execute
            *args: Arguments to pass to script

        Returns:
            Script execution result
        """
        page = await self.get_page(page_id)
        if not page:
            raise ValueError(f"Page {page_id} not found")

        try:
            result = await page.evaluate(script, *args)
            return result
        except Exception as e:
            logger.error(f"Script execution failed in page {page_id}: {str(e)}")
            raise

    async def wait_for_element(
        self,
        page_id: str,
        selector: str,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for an element to appear.

        Args:
            page_id: Page ID
            selector: CSS selector
            timeout: Wait timeout

        Returns:
            True if element found
        """
        page = await self.get_page(page_id)
        if not page:
            raise ValueError(f"Page {page_id} not found")

        try:
            await page.wait_for_selector(selector, timeout=timeout or self.launch_config.timeout)
            return True
        except Exception as e:
            logger.warning(f"Element not found in page {page_id}: {selector}")
            return False

    async def take_screenshot(
        self,
        page_id: str,
        file_path: Optional[str] = None,
        full_page: bool = False
    ) -> bytes:
        """
        Take a screenshot of a page.

        Args:
            page_id: Page ID
            file_path: Optional file path to save screenshot
            full_page: Whether to capture full page

        Returns:
            Screenshot bytes
        """
        page = await self.get_page(page_id)
        if not page:
            raise ValueError(f"Page {page_id} not found")

        try:
            screenshot = await page.screenshot(
                path=file_path,
                full_page=full_page
            )
            return screenshot
        except Exception as e:
            logger.error(f"Screenshot failed for page {page_id}: {str(e)}")
            raise

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive browser manager status."""
        status_info = {
            "status": self.status.value,
            "uptime_seconds": self.metrics.uptime_seconds,
            "profile_id": self.profile.profile_id if self.profile else None,
            "browser_type": self.profile.browser_type.value if self.profile else None,
            "proxy_url": self.current_proxy_url,
            "binary_path": self.current_binary_path,
            "metrics": {
                "total_pages": self.metrics.total_pages,
                "successful_navigations": self.metrics.successful_navigations,
                "failed_navigations": self.metrics.failed_navigations,
                "success_rate": self.metrics.success_rate,
                "active_pages": self.metrics.active_pages,
                "average_page_load_time": self.metrics.average_page_load_time
            },
            "pages": list(self.pages.keys()),
            "components": {
                "playwright": self.playwright is not None,
                "browser": self.browser is not None,
                "context": self.context is not None,
                "network_obfuscator": self.network_obfuscator is not None,
                "binary_manager": self.binary_manager is not None
            }
        }

        # Add component-specific status
        if self.network_obfuscator:
            try:
                obfuscation_status = await self.network_obfuscator.get_status()
                status_info["obfuscation_status"] = obfuscation_status
            except Exception as e:
                status_info["obfuscation_status"] = {"error": str(e)}

        return status_info

    def add_status_callback(self, callback: Callable[[BrowserManagerStatus], None]):
        """Add callback for status changes."""
        self._status_callbacks.append(callback)

    def add_error_callback(self, callback: Callable[[Exception], None]):
        """Add callback for error notifications."""
        self._error_callbacks.append(callback)

    def add_page_callback(self, callback: Callable[[Page, str, Optional[Dict]], None]):
        """Add callback for page events."""
        self._page_callbacks[callback] = True

    async def _initialize_services(self):
        """Initialize service managers."""
        # Initialize binary manager
        self.binary_manager = CustomBinaryManager()
        await self.binary_manager.start()

        # Initialize fingerprint client
        self.fingerprint_client = FingerprintServiceClient()

    async def _start_network_obfuscation(self):
        """Start network obfuscation."""
        self.network_obfuscator = NetworkObfuscator(self.obfuscation_config)
        proxy_url = await self.network_obfuscator.start(self.profile)
        self.current_proxy_url = proxy_url

    async def _initialize_playwright(self):
        """Initialize Playwright."""
        self.playwright = await async_playwright().start()

        # Determine browser type
        if self.profile.browser_type == BrowserType.CHROME:
            self.browser_type = self.playwright.chromium
        elif self.profile.browser_type == BrowserType.FIREFOX:
            self.browser_type = self.playwright.firefox
        elif self.profile.browser_type == BrowserType.SAFARI:
            self.browser_type = self.playwright.webkit
        else:
            self.browser_type = self.playwright.chromium  # Default to Chromium

    async def _launch_browser(self):
        """Launch browser with custom configuration."""
        # Get custom binary path
        binary_type = {
            BrowserType.CHROME: BinaryType.CHROME,
            BrowserType.FIREFOX: BinaryType.FIREFOX,
            BrowserType.SAFARI: BinaryType.SAFARI,
            BrowserType.EDGE: BinaryType.CHROME
        }.get(self.profile.browser_type, BinaryType.CHROME)

        binary_info = await self.binary_manager.get_binary(
            binary_type=binary_type,
            auto_install=True
        )
        self.current_binary_path = str(binary_info.executable_path)

        # Prepare launch arguments
        launch_args = self._prepare_launch_args()

        # Launch browser
        launch_options = {
            "headless": self.launch_config.headless,
            "devtools": self.launch_config.devtools,
            "slow_mo": self.launch_config.slow_mo,
            "timeout": self.launch_config.timeout,
            "ignore_https_errors": self.launch_config.ignore_https_errors,
            "ignore_default_args": self.launch_config.ignore_default_args,
            "args": launch_args,
            "env": self.launch_config.env,
            "executable_path": self.current_binary_path
        }

        # Add proxy configuration
        if self.current_proxy_url:
            launch_options["proxy"] = {
                "server": self.current_proxy_url,
                "bypass": "localhost,127.0.0.1"
            }

        self.browser = await self.browser_type.launch(**launch_options)
        logger.info(f"Browser launched with binary: {self.current_binary_path}")

    async def _create_browser_context(self):
        """Create browser context with profile configuration."""
        if not self.browser:
            raise RuntimeError("Browser not launched")

        # Prepare context options
        context_options = {
            "java_script_enabled": self.launch_config.java_script_enabled,
            "ignore_https_errors": self.launch_config.ignore_https_errors,
            "bypass_csp": self.launch_config.bypass_csp,
            "user_agent": self.profile.navigator.user_agent,
            "viewport": {
                "width": self.profile.viewport.width if self.profile.viewport else self.profile.screen.width,
                "height": self.profile.viewport.height if self.profile.viewport else self.profile.screen.height
            },
            "locale": self.profile.navigator.languages[0] if self.profile.navigator.languages else "en-US",
            "timezone_id": self._get_timezone_id()
        }

        # Set permissions
        permissions = ["geolocation", "notifications"]
        await self.browser.grant_permissions(*permissions)

        # Create context
        self.context = await self.browser.new_context(**context_options)
        logger.info("Browser context created with profile configuration")

    async def _inject_stealth_scripts(self):
        """Inject stealth scripts into browser context."""
        if not self.context:
            return

        stealth_scripts = [
            self._get_navigator_override_script(),
            self._get_webgl_override_script(),
            self._get_canvas_override_script(),
            self._get_audio_override_script(),
            self._get_timezone_override_script(),
            self._get_language_override_script()
        ]

        for script in stealth_scripts:
            try:
                await self.context.add_init_script(script)
            except Exception as e:
                logger.warning(f"Failed to inject stealth script: {str(e)}")

        logger.info("Stealth scripts injected into browser context")

    def _prepare_launch_args(self) -> List[str]:
        """Prepare browser launch arguments."""
        args = []

        # Base stealth arguments
        stealth_args = [
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-ipc-flooding-protection",
            "--disable-features=TranslateUI",
            "--disable-features=VizDisplayCompositor"
        ]

        if self.profile.browser_type == BrowserType.CHROME:
            stealth_args.extend([
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions-except",
                "--disable-plugins",
                "--disable-images",
                "--disable-javascript",
                "--disable-default-apps",
                "--mute-audio"
            ])

        # Custom arguments from config
        args.extend(self.launch_config.args)
        args.extend(stealth_args)

        # Remove duplicates
        args = list(dict.fromkeys(args))

        return args

    def _get_navigator_override_script(self) -> str:
        """Get navigator property override script."""
        if not self.profile or not self.profile.navigator:
            return ""

        return f"""
        // Override navigator properties
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => false
        }});

        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {self.profile.navigator.hardware_concurrency}
        }});

        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {self.profile.navigator.device_memory or 8}
        }});

        Object.defineProperty(navigator, 'platform', {{
            get: () => '{self.profile.navigator.platform}'
        }});

        Object.defineProperty(navigator, 'languages', {{
            get: () => {json.dumps(self.profile.navigator.languages)}
        }});

        // Override plugins
        Object.defineProperty(navigator, 'plugins', {{
            get: () => [
                {{
                    0: {{type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin}},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                }}
            ]
        }});
        """

    def _get_webgl_override_script(self) -> str:
        """Get WebGL override script."""
        if not self.profile or not self.profile.navigator.webgl:
            return ""

        webgl = self.profile.navigator.webgl
        return f"""
        // Override WebGL parameters
        const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{ // UNMASKED_VENDOR_WEBGL
                return '{webgl.vendor}';
            }}
            if (parameter === 37446) {{ // UNMASKED_RENDERER_WEBGL
                return '{webgl.renderer}';
            }}
            if (parameter === 34076) {{ // MAX_TEXTURE_SIZE
                return {webgl.max_texture_size or 16384};
            }}
            return originalGetParameter.call(this, parameter);
        }};
        """

    def _get_canvas_override_script(self) -> str:
        """Get canvas override script."""
        if not self.launch_config.randomize_canvas:
            return ""

        return """
        // Add small noise to canvas fingerprint
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function() {
            const context = this.getContext('2d');
            if (context) {
                const imageData = context.getImageData(0, 0, 1, 1);
                if (imageData.data[3] === 0) {
                    imageData.data[3] = Math.random() * 255;
                    context.putImageData(imageData, 0, 0);
                }
            }
            return originalToDataURL.apply(this, arguments);
        };
        """

    def _get_audio_override_script(self) -> str:
        """Get audio context override script."""
        if not self.launch_config.randomize_audio_context:
            return ""

        return """
        // Randomize audio context fingerprint
        const originalGetChannelData = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function() {
            const data = originalGetChannelData.apply(this, arguments);
            // Add tiny noise to audio data
            for (let i = 0; i < data.length; i++) {
                data[i] += (Math.random() - 0.5) * 0.0000001;
            }
            return data;
        }};
        """

    def _get_timezone_override_script(self) -> str:
        """Get timezone override script."""
        if not self.launch_config.randomize_timezone:
            return ""

        return """
        // Randomize timezone
        const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
        Date.prototype.getTimezoneOffset = function() {
            return originalGetTimezoneOffset.call(this) + (Math.random() - 0.5) * 120;
        }};
        """

    def _get_language_override_script(self) -> str:
        """Get language override script."""
        if not self.launch_config.randomize_language:
            return ""

        return """
        // Randomize language order slightly
        const originalGet = Object.getOwnPropertyDescriptor(Navigator.prototype, 'language').get;
        Object.defineProperty(Navigator.prototype, 'language', {
            get: function() {
                const langs = navigator.languages;
                if (langs && langs.length > 1 && Math.random() > 0.8) {
                    return langs[1];
                }
                return originalGet.call(this);
            }
        });
        """

    def _get_timezone_id(self) -> str:
        """Get timezone ID from profile."""
        if self.profile and self.profile.operating_system == OperatingSystem.WINDOWS:
            return "America/New_York"
        elif self.profile and self.profile.operating_system == OperatingSystem.MACOS:
            return "America/Los_Angeles"
        else:
            return "Europe/London"

    async def _setup_page_handlers(self, page: Page, page_id: str):
        """Setup event handlers for a page."""
        # Request handling
        page.on("request", lambda request: self._handle_request(page, page_id, request))
        page.on("response", lambda response: self._handle_response(page, page_id, response))

        # Error handling
        page.on("pageerror", lambda error: self._handle_page_error(page, page_id, error))

        # Console logging
        page.on("console", lambda msg: self._handle_console_message(page, page_id, msg))

    def _handle_request(self, page: Page, page_id: str, request):
        """Handle page request."""
        self.metrics.total_requests += 1

        # Block certain requests if configured
        if self.launch_config.hide_captcha and "captcha" in request.url.lower():
            request.abort()
            self.metrics.blocked_requests += 1

    def _handle_response(self, page: Page, page_id: str, response):
        """Handle page response."""
        # Log response for debugging
        logger.debug(f"Page {page_id} response: {response.status} {response.url}")

    def _handle_page_error(self, page: Page, page_id: str, error):
        """Handle page error."""
        logger.error(f"Page {page_id} error: {str(error)}")
        self._notify_error(error)

    def _handle_console_message(self, page: Page, page_id: str, msg):
        """Handle console message."""
        if msg.type == "error":
            logger.warning(f"Page {page_id} console error: {msg.text}")

    def _update_navigation_metrics(self, navigation_time: float, success: bool):
        """Update navigation metrics."""
        if success:
            self.metrics.successful_navigations += 1
        else:
            self.metrics.failed_navigations += 1

        # Update average page load time
        if self.metrics.total_pages > 0:
            self.metrics.average_page_load_time = (
                (self.metrics.average_page_load_time * (self.metrics.total_pages - 1) + navigation_time) /
                self.metrics.total_pages
            )

    async def _set_status(self, status: BrowserManagerStatus):
        """Set browser manager status and notify callbacks."""
        old_status = self.status
        self.status = status

        if old_status != status:
            logger.info(f"Browser manager status changed: {old_status.value} -> {status.value}")

            for callback in self._status_callbacks:
                try:
                    callback(status)
                except Exception as e:
                    logger.error(f"Status callback error: {str(e)}")

    async def _notify_error(self, error: Exception):
        """Notify error callbacks."""
        for callback in self._error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error callback error: {str(e)}")

    async def _notify_page_callbacks(self, page: Page, event: str, data: Optional[Dict] = None):
        """Notify page event callbacks."""
        for callback in self._page_callbacks.keys():
            try:
                callback(page, event, data)
            except Exception as e:
                logger.error(f"Page callback error: {str(e)}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()