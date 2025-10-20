---
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: MIT
---

# KRL Core Utilities

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/KR-Labs/krl-open-core/workflows/Tests/badge.svg)](https://github.com/KR-Labs/krl-open-core/actions)
[![Coverage](https://codecov.io/gh/KR-Labs/krl-open-core/branch/main/graph/badge.svg)](https://codecov.io/gh/KR-Labs/krl-open-core)

> **Shared foundation utilities for the KR-Labs analytics platform**

`krl-core` provides common utilities, configuration management, logging, caching, and base classes used across all KRL packages. It serves as the foundational layer for the entire KR-Labs ecosystem.

## Features

- 🔧 **Configuration Management**: Environment variable and YAML-based configuration
- 📝 **Structured Logging**: JSON-formatted logging with context and correlation IDs
- ⚡ **Caching**: File-based and Redis caching with TTL support
- 🌐 **API Client Base**: Reusable HTTP client with retry logic and rate limiting
- 🛠️ **Utilities**: Date parsing, validation, decorators, and common helpers

## Installation

```bash
pip install krl-core
```

## Quick Start

### Logging

```python
from krl_core import get_logger

logger = get_logger(__name__)
logger.info("Application started", extra={"user_id": 123})
```

### Configuration

```python
from krl_core import ConfigManager

config = ConfigManager()
api_key = config.get("FRED_API_KEY")  # From environment or config file
```

### Caching

```python
from krl_core import FileCache

cache = FileCache(cache_dir="./cache", ttl=3600)
data = cache.get("my_key")
if data is None:
    data = expensive_operation()
    cache.set("my_key", data)
```

## Documentation

Full documentation is available at [krl-core.readthedocs.io](https://krl-core.readthedocs.io)

- [Installation Guide](https://krl-core.readthedocs.io/en/latest/quickstart.html)
- [API Reference](https://krl-core.readthedocs.io/en/latest/api.html)
- [Configuration](https://krl-core.readthedocs.io/en/latest/config.html)
- [Logging](https://krl-core.readthedocs.io/en/latest/logging.html)
- [Caching](https://krl-core.readthedocs.io/en/latest/cache.html)

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/KR-Labs/krl-open-core.git
cd krl-open-core

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev,test]"

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_logging.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check imports
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

## Architecture

```
krl-core/
├── logging/       # Structured logging with JSON formatting
├── config/        # Configuration management (env vars, YAML)
├── cache/         # File and Redis caching with TTL
├── api/           # Base HTTP client with retry/rate limiting
└── utils/         # Common utilities (dates, validators, decorators)
```

## Dependencies

**Core Dependencies:**
- Python 3.9+
- `pyyaml` - Configuration file parsing
- `python-json-logger` - Structured JSON logging
- `requests` - HTTP client
- `redis` (optional) - Redis caching support

**Development Dependencies:**
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking
- `isort` - Import sorting

## Related Packages

`krl-core` is the foundation for these KRL packages:

- [krl-data-connectors](https://github.com/KR-Labs/krl-data-connectors) - 40+ data source connectors
- [krl-model-zoo](https://github.com/KR-Labs/krl-model-zoo) - 100+ analytical models
- [krl-dashboard](https://github.com/KR-Labs/krl-dashboard) - Interactive dashboards
- [krl-causal-policy-toolkit](https://github.com/KR-Labs/krl-causal-policy-toolkit) - Causal inference tools
- [krl-network-analysis](https://github.com/KR-Labs/krl-network-analysis) - Network analytics
- [krl-geospatial-tools](https://github.com/KR-Labs/krl-geospatial-tools) - GIS tools

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Contributor License Agreement

Before we can accept your contributions, you'll need to sign our CLA:
- [Individual CLA](https://github.com/KR-Labs/.github/blob/main/CLA/INDIVIDUAL_CLA.md)
- [Corporate CLA](https://github.com/KR-Labs/.github/blob/main/CLA/CORPORATE_CLA.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@krlabs.dev
- 💬 GitHub Issues: [Report a bug](https://github.com/KR-Labs/krl-open-core/issues/new?template=bug_report.md)
- 📖 Documentation: [krl-core.readthedocs.io](https://krl-core.readthedocs.io)
- 🌐 Website: [krlabs.dev](https://krlabs.dev)

## Citation

If you use KRL Core in your research, please cite:

```bibtex
@software{krl_core_2025,
  title = {KRL Core: Shared Utilities for KR-Labs Analytics Platform},
  author = {{KR-Labs Foundation}},
  year = {2025},
  url = {https://github.com/KR-Labs/krl-open-core},
  license = {MIT}
}
```

---

**KRL™** is a trademark of KR-Labs Foundation.  
Copyright © 2025 KR-Labs Foundation. All rights reserved.
