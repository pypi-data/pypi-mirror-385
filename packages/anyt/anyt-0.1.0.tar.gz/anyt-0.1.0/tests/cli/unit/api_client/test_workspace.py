"""Tests for workspace CRUD operations."""

import pytest
from unittest.mock import patch

from cli.client import APIClient
from .conftest import create_mock_response, create_mock_async_client


@pytest.mark.asyncio
class TestWorkspaceOperations:
    """Test workspace CRUD operations."""

    async def test_list_workspaces(self):
        """Test list_workspaces() with multiple workspaces."""
        client = APIClient(
            base_url="http://localhost:8000",
            auth_token="test-token",
        )

        workspaces = [
            {"id": 1, "identifier": "DEV", "name": "Development"},
            {"id": 2, "identifier": "PROD", "name": "Production"},
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": workspaces})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.list_workspaces()

            assert result == workspaces
            mock_client.get.assert_called_once_with(
                "http://localhost:8000/v1/workspaces",
                headers={"Authorization": "Bearer test-token"},
                timeout=10.0,
            )

    async def test_list_workspaces_direct_array_response(self):
        """Test list_workspaces() with direct array response (no wrapper)."""
        client = APIClient(base_url="http://localhost:8000")

        workspaces = [
            {"id": 1, "identifier": "DEV", "name": "Development"},
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response(workspaces)
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.list_workspaces()

            assert result == workspaces

    async def test_get_workspace(self):
        """Test get_workspace() by ID."""
        client = APIClient(
            base_url="http://localhost:8000",
            auth_token="test-token",
        )

        workspace = {
            "id": 1,
            "identifier": "DEV",
            "name": "Development",
            "description": "Dev workspace",
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": workspace})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.get_workspace("1")

            assert result == workspace
            mock_client.get.assert_called_once_with(
                "http://localhost:8000/v1/workspaces/1",
                headers={"Authorization": "Bearer test-token"},
                timeout=10.0,
            )

    async def test_create_workspace(self):
        """Test create_workspace() with required fields."""
        client = APIClient(
            base_url="http://localhost:8000",
            auth_token="test-token",
        )

        created_workspace = {
            "id": 3,
            "identifier": "TST",
            "name": "Test Workspace",
            "description": "A test workspace",
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": created_workspace})
            mock_client = create_mock_async_client(mock_response, method="post")
            mock_client_class.return_value = mock_client

            result = await client.create_workspace(
                name="Test Workspace",
                identifier="TST",
                description="A test workspace",
            )

            assert result == created_workspace
            mock_client.post.assert_called_once_with(
                "http://localhost:8000/v1/workspaces/",
                headers={"Authorization": "Bearer test-token"},
                json={
                    "name": "Test Workspace",
                    "identifier": "TST",
                    "description": "A test workspace",
                },
                timeout=10.0,
            )

    async def test_create_workspace_minimal(self):
        """Test create_workspace() with only required fields."""
        client = APIClient(base_url="http://localhost:8000")

        created_workspace = {
            "id": 3,
            "identifier": "TST",
            "name": "Test Workspace",
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": created_workspace})
            mock_client = create_mock_async_client(mock_response, method="post")
            mock_client_class.return_value = mock_client

            result = await client.create_workspace(
                name="Test Workspace",
                identifier="TST",
                description=None,
            )

            assert result["id"] == 3
            call_kwargs = mock_client.post.call_args[1]
            assert call_kwargs["json"]["name"] == "Test Workspace"
            assert call_kwargs["json"]["identifier"] == "TST"
            assert call_kwargs["json"]["description"] is None
