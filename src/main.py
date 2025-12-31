from fastapi import FastAPI, Depends
import asyncio

from .buda_api_service import BudaAPIService
from .dependencies import get_buda_api_service
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

    sales_values_responses = await asyncio.gather(
        *[buda_api_service.get_base_currency_sale_value(
            currency, 
            fiat_currency, 
            portfolio[currency]
        ) for currency in portfolio_currencies]
    )

    portfolio_value = sum([response.sale_value for response in sales_values_responses])
    return PortfolioValueResponse(portfolio_value=portfolio_value, fiat_currency=fiat_currency)