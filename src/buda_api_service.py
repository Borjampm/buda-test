from httpx import AsyncClient
from pydantic import BaseModel

from .exceptions import BudaAPIError, MarketNotFoundError

class Quotation(BaseModel):
    quote_exchanged: list[str]

class QuotationResponse(BaseModel):
    quotation: Quotation

class SaleValueResponse(BaseModel):
    sale_value: float
    base_currency: str

class BudaAPIService:
    def __init__(self, client: AsyncClient):
        self.client = client
    
    async def get_base_currency_sale_value(self, base_currency: str, quote_currency: str, amount: float) -> SaleValueResponse:
        market = f'{base_currency}-{quote_currency}'
        response = await self.client.post(
            f"/markets/{market}/quotations", 
            json={
                'type': 'ask_given_size', 
                'amount': amount
            })
        
        if response.status_code == 404:
            raise MarketNotFoundError(market)
        
        if response.status_code >= 400 and response.status_code < 500:
            error_detail = response.json().get("message", response.text)
            raise BudaAPIError(f"Client error for market '{market}': {error_detail}", status_code=response.status_code)
        
        if response.status_code >= 500:
            raise BudaAPIError(f"Buda API is unavailable (status {response.status_code})", status_code=response.status_code)
        
        quotation_response = QuotationResponse(**response.json())
        quotation = quotation_response.quotation
        return SaleValueResponse(sale_value=float(quotation.quote_exchanged[0]), base_currency=base_currency)