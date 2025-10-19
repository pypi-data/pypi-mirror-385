# vntickers

A unified Python package for fetching Vietnamese stock market data. This package combines vnstock, vnquant, and vietfin into a single source of truth for retrieving OHLCV (Open, High, Low, Close, Volume) and close prices for stock analysis in the Vietnamese market.

## Installation

### From source (development)

```bash
git clone https://github.com/gahoccode/vntickers.git
cd vntickers
uv sync
```

### Add to your project

```bash
uv add vntickers
```

## Usage

### Using vnstock (VCI source)

```python
from vntickers.loader import VNStockData

stocks = ["VNM", "VCB", "HPG"]
start_date = "2024-01-01"
end_date = "2024-12-31"

df = VNStockData.get_close_prices_vns(
    symbols=stocks,
    start_date=start_date,
    end_date=end_date,
    interval="1D"
)
print(df.head())
```

### Using vnquant

```python
from vntickers.loader import VNStockData

stocks = ["VNM", "VCB", "HPG"]
start_date = "2024-01-01"
end_date = "2024-12-31"

df = VNStockData.get_close_prices_vnq(
    symbols=stocks,
    start_date=start_date,
    end_date=end_date
)
print(df.head())
```

### Using vietfin (Recommended - Modern API)

```python
from vntickers import VietfinLoader
from datetime import date

# Daily data for multiple stocks (DNSE or TCBS)
df = VietfinLoader.get_close_prices(
    symbols=["VNM", "VCB", "HPG"],
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    provider="dnse",  # or "tcbs"
    interval="1d"
)
print(df.head())

# Intraday data - hourly (DNSE only, single symbol, max 90 days)
df_hourly = VietfinLoader.get_close_prices(
    symbols="VNM",  # Single symbol for intraday
    start_date=date(2024, 10, 1),
    end_date=date(2024, 12, 30),  # Max 90 days
    provider="dnse",
    interval="1h"  # Supported: 1m, 15m, 30m, 1h
)
print(df_hourly.head())
```

**Vietfin Provider Support:**
- **DNSE**: Supports `1m`, `15m`, `30m`, `1h`, `1d`
  - Intraday intervals (1m, 15m, 30m, 1h): Single symbol only, max 90 days
  - Daily (1d): Multiple symbols, unlimited range
- **TCBS**: Supports `1d` only (multiple symbols, unlimited range)

All methods return a pandas DataFrame with:
- Index: time/date (datetime)
- Columns: ticker symbols
- Values: close prices (adjusted close for vnquant)

## Requirements

- Python >=3.10
- vnstock >=3.2.6
- vnquant
- vietfin
- pandas
- pydantic

## Publishing to PyPI

### Prerequisites
1. Create a PyPI account at https://pypi.org
2. Create an API token at https://pypi.org/manage/account/token/

### Build and Publish

```bash
# Build the package
uv build

# Publish to PyPI (you'll be prompted for your API token)
uv publish

# Or use token directly
uv publish --token <your-pypi-token>
```

