from pydantic import BaseModel

class PortfolioValueRequest(BaseModel):
    portfolio: dict[str, float]
    fiat_currency: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "portfolio": {
                        "BTC": 0.5,
                        "ETH": 2.0,
                        "USDT": 1000
                    },
                    "fiat_currency": "CLP"
                }
            ]
        }
    }


class PortfolioValueResponse(BaseModel):
    portfolio_value: float
    fiat_currency: str