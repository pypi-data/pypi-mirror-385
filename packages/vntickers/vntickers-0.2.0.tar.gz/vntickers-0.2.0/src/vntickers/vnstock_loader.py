"""Vnstock data loader for Vietnamese stock market data."""

import pandas as pd
from vnstock import Vnstock
from .validators import VnstockParams


class VnstockLoader:
    """Loader for fetching stock data using vnstock library (VCI source)."""

    @staticmethod
    def get_close_prices(
        symbols: list[str],
        start_date: str,
        end_date: str,
        interval: str = "1D",
        source: str = "VCI"
    ) -> pd.DataFrame:
        """
        Fetch close prices for multiple stocks and return a DataFrame
        where each column is a ticker symbol.

        Args:
            symbols (list[str]): List of stock ticker symbols.
            start_date (str): Start date in 'YYYY-MM-DD' format.
            end_date (str): End date in 'YYYY-MM-DD' format.
            interval (str): Time interval ('1D' for daily, etc.). Default is '1D'.
            source (str): Data source ('VCI' or 'TCBS'). Default is 'VCI'.

        Returns:
            pd.DataFrame: Wide-format DataFrame with 'time' as index and
                ticker symbols as columns (values = close prices).
        """
        # Validate parameters
        params = VnstockParams(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            source=source
        )

        all_data = {}

        for symbol in params.get_symbols_list():
            stock = Vnstock().stock(symbol=symbol, source=params.source)
            price = stock.quote.history(
                start=params.get_start_date_str(),
                end=params.get_end_date_str(),
                interval=params.interval,
                to_df=True
            )

            # Set index to 'time' (already datetime64[ns])
            price = price.set_index("time").sort_index()

            # Store the 'close' column under the stock symbol
            all_data[symbol] = price["close"]

        # Combine into one DataFrame (outer join on time index)
        df = pd.DataFrame(all_data)

        return df
