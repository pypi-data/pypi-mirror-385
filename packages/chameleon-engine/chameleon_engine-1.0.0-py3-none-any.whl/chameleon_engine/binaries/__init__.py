"""
Chameleon Engine - Binary Installation Module

This module handles the automatic installation and management of
Go-based proxy binaries for different platforms.
"""

import os
import sys
import platform
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BinaryInstaller:
    """
    Handles installation and management of platform-specific binaries.
    """

    def __init__(self, package_dir: Optional[Path] = None):
        """
        Initialize the binary installer.

        Args:
            package_dir: Directory where binaries are stored
        """
        if package_dir is None:
            # Use the package's binaries directory
            self.package_dir = Path(__file__).parent
        else:
            self.package_dir = package_dir

        self.binary_name = "chameleon-proxy"
        self.platform_mapping_file = self.package_dir / "platform_mapping.json"
        self.install_dirs = self._get_install_directories()

    def _get_install_directories(self) -> list[Path]:
        """
        Get potential installation directories in order of preference.
        """
        directories = []

        # User-specific bin directory (most accessible)
        if platform.system() == "Windows":
            directories.append(Path.home() / "AppData" / "Local" / "Programs" / "ChameleonEngine" / "bin")
        else:
            directories.append(Path.home() / ".local" / "bin")

        # System-wide bin directories
        if platform.system() != "Windows":
            directories.append(Path("/usr/local/bin"))

        # Virtual environment bin directory
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            venv_bin = Path(sys.prefix) / "bin"
            directories.append(venv_bin)

        # Package directory (fallback)
        directories.append(self.package_dir)

        return directories

    def get_platform_info(self) -> Dict[str, str]:
        """
        Get current platform information.

        Returns:
            Dictionary with platform details
        """
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Normalize architecture names
        arch_mapping = {
            "x86_64": "amd64",
            "amd64": "amd64",
            "intel": "amd64",
            "arm64": "arm64",
            "aarch64": "arm64",
            "arm": "arm64"
        }

        arch = arch_mapping.get(machine, "amd64")

        return {
            "system": system,
            "arch": arch,
            "platform_key": f"{system}-{arch}"
        }

    def get_platform_binary_name(self) -> str:
        """
        Get the binary name for the current platform.

        Returns:
            Binary filename for current platform
        """
        platform_info = self.get_platform_info()
        system = platform_info["system"]
        arch = platform_info["arch"]

        # Windows binaries have .exe extension
        extension = ".exe" if system == "windows" else ""

        return f"{self.binary_name}-{system}-{arch}{extension}"

    def find_package_binary(self) -> Optional[Path]:
        """
        Find the binary in the package directory.

        Returns:
            Path to binary if found, None otherwise
        """
        binary_name = self.get_platform_binary_name()
        binary_path = self.package_dir / binary_name

        if binary_path.exists():
            logger.debug(f"Found package binary: {binary_path}")
            return binary_path

        logger.warning(f"Package binary not found: {binary_path}")
        return None

    def load_platform_mapping(self) -> Dict[str, Any]:
        """
        Load platform mapping from JSON file.

        Returns:
            Platform mapping dictionary
        """
        if not self.platform_mapping_file.exists():
            logger.warning("Platform mapping file not found")
            return {}

        try:
            with open(self.platform_mapping_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load platform mapping: {e}")
            return {}

    def get_installed_binary(self) -> Optional[Path]:
        """
        Find an already installed binary.

        Returns:
            Path to installed binary if found, None otherwise
        """
        binary_name = self.binary_name
        if platform.system() == "Windows":
            binary_name += ".exe"

        for install_dir in self.install_dirs:
            binary_path = install_dir / binary_name
            if binary_path.exists() and binary_path.is_file():
                logger.debug(f"Found installed binary: {binary_path}")
                return binary_path

        return None

    def install_binary(self, force: bool = False) -> Optional[Path]:
        """
        Install the appropriate binary for the current platform.

        Args:
            force: Force installation even if binary already exists

        Returns:
            Path to installed binary if successful, None otherwise
        """
        # Check if binary is already installed
        if not force:
            existing_binary = self.get_installed_binary()
            if existing_binary:
                logger.info(f"Binary already installed: {existing_binary}")
                return existing_binary

        # Find the package binary
        package_binary = self.find_package_binary()
        if not package_binary:
            logger.error("No package binary found for current platform")
            return None

        # Determine installation directory
        install_dir = self._choose_install_directory()
        if not install_dir:
            logger.error("No suitable installation directory found")
            return None

        # Create installation directory if it doesn't exist
        try:
            install_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create install directory {install_dir}: {e}")
            return None

        # Determine target binary name
        target_name = self.binary_name
        if platform.system() == "Windows":
            target_name += ".exe"

        target_path = install_dir / target_name

        # Copy binary
        try:
            shutil.copy2(package_binary, target_path)

            # Make executable on Unix systems
            if platform.system() != "Windows":
                target_path.chmod(0o755)

            logger.info(f"Successfully installed binary to: {target_path}")
            return target_path

        except Exception as e:
            logger.error(f"Failed to install binary: {e}")
            return None

    def _choose_install_directory(self) -> Optional[Path]:
        """
        Choose the best installation directory.

        Returns:
            Best installation directory if available, None otherwise
        """
        for install_dir in self.install_dirs:
            # Try to create a test file to check writability
            try:
                test_file = install_dir / ".chameleon_test"
                install_dir.mkdir(parents=True, exist_ok=True)
                test_file.touch()
                test_file.unlink()
                return install_dir
            except Exception:
                continue

        return None

    def get_binary_path(self) -> Optional[Path]:
        """
        Get the path to the binary, installing if necessary.

        Returns:
            Path to binary if available, None otherwise
        """
        # First try to find installed binary
        binary = self.get_installed_binary()
        if binary:
            return binary

        # Try to install from package
        return self.install_binary()

    def is_binary_available(self) -> bool:
        """
        Check if the binary is available (either installed or in package).

        Returns:
            True if binary is available, False otherwise
        """
        return (self.get_installed_binary() is not None or
                self.find_package_binary() is not None)

    def get_version_info(self) -> Dict[str, Any]:
        """
        Get version and build information.

        Returns:
            Version information dictionary
        """
        mapping = self.load_platform_mapping()
        binary_path = self.get_installed_binary() or self.find_package_binary()

        info = {
            "platform": self.get_platform_info(),
            "binary_available": binary_path is not None,
            "binary_path": str(binary_path) if binary_path else None,
            "package_version": mapping.get("version", "unknown"),
            "build_date": mapping.get("build_date", "unknown")
        }

        return info

    def cleanup_old_installations(self) -> None:
        """
        Clean up old or duplicate installations.
        """
        binary_name = self.binary_name
        if platform.system() == "Windows":
            binary_name += ".exe"

        found_binaries = []

        for install_dir in self.install_dirs:
            binary_path = install_dir / binary_name
            if binary_path.exists():
                found_binaries.append(binary_path)

        # Keep only the first (most preferred) binary
        if len(found_binaries) > 1:
            logger.info(f"Found {len(found_binaries)} installations, cleaning up duplicates")
            keep_binary = found_binaries[0]

            for binary in found_binaries[1:]:
                try:
                    binary.unlink()
                    logger.info(f"Removed duplicate binary: {binary}")
                except Exception as e:
                    logger.warning(f"Failed to remove duplicate binary {binary}: {e}")


# Global installer instance
_installer = None

def get_installer() -> BinaryInstaller:
    """
    Get the global binary installer instance.

    Returns:
        BinaryInstaller instance
    """
    global _installer
    if _installer is None:
        _installer = BinaryInstaller()
    return _installer


def ensure_binary_installed() -> Optional[Path]:
    """
    Ensure the binary is installed and return its path.

    Returns:
        Path to installed binary if successful, None otherwise
    """
    installer = get_installer()
    return installer.get_binary_path()


def is_proxy_available() -> bool:
    """
    Check if the proxy binary is available.

    Returns:
        True if proxy binary is available, False otherwise
    """
    installer = get_installer()
    return installer.is_binary_available()


# Installation hook that runs during package installation
def install_on_import() -> None:
    """
    Auto-install binary when package is imported.
    This is called from __init__.py
    """
    try:
        installer = get_installer()
        if installer.is_binary_available():
            binary_path = installer.get_binary_path()
            if binary_path:
                logger.info(f"Chameleon Proxy binary available: {binary_path}")
            else:
                logger.info("Chameleon Proxy binary package found, ready to install")
        else:
            logger.warning("Chameleon Proxy binary not found for this platform")
            logger.info("Install with: pip install chameleon-engine[full]")
    except Exception as e:
        logger.error(f"Failed to initialize binary installer: {e}")