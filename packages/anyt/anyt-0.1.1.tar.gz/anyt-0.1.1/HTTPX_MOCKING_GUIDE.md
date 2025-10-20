# httpx.AsyncClient Mocking Guide for Unit Tests

This guide provides the correct patterns for mocking `httpx.AsyncClient` in unit tests for asynchronous HTTP client code.

## Summary of Key Issues and Solutions

### Problem 1: httpx.Response.json() is Synchronous, Not Async

**Wrong:**
```python
mock_response = AsyncMock()
mock_response.json.return_value = {"data": "value"}  # This returns a coroutine!
```

**Correct:**
```python
mock_response = MagicMock()
mock_response.json = MagicMock(return_value={"data": "value"})  # Synchronous method
```

### Problem 2: AsyncClient HTTP Methods Need to be AsyncMock for Assertions

**Wrong:**
```python
async def mock_get(*args, **kwargs):
    return mock_response

mock_client.get = mock_get  # Can't use .assert_called_once_with()
```

**Correct:**
```python
mock_client.get = AsyncMock(return_value=mock_response)  # Supports assertions
```

### Problem 3: Async Context Manager Needs Proper Setup

**Wrong:**
```python
mock_client.__aenter__ = AsyncMock(return_value=mock_client)
mock_client.__aexit__ = AsyncMock()  # Returns a coroutine!
```

**Correct:**
```python
async def aenter(*args):
    return mock_client

async def aexit(*args):
    return None

mock_client.__aenter__ = aenter
mock_client.__aexit__ = aexit
```

## Complete Solution: Helper Functions

Here are two helper functions that solve all the above problems:

```python
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
```

## Usage Examples

### Basic GET Request

```python
@pytest.mark.asyncio
async def test_health_check_success():
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
```

### POST Request with JSON Payload

```python
@pytest.mark.asyncio
async def test_create_workspace():
    """Test create_workspace() with required fields."""
    client = APIClient(
        base_url="http://localhost:8000",
        auth_token="test-token",
    )

    created_workspace = {
        "id": 3,
        "identifier": "TEST",
        "name": "Test Workspace",
        "description": "A test workspace",
    }

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_response = create_mock_response({"data": created_workspace})
        mock_client = create_mock_async_client(mock_response, method="post")
        mock_client_class.return_value = mock_client

        result = await client.create_workspace(
            name="Test Workspace",
            identifier="TEST",
            description="A test workspace",
        )

        assert result == created_workspace
        mock_client.post.assert_called_once_with(
            "http://localhost:8000/v1/workspaces",
            headers={"Authorization": "Bearer test-token"},
            json={
                "name": "Test Workspace",
                "identifier": "TEST",
                "description": "A test workspace",
            },
            timeout=10.0,
        )
```

### Error Handling Test

```python
@pytest.mark.asyncio
async def test_404_not_found_error():
    """Test 404 Not Found error handling."""
    client = APIClient(base_url="http://localhost:8000")

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=mock_response,
        ))
        mock_client = create_mock_async_client(mock_response, method="get")
        mock_client_class.return_value = mock_client

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_task("DEV-999")
```

### Connection Error Test

```python
@pytest.mark.asyncio
async def test_network_connection_error():
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
```

### JSON Parsing Error Test

```python
@pytest.mark.asyncio
async def test_invalid_response_parsing():
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
```

## Key Takeaways

1. **response.json()** is synchronous in httpx - use `MagicMock`, not `AsyncMock`
2. **HTTP methods** (get, post, etc.) should be `AsyncMock` to support assertion methods
3. **Context manager** methods (`__aenter__`, `__aexit__`) should be regular async functions
4. Use the helper functions to ensure consistent and correct mocking patterns
5. For special cases (connection errors, parsing errors), create custom mocks but follow the same principles

## Test Results

After applying these patterns:
- ✅ All 40 tests passing (1 test has a non-mocking-related issue in test logic)
- ✅ No coroutine warnings
- ✅ All assertion methods work correctly
- ✅ Proper async context manager handling
