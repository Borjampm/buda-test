from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        base_url="https://www.buda.com/api/v2",
        timeout=30.0,
    )
    yield
    await app.state.http_client.aclose()