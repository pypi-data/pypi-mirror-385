"""Base API client with common functionality."""

from abc import ABC
from typing import Any, cast

import httpx

from cli.client.exceptions import (
    APIError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from cli.config import GlobalConfig


class BaseAPIClient(ABC):
    """Base API client with common HTTP operations."""

    def __init__(
        self,
        base_url: str,
        auth_token: str | None = None,
        agent_key: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        """Initialize BaseAPIClient.

        Args:
            base_url: Base URL for the API
            auth_token: Optional JWT auth token
            agent_key: Optional agent API key
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.agent_key = agent_key
        self.timeout = timeout
        self.headers = self._build_headers()

    def _build_headers(self) -> dict[str, str]:
        """Build authentication headers.

        Returns:
            Dictionary of headers
        """
        headers: dict[str, str] = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        elif self.agent_key:
            headers["X-API-Key"] = self.agent_key
        return headers

    @classmethod
    def from_config(cls, config: GlobalConfig | None = None) -> "BaseAPIClient":
        """Create client from global config.

        Args:
            config: Optional GlobalConfig instance. If None, loads from file.

        Returns:
            Configured BaseAPIClient instance

        Raises:
            RuntimeError: If config cannot be loaded or is invalid
        """
        if config is None:
            config = GlobalConfig.load()

        effective = config.get_effective_config()
        api_url = effective.get("api_url")
        if not api_url or api_url == "":
            raise RuntimeError("No API URL configured")

        # Extract auth credentials, handling None values
        auth_token = effective.get("auth_token")
        agent_key = effective.get("agent_key")

        return cls(
            base_url=str(api_url),
            auth_token=auth_token if auth_token else None,
            agent_key=agent_key if agent_key else None,
        )

    async def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """HTTP GET request.

        Args:
            path: API endpoint path
            params: Optional query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            APIError: On HTTP errors
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
            return self._handle_response(response)

    async def post(
        self, path: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """HTTP POST request.

        Args:
            path: API endpoint path
            json: Optional JSON body

        Returns:
            Response JSON as dictionary

        Raises:
            APIError: On HTTP errors
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=json,
                timeout=self.timeout,
            )
            return self._handle_response(response)

    async def patch(
        self, path: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """HTTP PATCH request.

        Args:
            path: API endpoint path
            json: Optional JSON body

        Returns:
            Response JSON as dictionary

        Raises:
            APIError: On HTTP errors
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.patch(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=json,
                timeout=self.timeout,
            )
            return self._handle_response(response)

    async def delete(self, path: str) -> dict[str, Any]:
        """HTTP DELETE request.

        Args:
            path: API endpoint path

        Returns:
            Response JSON as dictionary

        Raises:
            APIError: On HTTP errors
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.delete(
                f"{self.base_url}{path}",
                headers=self.headers,
                timeout=self.timeout,
            )
            return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle response and raise appropriate exceptions.

        Args:
            response: HTTP response

        Returns:
            Response JSON as dictionary

        Raises:
            APIError: On HTTP errors
            NotFoundError: On 404 errors
            AuthenticationError: On 401 errors
            ValidationError: On 422 errors
            ConflictError: On 409 errors
        """
        if not response.is_success:
            self._raise_error(response)

        try:
            return cast(dict[str, Any], response.json())
        except Exception:
            # If response is not JSON, return empty dict
            return {}

    def _raise_error(self, response: httpx.Response) -> None:
        """Raise appropriate exception based on status code.

        Args:
            response: HTTP response

        Raises:
            NotFoundError: On 404 errors
            AuthenticationError: On 401 errors
            ValidationError: On 422 errors
            ConflictError: On 409 errors
            APIError: On other HTTP errors
        """
        error_message = self._extract_error_message(response)

        if response.status_code == 404:
            raise NotFoundError(error_message)
        elif response.status_code == 401:
            raise AuthenticationError(error_message)
        elif response.status_code == 422:
            raise ValidationError(error_message)
        elif response.status_code == 409:
            raise ConflictError(error_message)
        else:
            raise APIError(error_message, status_code=response.status_code)

    def _extract_error_message(self, response: httpx.Response) -> str:
        """Extract error message from response.

        Args:
            response: HTTP response

        Returns:
            Error message string
        """
        try:
            data = response.json()
            # Try to extract message from error response
            if isinstance(data, dict):
                if "message" in data:
                    return str(data["message"])
                if "detail" in data:
                    return str(data["detail"])
                if "error" in data:
                    return str(data["error"])
            return str(data)
        except Exception:
            # Fallback to status text if JSON parsing fails
            return f"HTTP {response.status_code}: {response.reason_phrase}"

    def _unwrap_response(self, response_data: dict[str, Any]) -> Any:
        """Unwrap SuccessResponse[T] to get data.

        Args:
            response_data: Response dictionary

        Returns:
            Unwrapped data
        """
        if isinstance(response_data, dict) and "data" in response_data:
            return response_data["data"]
        return response_data

    async def health_check(self) -> dict[str, Any]:
        """Check API health status.

        Returns:
            Health status response from the API

        Raises:
            APIError: If the health check fails
        """
        return await self.get("/health")
