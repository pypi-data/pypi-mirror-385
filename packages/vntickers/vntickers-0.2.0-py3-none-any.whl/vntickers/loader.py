"""
Backward-compatible facade for VNStockData.

This module maintains backward compatibility with existing code while delegating
to the new modular loaders. For new code, prefer using the focused loaders directly:
- VnstockLoader from vnstock_loader
- VnquantLoader from vnquant_loader
- VietfinLoader from vietfin_loader

Uses lazy imports to only load dependencies when methods are actually called.
"""

import pandas as pd
from typing import List, Optional, Union, TYPE_CHECKING
from datetime import date
from typing import Literal

# Lazy import - only load when needed
if TYPE_CHECKING:
    from .vietfin_loader import PriceDataParams

# Re-export PriceDataParams for backward compatibility
__all__ = ["VNStockData", "PriceDataParams"]


def __getattr__(name: str):
    """Lazy load PriceDataParams only when accessed."""
    if name == "PriceDataParams":
        from .vietfin_loader import PriceDataParams
        return PriceDataParams
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


class VNStockData:
    """
    Legacy facade class for fetching Vietnamese stock market data.

    This class maintains backward compatibility with existing code.
    For new code, prefer using the focused loaders directly:
    - VnstockLoader.get_close_prices() for vnstock data
    - VnquantLoader.get_close_prices() for vnquant data
    - VietfinLoader.get_close_prices() for vietfin data
    """

    @staticmethod
    def get_close_prices_vns(symbols, start_date, end_date, interval="1D"):
        """
        Fetch close prices for multiple stocks using vnstock (VCI source).

        Args:
            symbols: List of stock ticker symbols.
            start_date (str): Start date in 'YYYY-MM-DD' format.
            end_date (str): End date in 'YYYY-MM-DD' format.
            interval (str): Time interval ('1D' for daily, etc.). Default is '1D'.

        Returns:
            pd.DataFrame: Wide-format DataFrame with 'time' as index and
                ticker symbols as columns (values = close prices).
        """
        from .vnstock_loader import VnstockLoader
        return VnstockLoader.get_close_prices(symbols, start_date, end_date, interval)

    @staticmethod
    def get_close_prices_vnq(
        symbols: List[str], start_date: str, end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        Load adjusted close stock data for given symbols from vnquant DataLoader.

        Args:
            symbols (List[str]): List of stock symbols.
            start_date (str): Start date in 'YYYY-MM-DD' format.
            end_date (str): End date in 'YYYY-MM-DD' format.

        Returns:
            Optional[pd.DataFrame]: Wide-format DataFrame with 'time' as index and
                ticker symbols as columns (values = adjusted close).
                Returns None if data is not available.
        """
        from .vnquant_loader import VnquantLoader
        return VnquantLoader.get_close_prices(symbols, start_date, end_date)

    @staticmethod
    def get_close_prices_vf(
        symbols: Union[str, List[str]],
        start_date: date,
        end_date: date,
        provider: Literal["dnse", "tcbs"] = "dnse",
    ) -> pd.DataFrame:
        """
        Fetch historical close prices using the Vietfin (vf) provider.

        Parameters
        ----------
        symbols : Union[str, List[str]]
            Stock ticker symbol or list of symbols.
        start_date : date
            Start date for fetching data.
        end_date : date
            End date for fetching data.
        provider : Literal["dnse", "tcbs"], optional
            Data provider to use ('dnse' or 'tcbs'). Default is 'dnse'.

        Returns
        -------
        pandas.DataFrame
            DataFrame with 'date' as index and columns for each symbol containing close prices.
        """
        from .vietfin_loader import VietfinLoader
        return VietfinLoader.get_close_prices(symbols, start_date, end_date, provider)
