"""
Chameleon Engine - Proxy Launcher

This module provides a launcher for the Go-based proxy service.
It handles binary discovery, installation, and execution.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import argparse
import json
import logging

from .binaries import get_installer, ensure_binary_installed, is_proxy_available

logger = logging.getLogger(__name__)


class ProxyLauncher:
    """
    Launcher for the Chameleon Proxy service.
    """

    def __init__(self):
        """Initialize the proxy launcher."""
        self.installer = get_installer()
        self.binary_path: Optional[Path] = None
        self.process: Optional[subprocess.Popen] = None
        self.config_file: Optional[Path] = None
        self.args: List[str] = []

    def find_binary(self) -> bool:
        """
        Find and ensure the proxy binary is available.

        Returns:
            True if binary is available, False otherwise
        """
        if not is_proxy_available():
            print("❌ Chameleon Proxy binary not found!")
            print("💡 Please install with: pip install chameleon-engine[full]")
            return False

        self.binary_path = ensure_binary_installed()
        if not self.binary_path:
            print("❌ Failed to install proxy binary!")
            return False

        print(f"✅ Found proxy binary: {self.binary_path}")
        return True

    def find_config_file(self, config_path: Optional[str] = None) -> Optional[Path]:
        """
        Find configuration file.

        Args:
            config_path: Path to config file (optional)

        Returns:
            Path to config file if found, None otherwise
        """
        if config_path:
            config_file = Path(config_path)
            if config_file.exists():
                return config_file
            else:
                print(f"❌ Config file not found: {config_file}")
                return None

        # Search for config files in standard locations
        config_names = [
            "chameleon-proxy.yaml",
            "config.yaml",
            "proxy.yaml",
            "config.yml",
            "proxy.yml"
        ]

        search_paths = [
            Path.cwd(),
            Path.home() / ".chameleon",
            Path(__file__).parent / "config",
            Path("/etc/chameleon")
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for config_name in config_names:
                config_file = search_path / config_name
                if config_file.exists():
                    print(f"✅ Found config file: {config_file}")
                    return config_file

        print("⚠️ No config file found, using defaults")
        return None

    def prepare_arguments(self, args: List[str]) -> None:
        """
        Prepare arguments for the proxy binary.

        Args:
            args: Command line arguments
        """
        self.args = []

        # Parse command line arguments
        parser = argparse.ArgumentParser(
            prog="chameleon-proxy",
            description="Chameleon Engine - Go-based Proxy Service"
        )

        parser.add_argument(
            "--config", "-c",
            type=str,
            help="Path to configuration file"
        )

        parser.add_argument(
            "--port", "-p",
            type=int,
            default=8080,
            help="Port to listen on (default: 8080)"
        )

        parser.add_argument(
            "--host",
            type=str,
            default="localhost",
            help="Host to bind to (default: localhost)"
        )

        parser.add_argument(
            "--debug", "-d",
            action="store_true",
            help="Enable debug mode"
        )

        parser.add_argument(
            "--log-level",
            choices=["debug", "info", "warn", "error"],
            default="info",
            help="Log level (default: info)"
        )

        parser.add_argument(
            "--version", "-v",
            action="store_true",
            help="Show version information"
        )

        parser.add_argument(
            "--help", "-h",
            action="store_true",
            help="Show help message"
        )

        # Parse known args, pass unknown args to proxy
        parsed_args, unknown_args = parser.parse_known_args(args)

        # Handle special cases
        if parsed_args.version:
            self.show_version()
            sys.exit(0)

        if parsed_args.help:
            parser.print_help()
            sys.exit(0)

        # Find config file
        if parsed_args.config:
            self.config_file = self.find_config_file(parsed_args.config)
        else:
            self.config_file = self.find_config_file()

        # Build arguments for proxy binary
        if self.config_file:
            self.args.extend(["--config", str(self.config_file)])

        self.args.extend(["--port", str(parsed_args.port)])
        self.args.extend(["--host", parsed_args.host])

        if parsed_args.debug:
            self.args.append("--debug")

        self.args.extend(["--log-level", parsed_args.log_level])

        # Add unknown arguments (pass-through)
        self.args.extend(unknown_args)

    def show_version(self) -> None:
        """Show version information."""
        version_info = self.installer.get_version_info()

        print("Chameleon Proxy Service")
        print(f"Version: {version_info.get('package_version', 'unknown')}")
        print(f"Build Date: {version_info.get('build_date', 'unknown')}")
        print(f"Platform: {version_info['platform']['system']}-{version_info['platform']['arch']}")

        if version_info.get('binary_path'):
            print(f"Binary: {version_info['binary_path']}")
        else:
            print("Binary: Not installed")

    def start_proxy(self, args: List[str]) -> int:
        """
        Start the proxy service.

        Args:
            args: Command line arguments

        Returns:
            Exit code
        """
        # Find binary
        if not self.find_binary():
            return 1

        # Prepare arguments
        self.prepare_arguments(args)

        # Print startup information
        print("🚀 Starting Chameleon Proxy Service...")
        print(f"📁 Binary: {self.binary_path}")
        if self.config_file:
            print(f"⚙️ Config: {self.config_file}")
        if self.args:
            print(f"📝 Arguments: {' '.join(self.args)}")

        try:
            # Start the process
            self.process = subprocess.Popen(
                [str(self.binary_path)] + self.args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )

            # Set up signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                print(f"\nReceived signal {signum}, shutting down...")
                self.stop_proxy()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Stream output
            print("\n📋 Proxy Service Output:")
            print("=" * 50)

            while self.process.poll() is None:
                # Read stdout
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        print(line.strip())

                # Read stderr
                if self.process.stderr:
                    line = self.process.stderr.readline()
                    if line:
                        print(f"ERROR: {line.strip()}", file=sys.stderr)

                time.sleep(0.01)

            # Process has ended
            return_code = self.process.returncode

            if return_code == 0:
                print("\n✅ Proxy service exited successfully")
            else:
                print(f"\n❌ Proxy service exited with code {return_code}")

            return return_code

        except FileNotFoundError:
            print(f"❌ Binary not found: {self.binary_path}")
            return 1
        except PermissionError:
            print(f"❌ Permission denied: {self.binary_path}")
            return 1
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            self.stop_proxy()
            return 130
        except Exception as e:
            print(f"❌ Failed to start proxy: {e}")
            return 1

    def stop_proxy(self) -> None:
        """Stop the proxy service gracefully."""
        if self.process:
            try:
                print("🛑 Stopping proxy service...")
                self.process.terminate()

                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=10)
                    print("✅ Proxy service stopped gracefully")
                except subprocess.TimeoutExpired:
                    print("⚠️ Proxy service didn't stop gracefully, forcing...")
                    self.process.kill()
                    self.process.wait()
                    print("✅ Proxy service stopped forcefully")

            except Exception as e:
                print(f"⚠️ Error stopping proxy service: {e}")

    def install_binary_only(self) -> int:
        """
        Install only the binary without starting the service.

        Returns:
            Exit code
        """
        print("📦 Installing Chameleon Proxy binary...")

        if not self.find_binary():
            return 1

        print(f"✅ Binary installed successfully: {self.binary_path}")
        print("💡 You can now start the service with: chameleon-proxy")
        return 0

    def check_installation(self) -> int:
        """
        Check binary installation status.

        Returns:
            Exit code
        """
        print("🔍 Checking Chameleon Proxy installation...")

        version_info = self.installer.get_version_info()

        print(f"Platform: {version_info['platform']['system']}-{version_info['platform']['arch']}")
        print(f"Binary Available: {'✅ Yes' if version_info['binary_available'] else '❌ No'}")

        if version_info.get('binary_path'):
            print(f"Binary Path: {version_info['binary_path']}")

        print(f"Package Version: {version_info.get('package_version', 'unknown')}")
        print(f"Build Date: {version_info.get('build_date', 'unknown')}")

        return 0 if version_info['binary_available'] else 1


def main() -> int:
    """
    Main entry point for the proxy launcher.

    Returns:
        Exit code
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Parse special launcher commands
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "install":
            launcher = ProxyLauncher()
            return launcher.install_binary_only()

        elif command == "check":
            launcher = ProxyLauncher()
            return launcher.check_installation()

        elif command == "version":
            launcher = ProxyLauncher()
            launcher.show_version()
            return 0

        elif command == "--help" or command == "-h":
            print("""Chameleon Proxy Service Launcher

Usage: chameleon-proxy [COMMAND] [OPTIONS]

Commands:
  (none)     Start the proxy service
  install    Install the proxy binary only
  check      Check installation status
  version    Show version information
  help       Show this help message

Options:
  --config, -c PATH    Path to configuration file
  --port, -p PORT      Port to listen on (default: 8080)
  --host HOST          Host to bind to (default: localhost)
  --debug, -d          Enable debug mode
  --log-level LEVEL    Log level (debug, info, warn, error)
  --version, -v        Show version information

Examples:
  chameleon-proxy                    # Start with defaults
  chameleon-proxy --port 9090       # Start on port 9090
  chameleon-proxy --config my.yaml  # Use custom config
  chameleon-proxy install            # Install binary only
  chameleon-proxy check              # Check installation
""")
            return 0

    # Default: start proxy service
    launcher = ProxyLauncher()
    return launcher.start_proxy(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())