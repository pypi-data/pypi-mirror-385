"""Tests for BaseAPIClient."""

import httpx
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from cli.client.base import BaseAPIClient
from cli.client.exceptions import (
    APIError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from cli.config import GlobalConfig, EnvironmentConfig


class ConcreteAPIClient(BaseAPIClient):
    """Concrete implementation for testing."""

    pass


@pytest.fixture
def client():
    """Create a test client instance."""
    return ConcreteAPIClient(
        base_url="http://test.example.com",
        auth_token="test_token",
        timeout=5.0,
    )


@pytest.fixture
def agent_client():
    """Create a test client with agent key."""
    return ConcreteAPIClient(
        base_url="http://test.example.com",
        agent_key="anyt_agent_test_key",
        timeout=5.0,
    )


class TestInitialization:
    """Test client initialization."""

    def test_init_with_auth_token(self, client):
        """Test initialization with auth token."""
        assert client.base_url == "http://test.example.com"
        assert client.auth_token == "test_token"
        assert client.agent_key is None
        assert client.timeout == 5.0
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test_token"

    def test_init_with_agent_key(self, agent_client):
        """Test initialization with agent key."""
        assert agent_client.base_url == "http://test.example.com"
        assert agent_client.auth_token is None
        assert agent_client.agent_key == "anyt_agent_test_key"
        assert "X-API-Key" in agent_client.headers
        assert agent_client.headers["X-API-Key"] == "anyt_agent_test_key"

    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base URL."""
        client = ConcreteAPIClient(base_url="http://test.example.com/")
        assert client.base_url == "http://test.example.com"

    def test_init_default_timeout(self):
        """Test default timeout value."""
        client = ConcreteAPIClient(base_url="http://test.example.com")
        assert client.timeout == 10.0


class TestFromConfig:
    """Test from_config class method."""

    def test_from_config_with_auth_token(self, monkeypatch):
        """Test creating client from config with auth token."""
        # Clear environment variables to avoid interference
        monkeypatch.delenv("ANYT_AUTH_TOKEN", raising=False)
        monkeypatch.delenv("ANYT_AGENT_KEY", raising=False)
        monkeypatch.delenv("ANYT_API_URL", raising=False)
        monkeypatch.delenv("ANYT_ENV", raising=False)

        config = GlobalConfig(
            current_environment="test",
            environments={
                "test": EnvironmentConfig(
                    api_url="http://test.example.com",
                    auth_token="test_token",
                )
            },
        )

        client = ConcreteAPIClient.from_config(config)
        assert client.base_url == "http://test.example.com"
        assert client.auth_token == "test_token"
        assert client.agent_key is None

    def test_from_config_with_agent_key(self, monkeypatch):
        """Test creating client from config with agent key."""
        # Clear environment variables to avoid interference
        monkeypatch.delenv("ANYT_AUTH_TOKEN", raising=False)
        monkeypatch.delenv("ANYT_AGENT_KEY", raising=False)
        monkeypatch.delenv("ANYT_API_URL", raising=False)
        monkeypatch.delenv("ANYT_ENV", raising=False)

        config = GlobalConfig(
            current_environment="test",
            environments={
                "test": EnvironmentConfig(
                    api_url="http://test.example.com",
                    agent_key="anyt_agent_test_key",
                )
            },
        )

        client = ConcreteAPIClient.from_config(config)
        assert client.base_url == "http://test.example.com"
        assert client.auth_token is None
        assert client.agent_key == "anyt_agent_test_key"

    def test_from_config_no_api_url(self):
        """Test that from_config raises error if no API URL configured."""
        config = GlobalConfig(
            current_environment="test",
            environments={
                "test": EnvironmentConfig(
                    api_url="",  # Empty API URL
                )
            },
        )

        with pytest.raises(RuntimeError, match="No API URL configured"):
            ConcreteAPIClient.from_config(config)


class TestHTTPMethods:
    """Test HTTP methods."""

    @pytest.mark.asyncio
    async def test_get_request(self, client):
        """Test GET request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = True
        mock_response.json.return_value = {"data": "test"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await client.get("/test", params={"key": "value"})

            mock_client.get.assert_called_once_with(
                "http://test.example.com/test",
                headers={"Authorization": "Bearer test_token"},
                params={"key": "value"},
                timeout=5.0,
            )
            assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_post_request(self, client):
        """Test POST request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = True
        mock_response.json.return_value = {"data": "created"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await client.post("/test", json={"title": "test"})

            mock_client.post.assert_called_once_with(
                "http://test.example.com/test",
                headers={"Authorization": "Bearer test_token"},
                json={"title": "test"},
                timeout=5.0,
            )
            assert result == {"data": "created"}

    @pytest.mark.asyncio
    async def test_patch_request(self, client):
        """Test PATCH request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = True
        mock_response.json.return_value = {"data": "updated"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.patch.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await client.patch("/test/1", json={"title": "new title"})

            mock_client.patch.assert_called_once_with(
                "http://test.example.com/test/1",
                headers={"Authorization": "Bearer test_token"},
                json={"title": "new title"},
                timeout=5.0,
            )
            assert result == {"data": "updated"}

    @pytest.mark.asyncio
    async def test_delete_request(self, client):
        """Test DELETE request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = True
        mock_response.json.return_value = {}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.delete.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await client.delete("/test/1")

            mock_client.delete.assert_called_once_with(
                "http://test.example.com/test/1",
                headers={"Authorization": "Bearer test_token"},
                timeout=5.0,
            )
            assert result == {}


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_404_raises_not_found(self, client):
        """Test that 404 raises NotFoundError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Task not found"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(NotFoundError, match="Task not found"):
                await client.get("/test")

    @pytest.mark.asyncio
    async def test_401_raises_authentication_error(self, client):
        """Test that 401 raises AuthenticationError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid token"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(AuthenticationError, match="Invalid token"):
                await client.get("/test")

    @pytest.mark.asyncio
    async def test_422_raises_validation_error(self, client):
        """Test that 422 raises ValidationError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 422
        mock_response.json.return_value = {"message": "Invalid data"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(ValidationError, match="Invalid data"):
                await client.post("/test", json={})

    @pytest.mark.asyncio
    async def test_409_raises_conflict_error(self, client):
        """Test that 409 raises ConflictError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 409
        mock_response.json.return_value = {"message": "Duplicate identifier"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(ConflictError, match="Duplicate identifier"):
                await client.post("/test", json={})

    @pytest.mark.asyncio
    async def test_500_raises_api_error(self, client):
        """Test that 500 raises generic APIError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Server error"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(APIError, match="Server error"):
                await client.get("/test")

    def test_extract_error_message_with_detail(self, client):
        """Test extracting error message from 'detail' field."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.reason_phrase = "Not Found"
        mock_response.json.return_value = {"detail": "Resource not found"}

        message = client._extract_error_message(mock_response)
        assert message == "Resource not found"

    def test_extract_error_message_fallback(self, client):
        """Test fallback error message when JSON parsing fails."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.reason_phrase = "Internal Server Error"
        mock_response.json.side_effect = Exception("JSON parse error")

        message = client._extract_error_message(mock_response)
        assert "HTTP 500" in message


class TestResponseUnwrapping:
    """Test response unwrapping."""

    def test_unwrap_success_response(self, client):
        """Test unwrapping SuccessResponse[T] wrapper."""
        response = {"data": {"id": 1, "title": "test"}}
        unwrapped = client._unwrap_response(response)
        assert unwrapped == {"id": 1, "title": "test"}

    def test_unwrap_non_wrapped_response(self, client):
        """Test that non-wrapped responses pass through."""
        response = {"id": 1, "title": "test"}
        unwrapped = client._unwrap_response(response)
        assert unwrapped == {"id": 1, "title": "test"}

    def test_unwrap_list_response(self, client):
        """Test unwrapping returns list as-is."""
        response = [{"id": 1}, {"id": 2}]
        unwrapped = client._unwrap_response(response)
        assert unwrapped == [{"id": 1}, {"id": 2}]
