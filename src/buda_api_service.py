from httpx import AsyncClient
from pydantic import BaseModel

class Quotation(BaseModel):
    quote_exchanged: list[str]

class QuotationResponse(BaseModel):
    quotation: Quotation

class SaleValueResponse(BaseModel):
    sale_value: float

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
        response.raise_for_status()
        quotation_response = QuotationResponse(**response.json())
        quotation = quotation_response.quotation
        return SaleValueResponse(sale_value=quotation.quote_exchanged[0])