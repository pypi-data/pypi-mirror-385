"""Tests for health check and user status endpoints."""

import pytest
from unittest.mock import MagicMock, patch
import httpx

from cli.client import APIClient
from .conftest import create_mock_response, create_mock_async_client


@pytest.mark.asyncio
class TestHealthAndStatus:
    """Test health check and user status endpoints."""

    async def test_health_check_success(self):
        """Test successful health check."""
        client = APIClient(base_url="http://localhost:8000")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"status": "ok"})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.health_check()

            assert result == {"status": "ok"}
            mock_client.get.assert_called_once_with(
                "http://localhost:8000/v1/health",
                headers={},
                timeout=5.0,
            )

    async def test_health_check_with_auth(self):
        """Test health check with authentication headers."""
        client = APIClient(
            base_url="http://localhost:8000",
            auth_token="test-token",
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"status": "ok"})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.health_check()

            assert result == {"status": "ok"}
            mock_client.get.assert_called_once_with(
                "http://localhost:8000/v1/health",
                headers={"Authorization": "Bearer test-token"},
                timeout=5.0,
            )

    async def test_get_current_user_for_user_token(self):
        """Test get_current_user() for user token."""
        client = APIClient(
            base_url="http://localhost:8000",
            auth_token="test-user-token",
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"id": 1, "name": "Development"})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.get_current_user()

            assert result["authenticated"] is True
            assert result["type"] == "user"

    async def test_get_current_user_for_agent_key(self):
        """Test get_current_user() for agent key."""
        client = APIClient(
            base_url="http://localhost:8000",
            agent_key="anyt_agent_abcdef123456789012345678901234",
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"id": 1, "name": "Development"})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.get_current_user()

            assert result["authenticated"] is True
            assert result["type"] == "agent"

    async def test_health_check_http_error(self):
        """Test health check with HTTP error."""
        client = APIClient(base_url="http://localhost:8000")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "404 Not Found", request=MagicMock(), response=mock_response
                )
            )
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await client.health_check()
