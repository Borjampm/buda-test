from fastapi import FastAPI, Depends
import asyncio
from pydantic import BaseModel

from .buda_api_service import BudaAPIService
from .dependencies import get_buda_api_service
from .lifespan import lifespan

app = FastAPI(lifespan=lifespan)


class PortfolioValueRequest(BaseModel):
    portfolio: dict[str, float]
    fiat_currency: str

class PortfolioValueResponse(BaseModel):
    portfolio_value: float
    fiat_currency: str


@app.get("/health")
async def health_check():
    return {"message": "ok"}

@app.post("/calculate-portfolio-value")
async def calculate_portfolio_value(
    request: PortfolioValueRequest, 
    buda_api_service: BudaAPIService = Depends(get_buda_api_service)
    ) -> PortfolioValueResponse:

    portfolio_currencies = request.portfolio.keys()

    responses = await asyncio.gather(
        *[buda_api_service.get_base_currency_sale_value(
            currency, 
            request.fiat_currency, 
            request.portfolio[currency]
        ) for currency in portfolio_currencies]
    )
    portfolio_value = sum([response.sale_value for response in responses])

    return PortfolioValueResponse(portfolio_value=portfolio_value, fiat_currency=request.fiat_currency)