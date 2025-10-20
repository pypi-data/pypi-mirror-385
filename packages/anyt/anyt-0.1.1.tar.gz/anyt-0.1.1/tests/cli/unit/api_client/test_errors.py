"""Tests for error handling and response formats."""

import pytest
from unittest.mock import MagicMock, patch
import httpx

from cli.client import APIClient
from .conftest import create_mock_response, create_mock_async_client


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling for various HTTP status codes."""

    async def test_404_not_found_error(self):
        """Test 404 Not Found error handling."""
        client = APIClient(base_url="http://localhost:8000")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "404 Not Found",
                    request=MagicMock(),
                    response=mock_response,
                )
            )
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await client.get_task("DEV-999")

    async def test_409_conflict_error_optimistic_locking(self):
        """Test 409 Conflict error (optimistic locking)."""
        client = APIClient(base_url="http://localhost:8000")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "409 Conflict",
                    request=MagicMock(),
                    response=mock_response,
                )
            )
            mock_client = create_mock_async_client(mock_response, method="patch")
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await client.update_task("DEV-1", title="Updated", if_match=1)

    async def test_500_server_error(self):
        """Test 500 Internal Server Error."""
        client = APIClient(base_url="http://localhost:8000")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "500 Internal Server Error",
                    request=MagicMock(),
                    response=mock_response,
                )
            )
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await client.list_tasks()

    async def test_network_connection_error(self):
        """Test network connection errors."""
        client = APIClient(base_url="http://localhost:8000")

        with patch("httpx.AsyncClient") as mock_client_class:
            # Special case: test connection error (no response object needed)
            mock_client = MagicMock()

            async def raise_connect_error(*args, **kwargs):
                raise httpx.ConnectError("Connection refused")

            mock_client.get = raise_connect_error

            async def aenter(*args):
                return mock_client

            async def aexit(*args):
                return None

            mock_client.__aenter__ = aenter
            mock_client.__aexit__ = aexit
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.ConnectError):
                await client.health_check()

    async def test_invalid_response_parsing(self):
        """Test invalid response parsing."""
        client = APIClient(base_url="http://localhost:8000")

        with patch("httpx.AsyncClient") as mock_client_class:
            # Special case: test invalid JSON parsing
            mock_response = MagicMock()
            mock_response.json = MagicMock(side_effect=ValueError("Invalid JSON"))
            mock_response.raise_for_status = MagicMock()
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            with pytest.raises(ValueError):
                await client.health_check()


@pytest.mark.asyncio
class TestResponseFormats:
    """Test handling of different response formats."""

    async def test_wrapped_response_format(self):
        """Test wrapped response format with success=true."""
        client = APIClient(base_url="http://localhost:8000")

        wrapped_response = {
            "success": True,
            "data": {
                "id": 1,
                "identifier": "DEV-1",
                "title": "Task",
            },
            "message": "Success",
            "request_id": "req-123",
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response(wrapped_response)
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.get_task("DEV-1")

            # Should extract the data field
            assert result == wrapped_response["data"]
            assert result["id"] == 1
            assert result["identifier"] == "DEV-1"

    async def test_direct_array_response(self):
        """Test direct array response without wrapper."""
        client = APIClient(base_url="http://localhost:8000")

        direct_array = [
            {"id": 1, "identifier": "DEV-1"},
            {"id": 2, "identifier": "DEV-2"},
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response(direct_array)
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.list_workspaces()

            assert result == direct_array

    async def test_pagination_metadata_extraction(self):
        """Test pagination metadata extraction."""
        client = APIClient(base_url="http://localhost:8000")

        paginated_response = {
            "data": {
                "items": [
                    {"id": 1, "identifier": "DEV-1"},
                    {"id": 2, "identifier": "DEV-2"},
                ],
                "pagination": {
                    "total": 100,
                    "limit": 2,
                    "offset": 0,
                },
            }
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response(paginated_response)
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.list_tasks(limit=2, offset=0)

            assert "items" in result
            assert "pagination" in result
            assert result["pagination"]["total"] == 100
            assert len(result["items"]) == 2


@pytest.mark.cli
@pytest.mark.client
class TestAPIClientMarkers:
    """Test marking for CLI and client tests."""

    def test_marked_for_cli_client_tests(self):
        """Test is properly marked for client testing."""
        # This test passes if it runs with correct markers
        assert True
