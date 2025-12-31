from fastapi import FastAPI, Depends, HTTPException
import asyncio

from .buda_api_service import BudaAPIService
from .dependencies import get_buda_api_service
from .exceptions import BudaAPIError, MarketNotFoundError
from .lifespan import lifespan
from .schemas import PortfolioValueRequest, PortfolioValueResponse

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"message": "ok"}


@app.post("/calculate-portfolio-value")
async def calculate_portfolio_value(
    request: PortfolioValueRequest, 
    buda_api_service: BudaAPIService = Depends(get_buda_api_service)
    ) -> PortfolioValueResponse:
    """
    Calculate the value of a portfolio in a given fiat currency in real time, by simulating the sale of the portfolio using the Buda API.
    """

    portfolio = request.portfolio
    portfolio_currencies = portfolio.keys()
    fiat_currency = request.fiat_currency

    if not has_only_positive_amounts(portfolio):
        raise HTTPException(status_code=400, detail="All amounts must be higher than 0")

    try:
        sales_values_responses = await asyncio.gather(
            *[buda_api_service.get_base_currency_sale_value(
                currency, 
                fiat_currency, 
                portfolio[currency]
            ) for currency in portfolio_currencies]
        )
    except MarketNotFoundError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except BudaAPIError as e:
        status_code = 502 if e.status_code and e.status_code >= 500 else 400
        raise HTTPException(status_code=status_code, detail=e.message)

    portfolio_value = sum([response.sale_value for response in sales_values_responses])
    return PortfolioValueResponse(portfolio_value=portfolio_value, fiat_currency=fiat_currency)


def has_only_positive_amounts(portfolio: dict[str, float]) -> bool:
    return all(amount > 0 for amount in portfolio.values())