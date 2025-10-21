"""Tests for LabelsAPIClient."""

from unittest.mock import AsyncMock, patch

import pytest

from cli.client.labels import LabelsAPIClient
from cli.models.label import Label, LabelCreate, LabelUpdate


@pytest.fixture
def client():
    """Create a LabelsAPIClient instance for testing."""
    return LabelsAPIClient(
        base_url="http://test.example.com",
        auth_token="test_token",
    )


@pytest.fixture
def sample_label_data():
    """Sample label data for testing."""
    return {
        "id": 1,
        "name": "bug",
        "color": "#FF0000",
        "description": "Bug fixes",
        "workspace_id": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


class TestListLabels:
    """Test list_labels method."""

    @pytest.mark.asyncio
    async def test_list_labels_success(self, client, sample_label_data):
        """Test successful label listing."""
        mock_response = {"data": [sample_label_data]}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.list_labels(workspace_id=1)

            mock_get.assert_called_once_with("/v1/workspaces/1/labels")
            assert len(result) == 1
            assert isinstance(result[0], Label)
            assert result[0].name == "bug"
            assert result[0].color == "#FF0000"

    @pytest.mark.asyncio
    async def test_list_labels_empty(self, client):
        """Test listing labels with empty result."""
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": []}

            result = await client.list_labels(workspace_id=1)

            assert result == []


class TestCreateLabel:
    """Test create_label method."""

    @pytest.mark.asyncio
    async def test_create_label_success(self, client, sample_label_data):
        """Test successful label creation."""
        label_create = LabelCreate(
            name="bug",
            color="#FF0000",
            description="Bug fixes",
        )

        mock_response = {"data": sample_label_data}

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client.create_label(workspace_id=1, label=label_create)

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "/v1/workspaces/1/labels"
            assert call_args[1]["json"]["name"] == "bug"
            assert isinstance(result, Label)
            assert result.id == 1


class TestGetLabel:
    """Test get_label method."""

    @pytest.mark.asyncio
    async def test_get_label_success(self, client, sample_label_data):
        """Test successful label retrieval."""
        mock_response = {"data": sample_label_data}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_label(workspace_id=1, label_id=1)

            mock_get.assert_called_once_with("/v1/workspaces/1/labels/1")
            assert isinstance(result, Label)
            assert result.id == 1


class TestUpdateLabel:
    """Test update_label method."""

    @pytest.mark.asyncio
    async def test_update_label_success(self, client, sample_label_data):
        """Test successful label update."""
        label_update = LabelUpdate(
            name="critical-bug",
            description="Critical bugs only",
        )

        updated_data = {**sample_label_data, "name": "critical-bug"}
        mock_response = {"data": updated_data}

        with patch.object(client, "patch", new_callable=AsyncMock) as mock_patch:
            mock_patch.return_value = mock_response

            result = await client.update_label(
                workspace_id=1, label_id=1, updates=label_update
            )

            mock_patch.assert_called_once()
            call_args = mock_patch.call_args
            assert call_args[0][0] == "/v1/workspaces/1/labels/1"
            assert isinstance(result, Label)
            assert result.name == "critical-bug"


class TestDeleteLabel:
    """Test delete_label method."""

    @pytest.mark.asyncio
    async def test_delete_label_success(self, client):
        """Test successful label deletion."""
        with patch.object(client, "delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = {}

            await client.delete_label(workspace_id=1, label_id=1)

            mock_delete.assert_called_once_with("/v1/workspaces/1/labels/1")
