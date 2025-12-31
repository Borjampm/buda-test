class BudaAPIError(Exception):
    """Base exception for Buda API errors."""
    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class MarketNotFoundError(BudaAPIError):
    """Raised when a market (currency pair) does not exist."""
    def __init__(self, market: str):
        self.market = market
        super().__init__(f"Market '{market}' does not exist", status_code=404)

