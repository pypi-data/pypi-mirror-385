# KRL Data Connectors

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/krl-data-connectors.svg)](https://pypi.org/project/krl-data-connectors/)
[![Python Version](https://img.shields.io/pypi/pyversions/krl-data-connectors.svg)](https://pypi.org/project/krl-data-connectors/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/krl-data-connectors/badge/?version=latest)](https://krl-data-connectors.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/KR-Labs/krl-data-connectors/workflows/tests/badge.svg)](https://github.com/KR-Labs/krl-data-connectors/actions)
[![Coverage](https://img.shields.io/badge/coverage-90%25%2B-green)](https://github.com/KR-Labs/krl-data-connectors)
[![Downloads](https://img.shields.io/pypi/dm/krl-data-connectors.svg)](https://pypi.org/project/krl-data-connectors/)

**Institutional-grade, production-ready connectors for socioeconomic and policy data infrastructure**

[Installation](#installation) •
[Quick Start](#quick-start) •
[Documentation](https://krl-data-connectors.readthedocs.io) •
[Examples](./examples/) •
[Contributing](./CONTRIBUTING.md)

</div>

---

## Overview

KRL Data Connectors provide standardized, robust interfaces for accessing a broad spectrum of socioeconomic, demographic, health, and environmental datasets. Designed for institutional workflows, these connectors ensure reproducibility, scalability, and operational reliability. KRL Data Connectors are a core component of the [KRL Analytics Suite](https://krlabs.dev), supporting high-impact economic analysis, causal inference, and policy evaluation at scale.

### Key Advantages

- **Unified API**: Interact with diverse data sources via a consistent, type-safe interface.
- **Production-Ready**: Engineered for operational resilience with structured logging, error handling, and retry logic.
- **Type-Safe**: Full type hints and validation across all connectors.
- **Smart Caching**: Minimize redundant API calls and optimize data retrieval.
- **Rich Metadata**: Automatic metadata extraction and data profiling.
- **Comprehensive Testing**: 297+ tests, 90%+ coverage.
- **Quickstart Notebooks**: Jupyter notebooks for rapid onboarding.
- **Secure API Key Management**: Multiple secure credential resolution strategies.

### Supported Data Sources

KRL Data Connectors deliver institutional access to a growing catalog of production-ready datasets:

| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|---------------------- |---------------|---------------|---------------------|---------------------|--------------|
| Census ACS            | Demographics   | Optional      | Annual              | All US geographies  | ✅ Production |
| Census CBP            | Business       | Optional      | Annual              | County-level        | ✅ Production |
| Census LEHD           | Employment     | No            | Quarterly           | County-level        | ✅ Production |
| FRED                  | Economics      | Yes           | Daily/Real-time     | 800K+ series        | ✅ Production |
| BLS                   | Labor          | Recommended   | Monthly             | National/State      | ✅ Production |
| BEA                   | Economics      | Yes           | Quarterly/Annual    | National/Regional   | ✅ Production |
| CDC WONDER            | Health         | No            | Varies              | County-level        | ✅ Production |
| HRSA                  | Health         | No            | Annual              | HPSA/MUA/P          | ✅ Production |
| County Health Rankings| Health         | No            | Annual              | County-level        | ✅ Production |
| EPA EJScreen          | Environment    | No            | Annual              | Block group         | ✅ Production |
| EPA Air Quality       | Environment    | No            | Hourly/Real-time    | Station-level       | ✅ Production |
| HUD Fair Market Rent  | Housing        | Yes           | Annual              | Metro/County        | ✅ Production |
| FBI UCR               | Crime          | Recommended   | Annual              | Agency-level        | ✅ Production |
| NCES                  | Education      | No            | Annual              | School-level        | ✅ Production |
| Zillow Research       | Housing        | No            | Monthly             | Metro/ZIP           | ✅ Production |
| USDA Food Atlas       | Food Security  | No            | Annual              | County-level        | 🔄 Planned   |
| College Scorecard     | Education      | Yes           | Annual              | Institution         | 🔄 Planned   |
| World Bank            | International  | No            | Annual              | Country-level       | 🔄 Planned   |
| OECD                  | International  | No            | Varies              | Country-level       | 🔄 Planned   |

**Legend:** ✅ Production | 🔄 Planned | ⚠️ Beta

---

## Installation

This section describes installation options for integrating KRL Data Connectors into institutional environments.

```bash
# Basic installation
pip install krl-data-connectors

# With all optional dependencies
pip install krl-data-connectors[all]

# Development installation
pip install krl-data-connectors[dev]
```

---

## Quick Start

The following examples illustrate initializing and using KRL Data Connectors for key data sources. All connectors are designed for direct integration into reproducible, scalable analytics pipelines.

### County Business Patterns (CBP)

```python
from krl_data_connectors import CountyBusinessPatternsConnector

# Initialize connector (API key detected from environment: CENSUS_API_KEY)
cbp = CountyBusinessPatternsConnector()

# Retrieve retail trade data for Rhode Island
retail_data = cbp.get_state_data(
    year=2021,
    state='44',  # Rhode Island FIPS code
    naics='44'   # Retail trade sector
)

print(f"Retrieved {len(retail_data)} records")
print(retail_data[['NAICS2017', 'ESTAB', 'EMP', 'PAYANN']].head())
```

### LEHD Origin-Destination

```python
from krl_data_connectors import LEHDConnector

# Initialize connector
lehd = LEHDConnector()

# Retrieve origin-destination employment flows
od_data = lehd.get_od_data(
    state='ri',
    year=2021,
    job_type='JT00',  # All jobs
    segment='S000'    # All workers
)

print(f"Retrieved {len(od_data)} origin-destination pairs")
print(od_data[['w_geocode', 'h_geocode', 'S000', 'SA01']].head())
```

### FRED

```python
from krl_data_connectors import FREDConnector

# Initialize connector (API key from FRED_API_KEY)
fred = FREDConnector()

# Fetch unemployment rate time series
unemployment = fred.get_series(
    series_id="UNRATE",
    observation_start="2020-01-01",
    observation_end="2023-12-31"
)

print(unemployment.head())
```

### BLS

```python
from krl_data_connectors import BLSConnector

# Initialize connector (API key from BLS_API_KEY)
bls = BLSConnector()

# Get unemployment rate for multiple states
unemployment = bls.get_series(
    series_ids=['LASST060000000000003', 'LASST440000000000003'],
    start_year=2020,
    end_year=2023
)

print(unemployment.head())
```

### BEA

```python
from krl_data_connectors import BEAConnector

# Initialize connector (API key from BEA_API_KEY)
bea = BEAConnector()

# Get GDP by state
gdp_data = bea.get_data(
    dataset='Regional',
    method='GetData',
    TableName='SAGDP2N',
    LineCode=1,
    Year='2021',
    GeoFips='STATE'
)

print(gdp_data.head())
```

### Caching and Base Connector

All connectors inherit from `BaseConnector`, which provides standardized caching, configuration, and logging.

```python
from krl_data_connectors import FREDConnector

# Enable automatic caching
fred = FREDConnector(
    api_key="your_api_key",
    cache_dir="/tmp/fred_cache",
    cache_ttl=3600  # 1 hour
)

# Cached responses are automatic
data1 = fred.get_series("UNRATE")  # Fetches from API
data2 = fred.get_series("UNRATE")  # Returns from cache

# Access cache statistics
stats = fred.cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.1f}%")
```

---

## Architecture

KRL Data Connectors are engineered for extensibility and operational precision. Each connector extends a common `BaseConnector`, standardizing logging, configuration, caching, and request management.

### BaseConnector Capabilities

The `BaseConnector` class implements:

- **Structured Logging**: JSON logs with request and response metadata.
- **Configuration Management**: Supports environment variables and YAML configuration.
- **Intelligent Caching**: File-based and Redis caching with configurable TTL.
- **Error Handling**: Automatic retries, API rate limiting, and timeouts.
- **Request Management**: HTTP session pooling and connection reuse.

```python
from abc import ABC, abstractmethod
from krl_core import get_logger, ConfigManager, FileCache

class BaseConnector(ABC):
    """Abstract base class for data connectors."""
    def __init__(self, api_key=None, cache_dir=None, cache_ttl=3600):
        self.logger = get_logger(self.__class__.__name__)
        self.config = ConfigManager()
        self.cache = FileCache(
            cache_dir=cache_dir,
            default_ttl=cache_ttl,
            namespace=self.__class__.__name__.lower()
        )
        # ... initialization
```

---

## API Key Management

KRL Data Connectors resolve API credentials securely and automatically, supporting multiple strategies for institutional and development environments. For comprehensive details, see [API_KEY_SETUP.md](./API_KEY_SETUP.md).

### Credential Resolution Order

1. **Environment Variables** (recommended for production)
2. **Configuration file** at `~/.krl/apikeys` (recommended for development)
3. **Direct assignment in code** (not recommended for production)

#### Example: Environment Variables

```bash
export BEA_API_KEY="your_bea_key"
export FRED_API_KEY="your_fred_key"
export BLS_API_KEY="your_bls_key"
export CENSUS_API_KEY="your_census_key"
```

#### Example: Configuration File

```bash
mkdir -p ~/.krl
cat > ~/.krl/apikeys << EOF
BEA API KEY: your_bea_key
FRED API KEY: your_fred_key
BLS API KEY: your_bls_key
CENSUS API: your_census_key
EOF
chmod 600 ~/.krl/apikeys
```

#### Obtaining API Keys

| Service           | Required?    | Registration URL                                      |
|-------------------|--------------|-------------------------------------------------------|
| CBP/Census        | Optional     | https://api.census.gov/data/key_signup.html           |
| FRED              | Yes          | https://fred.stlouisfed.org/docs/api/api_key.html     |
| BLS               | Recommended* | https://www.bls.gov/developers/home.htm               |
| BEA               | Yes          | https://apps.bea.gov/api/signup/                      |
| LEHD              | No           | N/A                                                  |

*BLS is accessible without a key but with reduced rate limits.

#### Configuration Utilities

KRL Data Connectors provide utilities for automatic discovery of configuration files:

```python
from krl_data_connectors import find_config_file, BEAConnector

config_path = find_config_file('apikeys')
print(f"Config found at: {config_path}")

# Connectors use config file or environment variables automatically
bea = BEAConnector()
```

---

## Configuration

KRL Data Connectors support flexible configuration via environment variables and YAML files, enabling precise control over credentials, caching, and logging.

### Environment Variables

```bash
# API Keys
export CENSUS_API_KEY="your_census_key"
export FRED_API_KEY="your_fred_key"
export BLS_API_KEY="your_bls_key"
export BEA_API_KEY="your_bea_key"

# Cache settings
export KRL_CACHE_DIR="~/.krl_cache"
export KRL_CACHE_TTL="3600"

# Logging
export KRL_LOG_LEVEL="INFO"
export KRL_LOG_FORMAT="json"
```

### YAML Configuration File

```yaml
fred:
  api_key: "your_fred_key"
  base_url: "https://api.stlouisfed.org/fred"
  timeout: 30

census:
  api_key: "your_census_key"
  base_url: "https://api.census.gov/data"

cache:
  directory: "~/.krl_cache"
  ttl: 3600

logging:
  level: "INFO"
  format: "json"
```

Apply configuration in code:

```python
from krl_core import ConfigManager

config = ConfigManager("config.yaml")
fred = FREDConnector(api_key=config.get("fred.api_key"))
```

---

## Connector Catalog

KRL Data Connectors deliver reliable, scalable integration with the following data sources. All connectors are engineered for institutional-grade reliability and seamless analytics integration.

### Production-Ready Connectors

- **County Business Patterns (CBP):** Establishment and employment statistics by industry and geography. [examples/cbp_quickstart.ipynb](examples/)
- **LEHD Origin-Destination:** Worker flows and employment demographics. [examples/lehd_quickstart.ipynb](examples/)
- **FRED:** Economic time series and metadata.
- **BLS:** Labor market and inflation statistics.
- **BEA:** GDP, regional accounts, and personal income.
- **EPA EJScreen:** Environmental justice indicators. [examples/ejscreen_quickstart.ipynb](examples/ejscreen_quickstart.ipynb)
- **HRSA:** Health Professional Shortage Areas, MUA/P, FQHC. [examples/hrsa_quickstart.ipynb](examples/hrsa_quickstart.ipynb)
- **County Health Rankings:** County-level health measures. [examples/chr_quickstart.ipynb](examples/chr_quickstart.ipynb)
- **EPA Air Quality / AirNow:** Real-time and historical AQI. [examples/air_quality_quickstart.ipynb](examples/air_quality_quickstart.ipynb)
- **Zillow Research:** Housing price and rent indices. [examples/zillow_quickstart.ipynb](examples/zillow_quickstart.ipynb)
- **HUD Fair Market Rents:** Rental affordability and income limits. [examples/hud_fmr_quickstart.ipynb](examples/hud_fmr_quickstart.ipynb)
- **FBI UCR:** Crime statistics and arrest data. [examples/fbi_ucr_quickstart.ipynb](examples/fbi_ucr_quickstart.ipynb)
- **NCES:** School and district education statistics. [examples/nces_quickstart.ipynb](examples/nces_quickstart.ipynb)

### In Development and Planned

- **CDC WONDER:** Mortality and natality data (API non-functional; web interface recommended).
- **USDA Food Environment Atlas:** Food access, insecurity, and local food systems.
- **OECD, World Bank, College Scorecard, IPEDS, Superfund Sites, and more:** See [REMAINING_CONNECTORS_ROADMAP.md](REMAINING_CONNECTORS_ROADMAP.md) for the full roadmap.

---

## Roadmap and Quality Standards

KRL Data Connectors are developed according to a structured roadmap, targeting 40 connectors across all major institutional domains. Connectors are prioritized by institutional demand, API availability, and domain coverage.

**Quality controls:**
- Minimum 80% test coverage with comprehensive unit tests
- Full type hints and validation on all public methods
- Robust error handling and informative error messages
- Intelligent, configurable caching
- Structured JSON logging
- Docstrings, usage examples, and quickstart notebooks
- Secure API key management and input validation

For implementation schedules and API specifications, see [REMAINING_CONNECTORS_ROADMAP.md](REMAINING_CONNECTORS_ROADMAP.md).

---

## Testing

KRL Data Connectors include a comprehensive test suite to ensure operational reliability and reproducibility. Execute tests and measure coverage as follows:

```bash
# Run all tests
pytest

# Run specific connector tests
pytest tests/unit/test_ejscreen_connector.py tests/unit/test_hrsa_connector.py tests/unit/test_air_quality_connector.py -v

# Run with coverage reporting
pytest --cov=src --cov-report=html

# Run integration tests (requires API keys)
pytest tests/integration/ -v
```

---

## Development

Establish a reproducible development environment and contribute to KRL Data Connectors using the following workflow:

```bash
# Clone the repository
git clone https://github.com/KR-Labs/krl-data-connectors.git
cd krl-data-connectors

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install development and test dependencies
pip install -e ".[dev,test]"

# Run pre-commit hooks
pre-commit install
pre-commit run --all-files

# Execute tests
pytest

# Build documentation
cd docs && make html
```

---

## Contributing

KR-Labs welcomes contributions that advance the scalability, reliability, and coverage of KRL Data Connectors. Review the [CONTRIBUTING.md](CONTRIBUTING.md) guidelines prior to submitting changes.

All contributors must sign the [Contributor License Agreement (CLA)](https://krlabs.dev/cla) before code can be merged.

---

## License

KRL Data Connectors are distributed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for full license text.

**License highlights:**
- Permits commercial use, modification, and redistribution
- Patent grant included
- Compatible with proprietary software

---

## Support

For technical support, institutional deployment, and community engagement:
- **Documentation:** https://docs.krlabs.dev/data-connectors
- **Issue Tracker:** https://github.com/KR-Labs/krl-data-connectors/issues
- **Discussions:** https://github.com/KR-Labs/krl-data-connectors/discussions
- **Email:** support@krlabs.dev

---

## Related Projects

KRL Data Connectors are part of the KR-Labs analytics infrastructure ecosystem:
- **[krl-open-core](https://github.com/KR-Labs/krl-open-core):** Logging, configuration, and caching utilities
- **[krl-model-zoo](https://github.com/KR-Labs/krl-model-zoo):** Causal inference and forecasting models
- **[krl-dashboard](https://github.com/KR-Labs/krl-dashboard):** Interactive analytics and visualization platform
- **[krl-tutorials](https://github.com/KR-Labs/krl-tutorials):** Reproducible example workflows and onboarding materials

---

## Citation

To cite KRL Data Connectors in research or institutional documentation, use:

```bibtex
@software{krl_data_connectors,
  title = {KRL Data Connectors: Standardized Interfaces for Economic and Social Data},
  author = {KR-Labs},
  year = {2025},
  url = {https://github.com/KR-Labs/krl-data-connectors},
  license = {Apache-2.0}
}
```

---

**Built for reproducibility, scalability, and institutional trust by [KR-Labs](https://krlabs.dev)**

*© 2025 KR-Labs. All rights reserved.*  
*KR-Labs is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.*
