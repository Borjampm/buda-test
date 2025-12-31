import pytest
from httpx import Response

from src.buda_api_service import BudaAPIService
from src.exceptions import MarketNotFoundError, BudaAPIError


class TestGetBaseCurrencySaleValue:
    """Unit tests for BudaAPIService.get_base_currency_sale_value"""

    async def test_success_returns_sale_value(self, mock_http_client, buda_service):
        """Test successful quotation response returns correct sale value."""
        mock_http_client.post.return_value = Response(
            200,
            json={"quotation": {"quote_exchanged": ["1500000.0", "CLP"]}}
        )
        
        result = await buda_service.get_base_currency_sale_value("BTC", "CLP", 0.5)
        
        assert result.sale_value == 1500000.0
        assert result.base_currency == "BTC"
        mock_http_client.post.assert_called_once_with(
            "/markets/BTC-CLP/quotations",
            json={"type": "ask_given_size", "amount": 0.5}
        )

    async def test_market_not_found_raises_exception(self, mock_http_client, buda_service):
        """Test 404 response raises MarketNotFoundError."""
        mock_http_client.post.return_value = Response(404)
        
        with pytest.raises(MarketNotFoundError) as exc_info:
            await buda_service.get_base_currency_sale_value("FAKE", "CLP", 1.0)
        
        assert exc_info.value.market == "FAKE-CLP"
        assert "FAKE-CLP" in exc_info.value.message

    async def test_client_error_raises_buda_api_error(self, mock_http_client, buda_service):
        """Test 4xx response (non-404) raises BudaAPIError."""
        mock_http_client.post.return_value = Response(
            400,
            json={"message": "Invalid amount"}
        )
        
        with pytest.raises(BudaAPIError) as exc_info:
            await buda_service.get_base_currency_sale_value("BTC", "CLP", -1.0)
        
        assert exc_info.value.status_code == 400
        assert "Invalid amount" in exc_info.value.message

    async def test_server_error_raises_buda_api_error(self, mock_http_client, buda_service):
        """Test 5xx response raises BudaAPIError with server error status."""
        mock_http_client.post.return_value = Response(503)
        
        with pytest.raises(BudaAPIError) as exc_info:
            await buda_service.get_base_currency_sale_value("BTC", "CLP", 1.0)
        
        assert exc_info.value.status_code == 503
        assert "unavailable" in exc_info.value.message.lower()

    async def test_internal_server_error(self, mock_http_client, buda_service):
        """Test 500 response raises BudaAPIError."""
        mock_http_client.post.return_value = Response(500)
        
        with pytest.raises(BudaAPIError) as exc_info:
            await buda_service.get_base_currency_sale_value("ETH", "CLP", 2.0)
        
        assert exc_info.value.status_code == 500

    async def test_constructs_correct_market_pair(self, mock_http_client, buda_service):
        """Test market pair is correctly constructed from currencies."""
        mock_http_client.post.return_value = Response(
            200,
            json={"quotation": {"quote_exchanged": ["5000.0", "USD"]}}
        )
        
        await buda_service.get_base_currency_sale_value("ETH", "USD", 1.0)
        
        call_args = mock_http_client.post.call_args
        assert call_args[0][0] == "/markets/ETH-USD/quotations"

