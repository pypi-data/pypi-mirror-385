"""Parameter validator for VnquantLoader."""

from .base import StockCloseParams


class VnquantParams(StockCloseParams):
    """
    Validator for vnquant loader parameters.

    Currently only uses base validation.
    Reserved for future vnquant-specific parameters (e.g., source="cafe"/"vnd").
    """

    pass
