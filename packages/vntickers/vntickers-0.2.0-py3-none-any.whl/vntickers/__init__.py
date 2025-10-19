"""
vntickers - A Python package for fetching Vietnamese stock market data.

This package provides a unified interface to access stock price data from multiple
data sources (vnstock, vnquant, and vietfin).

Uses lazy imports to avoid loading unnecessary dependencies.
"""

from typing import TYPE_CHECKING

# Type hints for better IDE support
if TYPE_CHECKING:
    from .vnstock_loader import VnstockLoader
    from .vnquant_loader import VnquantLoader
    from .vietfin_loader import VietfinLoader, PriceDataParams
    from .loader import VNStockData
    from .validators import StockCloseParams, VnstockParams, VnquantParams, VietfinParams

# Export all public APIs
__all__ = [
    # Focused loaders (recommended for new code)
    "VnstockLoader",
    "VnquantLoader",
    "VietfinLoader",
    # Parameter validators
    "StockCloseParams",
    "VnstockParams",
    "VnquantParams",
    "VietfinParams",
    "PriceDataParams",
    # Legacy facade (for backward compatibility)
    "VNStockData",
]


def __getattr__(name: str):
    """
    Lazy import loaders and validators to avoid loading all dependencies at once.

    This allows users to import only what they need without
    loading dependencies for other data sources.
    """
    # Loaders
    if name == "VnstockLoader":
        from .vnstock_loader import VnstockLoader
        return VnstockLoader
    elif name == "VnquantLoader":
        from .vnquant_loader import VnquantLoader
        return VnquantLoader
    elif name == "VietfinLoader":
        from .vietfin_loader import VietfinLoader
        return VietfinLoader
    elif name == "VNStockData":
        from .loader import VNStockData
        return VNStockData

    # Validators
    elif name == "StockCloseParams":
        from .validators import StockCloseParams
        return StockCloseParams
    elif name == "VnstockParams":
        from .validators import VnstockParams
        return VnstockParams
    elif name == "VnquantParams":
        from .validators import VnquantParams
        return VnquantParams
    elif name == "VietfinParams":
        from .validators import VietfinParams
        return VietfinParams
    elif name == "PriceDataParams":
        from .vietfin_loader import PriceDataParams
        return PriceDataParams

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def main() -> None:
    """CLI entry point for vntickers."""
    print("Hello from vntickers!")
