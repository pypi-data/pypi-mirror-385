"""Shared fixtures and mock helpers for API client tests."""

from unittest.mock import AsyncMock, MagicMock


def create_mock_response(json_data: dict | list, raise_error: Exception | None = None):
    """Create a properly configured mock httpx.Response object.

    Args:
        json_data: The data to return from response.json()
        raise_error: Optional exception to raise from raise_for_status()

    Returns:
        A MagicMock configured to work as an httpx.Response
    """
    mock_response = MagicMock()

    # httpx.Response.json() is synchronous, not async!
    mock_response.json = MagicMock(return_value=json_data)

    if raise_error:
        mock_response.raise_for_status = MagicMock(side_effect=raise_error)
    else:
        mock_response.raise_for_status = MagicMock()

    return mock_response


def create_mock_async_client(mock_response, method: str = "get"):
    """Create a properly configured mock httpx.AsyncClient.

    Args:
        mock_response: The mock response object to return
        method: The HTTP method to mock ("get", "post", "patch", "delete")

    Returns:
        A mock AsyncClient ready to use in tests
    """
    mock_client = MagicMock()

    # Create AsyncMock for HTTP methods so they support assertion methods
    mock_method = AsyncMock(return_value=mock_response)

    # Set the appropriate method
    if method == "get":
        mock_client.get = mock_method
    elif method == "post":
        mock_client.post = mock_method
    elif method == "patch":
        mock_client.patch = mock_method
    elif method == "delete":
        mock_client.delete = mock_method

    # Configure async context manager
    async def aenter(*args):
        return mock_client

    async def aexit(*args):
        return None

    mock_client.__aenter__ = aenter
    mock_client.__aexit__ = aexit

    return mock_client
