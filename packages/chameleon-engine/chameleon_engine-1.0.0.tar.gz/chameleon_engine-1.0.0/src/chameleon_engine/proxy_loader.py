"""
Proxy Loader Module - Chameleon Engine

This module provides utilities for loading proxies from various sources
including files, APIs, and dynamic generation.
"""

import json
import csv
import os
import random
import time
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, Union
from urllib.parse import urlparse
from dataclasses import dataclass, asdict


@dataclass
class ProxyConfig:
    """Proxy configuration data class."""
    id: str
    url: str
    protocol: str = "http"
    ip: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    auth: Optional[Dict[str, Any]] = None
    country: Optional[str] = None
    weight: int = 1
    max_connections: int = 50
    timeout: int = 30
    retry_count: int = 3
    health_check: bool = True
    headers: Dict[str, str] = None
    tags: List[str] = None
    source: str = "unknown"

    def __post_init__(self):
        """Post-initialization processing."""
        if self.headers is None:
            self.headers = {}
        if self.tags is None:
            self.tags = []

        # Extract IP and port from URL if not provided
        if not self.ip or not self.port:
            try:
                parsed = urlparse(self.url)
                self.ip = parsed.hostname
                self.port = parsed.port
                self.protocol = parsed.scheme or "http"
            except Exception:
                pass

        # Build auth object if username/password provided
        if self.username and self.password and not self.auth:
            self.auth = {
                "username": self.username,
                "password": self.password,
                "type": "basic"
            }


class ProxyLoader:
    """Advanced proxy loader with caching and multiple format support."""

    def __init__(self, cache_enabled: bool = True, cache_ttl: int = 300):
        """
        Initialize proxy loader.

        Args:
            cache_enabled: Enable proxy caching
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_timestamps = {}

    def load_from_txt(self, file_path: Union[str, Path], format_type: str = "simple") -> List[ProxyConfig]:
        """
        Load proxies from text file.

        Args:
            file_path: Path to text file
            format_type: Format type ("simple", "http", "csv", "json")

        Returns:
            List of ProxyConfig objects
        """
        file_path = Path(file_path)

        # Check cache
        cache_key = f"txt:{file_path}:{format_type}"
        if self.cache_enabled and self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        proxies = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                try:
                    if format_type == "simple":
                        proxy = self._parse_simple_format(line)
                    elif format_type == "http":
                        proxy = self._parse_http_format(line)
                    elif format_type == "csv":
                        proxy = self._parse_csv_format(line)
                    elif format_type == "json":
                        proxy_data = json.loads(line)
                        proxy = ProxyConfig(**proxy_data)
                    else:
                        continue

                    if proxy and self._validate_proxy(proxy):
                        proxies.append(proxy)

                except Exception as e:
                    print(f"⚠️  Error parsing line {line_num} in {file_path}: {e}")
                    continue

            print(f"✅ Loaded {len(proxies)} proxies from {file_path} (format: {format_type})")

            # Cache result
            if self.cache_enabled:
                self._cache[cache_key] = [asdict(p) for p in proxies]
                self._cache_timestamps[cache_key] = time.time()

            return proxies

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error loading file {file_path}: {e}")

    def load_from_csv(self, file_path: Union[str, Path], delimiter: str = ",",
                     has_header: bool = True) -> List[ProxyConfig]:
        """
        Load proxies from CSV file.

        Args:
            file_path: Path to CSV file
            delimiter: CSV delimiter
            has_header: Whether CSV has header row

        Returns:
            List of ProxyConfig objects
        """
        file_path = Path(file_path)

        # Check cache
        cache_key = f"csv:{file_path}:{delimiter}:{has_header}"
        if self.cache_enabled and self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        proxies = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                for row_num, row in enumerate(reader, 1 if has_header else 0):
                    try:
                        if has_header and row_num == 0:
                            continue  # Skip header

                        proxy = self._csv_row_to_proxy(row)
                        if proxy and self._validate_proxy(proxy):
                            proxies.append(proxy)

                    except Exception as e:
                        print(f"⚠️  Error parsing CSV row {row_num} in {file_path}: {e}")
                        continue

            print(f"✅ Loaded {len(proxies)} proxies from CSV file: {file_path}")

            # Cache result
            if self.cache_enabled:
                self._cache[cache_key] = [asdict(p) for p in proxies]
                self._cache_timestamps[cache_key] = time.time()

            return proxies

        except Exception as e:
            raise Exception(f"Error loading CSV file {file_path}: {e}")

    def load_from_json(self, file_path: Union[str, Path]) -> List[ProxyConfig]:
        """
        Load proxies from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            List of ProxyConfig objects
        """
        file_path = Path(file_path)

        # Check cache
        cache_key = f"json:{file_path}"
        if self.cache_enabled and self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            proxies_data = self._extract_proxies_from_json(data)
            proxies = [ProxyConfig(**proxy_data) for proxy_data in proxies_data]

            # Validate proxies
            valid_proxies = [p for p in proxies if self._validate_proxy(p)]

            print(f"✅ Loaded {len(valid_proxies)} proxies from JSON file: {file_path}")

            # Cache result
            if self.cache_enabled:
                self._cache[cache_key] = [asdict(p) for p in valid_proxies]
                self._cache_timestamps[cache_key] = time.time()

            return valid_proxies

        except Exception as e:
            raise Exception(f"Error loading JSON file {file_path}: {e}")

    async def load_from_api(self, api_url: str, headers: Optional[Dict[str, str]] = None,
                            timeout: int = 30) -> List[ProxyConfig]:
        """
        Load proxies from API endpoint.

        Args:
            api_url: API endpoint URL
            headers: HTTP headers
            timeout: Request timeout in seconds

        Returns:
            List of ProxyConfig objects
        """
        # Check cache
        cache_key = f"api:{api_url}"
        if self.cache_enabled and self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    if response.status == 200:
                        data = await response.json()
                        proxies_data = self._extract_proxies_from_api_response(data)
                        proxies = [ProxyConfig(**proxy_data) for proxy_data in proxies_data]

                        print(f"✅ Loaded {len(proxies)} proxies from API: {api_url}")

                        # Cache result
                        if self.cache_enabled:
                            self._cache[cache_key] = [asdict(p) for p in proxies]
                            self._cache_timestamps[cache_key] = time.time()

                        return proxies
                    else:
                        raise Exception(f"API request failed with status {response.status}")

        except Exception as e:
            raise Exception(f"Error loading proxies from API {api_url}: {e}")

    def load_from_env(self, prefix: str = "PROXY", separator: str = "_") -> List[ProxyConfig]:
        """
        Load proxies from environment variables.

        Args:
            prefix: Environment variable prefix
            separator: Separator for variable names

        Returns:
            List of ProxyConfig objects
        """
        proxies = []

        # Find all environment variables with the prefix
        env_proxies = {}
        prefix_with_sep = f"{prefix}{separator}"

        for key, value in os.environ.items():
            if key.startswith(prefix_with_sep):
                proxy_id = key[len(prefix_with_sep):]
                env_proxies[proxy_id] = value
            elif key == prefix and value.strip():
                # Handle single variable case
                env_proxies['default'] = value

        for proxy_id, value in env_proxies.items():
            try:
                if value.strip():
                    proxy = self._parse_proxy_string(value)
                    if proxy and self._validate_proxy(proxy):
                        proxy.id = proxy_id
                        proxy.source = 'environment'
                        proxies.append(proxy)
            except Exception as e:
                print(f"⚠️  Error parsing environment variable {key}: {e}")

        print(f"✅ Loaded {len(proxies)} proxies from environment variables (prefix: {prefix})")
        return proxies

    def generate_proxies(self, count: int, pattern: str = "random", **kwargs) -> List[ProxyConfig]:
        """
        Generate proxies programmatically.

        Args:
            count: Number of proxies to generate
            pattern: Generation pattern
            **kwargs: Additional parameters for generation

        Returns:
            List of ProxyConfig objects
        """
        if pattern == "random":
            proxies = self._generate_random_proxies(count, **kwargs)
        elif pattern == "sequential":
            proxies = self._generate_sequential_proxies(count, **kwargs)
        elif pattern == "geo":
            proxies = self._generate_geo_proxies(count, **kwargs)
        elif pattern == "residential":
            proxies = self._generate_residential_proxies(count, **kwargs)
        elif pattern == "datacenter":
            proxies = self._generate_datacenter_proxies(count, **kwargs)
        elif pattern == "mobile":
            proxies = self._generate_mobile_proxies(count, **kwargs)
        elif pattern == "isp":
            proxies = self._generate_isp_proxies(count, **kwargs)
        else:
            raise ValueError(f"Unknown pattern: {pattern}")

        print(f"✅ Generated {len(proxies)} proxies using pattern: {pattern}")
        return proxies

    def filter_proxies(self, proxies: List[ProxyConfig], **filters) -> List[ProxyConfig]:
        """
        Filter proxies based on criteria.

        Args:
            proxies: List of proxies to filter
            **filters: Filter criteria

        Returns:
            Filtered list of proxies
        """
        filtered = proxies.copy()

        if 'country' in filters:
            countries = filters['country']
            if isinstance(countries, str):
                countries = [countries]
            filtered = [p for p in filtered if p.country in countries]

        if 'protocol' in filters:
            protocols = filters['protocol']
            if isinstance(protocols, str):
                protocols = [protocols]
            filtered = [p for p in filtered if p.protocol in protocols]

        if 'healthy' in filters:
            is_healthy = filters['healthy']
            filtered = [p for p in filtered if p.health_check == is_healthy]

        if 'min_weight' in filters:
            min_weight = filters['min_weight']
            filtered = [p for p in filtered if p.weight >= min_weight]

        if 'max_weight' in filters:
            max_weight = filters['max_weight']
            filtered = [p for p in filtered if p.weight <= max_weight]

        if 'source' in filters:
            sources = filters['source']
            if isinstance(sources, str):
                sources = [sources]
            filtered = [p for p in filtered if p.source in sources]

        if 'tags' in filters:
            required_tags = filters['tags']
            if isinstance(required_tags, str):
                required_tags = [required_tags]
            filtered = [p for p in filtered if any(tag in p.tags for tag in required_tags)]

        if 'exclude_auth' in filters:
            filtered = [p for p in filtered if not p.auth]

        print(f"✅ Filtered {len(proxies)} proxies to {len(filtered)} proxies")
        return filtered

    def shuffle_proxies(self, proxies: List[ProxyConfig]) -> List[ProxyConfig]:
        """Shuffle proxy list randomly."""
        shuffled = proxies.copy()
        random.shuffle(shuffled)
        return shuffled

    def save_proxies_to_file(self, proxies: List[ProxyConfig], file_path: Union[str, Path],
                           format_type: str = "json") -> None:
        """
        Save proxy list to file.

        Args:
            proxies: List of proxies to save
            file_path: Output file path
            format_type: Output format ("json", "csv", "txt")
        """
        file_path = Path(file_path)

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if format_type == "json":
                data = [asdict(proxy) for proxy in proxies]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

            elif format_type == "csv":
                if proxies:
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        fieldnames = list(proxies[0].__dataclass_fields__.keys())
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for proxy in proxies:
                            writer.writerow(asdict(proxy))

            elif format_type == "txt":
                with open(file_path, 'w', encoding='utf-8') as f:
                    for proxy in proxies:
                        line = self._proxy_to_line(proxy, format_type)
                        f.write(line + '\n')

            print(f"✅ Saved {len(proxies)} proxies to {file_path} (format: {format_type})")

        except Exception as e:
            raise Exception(f"Error saving proxies to file {file_path}: {e}")

    # Private helper methods
    def _parse_simple_format(self, line: str) -> Optional[ProxyConfig]:
        """Parse simple format: ip:port:user:password."""
        parts = line.split(':')

        if len(parts) >= 2:
            proxy = ProxyConfig(
                ip=parts[0],
                port=int(parts[1]),
                url=f"http://{parts[0]}:{parts[1]}"
            )

            if len(parts) >= 3:
                proxy.username = parts[2]
                proxy.auth = {
                    "username": parts[2],
                    "type": "basic"
                }

                if len(parts) >= 4:
                    proxy.password = parts[3]
                    proxy.auth["password"] = parts[3]

            return proxy

        return None

    def _parse_http_format(self, line: str) -> Optional[ProxyConfig]:
        """Parse HTTP format: http://user:pass@proxy:port."""
        try:
            parsed = urlparse(line)

            if parsed.scheme and parsed.netloc:
                proxy = ProxyConfig(
                    url=line,
                    protocol=parsed.scheme,
                    ip=parsed.hostname,
                    port=parsed.port or (80 if parsed.scheme == 'http' else 443)
                )

                if parsed.username:
                    proxy.username = parsed.username
                    proxy.auth = {
                        "username": parsed.username,
                        "password": parsed.password,
                        "type": "basic"
                    }

                return proxy

        except Exception:
            pass

        return None

    def _parse_csv_format(self, line: str) -> Optional[ProxyConfig]:
        """Parse CSV format: ip,port,user,password."""
        parts = [p.strip() for p in line.split(',')]

        if len(parts) >= 2:
            proxy = ProxyConfig(
                ip=parts[0],
                port=int(parts[1]),
                url=f"http://{parts[0]}:{parts[1]}"
            )

            if len(parts) >= 3 and parts[2]:
                proxy.username = parts[2]
                proxy.auth = {
                    "username": parts[2],
                    "type": "basic"
                }

                if len(parts) >= 4 and parts[3]:
                    proxy.password = parts[3]
                    proxy.auth["password"] = parts[3]

            return proxy

        return None

    def _parse_proxy_string(self, proxy_string: str) -> Optional[ProxyConfig]:
        """Parse proxy string in various formats."""
        # Try HTTP format first
        if proxy_string.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            return self._parse_http_format(proxy_string)

        # Try simple format
        return self._parse_simple_format(proxy_string)

    def _csv_row_to_proxy(self, row: Dict[str, Any]) -> Optional[ProxyConfig]:
        """Convert CSV row to ProxyConfig."""
        proxy_data = {}

        # Map common field names
        field_mapping = {
            'id': ['id', 'proxy_id', 'name', 'identifier'],
            'url': ['url', 'proxy_url', 'endpoint'],
            'protocol': ['protocol', 'scheme', 'type'],
            'ip': ['ip', 'server', 'host', 'address', 'proxy_ip'],
            'port': ['port', 'proxy_port', 'connection_port'],
            'username': ['username', 'user', 'login'],
            'password': ['password', 'pass', 'pwd'],
            'country': ['country', 'location', 'geo', 'region'],
            'weight': ['weight', 'priority'],
            'max_connections': ['max_connections', 'max_conn', 'max_concurrent'],
            'timeout': ['timeout', 'time_limit'],
            'retry_count': ['retry_count', 'retries'],
            'health_check': ['health_check', 'health'],
            'tags': ['tags', 'labels', 'categories']
        }

        # Extract data using field mapping
        for field, possible_names in field_mapping.items():
            for name in possible_names:
                if name in row and row[name]:
                    proxy_data[field] = row[name]
                    break

        return ProxyConfig(**proxy_data) if proxy_data else None

    def _generate_random_proxies(self, count: int, **kwargs) -> List[ProxyConfig]:
        """Generate random proxies."""
        proxies = []
        countries = kwargs.get('countries', ['US', 'UK', 'DE', 'FR', 'CA'])
        protocols = kwargs.get('protocols', ['http'])
        isps = kwargs.get('isps', ['comcast', 'att', 'verizon', 'spectrum'])
        ports = kwargs.get('ports', [8080, 8888, 3128, 8800])

        for i in range(count):
            # Generate random IP
            ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            port = random.choice(ports)
            protocol = random.choice(protocols)
            country = random.choice(countries)
            isp = random.choice(isps)

            proxy = ProxyConfig(
                id=f"gen_{i+1}",
                url=f"{protocol}://{ip}:{port}",
                ip=ip,
                port=port,
                protocol=protocol,
                country=country,
                weight=random.randint(1, 5),
                source="generated_random"
            )

            # Randomly add authentication
            if random.random() < 0.3:  # 30% have auth
                proxy.username = f"user{i+1}"
                proxy.password = f"pass{i+1}"
                proxy.auth = {
                    "username": proxy.username,
                    "password": proxy.password,
                    "type": "basic"
                }

            # Add ISP information
            proxy.tags = [f"isp:{isp}"]

            proxies.append(proxy)

        return proxies

    def _generate_sequential_proxies(self, count: int, **kwargs) -> List[ProxyConfig]:
        """Generate sequential proxies."""
        proxies = []
        base_ip = kwargs.get('base_ip', "192.168.1")
        start_port = kwargs.get('start_port', 8080)
        protocol = kwargs.get('protocol', "http")

        try:
            # Extract IP range
            if '.' in base_ip:
                parts = base_ip.split('.')
                if len(parts) == 4:
                    base_ip_prefix = '.'.join(parts[:3])
                    start_last_octet = int(parts[3])

                    for i in range(count):
                        last_octet = start_last_octet + i
                        if last_octet > 255:
                            break

                        ip = f"{base_ip_prefix}.{last_octet}"
                        port = start_port + i

                        proxy = ProxyConfig(
                            id=f"seq_{i+1}",
                            url=f"{protocol}://{ip}:{port}",
                            ip=ip,
                            port=port,
                            protocol=protocol,
                            source="generated_sequential"
                        )

                        proxies.append(proxy)

        except Exception:
            pass  # Fallback to empty list

        return proxies

    def _generate_geo_proxies(self, count: int, **kwargs) -> List[ProxyConfig]:
        """Generate geographically distributed proxies."""
        geo_data = {
            'US': {
                'ip_ranges': ['208.67', '208.68', '208.69'],
                'ports': [8080, 8888, 3128],
                'isps': ['comcast', 'att', 'verizon', 'spectrum', 'cox']
            },
            'UK': {
                'ip_ranges': ['185.216', '185.217', '185.218'],
                'ports': [3128, 8080, 8081],
                'isps': ['bt', 'sky', 'talktalk', 'virgin']
            },
            'DE': {
                'ip_ranges': ['46.4', '46.5', '46.6'],
                'ports': [8080, 3128, 8443],
                'isps': ['deutsche-telekom', 'vodafone', 'telefónica-deutschland']
            },
            'FR': {
                'ip_ranges': ['176.31', '176.32', '176.33'],
                'ports': [3128, 8080, 8888],
                'isps': ['orange', 'sfr', 'bouygues']
            },
            'CA': {
                'ip_ranges': ['198.48', '198.49', '198.50'],
                'ports': [8080, 8888, 8443],
                'isps': ['bell', 'rogers', 'telus']
            }
        }

        proxies = []
        selected_countries = kwargs.get('countries', list(geo_data.keys()))

        for i in range(count):
            country = random.choice(selected_countries)
            geo = geo_data[country]

            ip_prefix = random.choice(geo['ip_ranges'])
            port = random.choice(geo['ports'])
            last_octet = random.randint(1, 255)
            ip = f"{ip_prefix}.{last_octet}"
            isp = random.choice(geo['isps'])

            proxy = ProxyConfig(
                id=f"geo_{country.lower()}_{i+1}",
                url=f"http://{ip}:{port}",
                ip=ip,
                port=port,
                country=country,
                isp=isp,
                weight=random.randint(1, 5),
                source="generated_geo",
                tags=[f"geo:{country}", f"isp:{isp}"]
            )

            proxies.append(proxy)

        return proxies

    def _generate_residential_proxies(self, count: int, **kwargs) -> List[ProxyConfig]:
        """Generate residential proxy patterns."""
        isps = ['comcast', 'att', 'verizon', 'spectrum', 'cox', 'charter']
        cities = ['nyc', 'la', 'chicago', 'houston', 'phoenix']

        proxies = []

        for i in range(count):
            provider = random.choice(isps)
            city = random.choice(cities)

            # Simulate residential IP patterns (simplified)
            ip_parts = [random.randint(24, 200), random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)]
            ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{ip_parts[3]}"

            proxy = ProxyConfig(
                id=f"res_{provider}_{city}_{i+1}",
                url=f"http://{ip}:8080",
                ip=ip,
                port=8080,
                provider=provider,
                weight=1,
                source="generated_residential",
                tags=[f"residential", f"city:{city}", f"isp:{provider}"]
            )

            proxies.append(proxy)

        return proxies

    def _generate_datacenter_proxies(self, count: int, **kwargs) -> List[ProxyConfig]:
        """Generate datacenter proxy patterns."""
        providers = ['aws', 'google', 'azure', 'digitalocean', 'linode', 'vultr']
        datacenters = {
            'aws': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1'],
            'google': ['us-central1', 'us-east1', 'europe-west1', 'asia-southeast1'],
            'azure': ['eastus', 'westeurope', 'southeastasia'],
            'digitalocean': ['nyc1', 'sfo1', 'lon1', 'fra1', 'ams1'],
            'linode': ['us-east', 'us-west', 'eu-central', 'ap-south']
        }

        proxies = []

        for i in range(count):
            provider = random.choice(providers)
            region = random.choice(datacenters[provider])

            # Simulate datacenter IP patterns
            if provider == 'aws':
                ip_parts = [random.randint(3, 20), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
            elif provider == 'google':
                ip_parts = [random.randint(34, 36), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
            else:
                ip_parts = [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)]

            ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{ip_parts[3]}"
            port = random.choice([8080, 8888, 3128, 8443])

            proxy = ProxyConfig(
                id=f"{provider}_{region}_{i+1}",
                url=f"http://{ip}:{port}",
                ip=ip,
                port=port,
                provider=provider,
                region=region,
                weight=random.randint(3, 5),
                source="generated_datacenter",
                tags=[f"datacenter", f"provider:{provider}", f"region:{region}"]
            )

            proxies.append(proxy)

        return proxies

    def _generate_mobile_proxies(self, count: int, **kwargs) -> List[ProxyConfig]:
        """Generate mobile proxy patterns."""
        carriers = ['at&t', 'verizon', 't-mobile', 'sprint', 'vodafone']
        networks = ['4g', '5g', 'lte']

        proxies = []

        for i in range(count):
            carrier = random.choice(carriers)
            network = random.choice(networks)

            # Simulate mobile IP patterns (simplified)
            ip_parts = [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)]
            ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{ip_parts[3]}"

            proxy = ProxyConfig(
                id=f"mobile_{carrier}_{i+1}",
                url=f"http://{ip}:8080",
                ip=ip,
                port=8080,
                carrier=carrier,
                network=network,
                weight=1,
                source="generated_mobile",
                tags=[f"mobile", f"carrier:{carrier}", f"network:{network}"]
            )

            proxies.append(proxy)

        return proxies

    def _generate_isp_proxies(self, count: int, **kwargs) -> List[ProxyConfig]:
        """Generate ISP proxy patterns."""
        isps = ['comcast', 'att', 'verizon', 'spectrum', 'cox', 'charter', 'mediacom', 'frontier']

        proxies = []

        for i in range(count):
            isp = random.choice(isps)

            # Simulate ISP IP patterns (simplified)
            ip_parts = [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)]
            ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{ip_parts[3]}"

            proxy = ProxyConfig(
                id=f"isp_{isp}_{i+1}",
                url=f"http://{ip}:8080",
                ip=ip,
                port=8080,
                isp=isp,
                weight=1,
                source="generated_isp",
                tags=[f"isp:{isp}"]
            )

            proxies.append(proxy)

        return proxies

    def _validate_proxy(self, proxy: ProxyConfig) -> bool:
        """Validate proxy configuration."""
        if not proxy:
            return False

        # Check if proxy has URL or can build URL
        if not proxy.url:
            if proxy.ip and proxy.port:
                proxy.url = f"http://{proxy.ip}:{proxy.port}"
            else:
                return False

        # Validate URL format
        try:
            parsed = urlparse(proxy.url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False

    def _extract_proxies_from_json(self, data: Any) -> List[Dict[str, Any]]:
        """Extract proxies from various JSON response formats."""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if 'proxies' in data:
                return data['proxies']
            elif 'data' in data:
                return data['data']
            elif 'results' in data:
                return data['results']
            elif 'items' in data:
                return data['items']
            else:
                return [data]

        return []

    def _extract_proxies_from_api_response(self, data: Any) -> List[Dict[str, Any]]:
        """Extract proxies from API response data."""
        return self._extract_proxies_from_json(data)

    def _proxy_to_line(self, proxy: ProxyConfig, format_type: str = "simple") -> str:
        """Convert proxy to line format."""
        if format_type == "simple":
            line = f"{proxy.ip}:{proxy.port}"
            if proxy.username:
                line += f":{proxy.username}"
                if proxy.password:
                    line += f":{proxy.password}"
            return line

        elif format_type == "http":
            if proxy.username and proxy.password:
                return f"http://{proxy.username}:{proxy.password}@{proxy.ip}:{proxy.port}"
            else:
                return f"http://{proxy.ip}:{proxy.port}"

        return str(proxy.url)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if not self.cache_enabled or cache_key not in self._cache:
            return False

        cache_time = self._cache_timestamps.get(cache_key, 0)
        return (time.time() - cache_time) < self.cache_ttl

    def _get_from_cache(self, cache_key: str) -> List[ProxyConfig]:
        """Get data from cache."""
        cached_data = self._cache.get(cache_key, [])
        return [ProxyConfig(**data) for data in cached_data]


# Utility functions for common operations
def load_proxies_from_multiple_sources(sources: List[Dict[str, Any]]) -> List[ProxyConfig]:
    """
    Load proxies from multiple sources and combine them.

    Args:
        sources: List of source configurations

    Returns:
        Combined list of proxies
    """
    loader = ProxyLoader()
    all_proxies = []

    for source in sources:
        try:
            source_type = source.get('type', 'txt')
            source_path = source.get('path')

            if source_type == 'txt':
                proxies = loader.load_from_txt(source_path, source.get('format', 'simple'))
            elif source_type == 'csv':
                proxies = loader.load_from_csv(source_path)
            elif source_type == 'json':
                proxies = loader.load_from_json(source_path)
            elif source_type == 'env':
                proxies = loader.load_from_env(source.get('prefix', 'PROXY'))

            all_proxies.extend(proxies)

        except Exception as e:
            print(f"⚠️  Failed to load from {source_type} source: {e}")

    return all_proxies


# Convenience functions
def load_proxies_from_directory(directory: str, pattern: str = "*.txt") -> List[ProxyConfig]:
    """
    Load all proxy files from a directory.

    Args:
        directory: Directory path
        pattern: File pattern to match

    Returns:
        List of proxies from all matching files
    """
    loader = ProxyLoader()
    all_proxies = []

    directory_path = Path(directory)
    for file_path in directory_path.glob(pattern):
        try:
            if file_path.suffix.lower() == '.txt':
                proxies = loader.load_from_txt(file_path)
            elif file_path.suffix.lower() == '.csv':
                proxies = loader.load_from_csv(file_path)
            elif file_path.suffix.lower() == '.json':
                proxies = loader.load_from_json(file_path)

            all_proxies.extend(proxies)

        except Exception as e:
            print(f"⚠️  Failed to load {file_path}: {e}")

    return all_proxies


if __name__ == "__main__":
    # Example usage
    loader = ProxyLoader()

    # Load from text file
    txt_proxies = loader.load_from_txt('proxies.txt', 'simple')

    # Load from environment
    env_proxies = loader.load_from_env('PROXY')

    # Generate proxies
    gen_proxies = loader.generate_proxies(100, pattern='random')

    # Filter proxies
    us_proxies = loader.filter_proxies(gen_proxies, country='US')

    print(f"Loaded {len(txt_proxies)} text proxies")
    print(f"Loaded {len(env_proxies)} environment proxies")
    print(f"Generated {len(gen_proxies)} random proxies")
    print(f"Filtered to {len(us_proxies)} US proxies")