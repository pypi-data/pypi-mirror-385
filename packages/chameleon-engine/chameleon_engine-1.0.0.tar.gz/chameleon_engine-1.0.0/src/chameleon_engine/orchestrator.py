"""
Chameleon Engine - Advanced Stealth Web Scraping Orchestrator

This module provides the main orchestrator that integrates all microservices
and components for stealth web scraping operations.

The ChameleonEngine coordinates:
- Fingerprint generation and management
- Network obfuscation and proxy management
- Browser automation with stealth features
- Human-like behavior simulation
- Custom binary management
- Performance monitoring and analytics
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, List, Union, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

from .services.fingerprint.client import FingerprintServiceClient
from .services.fingerprint.models import BrowserType, OperatingSystem
from .fingerprinting.generator import FingerprintGenerator
from .network.obfuscator import NetworkObfuscator
from .core.browser_manager import BrowserManager, BrowserLaunchConfig
from .core.profiles import BrowserProfile
from .services.binary.manager import CustomBinaryManager
from .behavior.mouse import MouseMovement, MovementStyle, MouseConfig
from .behavior.keyboard import KeyboardTyping, TypingStyle, TypingConfig


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ChameleonEngineConfig:
    """Configuration for ChameleonEngine behavior"""
    # Service configuration
    fingerprint_service_url: str = "http://localhost:8000"

    # Browser configuration
    default_browser: BrowserType = BrowserType.CHROME
    default_os: OperatingSystem = OperatingSystem.WINDOWS
    headless: bool = True

    # Stealth configuration
    enable_network_obfuscation: bool = True
    enable_custom_binary: bool = True
    enable_stealth_scripts: bool = True

    # Behavior simulation
    enable_human_behavior: bool = True
    mouse_movement_style: MovementStyle = MovementStyle.NATURAL
    keyboard_typing_style: TypingStyle = TypingStyle.NORMAL_TOUCH

    # Performance settings
    max_concurrent_pages: int = 5
    page_timeout: float = 30.0
    session_timeout: float = 300.0  # 5 minutes

    # Monitoring
    enable_monitoring: bool = True
    enable_analytics: bool = True

    # Advanced options
    auto_rotate_profiles: bool = False
    profile_rotation_interval: float = 600.0  # 10 minutes
    enable_proxy_pooling: bool = False


@dataclass
class SessionMetrics:
    """Metrics for a scraping session"""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    pages_created: int = 0
    requests_made: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    profile_rotations: int = 0
    total_data_size: int = 0
    errors: List[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        """Get session duration"""
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def success_rate(self) -> float:
        """Get request success rate"""
        if self.requests_made == 0:
            return 0.0
        return self.successful_requests / self.requests_made


class ChameleonEngineError(Exception):
    """Base exception for ChameleonEngine errors"""
    pass


class EngineNotStartedError(ChameleonEngineError):
    """Raised when engine operations are attempted before start"""
    pass


class ComponentInitializationError(ChameleonEngineError):
    """Raised when a component fails to initialize"""
    pass


class ChameleonEngine:
    """
    Advanced stealth web scraping orchestrator.

    This class integrates all microservices and components to provide
    a comprehensive stealth scraping solution with human-like behavior.
    """

    def __init__(self, config: Optional[ChameleonEngineConfig] = None):
        """
        Initialize ChameleonEngine

        Args:
            config: Engine configuration
        """
        self.config = config or ChameleonEngineConfig()
        self._started = False
        self._session_id = None
        self._session_metrics: Optional[SessionMetrics] = None

        # Component placeholders
        self.fingerprint_generator: Optional[FingerprintGenerator] = None
        self.network_obfuscator: Optional[NetworkObfuscator] = None
        self.browser_manager: Optional[BrowserManager] = None
        self.binary_manager: Optional[CustomBinaryManager] = None
        self.mouse_movement: Optional[MouseMovement] = None
        self.keyboard_typing: Optional[KeyboardTyping] = None

        # Current state
        self.current_profile: Optional[BrowserProfile] = None
        self.proxy_url: Optional[str] = None
        self.active_pages: Dict[str, Any] = {}

        # Background tasks
        self._background_tasks: List[asyncio.Task] = []

        logger.info("ChameleonEngine initialized")

    async def start(
        self,
        browser_type: Optional[BrowserType] = None,
        operating_system: Optional[OperatingSystem] = None,
        profile: Optional[BrowserProfile] = None,
        **profile_kwargs
    ) -> str:
        """
        Start the ChameleonEngine with all components

        Args:
            browser_type: Browser type to use
            operating_system: Operating system to emulate
            profile: Pre-generated browser profile (optional)
            **profile_kwargs: Additional profile generation parameters

        Returns:
            Session ID for this scraping session

        Raises:
            ComponentInitializationError: If any component fails to initialize
        """
        if self._started:
            logger.warning("ChameleonEngine is already started")
            return self._session_id

        logger.info("Starting ChameleonEngine...")

        try:
            # Generate session ID
            self._session_id = f"session_{int(time.time())}_{hash(str(self.config)) % 10000}"
            self._session_metrics = SessionMetrics(
                session_id=self._session_id,
                start_time=time.time()
            )

            # Initialize components
            await self._initialize_components()

            # Generate or use provided profile
            if profile:
                self.current_profile = profile
            else:
                self.current_profile = await self._generate_profile(
                    browser_type or self.config.default_browser,
                    operating_system or self.config.default_os,
                    **profile_kwargs
                )

            # Start network obfuscation
            if self.config.enable_network_obfuscation:
                self.proxy_url = await self.network_obfuscator.start(self.current_profile)
                logger.info(f"Network obfuscation started with proxy: {self.proxy_url}")

            # Start browser manager
            await self._start_browser()

            # Initialize behavior simulation
            if self.config.enable_human_behavior:
                self._initialize_behavior_simulation()

            # Start background tasks
            await self._start_background_tasks()

            self._started = True
            logger.info(f"ChameleonEngine started successfully (Session: {self._session_id})")

            return self._session_id

        except Exception as e:
            logger.error(f"Failed to start ChameleonEngine: {e}")
            await self._cleanup_on_failure()
            raise ComponentInitializationError(f"Engine startup failed: {e}") from e

    async def _initialize_components(self) -> None:
        """Initialize all engine components"""
        logger.info("Initializing components...")

        # Initialize fingerprint generator
        self.fingerprint_generator = FingerprintGenerator(
            service_url=self.config.fingerprint_service_url
        )
        await self.fingerprint_generator.wait_for_service(timeout_seconds=30)
        logger.info("Fingerprint generator initialized")

        # Initialize network obfuscator
        if self.config.enable_network_obfuscation:
            self.network_obfuscator = NetworkObfuscator()
            logger.info("Network obfuscator initialized")

        # Initialize binary manager
        if self.config.enable_custom_binary:
            self.binary_manager = CustomBinaryManager()
            logger.info("Binary manager initialized")

        logger.info("All components initialized successfully")

    async def _generate_profile(
        self,
        browser_type: BrowserType,
        operating_system: OperatingSystem,
        **kwargs
    ) -> BrowserProfile:
        """Generate a browser profile"""
        logger.info(f"Generating profile for {browser_type.value} on {operating_system.value}")

        profile = await self.fingerprint_generator.generate(
            browser=browser_type,
            os=operating_system,
            **kwargs
        )

        logger.info(f"Profile generated: {profile.browser_type.value} {profile.browser_version}")
        return profile

    async def _start_browser(self) -> None:
        """Start the browser manager"""
        logger.info("Starting browser manager...")

        # Determine binary path
        binary_path = None
        if self.config.enable_custom_binary and self.binary_manager:
            try:
                binary_info = await self.binary_manager.get_binary(
                    browser_type=self.current_profile.browser_type
                )
                binary_path = binary_info.path
                logger.info(f"Using custom binary: {binary_path}")
            except Exception as e:
                logger.warning(f"Failed to get custom binary, using default: {e}")

        # Create browser launch config
        launch_config = BrowserLaunchConfig(
            headless=self.config.headless,
            binary_path=binary_path,
            proxy_url=self.proxy_url,
            enable_stealth=self.config.enable_stealth_scripts,
            viewport_width=self.current_profile.screen.width,
            viewport_height=self.current_profile.screen.height,
            user_agent=self.current_profile.navigator.user_agent
        )

        # Initialize browser manager
        self.browser_manager = BrowserManager(
            profile=self.current_profile,
            launch_config=launch_config
        )

        await self.browser_manager.start()
        logger.info("Browser manager started successfully")

    def _initialize_behavior_simulation(self) -> None:
        """Initialize human behavior simulation components"""
        logger.info("Initializing behavior simulation...")

        # Initialize mouse movement
        self.mouse_movement = MouseMovement()

        # Initialize keyboard typing
        self.keyboard_typing = KeyboardTyping()

        logger.info("Behavior simulation initialized")

    async def _start_background_tasks(self) -> None:
        """Start background monitoring and maintenance tasks"""
        if not self.config.enable_monitoring:
            return

        logger.info("Starting background tasks...")

        # Profile rotation task
        if self.config.auto_rotate_profiles:
            task = asyncio.create_task(self._profile_rotation_task())
            self._background_tasks.append(task)

        # Health monitoring task
        task = asyncio.create_task(self._health_monitoring_task())
        self._background_tasks.append(task)

        # Metrics collection task
        if self.config.enable_analytics:
            task = asyncio.create_task(self._metrics_collection_task())
            self._background_tasks.append(task)

        logger.info(f"Started {len(self._background_tasks)} background tasks")

    async def new_page(self, viewport: Optional[Dict[str, int]] = None) -> str:
        """
        Create a new browser page

        Args:
            viewport: Viewport dimensions (width, height)

        Returns:
            Page ID for the created page

        Raises:
            EngineNotStartedError: If engine is not started
        """
        if not self._started or not self.browser_manager:
            raise EngineNotStartedError("Engine must be started before creating pages")

        if len(self.active_pages) >= self.config.max_concurrent_pages:
            logger.warning(f"Maximum concurrent pages ({self.config.max_concurrent_pages}) reached")

        page_id = await self.browser_manager.new_page(viewport=viewport)
        self.active_pages[page_id] = {
            'created_at': time.time(),
            'requests': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }

        self._session_metrics.pages_created += 1
        logger.info(f"Created new page: {page_id}")

        return page_id

    async def navigate(
        self,
        page_id: str,
        url: str,
        wait_until: str = "domcontentloaded",
        timeout: Optional[float] = None
    ) -> bool:
        """
        Navigate to a URL

        Args:
            page_id: Page ID
            url: URL to navigate to
            wait_until: When to consider navigation complete
            timeout: Navigation timeout

        Returns:
            True if navigation was successful

        Raises:
            EngineNotStartedError: If engine is not started
        """
        if not self._started or not self.browser_manager:
            raise EngineNotStartedError("Engine must be started before navigation")

        success = await self.browser_manager.navigate(
            page_id, url, wait_until, timeout or self.config.page_timeout
        )

        if page_id in self.active_pages:
            self.active_pages[page_id]['requests'] += 1
            if success:
                self.active_pages[page_id]['successful_requests'] += 1
            else:
                self.active_pages[page_id]['failed_requests'] += 1

        self._session_metrics.requests_made += 1
        if success:
            self._session_metrics.successful_requests += 1
        else:
            self._session_metrics.failed_requests += 1
            self._session_metrics.errors.append(f"Navigation failed: {url}")

        return success

    async def execute_script(
        self,
        page_id: str,
        script: str,
        *args,
        timeout: Optional[float] = None
    ) -> Any:
        """
        Execute JavaScript on a page

        Args:
            page_id: Page ID
            script: JavaScript code to execute
            *args: Arguments to pass to the script
            timeout: Execution timeout

        Returns:
            Script execution result

        Raises:
            EngineNotStartedError: If engine is not started
        """
        if not self._started or not self.browser_manager:
            raise EngineNotStartedError("Engine must be started before script execution")

        return await self.browser_manager.execute_script(
            page_id, script, *args, timeout=timeout
        )

    async def click(
        self,
        page_id: str,
        selector: str,
        button: str = "left",
        modifiers: Optional[List[str]] = None,
        position: Optional[Dict[str, float]] = None
    ) -> bool:
        """
        Click on an element with human-like behavior

        Args:
            page_id: Page ID
            selector: CSS selector for the element
            button: Mouse button to click
            modifiers: Keyboard modifiers (Ctrl, Shift, etc.)
            position: Click position relative to element

        Returns:
            True if click was successful
        """
        if not self._started or not self.browser_manager:
            raise EngineNotStartedError("Engine must be started before clicking")

        # Get element position for realistic mouse movement
        try:
            element_info = await self.browser_manager.get_element_info(page_id, selector)
            if not element_info:
                return False

            # Calculate click position
            x = element_info['x'] + (element_info['width'] / 2)
            y = element_info['y'] + (element_info['height'] / 2)

            if position:
                x += position.get('x', 0)
                y += position.get('y', 0)

            # Move mouse realistically
            if self.mouse_movement:
                page = self.browser_manager.get_page(page_id)
                await self.mouse_movement.move_to(x, y, self.config.mouse_movement_style, page)

            # Perform click
            if self.mouse_movement:
                await self.mouse_movement.click(button, page=page)
            else:
                await self.browser_manager.click(page_id, selector, button, modifiers, position)

            return True

        except Exception as e:
            logger.error(f"Click failed: {e}")
            self._session_metrics.errors.append(f"Click failed: {e}")
            return False

    async def type_text(
        self,
        page_id: str,
        selector: str,
        text: str,
        style: Optional[TypingStyle] = None,
        clear_first: bool = True
    ) -> bool:
        """
        Type text with human-like behavior

        Args:
            page_id: Page ID
            selector: CSS selector for the input element
            text: Text to type
            style: Typing style to use
            clear_first: Whether to clear field first

        Returns:
            True if typing was successful
        """
        if not self._started or not self.browser_manager:
            raise EngineNotStartedError("Engine must be started before typing")

        try:
            if self.keyboard_typing:
                page = self.browser_manager.get_page(page_id)
                typing_style = style or self.config.keyboard_typing_style

                # Focus on element
                await self.browser_manager.focus(page_id, selector)

                # Clear field if requested
                if clear_first:
                    await page.keyboard.press("Control+a")
                    await asyncio.sleep(0.1)

                # Type text with human-like behavior
                await self.keyboard_typing.type_text(text, typing_style, page, selector)
            else:
                await self.browser_manager.type_text(page_id, selector, text, clear_first)

            return True

        except Exception as e:
            logger.error(f"Typing failed: {e}")
            self._session_metrics.errors.append(f"Typing failed: {e}")
            return False

    async def take_screenshot(
        self,
        page_id: str,
        file_path: Optional[str] = None,
        full_page: bool = False
    ) -> bytes:
        """
        Take a screenshot of a page

        Args:
            page_id: Page ID
            file_path: Path to save screenshot (optional)
            full_page: Whether to capture full page

        Returns:
            Screenshot image bytes
        """
        if not self._started or not self.browser_manager:
            raise EngineNotStartedError("Engine must be started before taking screenshots")

        screenshot_bytes = await self.browser_manager.take_screenshot(
            page_id, file_path, full_page
        )

        self._session_metrics.total_data_size += len(screenshot_bytes)

        return screenshot_bytes

    async def close_page(self, page_id: str) -> None:
        """
        Close a browser page

        Args:
            page_id: Page ID to close
        """
        if not self._started or not self.browser_manager:
            raise EngineNotStartedError("Engine must be started before closing pages")

        await self.browser_manager.close_page(page_id)

        if page_id in self.active_pages:
            del self.active_pages[page_id]

        logger.info(f"Closed page: {page_id}")

    async def rotate_profile(self) -> BrowserProfile:
        """
        Rotate to a new browser profile

        Returns:
            New browser profile
        """
        if not self._started:
            raise EngineNotStartedError("Engine must be started before rotating profiles")

        logger.info("Rotating browser profile...")

        # Generate new profile
        new_profile = await self._generate_profile(
            self.current_profile.browser_type,
            self.current_profile.operating_system
        )

        # Reconfigure network obfuscator
        if self.network_obfuscator:
            await self.network_obfuscator.reconfigure(new_profile)

        # Update current profile
        self.current_profile = new_profile
        self._session_metrics.profile_rotations += 1

        logger.info(f"Profile rotated: {new_profile.browser_type.value}")
        return new_profile

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive engine status

        Returns:
            Status information dictionary
        """
        if not self._started:
            return {
                'started': False,
                'session_id': None,
                'components': {}
            }

        status = {
            'started': True,
            'session_id': self._session_id,
            'session_duration': self._session_metrics.duration,
            'components': {}
        }

        # Component statuses
        if self.fingerprint_generator:
            status['components']['fingerprint_generator'] = 'active'

        if self.network_obfuscator:
            status['components']['network_obfuscator'] = self.network_obfuscator.get_status()

        if self.browser_manager:
            status['components']['browser_manager'] = self.browser_manager.get_status()

        if self.binary_manager:
            status['components']['binary_manager'] = 'active'

        # Active pages
        status['active_pages'] = len(self.active_pages)
        status['max_pages'] = self.config.max_concurrent_pages

        # Current profile
        if self.current_profile:
            status['current_profile'] = {
                'browser': self.current_profile.browser_type.value,
                'os': self.current_profile.operating_system.value,
                'version': self.current_profile.browser_version
            }

        # Session metrics
        status['session_metrics'] = {
            'pages_created': self._session_metrics.pages_created,
            'requests_made': self._session_metrics.requests_made,
            'success_rate': self._session_metrics.success_rate,
            'errors_count': len(self._session_metrics.errors),
            'profile_rotations': self._session_metrics.profile_rotations
        }

        return status

    async def _profile_rotation_task(self) -> None:
        """Background task for automatic profile rotation"""
        while self._started:
            try:
                await asyncio.sleep(self.config.profile_rotation_interval)

                if self._started:
                    await self.rotate_profile()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Profile rotation error: {e}")
                self._session_metrics.errors.append(f"Profile rotation error: {e}")

    async def _health_monitoring_task(self) -> None:
        """Background task for health monitoring"""
        while self._started:
            try:
                await asyncio.sleep(30.0)  # Check every 30 seconds

                if not self._started:
                    break

                # Check fingerprint service health
                if self.fingerprint_generator:
                    try:
                        await self.fingerprint_generator.get_service_status()
                    except Exception as e:
                        logger.warning(f"Fingerprint service health check failed: {e}")

                # Check browser manager health
                if self.browser_manager:
                    try:
                        status = self.browser_manager.get_status()
                        if not status.get('browser_running', False):
                            logger.warning("Browser is not running, attempting recovery...")
                            # Recovery logic could be implemented here
                    except Exception as e:
                        logger.warning(f"Browser health check failed: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")

    async def _metrics_collection_task(self) -> None:
        """Background task for metrics collection"""
        while self._started:
            try:
                await asyncio.sleep(60.0)  # Collect metrics every minute

                if not self._started:
                    break

                # Log current metrics
                metrics = self.get_session_metrics()
                logger.debug(f"Session metrics: {metrics}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")

    def get_session_metrics(self) -> Dict[str, Any]:
        """Get current session metrics"""
        if not self._session_metrics:
            return {}

        return {
            'session_id': self._session_metrics.session_id,
            'duration': self._session_metrics.duration,
            'pages_created': self._session_metrics.pages_created,
            'active_pages': len(self.active_pages),
            'requests_made': self._session_metrics.requests_made,
            'successful_requests': self._session_metrics.successful_requests,
            'failed_requests': self._session_metrics.failed_requests,
            'success_rate': self._session_metrics.success_rate,
            'profile_rotations': self._session_metrics.profile_rotations,
            'total_data_size': self._session_metrics.total_data_size,
            'errors_count': len(self._session_metrics.errors)
        }

    async def stop(self) -> None:
        """Stop the ChameleonEngine and clean up resources"""
        if not self._started:
            logger.warning("ChameleonEngine is not started")
            return

        logger.info("Stopping ChameleonEngine...")

        try:
            # Stop background tasks
            for task in self._background_tasks:
                task.cancel()

            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)

            # Close all pages
            page_ids = list(self.active_pages.keys())
            for page_id in page_ids:
                await self.close_page(page_id)

            # Stop browser manager
            if self.browser_manager:
                await self.browser_manager.stop()
                self.browser_manager = None

            # Stop network obfuscation
            if self.network_obfuscator:
                await self.network_obfuscator.stop()
                self.network_obfuscator = None

            # Close fingerprint generator
            if self.fingerprint_generator:
                await self.fingerprint_generator.close()
                self.fingerprint_generator = None

            # Finalize session metrics
            if self._session_metrics:
                self._session_metrics.end_time = time.time()
                final_metrics = self.get_session_metrics()
                logger.info(f"Session completed: {final_metrics}")

            # Reset state
            self._started = False
            self._session_id = None
            self.current_profile = None
            self.proxy_url = None
            self._background_tasks.clear()

            logger.info("ChameleonEngine stopped successfully")

        except Exception as e:
            logger.error(f"Error during engine shutdown: {e}")

    async def _cleanup_on_failure(self) -> None:
        """Clean up resources after startup failure"""
        try:
            if self.fingerprint_generator:
                await self.fingerprint_generator.close()
        except Exception:
            pass

        try:
            if self.network_obfuscator:
                await self.network_obfuscator.stop()
        except Exception:
            pass

        try:
            if self.browser_manager:
                await self.browser_manager.stop()
        except Exception:
            pass

    @asynccontextmanager
    async def session(
        self,
        browser_type: Optional[BrowserType] = None,
        operating_system: Optional[OperatingSystem] = None,
        profile: Optional[BrowserProfile] = None,
        **profile_kwargs
    ):
        """
        Context manager for scraping sessions

        Args:
            browser_type: Browser type to use
            operating_system: Operating system to emulate
            profile: Pre-generated browser profile
            **profile_kwargs: Additional profile parameters
        """
        session_id = await self.start(browser_type, operating_system, profile, **profile_kwargs)
        try:
            yield self
        finally:
            await self.stop()

    async def __aenter__(self):
        """Async context manager entry"""
        return await self.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()