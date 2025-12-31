import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from src.main import app
from src.dependencies import get_buda_api_service
from src.buda_api_service import BudaAPIService, SaleValueResponse
from src.exceptions import MarketNotFoundError, BudaAPIError


@pytest.fixture
def client():
    """Create a test client and cleanup dependency overrides after each test."""
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_mock_service(responses: dict[str, SaleValueResponse | Exception]):
    """
    Factory to create a mock BudaAPIService.
    
    Args:
        responses: Dict mapping currency to either a SaleValueResponse or an Exception to raise.
    """
    mock = AsyncMock(spec=BudaAPIService)
    
    async def mock_get_sale_value(base_currency: str, quote_currency: str, amount: float):
        if base_currency in responses:
            result = responses[base_currency]
            if isinstance(result, Exception):
                raise result
            return result
        raise MarketNotFoundError(f"{base_currency}-{quote_currency}")
    
    mock.get_base_currency_sale_value.side_effect = mock_get_sale_value
    return mock


class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check_returns_ok(self, client):
        """Test health check endpoint returns ok status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}


class TestCalculatePortfolioValue:
    """Integration tests for the calculate-portfolio-value endpoint."""

    def test_single_currency_portfolio(self, client):
        """Test portfolio calculation with a single currency."""
        mock_service = create_mock_service({
            "BTC": SaleValueResponse(sale_value=50000000.0, base_currency="BTC"),
        })
        app.dependency_overrides[get_buda_api_service] = lambda: mock_service
        
        response = client.post("/calculate-portfolio-value", json={
            "portfolio": {"BTC": 1.0},
            "fiat_currency": "CLP"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["portfolio_value"] == 50000000.0
        assert data["fiat_currency"] == "CLP"

    def test_multiple_currencies_portfolio(self, client):
        """Test portfolio calculation with multiple currencies."""
        mock_service = create_mock_service({
            "BTC": SaleValueResponse(sale_value=50000000.0, base_currency="BTC"),
            "ETH": SaleValueResponse(sale_value=2000000.0, base_currency="ETH"),
            "USDT": SaleValueResponse(sale_value=1000000.0, base_currency="USDT"),
        })
        app.dependency_overrides[get_buda_api_service] = lambda: mock_service
        
        response = client.post("/calculate-portfolio-value", json={
            "portfolio": {"BTC": 1.0, "ETH": 2.0, "USDT": 1000.0},
            "fiat_currency": "CLP"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["portfolio_value"] == 53000000.0

    def test_invalid_currency_returns_400(self, client):
        """Test that non-existent currency returns 400 error."""
        mock_service = create_mock_service({
            "BTC": SaleValueResponse(sale_value=100.0, base_currency="BTC"),
        })
        app.dependency_overrides[get_buda_api_service] = lambda: mock_service
        
        response = client.post("/calculate-portfolio-value", json={
            "portfolio": {"FAKECOIN": 1.0},
            "fiat_currency": "CLP"
        })
        
        assert response.status_code == 400
        assert "FAKECOIN-CLP" in response.json()["detail"]

    def test_negative_amount_returns_400(self, client):
        """Test that negative amount returns validation error."""
        response = client.post("/calculate-portfolio-value", json={
            "portfolio": {"BTC": -1.0},
            "fiat_currency": "CLP"
        })
        
        assert response.status_code == 400
        assert "higher than 0" in response.json()["detail"]

    def test_zero_amount_returns_400(self, client):
        """Test that zero amount returns validation error."""
        response = client.post("/calculate-portfolio-value", json={
            "portfolio": {"BTC": 0.0},
            "fiat_currency": "CLP"
        })
        
        assert response.status_code == 400
        assert "higher than 0" in response.json()["detail"]

    def test_buda_server_error_returns_502(self, client):
        """Test that Buda API server error returns 502 Bad Gateway."""
        mock_service = create_mock_service({
            "BTC": BudaAPIError("Buda API is unavailable", status_code=503),
        })
        app.dependency_overrides[get_buda_api_service] = lambda: mock_service
        
        response = client.post("/calculate-portfolio-value", json={
            "portfolio": {"BTC": 1.0},
            "fiat_currency": "CLP"
        })
        
        assert response.status_code == 502

    def test_buda_client_error_returns_400(self, client):
        """Test that Buda API client error returns 400."""
        mock_service = create_mock_service({
            "BTC": BudaAPIError("Invalid request", status_code=422),
        })
        app.dependency_overrides[get_buda_api_service] = lambda: mock_service
        
        response = client.post("/calculate-portfolio-value", json={
            "portfolio": {"BTC": 1.0},
            "fiat_currency": "CLP"
        })
        
        assert response.status_code == 400

    def test_empty_portfolio_returns_zero(self, client):
        """Test that empty portfolio returns zero value."""
        mock_service = create_mock_service({})
        app.dependency_overrides[get_buda_api_service] = lambda: mock_service
        
        response = client.post("/calculate-portfolio-value", json={
            "portfolio": {},
            "fiat_currency": "CLP"
        })
        
        assert response.status_code == 200
        assert response.json()["portfolio_value"] == 0.0

    def test_missing_portfolio_returns_422(self, client):
        """Test that missing portfolio field returns validation error."""
        response = client.post("/calculate-portfolio-value", json={
            "fiat_currency": "CLP"
        })
        
        assert response.status_code == 422

    def test_missing_fiat_currency_returns_422(self, client):
        """Test that missing fiat_currency field returns validation error."""
        response = client.post("/calculate-portfolio-value", json={
            "portfolio": {"BTC": 1.0}
        })
        
        assert response.status_code == 422

