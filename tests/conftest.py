import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient

from src.buda_api_service import BudaAPIService


@pytest.fixture
def mock_http_client():
    """Create a mock AsyncClient for testing."""
    return AsyncMock(spec=AsyncClient)


@pytest.fixture
def buda_service(mock_http_client):
    """Create a BudaAPIService with a mocked HTTP client."""
    return BudaAPIService(mock_http_client)

