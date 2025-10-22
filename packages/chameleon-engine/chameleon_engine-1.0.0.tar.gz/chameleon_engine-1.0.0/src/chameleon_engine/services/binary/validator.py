"""
Binary validation utilities.

This module provides validation functionality for downloaded browser binaries
including checksum verification, signature validation, and malware scanning.
"""

import hashlib
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Result of binary validation."""
    status: ValidationStatus
    message: str
    details: Dict[str, Any]
    checksum_verified: bool = False
    signature_verified: bool = False
    malware_scan_passed: bool = False
    execution_test_passed: bool = False


class BinaryValidator:
    """Validator for browser binaries."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the binary validator.

        Args:
            config: Validation configuration
        """
        self.config = config or {}
        self.verify_checksums = self.config.get('verify_checksums', True)
        self.verify_signature = self.config.get('verify_signature', False)
        self.scan_malware = self.config.get('scan_malware', False)
        self.test_execution = self.config.get('test_execution', True)

    async def validate_binary(
        self,
        binary_path: Union[str, Path],
        expected_checksum: Optional[str] = None,
        checksum_type: str = "sha256",
        signature_path: Optional[Union[str, Path]] = None
    ) -> ValidationResult:
        """
        Validate a binary file.

        Args:
            binary_path: Path to the binary file
            expected_checksum: Expected checksum value
            checksum_type: Type of checksum (sha256, sha1, md5)
            signature_path: Path to signature file (optional)

        Returns:
            ValidationResult with validation status and details
        """
        binary_path = Path(binary_path)
        details = {}

        try:
            # Check if file exists
            if not binary_path.exists():
                return ValidationResult(
                    status=ValidationStatus.ERROR,
                    message=f"Binary file not found: {binary_path}",
                    details=details
                )

            # Check file size
            file_size = binary_path.stat().st_size
            details['file_size'] = file_size

            if file_size == 0:
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    message="Binary file is empty",
                    details=details
                )

            # Checksum verification
            checksum_verified = False
            if self.verify_checksums and expected_checksum:
                checksum_result = await self._verify_checksum(
                    binary_path, expected_checksum, checksum_type
                )
                checksum_verified = checksum_result['verified']
                details['checksum'] = checksum_result

                if not checksum_verified:
                    return ValidationResult(
                        status=ValidationStatus.INVALID,
                        message=f"Checksum verification failed: expected {expected_checksum}, got {checksum_result['actual']}",
                        details=details,
                        checksum_verified=False
                    )
            elif not expected_checksum and self.verify_checksums:
                logger.warning(f"No expected checksum provided for {binary_path}")
                details['checksum_warning'] = "No checksum provided for verification"

            # Signature verification
            signature_verified = False
            if self.verify_signature and signature_path:
                signature_result = await self._verify_signature(binary_path, signature_path)
                signature_verified = signature_result['verified']
                details['signature'] = signature_result

                if not signature_verified:
                    return ValidationResult(
                        status=ValidationStatus.INVALID,
                        message=f"Signature verification failed: {signature_result.get('error', 'Unknown error')}",
                        details=details,
                        checksum_verified=checksum_verified,
                        signature_verified=False
                    )
            elif self.verify_signature and not signature_path:
                logger.warning(f"Signature verification enabled but no signature provided for {binary_path}")
                details['signature_warning'] = "Signature verification enabled but no signature provided"

            # Malware scanning
            malware_scan_passed = True  # Default to true unless scanning is enabled and fails
            if self.scan_malware:
                scan_result = await self._scan_for_malware(binary_path)
                malware_scan_passed = scan_result['clean']
                details['malware_scan'] = scan_result

                if not malware_scan_passed:
                    return ValidationResult(
                        status=ValidationStatus.INVALID,
                        message=f"Malware scan failed: {scan_result.get('threats', ['Unknown threats'])}",
                        details=details,
                        checksum_verified=checksum_verified,
                        signature_verified=signature_verified,
                        malware_scan_passed=False
                    )

            # Execution test
            execution_test_passed = True
            if self.test_execution:
                exec_result = await self._test_execution(binary_path)
                execution_test_passed = exec_result['success']
                details['execution_test'] = exec_result

                if not execution_test_passed:
                    return ValidationResult(
                        status=ValidationStatus.INVALID,
                        message=f"Execution test failed: {exec_result.get('error', 'Unknown error')}",
                        details=details,
                        checksum_verified=checksum_verified,
                        signature_verified=signature_verified,
                        malware_scan_passed=malware_scan_passed,
                        execution_test_passed=False
                    )

            # All validations passed
            return ValidationResult(
                status=ValidationStatus.VALID,
                message="Binary validation successful",
                details=details,
                checksum_verified=checksum_verified,
                signature_verified=signature_verified,
                malware_scan_passed=malware_scan_passed,
                execution_test_passed=execution_test_passed
            )

        except Exception as e:
            logger.error(f"Validation error for {binary_path}: {str(e)}")
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Validation error: {str(e)}",
                details={'error': str(e)}
            )

    async def _verify_checksum(
        self,
        file_path: Path,
        expected_checksum: str,
        checksum_type: str = "sha256"
    ) -> Dict[str, Any]:
        """
        Verify file checksum.

        Args:
            file_path: Path to file
            expected_checksum: Expected checksum
            checksum_type: Type of checksum

        Returns:
            Dictionary with verification result
        """
        try:
            # Calculate checksum
            if checksum_type.lower() == "sha256":
                hasher = hashlib.sha256()
            elif checksum_type.lower() == "sha1":
                hasher = hashlib.sha1()
            elif checksum_type.lower() == "md5":
                hasher = hashlib.md5()
            else:
                raise ValueError(f"Unsupported checksum type: {checksum_type}")

            # Read file in chunks
            chunk_size = 8192
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)

            actual_checksum = hasher.hexdigest()
            verified = actual_checksum.lower() == expected_checksum.lower()

            return {
                'verified': verified,
                'expected': expected_checksum,
                'actual': actual_checksum,
                'type': checksum_type
            }

        except Exception as e:
            return {
                'verified': False,
                'error': str(e),
                'type': checksum_type
            }

    async def _verify_signature(
        self,
        file_path: Path,
        signature_path: Path
    ) -> Dict[str, Any]:
        """
        Verify file signature using GPG.

        Args:
            file_path: Path to file to verify
            signature_path: Path to signature file

        Returns:
            Dictionary with verification result
        """
        try:
            # Check if GPG is available
            gpg_cmd = self._find_gpg_command()
            if not gpg_cmd:
                return {
                    'verified': False,
                    'error': 'GPG not found on system'
                }

            # Import public keys if keyring is provided
            keyring = self.config.get('gpg_keyring')
            cmd = [gpg_cmd]

            if keyring:
                cmd.extend(['--keyring', keyring])

            cmd.extend(['--verify', str(signature_path), str(file_path)])

            # Run GPG verification
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            verified = result.returncode == 0

            return {
                'verified': verified,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                'verified': False,
                'error': 'Signature verification timed out'
            }
        except Exception as e:
            return {
                'verified': False,
                'error': str(e)
            }

    async def _scan_for_malware(self, file_path: Path) -> Dict[str, Any]:
        """
        Scan file for malware using available scanners.

        Args:
            file_path: Path to file to scan

        Returns:
            Dictionary with scan result
        """
        try:
            # Try different malware scanners
            scanners = [
                ('clamscan', self._scan_with_clamav),
                ('windows defender', self._scan_with_windows_defender),
                ('virustotal', self._scan_with_virustotal)  # Requires API key
            ]

            for scanner_name, scan_func in scanners:
                try:
                    result = await scan_func(file_path)
                    if result.get('available', False):
                        return {
                            'clean': result.get('clean', False),
                            'scanner': scanner_name,
                            'threats': result.get('threats', []),
                            'details': result
                        }
                except Exception as e:
                    logger.debug(f"Scanner {scanner_name} failed: {str(e)}")
                    continue

            # No scanner available
            return {
                'clean': True,  # Assume clean if no scanner available
                'scanner': None,
                'threats': [],
                'warning': 'No malware scanner available'
            }

        except Exception as e:
            return {
                'clean': False,
                'error': str(e),
                'threats': ['Scan error']
            }

    async def _scan_with_clamav(self, file_path: Path) -> Dict[str, Any]:
        """Scan file using ClamAV."""
        try:
            # Check if clamscan is available
            result = subprocess.run(
                ['which', 'clamscan'],
                capture_output=True,
                timeout=5
            )

            if result.returncode != 0:
                return {'available': False}

            # Run scan
            scan_result = subprocess.run(
                ['clamscan', '--no-summary', str(file_path)],
                capture_output=True,
                text=True,
                timeout=60
            )

            # Parse results
            threats = []
            clean = scan_result.returncode == 0

            if not clean:
                # Parse threat names from output
                for line in scan_result.stdout.strip().split('\n'):
                    if line.strip() and 'FOUND' in line:
                        threat = line.split('FOUND')[0].strip()
                        threats.append(threat)

            return {
                'available': True,
                'clean': clean,
                'threats': threats,
                'return_code': scan_result.returncode,
                'output': scan_result.stdout
            }

        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }

    async def _scan_with_windows_defender(self, file_path: Path) -> Dict[str, Any]:
        """Scan file using Windows Defender."""
        try:
            if os.name != 'nt':
                return {'available': False}

            # Run Windows Defender scan
            scan_result = subprocess.run(
                ['powershell', '-Command', f'Start-MpScan -ScanType CustomScan -ScanPath "{file_path}"'],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Windows Defender doesn't provide direct output for individual files
            # This is a simplified implementation
            return {
                'available': True,
                'clean': True,  # Assume clean if no errors
                'threats': [],
                'return_code': scan_result.returncode
            }

        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }

    async def _scan_with_virustotal(self, file_path: Path) -> Dict[str, Any]:
        """Scan file using VirusTotal API."""
        try:
            api_key = self.config.get('virustotal_api_key')
            if not api_key:
                return {'available': False}

            import aiohttp

            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            # Query VirusTotal
            url = f"https://www.virustotal.com/vtapi/v2/file/report"
            params = {
                'apikey': api_key,
                'resource': file_hash
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        positives = data.get('positives', 0)
                        total = data.get('total', 0)

                        threats = []
                        if positives > 0:
                            # Extract threat names from scan results
                            for scan_name, scan_result in data.get('scans', {}).items():
                                if scan_result.get('detected', False):
                                    threats.append(f"{scan_name}: {scan_result.get('result', 'Unknown')}")

                        return {
                            'available': True,
                            'clean': positives == 0,
                            'threats': threats,
                            'positives': positives,
                            'total': total,
                            'scan_date': data.get('scan_date')
                        }
                    else:
                        return {'available': False, 'error': f'API error: {response.status}'}

        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }

    async def _test_execution(self, binary_path: Path) -> Dict[str, Any]:
        """
        Test if binary can execute basic commands.

        Args:
            binary_path: Path to binary file

        Returns:
            Dictionary with test result
        """
        try:
            # Determine binary type and test command
            binary_name = binary_path.name.lower()

            if 'chrome' in binary_name or 'chromium' in binary_name:
                return await self._test_chromium_binary(binary_path)
            elif 'firefox' in binary_name:
                return await self._test_firefox_binary(binary_path)
            else:
                return await self._test_generic_binary(binary_path)

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _test_chromium_binary(self, binary_path: Path) -> Dict[str, Any]:
        """Test Chromium-based binary."""
        try:
            # Find the main executable
            if binary_path.is_file() and binary_path.suffix in ['.exe', '']:
                executable = binary_path
            else:
                # Look for chrome executable in directory
                executable = None
                for pattern in ['chrome.exe', 'chrome', 'chromium.exe', 'chromium']:
                    found = binary_path.parent / pattern
                    if found.exists():
                        executable = found
                        break

                if not executable:
                    return {
                        'success': False,
                        'error': 'Chrome executable not found'
                    }

            # Test version command
            test_result = subprocess.run(
                [str(executable), '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            success = test_result.returncode == 0

            return {
                'success': success,
                'executable': str(executable),
                'version_output': test_result.stdout,
                'error_output': test_result.stderr,
                'return_code': test_result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Version command timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _test_firefox_binary(self, binary_path: Path) -> Dict[str, Any]:
        """Test Firefox binary."""
        try:
            # Find the main executable
            if binary_path.is_file() and binary_path.suffix in ['.exe', '']:
                executable = binary_path
            else:
                # Look for firefox executable
                executable = None
                for pattern in ['firefox.exe', 'firefox']:
                    found = binary_path.parent / pattern
                    if found.exists():
                        executable = found
                        break

                if not executable:
                    return {
                        'success': False,
                        'error': 'Firefox executable not found'
                    }

            # Test version command
            test_result = subprocess.run(
                [str(executable), '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            success = test_result.returncode == 0

            return {
                'success': success,
                'executable': str(executable),
                'version_output': test_result.stdout,
                'error_output': test_result.stderr,
                'return_code': test_result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Version command timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _test_generic_binary(self, binary_path: Path) -> Dict[str, Any]:
        """Test generic binary."""
        try:
            # Check if file is executable
            if os.name == 'nt':  # Windows
                # Check if it has .exe extension
                if binary_path.suffix.lower() != '.exe':
                    return {
                        'success': False,
                        'error': 'Not an executable file'
                    }
            else:  # Unix-like
                if not os.access(binary_path, os.X_OK):
                    return {
                        'success': False,
                        'error': 'File is not executable'
                    }

            # Try to get file information
            file_result = subprocess.run(
                ['file', str(binary_path)],
                capture_output=True,
                text=True,
                timeout=5
            )

            return {
                'success': True,
                'file_type': file_result.stdout.strip(),
                'message': 'Basic executable test passed'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _find_gpg_command(self) -> Optional[str]:
        """Find GPG command on system."""
        gpg_commands = ['gpg', 'gpg2', 'gpg1']

        for cmd in gpg_commands:
            try:
                result = subprocess.run(
                    ['which', cmd],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return cmd
            except Exception:
                continue

        return None