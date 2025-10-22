"""
Real-world data collector for browser fingerprints.

This module implements collectors that gather real browser data from various sources
including device libraries, analytics sites, and browser detection websites.
"""

import asyncio
import httpx
import random
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from playwright.async_api import async_playwright, Page, Browser
from urllib.parse import urljoin, urlparse
import logging

from ....core.profiles import BrowserProfile, BrowserType, OperatingSystem, ScreenResolution, NavigatorProperties

logger = logging.getLogger(__name__)


class RealWorldDataCollector:
    """Collects real-world browser fingerprint data from various sources."""

    def __init__(self):
        self.sources = {
            'user_agents': [
                "https://developers.whatismybrowser.com/useragents/explore/",
                "https://user-agents.net/",
                "https://techblog.willshouse.com/2012/01/03/most-common-user-agents/",
                "https://www.useragentstring.com/pages/useragentstring.php"
            ],
            'hardware_data': [
                "https://deviceatlas.com/blog/device-data",
                "https://www.whatismybrowser.com/detect/what-is-my-screen-resolution",
                "https://browserleaks.com/webgl",
                "https://webglreport.com/",
                "https://fingerprint.com/demo"
            ],
            'analytics_data': [
                "https://gs.statcounter.com/browser-market-share",
                "https://w3techs.com/technologies/details/bro-browser",
                "https://statcounter.com/screen-resolution-stats"
            ]
        }
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )

    async def collect_user_agents(self) -> List[Dict[str, Any]]:
        """Collect real user agents from multiple sources."""
        user_agents = []

        for source_url in self.sources['user_agents']:
            try:
                logger.info(f"Collecting user agents from {source_url}")
                agents = await self._parse_user_agents_from_source(source_url)
                user_agents.extend(agents)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to collect from {source_url}: {e}")
                continue

        # Deduplicate and validate
        unique_agents = self._deduplicate_user_agents(user_agents)
        return self._validate_user_agents(unique_agents)

    async def collect_hardware_data(self) -> List[Dict[str, Any]]:
        """Collect hardware fingerprint data from real browsers."""
        hardware_data = []

        async with async_playwright() as p:
            # Launch different browsers to get diverse data
            browsers_to_test = [
                ('chromium', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
                ('firefox', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0'),
                ('webkit', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            ]

            for browser_type, user_agent in browsers_to_test:
                try:
                    logger.info(f"Collecting hardware data using {browser_type}")
                    data = await self._collect_browser_hardware(p, browser_type, user_agent)
                    hardware_data.append(data)
                except Exception as e:
                    logger.error(f"Failed to collect {browser_type} hardware data: {e}")

        return hardware_data

    async def collect_screen_resolution_stats(self) -> Dict[str, float]:
        """Collect screen resolution statistics from analytics sources."""
        resolution_stats = {}

        for source_url in self.sources['analytics_data']:
            try:
                logger.info(f"Collecting screen resolution stats from {source_url}")
                stats = await self._parse_screen_stats_from_source(source_url)
                resolution_stats.update(stats)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Failed to collect screen stats from {source_url}: {e}")

        return resolution_stats

    async def collect_browser_market_share(self) -> Dict[str, float]:
        """Collect browser market share data."""
        market_share = {}

        for source_url in self.sources['analytics_data']:
            try:
                logger.info(f"Collecting browser market share from {source_url}")
                stats = await self._parse_browser_stats_from_source(source_url)
                market_share.update(stats)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Failed to collect browser stats from {source_url}: {e}")

        return market_share

    async def _parse_user_agents_from_source(self, url: str) -> List[Dict[str, Any]]:
        """Parse user agents from a specific source."""
        try:
            response = await self.session.get(url)
            response.raise_for_status()

            user_agents = []

            # Parse user agents from page content
            content = response.text

            # Common patterns for user agent strings
            ua_patterns = [
                r'Mozilla/[0-9.]+\s*\([^)]+\)\s*[A-Za-z0-9/.\s]+',
                r'Mozilla/[0-9.]+\s*\([^)]+\)\s*(?:AppleWebKit|Gecko|Chrome|Safari|Firefox|Edge)[^\\n]*',
                r'(?:Chrome|Firefox|Safari|Edge|Opera)[/][0-9.]+[^\\n]*'
            ]

            found_ua_strings = set()
            for pattern in ua_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match) > 20 and 'Mozilla' in match:  # Basic validation
                        found_ua_strings.add(match.strip())

            # Parse user agent strings
            for ua_string in list(found_ua_strings)[:100]:  # Limit per source
                parsed = self._parse_user_agent_string(ua_string)
                if parsed:
                    user_agents.append(parsed)

            return user_agents

        except Exception as e:
            logger.error(f"Error parsing user agents from {url}: {e}")
            return []

    async def _collect_browser_hardware(self, playwright, browser_type: str, user_agent: str) -> Dict[str, Any]:
        """Collect hardware data using a specific browser."""
        try:
            browser = await getattr(playwright, browser_type).launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            context = await browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1920, 'height': 1080}
            )

            page = await context.new_page()

            # Execute JavaScript to collect hardware data
            hardware_data = await page.evaluate("""
                () => {
                    // Screen data
                    const screenData = {
                        width: screen.width,
                        height: screen.height,
                        colorDepth: screen.colorDepth,
                        pixelDepth: screen.pixelDepth,
                        availWidth: screen.availWidth,
                        availHeight: screen.availHeight
                    };

                    // Navigator data
                    const navigatorData = {
                        userAgent: navigator.userAgent,
                        platform: navigator.platform,
                        hardwareConcurrency: navigator.hardwareConcurrency,
                        deviceMemory: navigator.deviceMemory || undefined,
                        maxTouchPoints: navigator.maxTouchPoints,
                        vendor: navigator.vendor,
                        vendorSub: navigator.vendorSub,
                        cookieEnabled: navigator.cookieEnabled,
                        onLine: navigator.onLine,
                        languages: Array.from(navigator.languages),
                        language: navigator.language,
                        doNotTrack: navigator.doNotTrack
                    };

                    // WebGL data
                    let webglData = null;
                    try {
                        const canvas = document.createElement('canvas');
                        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

                        if (gl) {
                            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                            webglData = {
                                vendor: gl.getParameter(gl.VENDOR),
                                renderer: gl.getParameter(gl.RENDERER),
                                unmaskedVendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : null,
                                unmaskedRenderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : null,
                                version: gl.getParameter(gl.VERSION),
                                shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
                                maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
                                maxViewportDims: gl.getParameter(gl.MAX_VIEWPORT_DIMS),
                                maxRenderBufferSize: gl.getParameter(gl.MAX_RENDERBUFFER_SIZE),
                                extensions: gl.getSupportedExtensions()
                            };
                        }
                    } catch (e) {
                        console.log('WebGL not available:', e);
                    }

                    // Canvas fingerprint
                    let canvasFingerprint = null;
                    try {
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        canvas.width = 200;
                        canvas.height = 50;

                        // Draw a complex pattern
                        ctx.textBaseline = 'top';
                        ctx.font = '14px Arial';
                        ctx.fillStyle = '#f60';
                        ctx.fillRect(125, 1, 62, 20);
                        ctx.fillStyle = '#069';
                        ctx.fillText('BrowserLeaks,com <canvas> 1.0', 2, 15);
                        ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
                        ctx.fillText('BrowserLeaks,com <canvas> 1.0', 4, 17);

                        canvasFingerprint = canvas.toDataURL().slice(-50);  // Last 50 chars as fingerprint
                    } catch (e) {
                        console.log('Canvas fingerprint failed:', e);
                    }

                    // Audio fingerprint
                    let audioFingerprint = null;
                    try {
                        const AudioContext = window.AudioContext || window.webkitAudioContext;
                        const audioCtx = new AudioContext();
                        const oscillator = audioCtx.createOscillator();
                        const analyser = audioCtx.createAnalyser();
                        const gainNode = audioCtx.createGain();

                        oscillator.type = 'triangle';
                        oscillator.frequency.setValueAtTime(10000, audioCtx.currentTime);

                        oscillator.connect(analyser);
                        analyser.connect(gainNode);
                        gainNode.connect(audioCtx.destination);

                        oscillator.start(0);
                        oscillator.stop(audioCtx.currentTime + 0.1);

                        const bufferLength = analyser.frequencyBinCount;
                        const dataArray = new Uint8Array(bufferLength);
                        analyser.getByteFrequencyData(dataArray);

                        audioFingerprint = Array.from(dataArray.slice(0, 50)).join(',');
                    } catch (e) {
                        console.log('Audio fingerprint failed:', e);
                    }

                    return {
                        screen: screenData,
                        navigator: navigatorData,
                        webgl: webglData,
                        canvasFingerprint: canvasFingerprint,
                        audioFingerprint: audioFingerprint,
                        timestamp: new Date().toISOString()
                    };
                }
            """)

            await browser.close()

            # Add metadata
            hardware_data['collection_metadata'] = {
                'browser_type': browser_type,
                'user_agent': user_agent,
                'collection_time': datetime.utcnow().isoformat()
            }

            return hardware_data

        except Exception as e:
            logger.error(f"Error collecting hardware data with {browser_type}: {e}")
            return {}

    def _parse_user_agent_string(self, ua_string: str) -> Optional[Dict[str, Any]]:
        """Parse a user agent string into components."""
        try:
            # Basic user agent parsing
            os_patterns = [
                (r'Windows NT ([0-9.]+)', 'Windows'),
                (r'Mac OS X ([0-9._]+)', 'macOS'),
                (r'Linux ([a-zA-Z0-9.]+)', 'Linux'),
                (r'Android ([0-9.]+)', 'Android'),
                (r'iPhone OS ([0-9_]+)', 'iOS')
            ]

            browser_patterns = [
                (r'Chrome/([0-9.]+)', 'Chrome'),
                (r'Firefox/([0-9.]+)', 'Firefox'),
                (r'Safari/([0-9.]+)', 'Safari'),
                (r'Edge/([0-9.]+)', 'Edge'),
                (r'Opera/([0-9.]+)', 'Opera')
            ]

            os_name = 'Unknown'
            os_version = 'Unknown'
            browser_name = 'Unknown'
            browser_version = 'Unknown'

            for pattern, name in os_patterns:
                match = re.search(pattern, ua_string)
                if match:
                    os_name = name
                    os_version = match.group(1).replace('_', '.')
                    break

            for pattern, name in browser_patterns:
                match = re.search(pattern, ua_string)
                if match:
                    browser_name = name
                    browser_version = match.group(1)
                    break

            # Skip if we couldn't identify browser or OS
            if browser_name == 'Unknown' or os_name == 'Unknown':
                return None

            return {
                'user_agent': ua_string,
                'browser_name': browser_name,
                'browser_version': browser_version,
                'os_name': os_name,
                'os_version': os_version,
                'mobile': any(mobile in ua_string.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad']),
                'platform': self._extract_platform(ua_string),
                'architecture': 'x64' if 'x64' in ua_string or 'win64' in ua_string.lower() else 'x86'
            }

        except Exception as e:
            logger.error(f"Error parsing user agent string: {e}")
            return None

    def _extract_platform(self, ua_string: str) -> str:
        """Extract platform from user agent string."""
        if 'Win64' in ua_string or 'WOW64' in ua_string:
            return 'Win32'
        elif 'Windows' in ua_string:
            return 'Win32'
        elif 'Mac' in ua_string:
            return 'MacIntel'
        elif 'Linux' in ua_string:
            return 'Linux x86_64'
        elif 'Android' in ua_string:
            return 'Linux armv7l'
        else:
            return 'Unknown'

    def _deduplicate_user_agents(self, user_agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate user agents."""
        seen = set()
        unique_agents = []

        for ua in user_agents:
            ua_key = ua['user_agent']
            if ua_key not in seen:
                seen.add(ua_key)
                unique_agents.append(ua)

        return unique_agents

    def _validate_user_agents(self, user_agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate user agents for quality and completeness."""
        valid_agents = []

        for ua in user_agents:
            # Quality checks
            if (
                len(ua['user_agent']) < 30 or  # Too short
                len(ua['user_agent']) > 500 or  # Too long
                ua['browser_name'] == 'Unknown' or
                ua['os_name'] == 'Unknown' or
                not re.match(r'[0-9]+\.[0-9]+', ua['browser_version'])  # Invalid version format
            ):
                continue

            valid_agents.append(ua)

        return valid_agents

    async def _parse_screen_stats_from_source(self, url: str) -> Dict[str, float]:
        """Parse screen resolution statistics from source."""
        # This would implement specific parsing for different analytics sites
        # For now, return common resolutions with estimated market share
        common_resolutions = {
            '1920x1080': 35.0,
            '1366x768': 22.0,
            '1536x864': 10.0,
            '1440x900': 8.0,
            '1280x720': 7.0,
            '1600x900': 5.0,
            '2560x1440': 4.0,
            '3840x2160': 2.0,
            '1280x1024': 2.0,
            '1024x768': 1.5
        }
        return common_resolutions

    async def _parse_browser_stats_from_source(self, url: str) -> Dict[str, float]:
        """Parse browser market share statistics from source."""
        # Return estimated market share data
        browser_stats = {
            'Chrome': 65.0,
            'Safari': 18.0,
            'Edge': 5.0,
            'Firefox': 3.0,
            'Opera': 2.5,
            'Other': 6.5
        }
        return browser_stats

    async def close(self):
        """Close the HTTP session."""
        await self.session.aclose()


class DataSourceValidator:
    """Validates and scores collected data sources."""

    def __init__(self):
        self.quality_thresholds = {
            'user_agent_completeness': 0.8,
            'hardware_data_completeness': 0.7,
            'source_reliability': 0.6
        }

    def validate_user_agent(self, ua_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and score a user agent data entry."""
        score = 0.0
        issues = []

        # Check completeness
        required_fields = ['user_agent', 'browser_name', 'browser_version', 'os_name']
        completeness = sum(1 for field in required_fields if ua_data.get(field))
        score += (completeness / len(required_fields)) * 0.4

        # Check format validity
        if re.match(r'Mozilla/[0-9.]+', ua_data.get('user_agent', '')):
            score += 0.2
        else:
            issues.append('Invalid user agent format')

        # Check version format
        if re.match(r'[0-9]+\.[0-9]+', ua_data.get('browser_version', '')):
            score += 0.2
        else:
            issues.append('Invalid browser version format')

        # Check for bot/automation indicators
        bot_indicators = ['bot', 'crawler', 'spider', 'headless', 'phantom', 'selenium']
        ua_lower = ua_data.get('user_agent', '').lower()
        if any(indicator in ua_lower for indicator in bot_indicators):
            score -= 0.5
            issues.append('Contains bot/automation indicators')

        # Check platform consistency
        if self._check_platform_consistency(ua_data):
            score += 0.2
        else:
            issues.append('Platform/browser OS inconsistency')

        return {
            'data': ua_data,
            'quality_score': max(0, min(1, score)),
            'issues': issues,
            'is_valid': score >= self.quality_thresholds['user_agent_completeness']
        }

    def validate_hardware_data(self, hardware_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and score hardware data."""
        score = 0.0
        issues = []

        # Check screen data
        screen = hardware_data.get('screen', {})
        if screen.get('width') and screen.get('height'):
            score += 0.3

            # Validate reasonable screen dimensions
            if (320 <= screen['width'] <= 7680 and
                240 <= screen['height'] <= 4320):
                score += 0.1
            else:
                issues.append('Unusual screen dimensions')
        else:
            issues.append('Missing screen data')

        # Check navigator data
        navigator = hardware_data.get('navigator', {})
        navigator_fields = ['hardwareConcurrency', 'platform', 'vendor']
        navigator_completeness = sum(1 for field in navigator_fields if navigator.get(field))
        score += (navigator_completeness / len(navigator_fields)) * 0.3

        # Check WebGL data
        webgl = hardware_data.get('webgl')
        if webgl and webgl.get('vendor') and webgl.get('renderer'):
            score += 0.2
        else:
            issues.append('Missing WebGL data')

        # Check for consistency
        if self._check_hardware_consistency(hardware_data):
            score += 0.1
        else:
            issues.append('Hardware data inconsistencies')

        return {
            'data': hardware_data,
            'quality_score': max(0, min(1, score)),
            'issues': issues,
            'is_valid': score >= self.quality_thresholds['hardware_data_completeness']
        }

    def _check_platform_consistency(self, ua_data: Dict[str, Any]) -> bool:
        """Check if platform and browser/OS are consistent."""
        os_name = ua_data.get('os_name', '').lower()
        platform = ua_data.get('platform', '').lower()

        # Basic consistency checks
        if 'windows' in os_name and 'win' not in platform:
            return False
        elif 'mac' in os_name and 'mac' not in platform:
            return False
        elif 'linux' in os_name and 'linux' not in platform:
            return False

        return True

    def _check_hardware_consistency(self, hardware_data: Dict[str, Any]) -> bool:
        """Check hardware data for consistency."""
        screen = hardware_data.get('screen', {})
        navigator = hardware_data.get('navigator', {})

        # Check screen vs viewport consistency
        if screen.get('width') and screen.get('availWidth'):
            if screen['availWidth'] > screen['width']:
                return False

        # Check reasonable hardware values
        if navigator.get('hardwareConcurrency'):
            cores = navigator['hardwareConcurrency']
            if not (1 <= cores <= 128):  # Reasonable CPU core range
                return False

        return True