"""
TLS fingerprint management for network obfuscation.

This module provides TLS fingerprint generation, management, and ClientHello
building capabilities for stealth network communication.
"""

import json
import hashlib
import secrets
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from ..core.profiles import TLSFingerprint

logger = logging.getLogger(__name__)


class TLSVersion(Enum):
    """Supported TLS versions."""
    TLS_1_0 = "tls1.0"
    TLS_1_1 = "tls1.1"
    TLS_1_2 = "tls1.2"
    TLS_1_3 = "tls1.3"


class CipherSuite(Enum):
    """Common TLS cipher suites."""
    # TLS 1.3
    TLS_AES_128_GCM_SHA256 = "TLS_AES_128_GCM_SHA256"
    TLS_AES_256_GCM_SHA384 = "TLS_AES_256_GCM_SHA384"
    TLS_CHACHA20_POLY1305_SHA256 = "TLS_CHACHA20_POLY1305_SHA256"

    # TLS 1.2
    TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 = "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256"
    TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 = "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384"
    TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256 = "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256"
    TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 = "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
    TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
    TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256 = "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"


@dataclass
class TLSClientHelloConfig:
    """Configuration for TLS ClientHello message."""
    version: str
    cipher_suites: List[str]
    extensions: List[str]
    elliptic_curves: List[str] = field(default_factory=lambda: ["secp256r1", "secp384r1", "secp521r1"])
    signature_algorithms: List[str] = field(default_factory=lambda: [
        "ecdsa_secp256r1_sha256",
        "ecdsa_secp384r1_sha384",
        "ecdsa_secp521r1_sha512",
        "rsa_pss_rsae_sha256",
        "rsa_pss_rsae_sha384",
        "rsa_pss_rsae_sha512",
        "rsa_pkcs1_sha256",
        "rsa_pkcs1_sha384",
        "rsa_pkcs1_sha512"
    ])
    alpn_protocols: List[str] = field(default_factory=lambda: ["h2", "http/1.1"])
    key_share_groups: List[str] = field(default_factory=lambda: ["x25519", "secp256r1"])
    psk_modes: List[str] = field(default_factory=lambda: ["psk_dhe_ke"])
    supported_versions: List[str] = field(default_factory=lambda: ["tls1.3", "tls1.2"])


@dataclass
class TLSFingerprintProfile:
    """Complete TLS fingerprint profile."""
    name: str
    browser_type: str
    browser_version: str
    operating_system: str
    client_hello_config: TLSClientHelloConfig
    ja3_hash: Optional[str] = None
    ja4_hash: Optional[str] = None
    utls_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TLSFingerprintManager:
    """
    Manager for TLS fingerprints and ClientHello building.

    This class provides functionality to generate, manage, and build TLS
    fingerprints for network-level obfuscation.
    """

    def __init__(self):
        """Initialize TLS fingerprint manager."""
        self.fingerprint_profiles: Dict[str, TLSFingerprintProfile] = {}
        self._load_default_profiles()

    def _load_default_profiles(self):
        """Load default TLS fingerprint profiles."""
        # Chrome 120 on Windows
        self.fingerprint_profiles["chrome_120_windows"] = TLSFingerprintProfile(
            name="Chrome 120 on Windows",
            browser_type="chrome",
            browser_version="120.0.0.0",
            operating_system="windows",
            client_hello_config=TLSClientHelloConfig(
                version="tls1.3",
                cipher_suites=[
                    TLSVersion.TLS_AES_128_GCM_SHA256.value,
                    TLSVersion.TLS_AES_256_GCM_SHA384.value,
                    TLSVersion.TLS_CHACHA20_POLY1305_SHA256.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256.value,
                    TLSVersion.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256.value,
                    TLSVersion.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384.value,
                    TLSVersion.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256.value
                ],
                extensions=[
                    "server_name",
                    "status_request",
                    "supported_groups",
                    "ec_point_formats",
                    "signature_algorithms",
                    "application_layer_protocol_negotiation",
                    "signed_certificate_timestamp",
                    "key_share",
                    "psk_key_exchange_modes",
                    "supported_versions",
                    "compress_certificate",
                    "application_settings"
                ]
            ),
            utls_config={
                "client": "chrome",
                "version": "120",
                "platform": "windows"
            }
        )

        # Chrome 120 on macOS
        self.fingerprint_profiles["chrome_120_macos"] = TLSFingerprintProfile(
            name="Chrome 120 on macOS",
            browser_type="chrome",
            browser_version="120.0.0.0",
            operating_system="macos",
            client_hello_config=TLSClientHelloConfig(
                version="tls1.3",
                cipher_suites=[
                    TLSVersion.TLS_AES_128_GCM_SHA256.value,
                    TLSVersion.TLS_AES_256_GCM_SHA384.value,
                    TLSVersion.TLS_CHACHA20_POLY1305_SHA256.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256.value
                ],
                extensions=[
                    "server_name",
                    "status_request",
                    "supported_groups",
                    "ec_point_formats",
                    "signature_algorithms",
                    "application_layer_protocol_negotiation",
                    "signed_certificate_timestamp",
                    "key_share",
                    "psk_key_exchange_modes",
                    "supported_versions",
                    "compress_certificate"
                ]
            ),
            utls_config={
                "client": "chrome",
                "version": "120",
                "platform": "macos"
            }
        )

        # Firefox 121 on Windows
        self.fingerprint_profiles["firefox_121_windows"] = TLSFingerprintProfile(
            name="Firefox 121 on Windows",
            browser_type="firefox",
            browser_version="121.0.0.0",
            operating_system="windows",
            client_hello_config=TLSClientHelloConfig(
                version="tls1.3",
                cipher_suites=[
                    TLSVersion.TLS_AES_128_GCM_SHA256.value,
                    TLSVersion.TLS_CHACHA20_POLY1305_SHA256.value,
                    TLSVersion.TLS_AES_256_GCM_SHA384.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384.value
                ],
                extensions=[
                    "server_name",
                    "status_request",
                    "supported_groups",
                    "ec_point_formats",
                    "signature_algorithms",
                    "application_layer_protocol_negotiation",
                    "signed_certificate_timestamp",
                    "key_share",
                    "psk_key_exchange_modes",
                    "supported_versions",
                    "record_size_limit"
                ]
            ),
            utls_config={
                "client": "firefox",
                "version": "121",
                "platform": "windows"
            }
        )

        # Safari 17 on macOS
        self.fingerprint_profiles["safari_17_macos"] = TLSFingerprintProfile(
            name="Safari 17 on macOS",
            browser_type="safari",
            browser_version="17.0.0.0",
            operating_system="macos",
            client_hello_config=TLSClientHelloConfig(
                version="tls1.3",
                cipher_suites=[
                    TLSVersion.TLS_AES_128_GCM_SHA256.value,
                    TLSVersion.TLS_AES_256_GCM_SHA384.value,
                    TLSVersion.TLS_CHACHA20_POLY1305_SHA256.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384.value,
                    TLSVersion.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256.value
                ],
                extensions=[
                    "server_name",
                    "status_request",
                    "supported_groups",
                    "ec_point_formats",
                    "signature_algorithms",
                    "application_layer_protocol_negotiation",
                    "signed_certificate_timestamp",
                    "key_share",
                    "psk_key_exchange_modes",
                    "supported_versions"
                ]
            ),
            utls_config={
                "client": "safari",
                "version": "17",
                "platform": "macos"
            }
        )

        logger.info(f"Loaded {len(self.fingerprint_profiles)} default TLS fingerprint profiles")

    def get_profile(self, profile_id: str) -> Optional[TLSFingerprintProfile]:
        """
        Get TLS fingerprint profile by ID.

        Args:
            profile_id: Profile identifier

        Returns:
            TLS fingerprint profile if found
        """
        return self.fingerprint_profiles.get(profile_id)

    def list_profiles(self) -> List[str]:
        """List all available profile IDs."""
        return list(self.fingerprint_profiles.keys())

    def add_profile(self, profile: TLSFingerprintProfile):
        """
        Add a new TLS fingerprint profile.

        Args:
            profile: Profile to add
        """
        self.fingerprint_profiles[profile.name] = profile
        logger.info(f"Added TLS fingerprint profile: {profile.name}")

    def generate_fingerprint(
        self,
        browser_type: str,
        browser_version: str,
        operating_system: str,
        randomize: bool = True
    ) -> TLSFingerprint:
        """
        Generate a TLS fingerprint for the given browser and OS.

        Args:
            browser_type: Browser type (chrome, firefox, safari, edge)
            browser_version: Browser version
            operating_system: Operating system (windows, macos, linux)
            randomize: Whether to randomize certain parameters

        Returns:
            Generated TLS fingerprint
        """
        # Find base profile
        base_profile_id = f"{browser_type}_{browser_version.split('.')[0]}_{operating_system}"
        base_profile = self.get_profile(base_profile_id)

        if not base_profile:
            # Fallback to generic profile
            base_profile = self.get_profile("chrome_120_windows")

        if not base_profile:
            raise ValueError("No suitable TLS fingerprint profile found")

        # Create fingerprint
        config = base_profile.client_hello_config

        if randomize:
            config = self._randomize_config(config)

        # Calculate JA3 hash
        ja3_hash = self._calculate_ja3_hash(config)

        # Create uTLS config
        utls_config = base_profile.utls_config.copy()
        if randomize:
            utls_config["randomized"] = True

        return TLSFingerprint(
            id=f"{browser_type}_{browser_version}_{operating_system}",
            utls_config=utls_config,
            ja3_hash=ja3_hash,
            cipher_suites=config.cipher_suites,
            extensions=config.extensions,
            version=config.version
        )

    def _randomize_config(self, config: TLSClientHelloConfig) -> TLSClientHelloConfig:
        """
        Randomize TLS configuration parameters.

        Args:
            config: Base configuration

        Returns:
            Randomized configuration
        """
        # Randomize cipher suite order
        cipher_suites = config.cipher_suites.copy()
        secrets.SystemRandom().shuffle(cipher_suites)

        # Randomize extension order (keep critical ones first)
        critical_extensions = ["server_name", "supported_versions", "key_share"]
        other_extensions = [ext for ext in config.extensions if ext not in critical_extensions]
        secrets.SystemRandom().shuffle(other_extensions)
        extensions = critical_extensions + other_extensions

        # Randomize elliptic curves order
        elliptic_curves = config.elliptic_curves.copy()
        secrets.SystemRandom().shuffle(elliptic_curves)

        return TLSClientHelloConfig(
            version=config.version,
            cipher_suites=cipher_suites,
            extensions=extensions,
            elliptic_curves=elliptic_curves,
            signature_algorithms=config.signature_algorithms.copy(),
            alpn_protocols=config.alpn_protocols.copy(),
            key_share_groups=config.key_share_groups.copy(),
            psk_modes=config.psk_modes.copy(),
            supported_versions=config.supported_versions.copy()
        )

    def _calculate_ja3_hash(self, config: TLSClientHelloConfig) -> str:
        """
        Calculate JA3 hash from TLS configuration.

        Args:
            config: TLS configuration

        Returns:
            JA3 hash string
        """
        # JA3 format: SSLVersion,CipherSuites,Extensions,EllipticCurves,SignatureAlgorithms
        ja3_string = ",".join([
            self._get_tls_version_number(config.version),
            "-".join(self._get_cipher_suite_numbers(config.cipher_suites)),
            "-".join(self._get_extension_numbers(config.extensions)),
            "-".join(self._get_elliptic_curve_numbers(config.elliptic_curves)),
            "-".join(self._get_signature_algorithm_numbers(config.signature_algorithms))
        ])

        # Calculate MD5 hash
        return hashlib.md5(ja3_string.encode()).hexdigest()

    def _get_tls_version_number(self, version: str) -> str:
        """Get TLS version number."""
        version_mapping = {
            "tls1.0": "771",
            "tls1.1": "772",
            "tls1.2": "771",
            "tls1.3": "771"
        }
        return version_mapping.get(version, "771")

    def _get_cipher_suite_numbers(self, cipher_suites: List[str]) -> List[str]:
        """Get cipher suite numbers."""
        # Simplified mapping - in practice, this would be more comprehensive
        suite_mapping = {
            "TLS_AES_128_GCM_SHA256": "1301",
            "TLS_AES_256_GCM_SHA384": "1302",
            "TLS_CHACHA20_POLY1305_SHA256": "1303",
            "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256": "c02b",
            "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384": "c02c",
            "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256": "cca9",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256": "c09c",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384": "c09d",
            "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256": "cca8"
        }

        return [suite_mapping.get(suite, suite) for suite in cipher_suites]

    def _get_extension_numbers(self, extensions: List[str]) -> List[str]:
        """Get extension numbers."""
        # Simplified mapping
        extension_mapping = {
            "server_name": "0",
            "status_request": "5",
            "supported_groups": "10",
            "ec_point_formats": "11",
            "signature_algorithms": "13",
            "application_layer_protocol_negotiation": "16",
            "signed_certificate_timestamp": "18",
            "key_share": "51",
            "psk_key_exchange_modes": "45",
            "supported_versions": "43",
            "compress_certificate": "27",
            "application_settings": "17513",
            "record_size_limit": "22"
        }

        return [extension_mapping.get(ext, ext) for ext in extensions]

    def _get_elliptic_curve_numbers(self, curves: List[str]) -> List[str]:
        """Get elliptic curve numbers."""
        curve_mapping = {
            "secp256r1": "23",
            "secp384r1": "24",
            "secp521r1": "25",
            "x25519": "29"
        }

        return [curve_mapping.get(curve, curve) for curve in curves]

    def _get_signature_algorithm_numbers(self, algorithms: List[str]) -> List[str]:
        """Get signature algorithm numbers."""
        algorithm_mapping = {
            "ecdsa_secp256r1_sha256": "1023",
            "ecdsa_secp384r1_sha384": "1024",
            "ecdsa_secp521r1_sha512": "1025",
            "rsa_pss_rsae_sha256": "2052",
            "rsa_pss_rsae_sha384": "2053",
            "rsa_pss_rsae_sha512": "2054",
            "rsa_pkcs1_sha256": "1027",
            "rsa_pkcs1_sha384": "1280",
            "rsa_pkcs1_sha512": "1537"
        }

        return [algorithm_mapping.get(algo, algo) for algo in algorithms]

    def validate_fingerprint(self, fingerprint: TLSFingerprint) -> List[str]:
        """
        Validate TLS fingerprint.

        Args:
            fingerprint: Fingerprint to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Check required fields
        if not fingerprint.id:
            issues.append("Missing fingerprint ID")

        if not fingerprint.version:
            issues.append("Missing TLS version")

        if not fingerprint.cipher_suites:
            issues.append("Missing cipher suites")

        if not fingerprint.extensions:
            issues.append("Missing TLS extensions")

        # Validate version
        valid_versions = ["tls1.0", "tls1.1", "tls1.2", "tls1.3"]
        if fingerprint.version not in valid_versions:
            issues.append(f"Invalid TLS version: {fingerprint.version}")

        # Validate cipher suites
        if fingerprint.cipher_suites:
            valid_suites = [suite.value for suite in CipherSuite]
            for suite in fingerprint.cipher_suites:
                if suite not in valid_suites:
                    issues.append(f"Unknown cipher suite: {suite}")

        # Validate uTLS config
        if fingerprint.utls_config:
            required_utls_fields = ["client", "version", "platform"]
            for field in required_utls_fields:
                if field not in fingerprint.utls_config:
                    issues.append(f"Missing uTLS config field: {field}")

        return issues


class TLSClientHelloBuilder:
    """
    Builder for TLS ClientHello messages.

    This class provides functionality to build TLS ClientHello messages
    from fingerprint configurations.
    """

    def __init__(self, fingerprint_manager: TLSFingerprintManager):
        """
        Initialize ClientHello builder.

        Args:
            fingerprint_manager: TLS fingerprint manager
        """
        self.fingerprint_manager = fingerprint_manager

    def build_client_hello(self, fingerprint: TLSFingerprint) -> Dict[str, Any]:
        """
        Build ClientHello message from fingerprint.

        Args:
            fingerprint: TLS fingerprint

        Returns:
            ClientHello message configuration
        """
        # Get corresponding profile
        profile_id = fingerprint.id.replace("_rotated", "")
        profile = self.fingerprint_manager.get_profile(profile_id)

        if not profile:
            raise ValueError(f"No profile found for fingerprint: {fingerprint.id}")

        config = profile.client_hello_config

        return {
            "version": config.version,
            "cipher_suites": config.cipher_suites,
            "extensions": config.extensions,
            "elliptic_curves": config.elliptic_curves,
            "signature_algorithms": config.signature_algorithms,
            "alpn_protocols": config.alpn_protocols,
            "key_share_groups": config.key_share_groups,
            "psk_modes": config.psk_modes,
            "supported_versions": config.supported_versions,
            "ja3_hash": fingerprint.ja3_hash,
            "utls_config": fingerprint.utls_config
        }

    def build_client_hello_json(self, fingerprint: TLSFingerprint) -> str:
        """
        Build ClientHello message as JSON string.

        Args:
            fingerprint: TLS fingerprint

        Returns:
            JSON string of ClientHello configuration
        """
        client_hello = self.build_client_hello(fingerprint)
        return json.dumps(client_hello, indent=2)

    def generate_client_hello_variants(
        self,
        base_fingerprint: TLSFingerprint,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple ClientHello variants from base fingerprint.

        Args:
            base_fingerprint: Base TLS fingerprint
            count: Number of variants to generate

        Returns:
            List of ClientHello configurations
        """
        variants = []

        for i in range(count):
            # Create a slightly modified fingerprint
            variant_fingerprint = TLSFingerprint(
                id=f"{base_fingerprint.id}_variant_{i}",
                utls_config=base_fingerprint.utls_config.copy(),
                ja3_hash=None,  # Will be recalculated
                cipher_suites=base_fingerprint.cipher_suites.copy(),
                extensions=base_fingerprint.extensions.copy(),
                version=base_fingerprint.version
            )

            # Randomize some parameters
            secrets.SystemRandom().shuffle(variant_fingerprint.cipher_suites)
            secrets.SystemRandom().shuffle(variant_fingerprint.extensions)

            # Recalculate JA3 hash
            config = self.fingerprint_manager._randomize_config(
                self.fingerprint_manager.get_profile(base_fingerprint.id).client_hello_config
            )
            variant_fingerprint.ja3_hash = self.fingerprint_manager._calculate_ja3_hash(config)

            # Build ClientHello
            client_hello = self.build_client_hello(variant_fingerprint)
            variants.append(client_hello)

        return variants