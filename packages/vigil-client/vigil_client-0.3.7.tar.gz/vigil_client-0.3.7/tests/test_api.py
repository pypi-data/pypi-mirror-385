"""Tests for vigil-client API."""

import pytest
from unittest.mock import Mock, patch
from vigil_client.api import VigilAPIError, VigilClient
from vigil_client.models import Artifact, ArtifactType, PlatformConfig


class TestVigilClient:
    """Test Vigil API client."""

    @pytest.fixture
    def platform_config(self):
        """Create test platform config."""
        return PlatformConfig(
            base_url="https://api.test.com",
            api_key="test-key"
        )

    @pytest.fixture
    def client(self, platform_config):
        """Create test client."""
        return VigilClient(platform_config)

    def test_client_initialization(self, platform_config):
        """Test client initialization."""
        client = VigilClient(platform_config)
        assert client.config == platform_config
        assert "Authorization" in client.client.headers

    @patch('httpx.Client.post')
    def test_create_artifact(self, mock_post, client):
        """Test creating an artifact."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "art-123",
            "name": "test-artifact",
            "type": "dataset"
        }
        mock_post.return_value = mock_response

        artifact = Artifact(
            name="test-artifact",
            type=ArtifactType.DATASET,
            uri="s3://test/"
        )

        result = client.create_artifact(artifact)

        assert result.id == "art-123"
        assert result.name == "test-artifact"
        mock_post.assert_called_once()

    @patch('httpx.Client.post')
    def test_api_error_handling(self, mock_post, client):
        """Test API error handling."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Bad request"}
        mock_post.return_value = mock_response

        artifact = Artifact(
            name="test",
            type=ArtifactType.DATASET,
            uri="s3://test/"
        )

        with pytest.raises(VigilAPIError) as exc_info:
            client.create_artifact(artifact)

        assert exc_info.value.status_code == 400
        assert "Bad request" in str(exc_info.value)

    def test_context_manager(self, platform_config):
        """Test client as context manager."""
        with VigilClient(platform_config) as client:
            assert client.client is not None

        # Client should be closed after context
        assert client.client.is_closed
