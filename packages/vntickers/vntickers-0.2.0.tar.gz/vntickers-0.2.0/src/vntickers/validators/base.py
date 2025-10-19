"""Base parameter validator for all stock data loaders."""

from pydantic import BaseModel, Field, validator
from typing import List, Union
from datetime import date, datetime


class StockCloseParams(BaseModel):
    """
    Base validator for common stock data parameters.

    All loader-specific param classes inherit from this.
    Provides validation for symbols and date parameters that are common
    across all data loaders.
    """

    symbols: List[str] = Field(..., description="List of stock ticker symbols")
    start_date: Union[str, date] = Field(..., description="Start date (YYYY-MM-DD or date object)")
    end_date: Union[str, date] = Field(..., description="End date (YYYY-MM-DD or date object)")

    @validator('symbols', pre=True)
    def validate_symbols(cls, v):
        """
        Validate and normalize symbols list.

        - Converts single string to list
        - Uppercases all symbols
        - Validates ticker format (2-4 alphanumeric characters)
        """
        if isinstance(v, str):
            v = [v]
        if not v or len(v) == 0:
            raise ValueError("symbols list cannot be empty")

        # Uppercase and validate format
        normalized = []
        for symbol in v:
            symbol = symbol.upper().strip()
            if not (2 <= len(symbol) <= 4 and symbol.isalnum()):
                raise ValueError(f"Invalid ticker format: {symbol}. Must be 2-4 alphanumeric characters.")
            normalized.append(symbol)
        return normalized

    @validator('start_date', 'end_date', pre=True)
    def validate_date(cls, v):
        """
        Validate and parse date.

        Accepts:
        - date objects (returned as-is)
        - Strings in YYYY-MM-DD format (parsed to date)
        """
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}")
        raise ValueError(f"Date must be string or date object, got: {type(v).__name__}")

    @validator('end_date')
    def check_date_order(cls, end_date, values):
        """Ensure end_date >= start_date."""
        start_date = values.get('start_date')
        if start_date and end_date < start_date:
            raise ValueError("end_date must be after or equal to start_date")
        return end_date

    # Helper methods for accessing validated/normalized data

    def get_symbols_list(self) -> List[str]:
        """Get normalized list of symbols (uppercased)."""
        return self.symbols

    def get_start_date_str(self) -> str:
        """Get start_date as YYYY-MM-DD string."""
        if isinstance(self.start_date, date):
            return self.start_date.strftime("%Y-%m-%d")
        return self.start_date

    def get_end_date_str(self) -> str:
        """Get end_date as YYYY-MM-DD string."""
        if isinstance(self.end_date, date):
            return self.end_date.strftime("%Y-%m-%d")
        return self.end_date

    def get_start_date_obj(self) -> date:
        """Get start_date as date object."""
        return self.start_date

    def get_end_date_obj(self) -> date:
        """Get end_date as date object."""
        return self.end_date
