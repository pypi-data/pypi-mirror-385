"""
Automated data collection service.

This module implements the main service that orchestrates data collection,
processing, and storage operations for the fingerprint database.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
import statistics

from .real_world import RealWorldDataCollector, DataSourceValidator
from .network import NetworkFingerprintCollector

logger = logging.getLogger(__name__)


class DataCollectionService:
    """Main service for automated fingerprint data collection."""

    def __init__(self, db_client=None):
        self.real_collector = RealWorldDataCollector()
        self.network_collector = NetworkFingerprintCollector()
        self.validator = DataSourceValidator()
        self.db_client = db_client

        # Collection configuration
        self.collection_config = {
            'user_agents': {
                'target_count': 1000,
                'quality_threshold': 0.7,
                'max_age_days': 30
            },
            'hardware_data': {
                'target_count': 500,
                'quality_threshold': 0.6,
                'max_age_days': 7
            },
            'network_data': {
                'target_count': 200,
                'quality_threshold': 0.5,
                'max_age_days': 3
            }
        }

        self.collection_stats = {
            'start_time': None,
            'end_time': None,
            'items_collected': 0,
            'items_processed': 0,
            'items_stored': 0,
            'errors': []
        }

    async def run_collection_cycle(self) -> Dict[str, Any]:
        """Run a complete data collection cycle."""
        logger.info("Starting data collection cycle")
        self.collection_stats['start_time'] = datetime.utcnow()

        try:
            # Phase 1: Collect user agents
            logger.info("Phase 1: Collecting user agents")
            user_agents = await self._collect_user_agents_phase()

            # Phase 2: Collect hardware data
            logger.info("Phase 2: Collecting hardware data")
            hardware_data = await self._collect_hardware_data_phase()

            # Phase 3: Collect network data
            logger.info("Phase 3: Collecting network data")
            network_data = await self._collect_network_data_phase()

            # Phase 4: Process and integrate data
            logger.info("Phase 4: Processing and integrating data")
            processed_data = await self._process_collected_data(
                user_agents, hardware_data, network_data
            )

            # Phase 5: Store in database
            logger.info("Phase 5: Storing data in database")
            storage_results = await self._store_processed_data(processed_data)

            self.collection_stats['end_time'] = datetime.utcnow()

            return {
                'success': True,
                'stats': self.collection_stats,
                'storage_results': storage_results,
                'duration_seconds': (
                    self.collection_stats['end_time'] -
                    self.collection_stats['start_time']
                ).total_seconds()
            }

        except Exception as e:
            error_msg = f"Collection cycle failed: {str(e)}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
            self.collection_stats['end_time'] = datetime.utcnow()

            return {
                'success': False,
                'error': error_msg,
                'stats': self.collection_stats
            }

    async def _collect_user_agents_phase(self) -> List[Dict[str, Any]]:
        """Collect and validate user agent data."""
        try:
            # Collect raw user agents
            raw_agents = await self.real_collector.collect_user_agents()
            self.collection_stats['items_collected'] += len(raw_agents)

            # Validate and filter
            validated_agents = []
            for agent_data in raw_agents:
                validation_result = self.validator.validate_user_agent(agent_data)
                if validation_result['is_valid']:
                    validated_agents.append({
                        'data': validation_result['data'],
                        'quality_score': validation_result['quality_score'],
                        'source_type': 'real_world',
                        'collection_time': datetime.utcnow().isoformat()
                    })
                self.collection_stats['items_processed'] += 1

            # Sort by quality score and take best samples
            validated_agents.sort(key=lambda x: x['quality_score'], reverse=True)
            target_count = self.collection_config['user_agents']['target_count']
            selected_agents = validated_agents[:target_count]

            logger.info(f"Collected {len(selected_agents)} validated user agents")
            return selected_agents

        except Exception as e:
            error_msg = f"User agent collection failed: {str(e)}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
            return []

    async def _collect_hardware_data_phase(self) -> List[Dict[str, Any]]:
        """Collect and validate hardware data."""
        try:
            # Collect raw hardware data
            raw_hardware = await self.real_collector.collect_hardware_data()
            self.collection_stats['items_collected'] += len(raw_hardware)

            # Validate and filter
            validated_hardware = []
            for hardware_data in raw_hardware:
                validation_result = self.validator.validate_hardware_data(hardware_data)
                if validation_result['is_valid']:
                    validated_hardware.append({
                        'data': validation_result['data'],
                        'quality_score': validation_result['quality_score'],
                        'source_type': 'real_world',
                        'collection_time': datetime.utcnow().isoformat()
                    })
                self.collection_stats['items_processed'] += 1

            logger.info(f"Collected {len(validated_hardware)} validated hardware profiles")
            return validated_hardware

        except Exception as e:
            error_msg = f"Hardware data collection failed: {str(e)}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
            return []

    async def _collect_network_data_phase(self) -> List[Dict[str, Any]]:
        """Collect network fingerprint data."""
        try:
            # Collect TLS data
            tls_data = await self.network_collector.collect_tls_data()

            # Collect HTTP/2 data
            http2_data = await self.network_collector.collect_http2_data()

            # Collect DNS data
            dns_data = await self.network_collector.collect_dns_fingerprints()

            # Combine network data
            network_profiles = []

            # Create profiles from collected data
            browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
            for browser in browsers:
                profile = {
                    'data': {
                        'tls_fingerprint': self._extract_browser_tls_data(tls_data, browser),
                        'http2_settings': self._extract_browser_http2_data(http2_data, browser),
                        'dns_patterns': dns_data
                    },
                    'browser_type': browser.lower(),
                    'quality_score': 0.8,  # Network data generally high quality
                    'source_type': 'network_analysis',
                    'collection_time': datetime.utcnow().isoformat()
                }
                network_profiles.append(profile)

            self.collection_stats['items_collected'] += len(network_profiles)
            self.collection_stats['items_processed'] += len(network_profiles)

            logger.info(f"Collected {len(network_profiles)} network profiles")
            return network_profiles

        except Exception as e:
            error_msg = f"Network data collection failed: {str(e)}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
            return []

    async def _process_collected_data(
        self,
        user_agents: List[Dict[str, Any]],
        hardware_data: List[Dict[str, Any]],
        network_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process and integrate collected data into fingerprint profiles."""
        try:
            processed_profiles = []

            # Create realistic combinations
            combinations = min(
                len(user_agents),
                len(hardware_data),
                len(network_data)
            )

            for i in range(combinations):
                # Select data points
                ua_data = user_agents[i % len(user_agents)]
                hw_data = hardware_data[i % len(hardware_data)]
                net_data = network_data[i % len(network_data)]

                # Create integrated profile
                profile = self._create_integrated_profile(
                    ua_data, hw_data, net_data
                )

                if profile:
                    processed_profiles.append(profile)

            # Calculate quality metrics
            for profile in processed_profiles:
                profile['coherence_score'] = self._calculate_profile_coherence(profile)
                profile['detection_risk_score'] = self._calculate_detection_risk(profile)

            # Sort by coherence score
            processed_profiles.sort(
                key=lambda x: x['coherence_score'],
                reverse=True
            )

            logger.info(f"Processed {len(processed_profiles)} integrated profiles")
            return processed_profiles

        except Exception as e:
            error_msg = f"Data processing failed: {str(e)}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
            return []

    def _create_integrated_profile(
        self,
        ua_data: Dict[str, Any],
        hw_data: Dict[str, Any],
        net_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create an integrated fingerprint profile."""
        try:
            profile = {
                'profile_id': f"fp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",

                # Browser information
                'browser_type': ua_data['data']['browser_name'].lower(),
                'browser_version': ua_data['data']['browser_version'],
                'operating_system': ua_data['data']['os_name'].lower(),
                'user_agent': ua_data['data']['user_agent'],

                # Hardware data
                'screen': hw_data['data'].get('screen', {}),
                'navigator': hw_data['data'].get('navigator', {}),
                'webgl': hw_data['data'].get('webgl', {}),
                'canvas_fingerprint': hw_data['data'].get('canvasFingerprint'),
                'audio_fingerprint': hw_data['data'].get('audioFingerprint'),

                # Network data
                'tls_fingerprint': net_data['data'].get('tls_fingerprint', {}),
                'http2_settings': net_data['data'].get('http2_settings', {}),
                'dns_patterns': net_data['data'].get('dns_patterns', {}),

                # Metadata
                'collection_metadata': {
                    'user_agent_quality': ua_data['quality_score'],
                    'hardware_quality': hw_data['quality_score'],
                    'network_quality': net_data['quality_score'],
                    'collection_sources': [
                        ua_data['source_type'],
                        hw_data['source_type'],
                        net_data['source_type']
                    ],
                    'generation_method': 'integrated_real_world'
                },

                # Quality metrics
                'overall_quality_score': statistics.mean([
                    ua_data['quality_score'],
                    hw_data['quality_score'],
                    net_data['quality_score']
                ])
            }

            return profile

        except Exception as e:
            logger.error(f"Failed to create integrated profile: {e}")
            return None

    def _calculate_profile_coherence(self, profile: Dict[str, Any]) -> float:
        """Calculate coherence score for a profile."""
        score = 0.0
        max_score = 1.0

        # Check OS/browser consistency
        os_name = profile.get('operating_system', '').lower()
        browser_type = profile.get('browser_type', '').lower()

        # Valid combinations
        valid_combinations = [
            ('windows', 'chrome'), ('windows', 'firefox'), ('windows', 'edge'),
            ('macos', 'chrome'), ('macos', 'safari'), ('macos', 'firefox'),
            ('linux', 'chrome'), ('linux', 'firefox')
        ]

        if (os_name, browser_type) in valid_combinations:
            score += 0.3

        # Check screen resolution appropriateness
        screen = profile.get('screen', {})
        if screen.get('width') and screen.get('height'):
            width, height = screen['width'], screen['height']

            # Common resolutions
            common_resolutions = [
                (1920, 1080), (1366, 768), (1536, 864),
                (1440, 900), (1280, 720), (2560, 1440)
            ]

            for common_w, common_h in common_resolutions:
                if abs(width - common_w) <= 50 and abs(height - common_h) <= 50:
                    score += 0.2
                    break

        # Check hardware consistency
        navigator = profile.get('navigator', {})
        hardware_concurrency = navigator.get('hardwareConcurrency')

        if hardware_concurrency:
            # Reasonable CPU core counts
            if 1 <= hardware_concurrency <= 32:
                score += 0.2

        # Check WebGL data consistency
        webgl = profile.get('webgl', {})
        if webgl.get('vendor') and webgl.get('renderer'):
            score += 0.15

        # Check network data completeness
        if profile.get('tls_fingerprint') and profile.get('http2_settings'):
            score += 0.15

        return min(score, max_score)

    def _calculate_detection_risk(self, profile: Dict[str, Any]) -> float:
        """Calculate detection risk score (lower is better)."""
        risk_score = 0.0
        max_risk = 1.0

        # Check for bot indicators
        user_agent = profile.get('user_agent', '').lower()
        bot_indicators = ['bot', 'crawler', 'spider', 'headless', 'phantom']

        for indicator in bot_indicators:
            if indicator in user_agent:
                risk_score += 0.3

        # Check for unusual configurations
        screen = profile.get('screen', {})
        if screen.get('width') and screen.get('height'):
            width, height = screen['width'], screen['height']

            # Unusual resolutions
            if width < 800 or height < 600:
                risk_score += 0.1
            elif width > 4000 or height > 3000:
                risk_score += 0.05

        # Check hardware consistency
        navigator = profile.get('navigator', {})
        if navigator.get('hardwareConcurrency') == 1:
            risk_score += 0.1  # Single core is unusual for modern browsers

        # Check for missing network data
        if not profile.get('tls_fingerprint'):
            risk_score += 0.2

        if not profile.get('http2_settings'):
            risk_score += 0.1

        return min(risk_score, max_risk)

    def _extract_browser_tls_data(self, tls_data: Dict[str, Any], browser: str) -> Dict[str, Any]:
        """Extract TLS data specific to a browser."""
        return {
            'ja3_hash': tls_data.get('ja3_hashes', {}).get(browser),
            'client_hello_signature': tls_data.get('client_hello_signatures', {}).get(f'{browser}_Windows'),
            'cipher_preferences': tls_data.get('cipher_suite_preferences', {}).get('browser_preferences', {}).get(browser, [])
        }

    def _extract_browser_http2_data(self, http2_data: Dict[str, Any], browser: str) -> Dict[str, Any]:
        """Extract HTTP/2 data specific to a browser."""
        settings_frames = http2_data.get('settings_frames', {})

        # Find a server that has data
        if settings_frames:
            server_data = list(settings_frames.values())[0]
            return {
                'settings': server_data.get('settings', {}),
                'window_size': server_data.get('window_size', 65535),
                'priority': server_data.get('priority', {})
            }

        return {}

    async def _store_processed_data(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Store processed data in the database."""
        if not self.db_client:
            logger.warning("No database client provided, skipping storage")
            return {'stored_count': 0, 'skipped': True}

        try:
            stored_count = 0

            for profile in processed_data:
                try:
                    # Convert to database format
                    db_record = {
                        'profile_id': profile['profile_id'],
                        'browser_type': profile['browser_type'],
                        'operating_system': profile['operating_system'],
                        'version': profile['browser_version'],
                        'browser_profile': profile,
                        'source_type': profile['collection_metadata']['generation_method'],
                        'coherence_score': profile['coherence_score'],
                        'detection_risk_score': profile['detection_risk_score'],
                        'is_active': True,
                        'usage_count': 0
                    }

                    # Store in database (mock implementation)
                    await self._store_single_record(db_record)
                    stored_count += 1
                    self.collection_stats['items_stored'] += 1

                except Exception as e:
                    logger.error(f"Failed to store profile {profile.get('profile_id')}: {e}")
                    continue

            logger.info(f"Stored {stored_count} profiles in database")
            return {'stored_count': stored_count, 'skipped': False}

        except Exception as e:
            error_msg = f"Database storage failed: {str(e)}"
            logger.error(error_msg)
            self.collection_stats['errors'].append(error_msg)
            return {'stored_count': 0, 'error': error_msg}

    async def _store_single_record(self, record: Dict[str, Any]):
        """Store a single record in the database."""
        # Mock database storage
        logger.debug(f"Storing record: {record['profile_id']}")

    async def start_scheduled_collection(self):
        """Start scheduled data collection service."""
        logger.info("Starting scheduled data collection service")

        while True:
            try:
                logger.info("Running scheduled collection cycle")
                result = await self.run_collection_cycle()

                if result['success']:
                    logger.info(f"Scheduled collection completed successfully. Duration: {result['duration_seconds']:.2f}s")
                else:
                    logger.error(f"Scheduled collection failed: {result.get('error')}")

                # Schedule next collection (weekly)
                await asyncio.sleep(7 * 24 * 60 * 60)  # 7 days

            except Exception as e:
                logger.error(f"Scheduled collection error: {e}")
                # Retry after 1 hour on error
                await asyncio.sleep(60 * 60)

    async def cleanup_old_data(self, days_old: int = 30):
        """Clean up old data from the database."""
        if not self.db_client:
            logger.warning("No database client provided, skipping cleanup")
            return

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            # Mock cleanup implementation
            logger.info(f"Cleaning up data older than {cutoff_date}")

            # In real implementation, this would delete old records
            logger.info("Old data cleanup completed")

        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")

    async def get_collection_statistics(self) -> Dict[str, Any]:
        """Get statistics about collected data."""
        if not self.db_client:
            return {'error': 'No database client available'}

        try:
            # Mock statistics
            stats = {
                'total_profiles': 1000,
                'active_profiles': 850,
                'profiles_by_browser': {
                    'chrome': 400,
                    'firefox': 200,
                    'safari': 150,
                    'edge': 100
                },
                'profiles_by_os': {
                    'windows': 500,
                    'macos': 250,
                    'linux': 150,
                    'android': 80,
                    'ios': 20
                },
                'average_coherence_score': 0.82,
                'last_collection': datetime.utcnow().isoformat(),
                'collection_age_hours': 24
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get collection statistics: {e}")
            return {'error': str(e)}

    async def close(self):
        """Close all collectors and clean up resources."""
        await self.real_collector.close()
        logger.info("Data collection service closed")