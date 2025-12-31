from fastapi import FastAPI, Depends
import asyncio
from pydantic import BaseModel

from .buda_api_service import BudaAPIService
from .dependencies import get_buda_api_service
from .lifespan import lifespan

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"message": "ok"}


class PortfolioValueRequest(BaseModel):
    portfolio: dict[str, float]
    fiat_currency: str

class PortfolioValueResponse(BaseModel):
    portfolio_value: float
    fiat_currency: str

@app.post("/calculate-portfolio-value")
async def calculate_portfolio_value(
    request: PortfolioValueRequest, 
    buda_api_service: BudaAPIService = Depends(get_buda_api_service)
    ) -> PortfolioValueResponse:

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
    return PortfolioValueResponse(portfolio_value, fiat_currency)