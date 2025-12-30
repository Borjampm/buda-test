from fastapi import Request, Depends
from httpx import AsyncClient
from .buda_api_service import BudaAPIService

def get_http_client(request: Request) -> AsyncClient:
    return request.app.state.http_client

def get_buda_api_service(
    client: AsyncClient = Depends(get_http_client)
) -> BudaAPIService:
    return BudaAPIService(client)