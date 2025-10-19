"""Parameter validator for VietfinLoader."""

from typing import Literal
from pydantic import validator
from .base import StockCloseParams


class VietfinParams(StockCloseParams):
    """
    Validator for vietfin loader parameters.

    Extends base validation with vietfin-specific parameters:
    - provider: Data provider (dnse or tcbs)
    - interval: Time interval for data points
      - DNSE supports: 1m, 15m, 30m, 1h, 1d
      - TCBS supports: 1d only
    """

    provider: Literal["dnse", "tcbs"] = "dnse"
    interval: Literal["1m", "15m", "30m", "1h", "1d"] = "1d"

    @validator('interval')
    def validate_interval_for_provider(cls, interval, values):
        """Validate interval is supported by the selected provider."""
        provider = values.get('provider')

        # TCBS only supports 1d
        if provider == 'tcbs' and interval != '1d':
            raise ValueError(
                f"TCBS provider only supports interval '1d'. "
                f"Got '{interval}'. Use DNSE provider for intraday data (1m, 15m, 30m, 1h)."
            )

        return interval

    @validator('symbols')
    def validate_symbols_for_interval(cls, symbols, values):
        """Validate symbols count for intraday intervals."""
        interval = values.get('interval', '1d')

        # Intraday intervals only support single stock
        if interval in ['1m', '15m', '30m', '1h'] and len(symbols) > 1:
            raise ValueError(
                f"Intraday interval '{interval}' only supports single symbol. "
                f"Got {len(symbols)} symbols. Please fetch one symbol at a time."
            )

        return symbols

    @validator('end_date')
    def validate_date_range_for_intraday(cls, end_date, values):
        """Validate date range for intraday intervals (DNSE 90-day limit)."""
        start_date = values.get('start_date')
        interval = values.get('interval', '1d')
        provider = values.get('provider', 'dnse')

        if start_date and provider == 'dnse' and interval in ['1m', '15m', '30m', '1h']:
            date_diff = (end_date - start_date).days

            if date_diff > 90:
                raise ValueError(
                    f"DNSE provider has a 90-day limit for interval '{interval}'. "
                    f"Requested range: {date_diff} days. "
                    f"Please reduce date range to 90 days or less."
                )

        return end_date
