"""Tests for vigil-client models."""

import pytest
from vigil_client.models import Artifact, ArtifactType, Link, LinkType, PlatformConfig, Receipt


class TestArtifact:
    """Test artifact model."""

    def test_artifact_creation(self):
        """Test creating an artifact."""
        artifact = Artifact(
            name="test-model",
            type=ArtifactType.MODEL,
            uri="s3://bucket/model.pkl",
            description="Test model"
        )

        assert artifact.name == "test-model"
        assert artifact.type == ArtifactType.MODEL
        assert artifact.uri == "s3://bucket/model.pkl"
        assert artifact.description == "Test model"
        assert artifact.status == "draft"  # default

    def test_artifact_serialization(self):
        """Test artifact JSON serialization."""
        artifact = Artifact(
            id="art-123",
            name="test-dataset",
            type=ArtifactType.DATASET,
            uri="s3://bucket/data/",
        )

        data = artifact.dict(exclude_unset=True)
        assert data["id"] == "art-123"
        assert data["type"] == "dataset"  # enum value


class TestLink:
    """Test link model."""

    def test_link_creation(self):
        """Test creating a link."""
        link = Link(
            from_artifact_id="art-1",
            to_artifact_id="art-2",
            type=LinkType.INPUT_OF
        )

        assert link.from_artifact_id == "art-1"
        assert link.to_artifact_id == "art-2"
        assert link.type == LinkType.INPUT_OF


class TestPlatformConfig:
    """Test platform configuration."""

    def test_platform_config_creation(self):
        """Test creating platform config."""
        config = PlatformConfig(
            base_url="https://api.vigil.app",
            api_key="test-key",
            project_id="proj-123"
        )

        assert config.base_url == "https://api.vigil.app"
        assert config.api_key == "test-key"
        assert config.project_id == "proj-123"
        assert config.timeout == 30  # default


class TestReceipt:
    """Test extended receipt model."""

    def test_receipt_creation(self):
        """Test creating an extended receipt."""
        receipt = Receipt(
            issuer="Vigil",
            runlet_id="rl-123",
            vigil_url="vigil://example.com/org/proj@refs/heads/main",
            git_ref="abc123",
            capsule_digest="sha256:def456",
            started_at="2025-01-01T10:00:00Z",
            finished_at="2025-01-01T10:30:00Z",
            version="2.0",
            synced=True
        )

        assert receipt.issuer == "Vigil"
        assert receipt.version == "2.0"
        assert receipt.synced is True
        assert receipt.platform_metadata == {}  # default
