# Shared Exchange Configuration Library

A Python library for managing cryptocurrency exchange configurations, providing clean access to exchange data and configuration override capabilities.

## Features

- **Load and manage multiple exchange configurations** from JSON files
- **Clean Python API** for accessing currency, network, and exchange-specific data
- **Configuration override system** for testing and customization

## Installation

```bash
pip install shared-exchange-config

# Requirements: Python 3.10+
```

## Quick Start

### Basic Usage (with default configurations)

```python
from exchange_config import ExchangeConfigManager

# Initialize the manager (loads default JSON configs)
manager = ExchangeConfigManager()

# Access exchange configurations
binance = manager.get_exchange('binance')
print(f"Binance supports {len(binance.available_currencies))} currencies")
```

### Production Usage (with startup configuration)

Check examples/ folder for more detailed usage

## Configuration Management

### Startup Configuration (Recommended for Production)

For Django/FastAPI applications, configure overrides once at startup:

```python
from exchange_config import configure_exchanges

# Multiple configuration sources supported
configure_exchanges(
    config_dict=EXCHANGE_OVERRIDES,        # From Django/FastAPI settings
    config_file="/path/to/overrides.json", # From file
    override_dir="/config/overrides/",     # From directory
    load_env=True,                         # From environment variables
    env_prefix="EXCHANGE_CONFIG_"          # Custom env prefix
)
```

**Configuration Sources:**

1. **Dictionary (Django/FastAPI settings):**
```python
EXCHANGE_OVERRIDES = {
    "exchanges": {
        "binance": {
            "add_currencies": ["CUSTOM_TOKEN"],
            "remove_currencies": ["OLD_TOKEN"],
            "add_fiat_currencies": ["GBP"]
        }
    },
    "global": {
        "add_currencies": ["PLATFORM_TOKEN", "UNIVERSAL_COIN"],
        "add_fiat_currencies": ["GBP", "CAD"]
    }
}
```

2. **Environment Variables:**
```bash
EXCHANGE_CONFIG_BINANCE_ADD_CURRENCIES=CUSTOM_TOKEN,COMPANY_COIN
EXCHANGE_CONFIG_GLOBAL_ADD_CURRENCIES=PLATFORM_TOKEN,UNIVERSAL_COIN
EXCHANGE_CONFIG_GLOBAL_ADD_FIAT_CURRENCIES=GBP,CAD
```

3. **JSON Configuration File:**
```json
{
  "exchanges": {
    "binance": {
      "add_currencies": ["CUSTOM_TOKEN"],
      "set_api_base_url": "https://api.custom.com"
    }
  }
}
```

### Configuration Operations

The library provides a complete, consistent API for both exchange-specific and global configurations. All operations support both single values and lists, and there are `add_` operations available for all core configuration fields:

**Currency Operations:**
- `add_currencies` - Add cryptocurrencies (supports both single values and lists)
- `add_fiat_currencies` - Add fiat currencies (supports both single values and lists)  
- `remove_currencies` - Remove currencies (supports both single values and lists)

**Network Operations:**
- `add_currency_networks` - Add network mappings for currencies
- `add_networks` - Add networks to the networks dictionary (format: {"NETWORK_NAME": "network_value"})
- `add_currency_and_network_to_alias_map` - Add currency-network to alias mappings

**Field Operations:**
- `set_*` - Set any configuration field directly (e.g., `set_api_timeout`, `set_custom_field`)

**Supported Override Fields:**
- `available_currencies` - List of available cryptocurrencies
- `available_fiat_currencies` - List of available fiat currencies  
- `currencies_to_networks` - Currency to networks mapping
- `networks` - Available networks
- `currency_and_network_to_alias_map` - Currency-network to alias mapping

**Usage Examples:**
```python
# Exchange-specific configuration
"binance": {
    "add_currencies": ["TOKEN1", "TOKEN2"],        # Multiple currencies
    "add_fiat_currencies": "GBP",                  # Single currency (string)
    "remove_currencies": ["OLD_TOKEN"],            # Remove multiple
    "add_currency_networks": {                     # Add network mappings
        "BTC": ["LIGHTNING"], 
        "ETH": ["ARBITRUM"]
    },
    "add_networks": {"POLYGON": "polygon", "BSC": "bsc"},            # Add available networks
    "add_currency_and_network_to_alias_map": {     # Add alias mappings
        "BTC-LIGHTNING": "BTC_LN",
        "ETH-ARBITRUM": "ETH_ARB"
    }
}

# Global configuration (applies to all exchanges)
"global": {
    "add_currencies": ["PLATFORM_TOKEN", "GLOBAL_COIN"],  # Multiple currencies
    "add_fiat_currencies": ["EUR", "JPY"],                # Multiple fiat currencies
    "remove_currencies": "DEPRECATED_TOKEN",              # Single removal (string)
    "add_networks": {"SOLANA": "solana"}                  # Add network globally
}
```

## Development

### Code Organization

The library has a clean, focused structure:

- **`overrides/`**: Configuration override management with clear separation of concerns:
  - `__init__.py`: Public API (`configure_exchanges`, `apply_startup_configuration`) and module functions
  - `settings_parser.py`: `ExchangeOverridesConfigSettings` class for loading override configuration from various sources
  - `applicator.py`: `ConfigurationApplicator` class for applying overrides to exchange configurations
- **`exchanges/`**: Exchange-specific classes with specialized functionality
- **`manager.py`**: High-level manager for working with multiple exchanges
- **`__init__.py`**: Main package exports for public API

This structure provides a clean, organized codebase with clear separation of concerns.
