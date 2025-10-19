"""Parameter validator for VnstockLoader."""

from typing import Literal
from .base import StockCloseParams


class VnstockParams(StockCloseParams):
    """
    Validator for vnstock loader parameters.

    Extends base validation with vnstock-specific parameters:
    - source: Data source (VCI or TCBS)
    - interval: Time interval for data points
    """

    source: Literal["VCI", "TCBS"] = "VCI"
    interval: str = "1D"
