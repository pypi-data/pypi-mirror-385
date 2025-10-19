"""Vietfin data loader for Vietnamese stock market data."""

import pandas as pd
from vietfin import vf
from typing import Union, List
from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, validator
from .validators import VietfinParams


class VietfinLoader:
    """Loader for fetching historical close prices using vietfin library."""

    @staticmethod
    def get_close_prices(
        symbols: Union[str, List[str]],
        start_date: date,
        end_date: date,
        provider: Literal["dnse", "tcbs"] = "dnse",
        interval: Literal["1m", "15m", "30m", "1h", "1d"] = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical close prices for one or multiple symbols using the Vietfin (vf) provider.

        Parameters
        ----------
        symbols : Union[str, List[str]]
            Stock ticker symbol or list of symbols.
            Note: For intraday intervals (1m, 15m, 30m, 1h), only single symbol supported.
        start_date : date
            Start date for fetching data.
        end_date : date
            End date for fetching data.
            Note: For intraday intervals, max 90-day range (DNSE only).
        provider : Literal["dnse", "tcbs"], optional
            Data provider to use. Default is 'dnse'.
            - 'dnse': Supports 1m, 15m, 30m, 1h, 1d
            - 'tcbs': Supports 1d only
        interval : Literal["1m", "15m", "30m", "1h", "1d"], optional
            Time interval for data points. Default is '1d' (daily).

            **DNSE provider:**
            - '1m': one minute (single symbol, max 90 days)
            - '15m': 15 minutes (single symbol, max 90 days)
            - '30m': 30 minutes (single symbol, max 90 days)
            - '1h': one hour (single symbol, max 90 days)
            - '1d': one day (multiple symbols, unlimited range)

            **TCBS provider:**
            - '1d': one day (multiple symbols, unlimited range)

        Returns
        -------
        pandas.DataFrame
            DataFrame with 'date' as index and columns for each symbol containing close prices.

        Raises
        ------
        ValueError
            - If using intraday interval (1m/15m/30m/1h) with TCBS provider
            - If using intraday intervals with multiple symbols
            - If using intraday intervals with date range > 90 days

        Examples
        --------
        # Daily data for multiple stocks (both providers)
        >>> df = VietfinLoader.get_close_prices(
        ...     symbols=["VNM", "VCB", "HPG"],
        ...     start_date=date(2024, 1, 1),
        ...     end_date=date(2024, 12, 31),
        ...     provider="dnse",  # or "tcbs"
        ...     interval="1d"
        ... )

        # Hourly data for single stock (DNSE only, max 90 days)
        >>> df = VietfinLoader.get_close_prices(
        ...     symbols="VNM",  # Single symbol only
        ...     start_date=date(2024, 10, 1),
        ...     end_date=date(2024, 12, 30),  # 90 days max
        ...     provider="dnse",
        ...     interval="1h"
        ... )

        # 15-minute data for single stock (DNSE only, max 90 days)
        >>> df = VietfinLoader.get_close_prices(
        ...     symbols="VNM",
        ...     start_date=date(2024, 12, 1),
        ...     end_date=date(2024, 12, 31),
        ...     provider="dnse",
        ...     interval="15m"
        ... )
        """
        # Validate common parameters
        params = VietfinParams(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            provider=provider,
            interval=interval
        )

        # Convert to list if single symbol (already handled by validator)
        symbols_list = params.get_symbols_list()

        all_data = []

        for symbol in symbols_list:
            # Use PriceDataParams for per-symbol vietfin-specific validation
            price_params = PriceDataParams(
                symbol=symbol,
                start_date=params.get_start_date_obj(),
                end_date=params.get_end_date_obj(),
                provider=params.provider,
            )

            price_df = vf.equity.price.historical(
                symbol=price_params.symbol,
                provider=price_params.provider,
                start_date=price_params.start_date.strftime("%Y-%m-%d"),
                end_date=price_params.end_date.strftime("%Y-%m-%d"),
                interval=params.interval
            ).to_df()

            if price_df is None or price_df.empty:
                continue

            price_df.index = pd.to_datetime(price_df.index, errors="coerce")
            price_df = price_df.sort_index()

            close_df = price_df[["close"]].copy()
            close_df = close_df.rename(columns={"close": symbol})

            all_data.append(close_df)

        if not all_data:
            return pd.DataFrame()

        combined_df = pd.concat(all_data, axis=1).sort_index()
        return combined_df


class PriceDataParams(BaseModel):
    """
    Parameters for fetching historical equity price data.
    """

    symbol: str = Field(..., description="Stock ticker symbol, e.g., 'VNM'")
    start_date: date = Field(..., description="Start date in 'YYYY-MM-DD' format")
    end_date: date = Field(..., description="End date in 'YYYY-MM-DD' format")
    provider: Literal["dnse", "tcbs"] = Field(
        "dnse", description="Data provider ('dnse' or 'tcbs')"
    )

    @validator("end_date")
    def check_date_order(cls, end_date: date, values):
        """Validate that end_date is after start_date."""
        start_date = values.get("start_date")
        if start_date and end_date < start_date:
            raise ValueError("end_date must be after start_date")
        return end_date
