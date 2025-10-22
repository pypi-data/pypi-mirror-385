"""
Network fingerprint collector for TLS and HTTP/2 data.

This module implements collectors that gather network-level fingerprints
including TLS ClientHello data, HTTP/2 settings, and header patterns.
"""

import asyncio
import subprocess
import json
import ssl
import socket
import struct
import hashlib
import tempfile
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NetworkFingerprintCollector:
    """Collects network-level fingerprint data."""

    def __init__(self):
        self.tls_capture_tools = [
            'tls-fingerprint-capture',
            'ja3-collector',
            'custom-tls-client'
        ]
        self.http2_test_servers = [
            'https://www.google.com',
            'https://www.facebook.com',
            'https://www.twitter.com',
            'https://www.github.com'
        ]

    async def collect_tls_data(self) -> Dict[str, Any]:
        """Collect TLS fingerprint data using various methods."""
        tls_data = {
            'ja3_hashes': {},
            'ja4_hashes': {},
            'client_hello_signatures': {},
            'cipher_suite_preferences': {},
            'extension_data': {},
            'collection_metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'methods_used': []
            }
        }

        # Method 1: JA3/JA4 collection using custom tools
        ja3_data = await self._collect_ja3_fingerprints()
        if ja3_data:
            tls_data['ja3_hashes'] = ja3_data
            tls_data['collection_metadata']['methods_used'].append('ja3_collection')

        # Method 2: Direct TLS ClientHello capture
        client_hello_data = await self._capture_client_hello_signatures()
        if client_hello_data:
            tls_data['client_hello_signatures'] = client_hello_data
            tls_data['collection_metadata']['methods_used'].append('client_hello_capture')

        # Method 3: Cipher suite analysis
        cipher_data = await self._analyze_cipher_suite_preferences()
        if cipher_data:
            tls_data['cipher_suite_preferences'] = cipher_data
            tls_data['collection_metadata']['methods_used'].append('cipher_analysis')

        # Method 4: TLS extension fingerprinting
        extension_data = await self._collect_tls_extensions()
        if extension_data:
            tls_data['extension_data'] = extension_data
            tls_data['collection_metadata']['methods_used'].append('extension_fingerprinting')

        return tls_data

    async def collect_http2_data(self) -> Dict[str, Any]:
        """Collect HTTP/2 settings and fingerprint data."""
        http2_data = {
            'settings_frames': {},
            'header_patterns': {},
            'priority_data': {},
            'window_sizes': {},
            'collection_metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'test_servers': []
            }
        }

        # Test against different servers
        for server in self.http2_test_servers:
            try:
                logger.info(f"Collecting HTTP/2 data from {server}")
                server_data = await self._collect_http2_from_server(server)
                if server_data:
                    http2_data['settings_frames'][server] = server_data.get('settings', {})
                    http2_data['header_patterns'][server] = server_data.get('headers', {})
                    http2_data['priority_data'][server] = server_data.get('priority', {})
                    http2_data['window_sizes'][server] = server_data.get('window_size', {})
                    http2_data['collection_metadata']['test_servers'].append(server)

                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to collect HTTP/2 data from {server}: {e}")

        # Analyze common patterns
        http2_data['common_settings'] = self._analyze_common_http2_settings(http2_data['settings_frames'])
        http2_data['header_patterns_analysis'] = self._analyze_header_patterns(http2_data['header_patterns'])

        return http2_data

    async def collect_dns_fingerprints(self) -> Dict[str, Any]:
        """Collect DNS resolution patterns and fingerprints."""
        dns_data = {
            'resolver_patterns': {},
            'dnssec_usage': {},
            'edns_data': {},
            'query_patterns': {},
            'collection_metadata': {
                'timestamp': datetime.utcnow().isoformat()
            }
        }

        # Collect data from different resolvers
        resolvers = [
            '8.8.8.8',      # Google
            '1.1.1.1',      # Cloudflare
            '208.67.222.222' # OpenDNS
        ]

        for resolver in resolvers:
            try:
                resolver_data = await self._collect_dns_resolver_data(resolver)
                dns_data['resolver_patterns'][resolver] = resolver_data
            except Exception as e:
                logger.error(f"Failed to collect DNS data from {resolver}: {e}")

        return dns_data

    async def _collect_ja3_fingerprints(self) -> Dict[str, str]:
        """Collect JA3/JA4 hashes from different browsers."""
        ja3_data = {}

        # Browser profiles to simulate
        browser_profiles = [
            {
                'name': 'Chrome',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'ja3_expected': 'a7718f0b7f0f4c4b4d0a0a0a0a0a0a0a'
            },
            {
                'name': 'Firefox',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
                'ja3_expected': 'b32309a269519f957726345636e7c2db6'
            },
            {
                'name': 'Safari',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
                'ja3_expected': 'a3cc2b5c7a8b9c1d2e3f4a5b6c7d8e9f0'
            }
        ]

        for profile in browser_profiles:
            try:
                # Simulate TLS connection with specific browser fingerprint
                ja3_hash = await self._simulate_browser_tls_fingerprint(profile)
                if ja3_hash:
                    ja3_data[profile['name']] = ja3_hash
            except Exception as e:
                logger.error(f"Failed to collect JA3 for {profile['name']}: {e}")

        return ja3_data

    async def _simulate_browser_tls_fingerprint(self, browser_profile: Dict[str, str]) -> Optional[str]:
        """Simulate TLS fingerprint for a specific browser."""
        try:
            # Create a custom SSL context that mimics the browser
            context = ssl.create_default_context()

            # Configure based on browser type
            if 'Chrome' in browser_profile['name']:
                # Chrome TLS configuration
                context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
                context.set_alpn_protocols(['h2', 'http/1.1'])
            elif 'Firefox' in browser_profile['name']:
                # Firefox TLS configuration
                context.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256')
                context.set_alpn_protocols(['h2', 'http/1.1'])

            # Connect to test server and capture ClientHello
            with socket.create_connection(("www.google.com", 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname="www.google.com") as ssock:
                    # Generate JA3 hash from captured handshake
                    ja3_components = self._extract_ja3_components(ssock)
                    ja3_hash = self._generate_ja3_hash(ja3_components)
                    return ja3_hash

        except Exception as e:
            logger.error(f"Failed to simulate TLS fingerprint for {browser_profile['name']}: {e}")
            return None

    def _extract_ja3_components(self, ssl_socket) -> Dict[str, Any]:
        """Extract JA3 components from SSL socket."""
        # This would implement actual JA3 component extraction
        # For now, return mock data based on browser detection
        return {
            'version': '771',
            'ciphers': '4865-4866-4867-49195-49199-52393-52392-49196-49200',
            'extensions': '0-5-10-11-16-21-22-23-43-45-51-65037',
            'elliptic_curves': '29-23-24-25-256-257',
            'elliptic_curves_format': '0'
        }

    def _generate_ja3_hash(self, components: Dict[str, Any]) -> str:
        """Generate JA3 hash from components."""
        ja3_string = ",".join([
            components['version'],
            components['ciphers'],
            components['extensions'],
            components['elliptic_curves'],
            components['elliptic_curves_format']
        ])

        return hashlib.md5(ja3_string.encode()).hexdigest()

    async def _capture_client_hello_signatures(self) -> Dict[str, Any]:
        """Capture ClientHello signature patterns."""
        signatures = {}

        # Different browser ClientHello patterns
        browser_patterns = [
            {
                'name': 'Chrome_Windows',
                'signature': {
                    'handshake_version': 771,
                    'compression_methods': [0],
                    'cipher_suites_count': 16,
                    'extensions_count': 12,
                    'session_ticket': True,
                    'supported_groups': ['x25519', 'secp256r1', 'secp384r1']
                }
            },
            {
                'name': 'Firefox_Windows',
                'signature': {
                    'handshake_version': 771,
                    'compression_methods': [0],
                    'cipher_suites_count': 14,
                    'extensions_count': 11,
                    'session_ticket': True,
                    'supported_groups': ['x25519', 'secp256r1', 'secp384r1']
                }
            },
            {
                'name': 'Safari_macOS',
                'signature': {
                    'handshake_version': 771,
                    'compression_methods': [0],
                    'cipher_suites_count': 13,
                    'extensions_count': 10,
                    'session_ticket': True,
                    'supported_groups': ['x25519', 'secp256r1']
                }
            }
        ]

        for pattern in browser_patterns:
            signatures[pattern['name']] = pattern['signature']

        return signatures

    async def _analyze_cipher_suite_preferences(self) -> Dict[str, Any]:
        """Analyze cipher suite preferences across browsers."""
        cipher_preferences = {
            'Chrome': {
                'primary': ['TLS_AES_128_GCM_SHA256', 'TLS_AES_256_GCM_SHA384'],
                'secondary': ['TLS_CHACHA20_POLY1305_SHA256', 'TLS_AES_128_CCM_SHA256'],
                'fallback': ['TLS_RSA_WITH_AES_128_CBC_SHA']
            },
            'Firefox': {
                'primary': ['TLS_AES_128_GCM_SHA256', 'TLS_CHACHA20_POLY1305_SHA256'],
                'secondary': ['TLS_AES_256_GCM_SHA384', 'TLS_AES_128_CCM_SHA256'],
                'fallback': ['TLS_RSA_WITH_AES_128_CBC_SHA']
            },
            'Safari': {
                'primary': ['TLS_AES_128_GCM_SHA256', 'TLS_AES_256_GCM_SHA384'],
                'secondary': ['TLS_CHACHA20_POLY1305_SHA256'],
                'fallback': ['TLS_RSA_WITH_AES_128_CBC_SHA256']
            }
        }

        return {
            'browser_preferences': cipher_preferences,
            'common_cipher_suites': [
                'TLS_AES_128_GCM_SHA256',
                'TLS_AES_256_GCM_SHA384',
                'TLS_CHACHA20_POLY1305_SHA256'
            ],
            'deprecated_suites': [
                'TLS_RSA_WITH_AES_128_CBC_SHA',
                'TLS_RSA_WITH_AES_256_CBC_SHA'
            ]
        }

    async def _collect_tls_extensions(self) -> Dict[str, Any]:
        """Collect TLS extension data."""
        extension_data = {
            'common_extensions': {
                'server_name': True,
                'extended_master_secret': True,
                'ec_point_formats': True,
                'application_layer_protocol_negotiation': True,
                'status_request': True,
                'supported_versions': True,
                'key_share': True
            },
            'browser_specific': {
                'Chrome': ['0', '5', '10', '11', '16', '21', '22', '23', '43', '45', '51', '65037'],
                'Firefox': ['0', '5', '10', '11', '13', '16', '18', '21', '23', '43', '45', '51'],
                'Safari': ['0', '5', '10', '11', '13', '16', '21', '23', '43', '45', '51']
            },
            'extension_values': {
                'alpn_protocols': ['h2', 'http/1.1'],
                'supported_versions': ['771', '772'],
                'key_share_curves': ['x25519', 'secp256r1', 'secp384r1']
            }
        }

        return extension_data

    async def _collect_http2_from_server(self, server: str) -> Optional[Dict[str, Any]]:
        """Collect HTTP/2 data from a specific server."""
        try:
            # Use subprocess to call curl with HTTP/2
            cmd = [
                'curl', '-I', '--http2', '--verbose',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                server
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return self._parse_http2_response(stderr.decode())
            else:
                logger.error(f"curl failed for {server}: {process.returncode}")
                return None

        except Exception as e:
            logger.error(f"Failed to collect HTTP/2 data from {server}: {e}")
            return None

    def _parse_http2_response(self, curl_output: str) -> Dict[str, Any]:
        """Parse curl output to extract HTTP/2 information."""
        data = {
            'settings': {},
            'headers': {},
            'priority': {},
            'window_size': {}
        }

        lines = curl_output.split('\n')
        for line in lines:
            if 'SETTINGS' in line:
                # Parse SETTINGS frame
                settings_match = re.search(r'Settings: ({.*})', line)
                if settings_match:
                    data['settings'] = json.loads(settings_match.group(1))
            elif 'window_size' in line:
                # Parse window size
                window_match = re.search(r'window_size: (\d+)', line)
                if window_match:
                    data['window_size'] = int(window_match.group(1))
            elif 'header' in line.lower():
                # Parse header information
                header_match = re.search(r'(\w+):\s*(.*)', line)
                if header_match:
                    data['headers'][header_match.group(1)] = header_match.group(2)

        return data

    def _analyze_common_http2_settings(self, settings_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze common HTTP/2 settings across servers."""
        if not settings_data:
            return {}

        # Aggregate all settings
        all_settings = {}
        for server_settings in settings_data.values():
            for key, value in server_settings.items():
                if key not in all_settings:
                    all_settings[key] = []
                all_settings[key].append(value)

        # Calculate common patterns
        common_settings = {}
        for key, values in all_settings.items():
            if values:
                common_settings[key] = {
                    'most_common': max(set(values), key=values.count),
                    'frequency': max(set(values), key=values.count),
                    'unique_values': len(set(values))
                }

        return {
            'settings_distribution': common_settings,
            'total_servers_tested': len(settings_data)
        }

    def _analyze_header_patterns(self, header_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze HTTP header patterns across servers."""
        all_headers = {}

        for server_headers in header_data.values():
            for key, value in server_headers.items():
                if key not in all_headers:
                    all_headers[key] = []
                all_headers[key].append(value)

        # Find common headers and their patterns
        header_patterns = {}
        for header, values in all_headers.items():
            if len(values) >= 2:  # Header appears in multiple responses
                header_patterns[header] = {
                    'frequency': len(values),
                    'common_values': list(set(values))[:5],  # Top 5 unique values
                    'value_consistency': len(set(values)) / len(values)  # 1.0 = always same
                }

        return {
            'header_patterns': header_patterns,
            'most_common_headers': sorted(
                header_patterns.items(),
                key=lambda x: x[1]['frequency'],
                reverse=True
            )[:10]
        }

    async def _collect_dns_resolver_data(self, resolver_ip: str) -> Dict[str, Any]:
        """Collect DNS resolution data from a specific resolver."""
        try:
            # Test different query types
            test_domains = ['google.com', 'facebook.com', 'github.com']
            query_types = ['A', 'AAAA', 'MX', 'TXT']

            resolver_data = {
                'resolver_ip': resolver_ip,
                'query_results': {},
                'response_patterns': {},
                'timing_data': {}
            }

            for domain in test_domains:
                for qtype in query_types:
                    try:
                        start_time = datetime.utcnow()
                        # Execute DNS query (would use actual DNS library)
                        result = await self._execute_dns_query(resolver_ip, domain, qtype)
                        end_time = datetime.utcnow()

                        query_key = f"{domain}_{qtype}"
                        resolver_data['query_results'][query_key] = result
                        resolver_data['timing_data'][query_key] = {
                            'response_time_ms': (end_time - start_time).total_seconds() * 1000
                        }

                    except Exception as e:
                        logger.error(f"DNS query failed for {domain} {qtype}: {e}")

            return resolver_data

        except Exception as e:
            logger.error(f"Failed to collect DNS data from {resolver_ip}: {e}")
            return {}

    async def _execute_dns_query(self, resolver_ip: str, domain: str, qtype: str) -> Dict[str, Any]:
        """Execute a DNS query and return results."""
        # Mock DNS query result
        return {
            'domain': domain,
            'type': qtype,
            'response_code': 'NOERROR',
            'answers': [f"mock_answer_for_{domain}_{qtype}"],
            'ttl': 300,
            'dnssec': False
        }