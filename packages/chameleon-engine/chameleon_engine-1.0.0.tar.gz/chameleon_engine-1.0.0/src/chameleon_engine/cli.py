#!/usr/bin/env python3
"""
Chameleon Engine CLI - Command Line Interface

Provides comprehensive CLI for managing Chameleon Engine including proxy rotation.
"""

import asyncio
import click
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from .core import ChameleonEngine
from .fingerprint.client import FingerprintClient


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Chameleon Engine - Advanced Stealth Web Scraping Framework"""
    pass


@cli.group()
def proxy():
    """Proxy management commands"""
    pass


@proxy.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--proxy-list', '-p', help='Comma-separated list of proxy URLs')
@click.option('--strategy', '-s', default='round_robin',
              type=click.Choice(['round_robin', 'random', 'weighted', 'least_connections']),
              help='Rotation strategy')
def configure(config, proxy_list, strategy):
    """Configure proxy rotation settings"""

    async def _configure():
        engine = ChameleonEngine()
        await engine.initialize()

        if config:
            # Load from configuration file
            with open(config, 'r') as f:
                config_data = yaml.safe_load(f)

            if 'proxy_pool' in config_data:
                result = await engine.configure_proxy_rotation(config_data)
                click.echo(f"✅ Proxy rotation configured from {config}")
                click.echo(json.dumps(result, indent=2))
            else:
                click.echo("❌ No proxy_pool configuration found in file")

        elif proxy_list:
            # Configure from command line
            proxies = [p.strip() for p in proxy_list.split(',')]
            config_data = {
                'proxy_pool': {
                    'proxies': proxies,
                    'strategy': strategy,
                    'health_check': True
                }
            }

            result = await engine.configure_proxy_rotation(config_data)
            click.echo(f"✅ Proxy rotation configured with {len(proxies)} proxies")
            click.echo(f"   Strategy: {strategy}")
            click.echo(json.dumps(result, indent=2))

        else:
            click.echo("❌ Please provide either --config or --proxy-list")

        await engine.cleanup()

    asyncio.run(_configure())


@proxy.command()
@click.option('--count', '-n', default=1, help='Number of rotations to perform')
@click.option('--delay', '-d', default=1.0, help='Delay between rotations in seconds')
def rotate(count, delay):
    """Manually rotate proxy"""

    async def _rotate():
        engine = ChameleonEngine()
        await engine.initialize()

        for i in range(count):
            click.echo(f"🔄 Rotating proxy {i+1}/{count}...")

            try:
                result = await engine.rotate_proxy()
                click.echo(f"✅ Rotation successful: {result.get('message', 'Done')}")

                if i < count - 1:
                    await asyncio.sleep(delay)

            except Exception as e:
                click.echo(f"❌ Rotation failed: {e}")

        await engine.cleanup()

    asyncio.run(_rotate())


@proxy.command()
def status():
    """Show current proxy status and statistics"""

    async def _status():
        engine = ChameleonEngine()
        await engine.initialize()

        try:
            status = await engine.get_proxy_status()

            click.echo("📊 Proxy Service Status")
            click.echo("=" * 40)

            # Service status
            click.echo(f"Service: {status.get('status', 'unknown')}")
            click.echo(f"Uptime: {status.get('uptime', 'unknown')}")
            click.echo(f"Version: {status.get('version', 'unknown')}")

            # Statistics
            stats = status.get('stats', {})
            if stats:
                click.echo("\n📈 Statistics:")
                click.echo(f"  Total Requests: {stats.get('total_requests', 0)}")
                click.echo(f"  Active Connections: {stats.get('active_connections', 0)}")
                click.echo(f"  Bytes Sent: {stats.get('total_bytes_sent', 0):,}")
                click.echo(f"  Bytes Received: {stats.get('total_bytes_received', 0):,}")
                click.echo(f"  Average Latency: {stats.get('average_latency', 0):.3f}s")
                click.echo(f"  Requests/Second: {stats.get('requests_per_second', 0):.2f}")

            # Current configuration
            config = status.get('config', {})
            if config:
                click.echo("\n⚙️  Configuration:")
                click.echo(f"  Rotation Strategy: {config.get('rotation_strategy', 'unknown')}")
                click.echo(f"  Proxy Pool Size: {config.get('proxy_pool_size', 0)}")
                click.echo(f"  Health Check: {'Enabled' if config.get('health_check') else 'Disabled'}")

            # Recent connections
            connections = status.get('recent_connections', [])
            if connections:
                click.echo(f"\n🔗 Recent Connections ({len(connections)}):")
                for conn in connections[:5]:  # Show last 5
                    click.echo(f"  {conn.get('method', 'N/A')} {conn.get('target_url', 'N/A')} - {conn.get('status_code', 'N/A')}")

        except Exception as e:
            click.echo(f"❌ Failed to get status: {e}")

        await engine.cleanup()

    asyncio.run(_status())


@proxy.command()
@click.option('--url', '-u', default='https://httpbin.org/ip', help='Test URL')
@click.option('--requests', '-r', default=10, help='Number of test requests')
@click.option('--concurrent', '-c', default=1, help='Number of concurrent requests')
def test(url, requests, concurrent):
    """Test proxy performance and functionality"""

    async def _test():
        engine = ChameleonEngine()
        await engine.initialize()

        click.echo(f"🧪 Testing proxy performance")
        click.echo(f"   URL: {url}")
        click.echo(f"   Requests: {requests}")
        click.echo(f"   Concurrent: {concurrent}")
        click.echo()

        try:
            results = await engine.test_proxy_performance(
                test_url=url,
                num_requests=requests,
                concurrency=concurrent
            )

            click.echo("📊 Test Results:")
            click.echo("=" * 30)
            click.echo(f"Total Requests: {results.get('total_requests', 0)}")
            click.echo(f"Successful: {results.get('successful_requests', 0)}")
            click.echo(f"Failed: {results.get('failed_requests', 0)}")
            click.echo(f"Success Rate: {results.get('success_rate', 0):.1f}%")
            click.echo(f"Total Time: {results.get('total_time', 0):.2f}s")
            click.echo(f"Requests/Second: {results.get('requests_per_second', 0):.2f}")
            click.echo(f"Average Response Time: {results.get('average_response_time', 0):.3f}s")

            if results.get('response_times'):
                click.echo(f"Min Response Time: {min(results['response_times']):.3f}s")
                click.echo(f"Max Response Time: {max(results['response_times']):.3f}s")

            # Show per-proxy results if available
            per_proxy_results = results.get('per_proxy_results', {})
            if per_proxy_results:
                click.echo("\n📈 Per-Proxy Results:")
                for proxy_id, proxy_results in per_proxy_results.items():
                    click.echo(f"  {proxy_id}:")
                    click.echo(f"    Requests: {proxy_results.get('requests', 0)}")
                    click.echo(f"    Success Rate: {proxy_results.get('success_rate', 0):.1f}%")
                    click.echo(f"    Avg Response Time: {proxy_results.get('avg_response_time', 0):.3f}s")

        except Exception as e:
            click.echo(f"❌ Test failed: {e}")

        await engine.cleanup()

    asyncio.run(_test())


@proxy.command()
@click.option('--duration', '-d', default=60, help='Monitoring duration in seconds')
@click.option('--interval', '-i', default=5, help='Update interval in seconds')
def monitor(duration, interval):
    """Monitor proxy activity in real-time"""

    async def _monitor():
        engine = ChameleonEngine()
        await engine.initialize()

        click.echo(f"👁️  Monitoring proxy activity for {duration} seconds")
        click.echo("Press Ctrl+C to stop monitoring early")
        click.echo()

        try:
            start_time = asyncio.get_event_loop().time()

            while True:
                current_time = asyncio.get_event_loop().time()
                elapsed = current_time - start_time

                if elapsed >= duration:
                    break

                try:
                    status = await engine.get_proxy_status()
                    stats = status.get('stats', {})

                    # Clear line and show status
                    click.echo(f"\r⏱️  {elapsed:.0f}s | "
                             f"Requests: {stats.get('total_requests', 0)} | "
                             f"Active: {stats.get('active_connections', 0)} | "
                             f"Latency: {stats.get('average_latency', 0):.3f}s | "
                             f"RPS: {stats.get('requests_per_second', 0):.1f}",
                             nl=False)

                    await asyncio.sleep(interval)

                except KeyboardInterrupt:
                    click.echo("\n\n⏹️  Monitoring stopped by user")
                    break
                except Exception as e:
                    click.echo(f"\n❌ Monitoring error: {e}")
                    break

            click.echo("\n✅ Monitoring completed")

        except Exception as e:
            click.echo(f"❌ Failed to start monitoring: {e}")

        await engine.cleanup()

    asyncio.run(_monitor())


@cli.group()
def fingerprint():
    """Fingerprint management commands"""
    pass


@fingerprint.command()
@click.option('--count', '-n', default=10, help='Number of fingerprints to list')
def list(count):
    """List available browser fingerprints"""

    async def _list():
        client = FingerprintClient("http://localhost:8000")

        try:
            profiles = await client.get_profiles()

            click.echo(f"📋 Available Browser Fingerprints (showing {min(count, len(profiles))}):")
            click.echo("=" * 80)

            for i, profile in enumerate(profiles[:count]):
                browser = profile.user_agent.split()[0] if profile.user_agent else "Unknown"
                click.echo(f"{i+1:2d}. {browser:15s} | "
                             f"{profile.id[:8]:8s}... | "
                             f"{profile.ja3_hash[:16]:16s}... | "
                             f"Uses: {profile.usage_count}")

        except Exception as e:
            click.echo(f"❌ Failed to list fingerprints: {e}")

    asyncio.run(_list())


@fingerprint.command()
@click.option('--browser', '-b', type=click.Choice(['chrome', 'firefox', 'safari', 'edge']), help='Browser type')
@click.option('--os', '-o', type=click.Choice(['windows', 'linux', 'macos']), help='Operating system')
@click.option('--random', '-r', is_flag=True, help='Generate random profile')
def create(browser, os, random):
    """Create a new browser fingerprint"""

    async def _create():
        client = FingerprintClient("http://localhost:8000")

        try:
            if random:
                config = {"random": True}
            else:
                config = {
                    "browser_type": browser or "chrome",
                    "os": os or "windows",
                    "version": "120.0.0.0",
                    "screen_resolution": "1920x1080"
                }

            profile = await client.create_profile(config)

            click.echo("✅ Fingerprint created successfully:")
            click.echo(f"   ID: {profile.id}")
            click.echo(f"   Browser: {profile.user_agent}")
            click.echo(f"   JA3 Hash: {profile.ja3_hash}")
            click.echo(f"   JA4 Hash: {profile.ja4_hash}")

        except Exception as e:
            click.echo(f"❌ Failed to create fingerprint: {e}")

    asyncio.run(_create())


if __name__ == '__main__':
    cli()