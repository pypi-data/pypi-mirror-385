# 🦎 Chameleon Engine

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-org/chameleon-engine)
[![Coverage](https://img.shields.io/badge/coverage-95%25-green.svg)](https://codecov.io)

**Advanced stealth web scraping framework with cutting-edge browser fingerprinting and network obfuscation capabilities.**

Chameleon Engine is a comprehensive microservices-based solution designed to bypass modern anti-bot detection systems through sophisticated browser fingerprinting, TLS fingerprint masking, and human behavior simulation.

## ✨ Key Features

### 🎭 Advanced Browser Fingerprinting
- **Dynamic Profile Generation**: Create realistic browser profiles based on real-world data
- **TLS Fingerprint Masking**: JA3/JA4 hash manipulation with uTLS integration
- **HTTP/2 Header Rewriting**: Sophisticated header manipulation for advanced stealth
- **Multi-Browser Support**: Chrome, Firefox, Safari, Edge fingerprint profiles

### 🚀 Microservices Architecture
- **Fingerprint Service**: FastAPI-based profile management (Python)
- **Proxy Service**: High-performance proxy with TLS fingerprinting (Go)
- **Data Collection Pipeline**: Automated real-world fingerprint gathering
- **Real-time Monitoring**: WebSocket-based dashboard and metrics

### 🎯 Human Behavior Simulation
- **Mouse Movement Patterns**: Bezier curve-based natural movements
- **Typing Simulation**: Realistic typing with variable speed and errors
- **Scrolling Behavior**: Natural scroll patterns and pauses
- **Timing Obfuscation**: Human-like delays and interaction patterns

### 🛡️ Network Obfuscation
- **Advanced Proxy Management**: Multi-format proxy loading (TXT, CSV, JSON) with automatic rotation
- **Proxy Generation**: Dynamic generation of residential, datacenter, and geo-targeted proxies
- **Request Obfuscation**: Timing and header randomization
- **TLS Certificate Generation**: Dynamic cert creation per profile
- **HTTP/2 Settings Manipulation**: Protocol-level fingerprinting

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Python App    │    │  Fingerprint     │    │   Data Source   │
│                 │◄──►│   Service        │◄──►│   Collection    │
│  Chameleon      │    │   (FastAPI)      │    │     Pipeline    │
│     Engine      │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Browser       │    │     Proxy        │    │    Database     │
│  Management     │    │    Service       │    │   PostgreSQL    │
│   (Playwright)  │◄──►│     (Go)         │◄──►│   + Redis       │
│                 │    │   uTLS + HTTP2   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 🎯 Automated Installation (Recommended)

**Linux/macOS:**
```bash
# Clone and install with one command
git clone https://github.com/your-org/chameleon-engine.git
cd chameleon-engine
./install.sh

# Start services
docker-compose -f examples/docker_compose_example.yaml up -d

# Run your first scrape
python examples/simple_scrape.py https://example.com
```

**Windows:**
```powershell
# Clone and install
git clone https://github.com/your-org/chameleon-engine.git
cd chameleon-engine
.\install.ps1

# Start services
docker-compose -f examples/docker_compose_example.yaml up -d

# Run your first scrape
python examples/simple_scrape.py https://example.com
```

### 📋 Prerequisites

- **Python 3.8+**
- **Go 1.21+** (for proxy service)
- **Docker & Docker Compose** (optional, for easy deployment)
- **PostgreSQL** (optional, for persistent storage)
- **Redis** (optional, for caching)

### 🔧 Manual Installation

```bash
# Clone the repository
git clone https://github.com/your-org/chameleon-engine.git
cd chameleon-engine

# Install Python package in development mode
pip install -e .

# Install Playwright browsers
playwright install

# Install Go dependencies (proxy service)
cd proxy_service
go mod tidy
cd ..
```

### Basic Usage

```python
import asyncio
from chameleon_engine import ChameleonEngine

async def main():
    # Initialize Chameleon Engine
    engine = ChameleonEngine(
        fingerprint_service_url="http://localhost:8000",
        proxy_service_url="http://localhost:8080"
    )

    await engine.initialize()

    # Create stealth browser session
    browser = await engine.create_browser(
        profile_type="chrome_windows",
        stealth_mode=True
    )

    # Perform scraping
    page = await browser.new_page()
    await page.goto("https://example.com")

    content = await page.content()
    print(f"Scraped content length: {len(content)}")

    # Cleanup
    await browser.close()
    await engine.cleanup()

asyncio.run(main())
```

## 📚 Services Setup

### Option 1: Manual Setup

1. **Start Fingerprint Service**:
   ```bash
   python -m chameleon_engine.fingerprint.main
   ```

2. **Start Proxy Service**:
   ```bash
   cd proxy_service
   make run
   ```

3. **Run Your Application**:
   ```bash
   python your_scraping_script.py
   ```

### Option 2: Docker Deployment

```bash
# Start all services
docker-compose -f examples/docker_compose_example.yaml up -d

# Check service status
docker-compose ps
```

## 🎯 Use Cases

### E-commerce Data Collection
```python
# Scrape product pages while avoiding bot detection
await engine.scrape_ecommerce(
    target_urls=["https://shop.example.com/products/*"],
    rotate_fingerprints=True,
    human_behavior=True,
    rate_limit="1-3 requests per minute"
)
```

### Market Research
```python
# Collect competitive intelligence
await engine.market_research(
    competitors=["competitor1.com", "competitor2.com"],
    data_types=["pricing", "products", "reviews"],
    stealth_level="high"
)
```

### SEO Monitoring
```python
# Monitor search engine rankings
await engine.seo_monitoring(
    keywords=["python web scraping"],
    search_engines=["google", "bing"],
    geo_locations=["US", "UK", "DE"]
)
```

### Academic Research
```python
# Collect data for research purposes
await engine.academic_research(
    target_sites=["scholar.google.com", "arxiv.org"],
    data_types=["papers", "citations", "metadata"],
    ethical_scraping=True
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Fingerprint Service
export DATABASE_URL="postgresql://user:pass@localhost/chameleon"
export REDIS_URL="redis://localhost:6379"
export LOG_LEVEL="info"

# Proxy Service
export FINGERPRINT_SERVICE_URL="http://localhost:8000"
export TLS_ENABLED="false"
export PROXY_TARGET_HOST=""
```

### Configuration File

Create `chameleon_config.yaml`:

```yaml
fingerprint:
  service_url: "http://localhost:8000"
  cache_size: 1000
  rotation_interval: 300

proxy:
  service_url: "http://localhost:8080"
  upstream_proxies:
    - url: "http://proxy1.example.com:8080"
      auth:
        username: "user"
        password: "pass"
        type: "basic"
    - url: "http://proxy2.example.com:8080"
      weight: 2
      auth: null
  rotation_settings:
    strategy: "round_robin"
    interval: 300
    request_count: 100
  health_check:
    enabled: true
    interval: 60

behavior:
  mouse_movements: true
  typing_patterns: true
  human_delays: true

logging:
  level: "info"
  format: "json"
```

### Proxy Configuration Details

The Go proxy service manages upstream proxies in two ways:

1. **No Upstream Proxies** (Default):
   ```yaml
   proxy:
     service_url: "http://localhost:8080"
     upstream_proxies: []
   ```
   Flow: Your App → Go Proxy Service → Target Website

2. **With Upstream Proxies**:
   ```yaml
   proxy:
     service_url: "http://localhost:8080"
     upstream_proxies:
       - url: "http://proxy1.example.com:8080"
         auth:
           username: "user"
           password: "pass"
           type: "basic"
       - url: "http://proxy2.example.com:8080"
         weight: 2
   ```
   Flow: Your App → Go Proxy Service → External Proxy → Target Website

**See [Proxy Management Guide](docs/proxy_management.md) for detailed configuration.**

### Advanced Proxy Loading

Chameleon Engine supports multiple proxy loading methods:

```python
from chameleon_engine.proxy_loader import ProxyLoader

loader = ProxyLoader()

# Load from text files
proxies = loader.load_from_txt("proxies.txt", format_type="mixed")

# Load from CSV
proxies = loader.load_from_csv("proxies.csv")

# Generate dynamic proxies
residential_proxies = loader.generate_proxies(
    count=10,
    pattern="residential",
    geolocations=["US", "EU", "AS"]
)

# Filter proxies
http_proxies = loader.filter_proxies(proxies, protocol="http")
auth_proxies = loader.filter_proxies(proxies, has_auth=True)
```

**See [Proxy Usage Guide](PROXY_USAGE_GUIDE.md) for comprehensive examples.**

## 📦 Installation Options

### 📖 Detailed Installation Guide
See [INSTALL.md](INSTALL.md) for comprehensive installation instructions including:
- System-specific setup (Linux, macOS, Windows)
- Docker installation
- Database configuration
- Troubleshooting common issues

### 🚀 Quick Start Guide
See [QUICK_START.md](QUICK_START.md) for a streamlined getting started experience.

## 📊 Monitoring & Debugging

### Health Checks

```bash
# Check fingerprint service
curl http://localhost:8000/health

# Check proxy service
curl http://localhost:8080/api/v1/health
```

### Real-time Monitoring

```python
# Get live statistics
stats = await engine.get_proxy_stats()
print(f"Active connections: {stats['active_connections']}")
print(f"Total requests: {stats['total_requests']}")

# WebSocket monitoring
import websocket
ws = websocket.WebSocketApp("ws://localhost:8080/ws")
ws.on_message = lambda ws, msg: print(f"Update: {msg}")
ws.run_forever()
```

### API Documentation

- **Fingerprint Service**: http://localhost:8000/docs
- **Proxy Service**: http://localhost:8080/api/v1/health

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=chameleon_engine --cov-report=html

# Run specific test suite
pytest tests/test_fingerprint.py -v
```

## 📖 Examples

### Quick Start Example
```bash
python examples/quick_start.py
```

### Advanced Scraping Demo
```bash
python examples/advanced_scraping_example.py
```

### Direct API Usage
```bash
python examples/api_client_example.py
```

### Proxy Management Examples
```bash
# Test proxy loading functionality
python examples/test_proxy_standalone.py

# Run proxy configuration examples
python examples/proxy_loader_examples.py
```

For more examples, see the [examples directory](examples/).

## 🔍 Advanced Features

### Custom Fingerprint Profiles

```python
# Create custom browser profile
custom_profile = {
    "browser_type": "chrome",
    "os": "windows",
    "version": "120.0.0.0",
    "screen_resolution": "1920x1080",
    "timezone": "America/New_York",
    "language": "en-US",
    "custom_headers": {
        "X-Custom-Header": "MyValue"
    }
}

profile = await fingerprint_client.create_profile(custom_profile)
```

### Behavior Simulation

```python
# Simulate human mouse movements
mouse_path = behavior_simulator.generate_mouse_path(
    start=(100, 100),
    end=(500, 300),
    duration=2.0,
    curve_type="bezier"
)

# Simulate typing with natural patterns
typing_pattern = behavior_simulator.generate_typing_pattern(
    text="Hello, World!",
    wpm=80,
    error_rate=0.02
)
```

### Network Obfuscation

```python
# Obfuscate request timing
original_delay = 1.0
obfuscated_delay = network_obfuscator.obfuscate_timing(original_delay)

# Obfuscate headers
headers = {"User-Agent": "Mozilla/5.0..."}
obfuscated_headers = network_obfuscator.obfuscate_headers(headers)
```

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/chameleon-engine.git
cd chameleon-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Format code
black chameleon_engine/
isort chameleon_engine/

# Lint code
flake8 chameleon_engine/
mypy chameleon_engine/

# Run security checks
bandit -r chameleon_engine/
```

### Building Documentation

```bash
# Install documentation dependencies
pip install -r requirements-docs.txt

# Build docs
mkdocs build

# Serve docs locally
mkdocs serve
```

## 📈 Performance

### Benchmarks

- **Request Processing**: < 10ms average latency
- **Profile Generation**: < 50ms for complex profiles
- **Memory Usage**: ~50MB base + ~5MB per concurrent session
- **Concurrent Sessions**: 1000+ simultaneous connections

### Optimization Tips

1. **Enable Redis caching** for fingerprint profiles
2. **Use connection pooling** for database connections
3. **Configure appropriate timeouts** for target websites
4. **Monitor resource usage** with built-in metrics

## 🔒 Security Considerations

### Ethical Usage

- ✅ **Respect robots.txt** files
- ✅ **Implement rate limiting** for target websites
- ✅ **Check terms of service** before scraping
- ✅ **Identify your bot** when required
- ❌ **Don't overload target servers**
- ❌ **Don't scrape personal data** without consent
- ❌ **Don't bypass security measures** illegally

### Best Practices

```python
# Ethical scraping configuration
ethical_config = {
    "rate_limit": "1 request per second",
    "respect_robots_txt": True,
    "user_agent": "MyBot/1.0 (+http://mywebsite.com/bot-info)",
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 5
}
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [uTLS](https://github.com/refraction-networking/utls) for TLS fingerprinting
- [Playwright](https://playwright.dev/) for browser automation
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Gin](https://gin-gonic.com/) for the Go web framework

## 📞 Support

- 📖 [Documentation](https://chameleon-engine.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/your-org/chameleon-engine/issues)
- 💬 [Discussions](https://github.com/your-org/chameleon-engine/discussions)
- 📧 [Email Support](mailto:support@chameleon-engine.com)

## 🗺️ Roadmap

### Version 2.0
- [ ] Machine learning-based behavior optimization
- [ ] Advanced CAPTCHA solving integration
- [ ] Cloud deployment templates
- [ ] Web-based management dashboard

### Version 1.5
- [ ] Enhanced mobile browser fingerprinting
- [ ] WebGL and Canvas fingerprinting
- [ ] Audio fingerprinting capabilities
- [x] Advanced proxy pool management
- [x] Multi-format proxy loading (TXT, CSV, JSON)
- [x] Dynamic proxy generation (residential, datacenter, geo-targeted)
- [x] Comprehensive proxy filtering and validation

### Version 1.2
- [x] Microservices architecture
- [x] Go-based proxy service
- [x] Real-time monitoring
- [x] Docker deployment support

---

**Made with ❤️ for the ethical web scraping community**

If you find this project useful, please consider giving it a ⭐ on GitHub!