# Vigil Client

**Vigil Client** extends Vigil Core with platform integration, enabling collaborative artifact management and provenance tracking across teams.

## Overview

Vigil Client bridges the cryptographic foundation of Vigil Core with platform features:

- **Authentication** - Secure login to Vigil platform
- **Artifact Registry** - Create, search, and manage typed artifacts
- **Provenance Links** - Track relationships between artifacts
- **Sync Operations** - Push/pull artifacts and receipts
- **Plugin System** - Extensible integrations (Benchling, HuggingFace, etc.)

## Installation

```bash
# Install vigil-client (includes vigil-core)
pip install vigil-client

# Or install vigil-core separately
pip install vigil-core
```

## Quick Start

### 1. Authenticate

```bash
# Interactive login
vigil client login

# Check authentication status
vigil client whoami
```

### 2. Push Artifacts

```bash
# Push local receipts and artifacts to the platform
vigil client push

# Push specific receipt
vigil client push app/code/receipts/receipt_20250101T120000Z.json
```

### 3. Search and Download

```bash
# Search for artifacts
vigil client artifacts-search "genomics"

# Download an artifact
vigil client pull artifact-id
```

### 4. Link Artifacts

```bash
# Create provenance relationships
vigil client link dataset-123 run-456 --relation INPUT_OF
vigil client link run-456 model-789 --relation OUTPUT_OF
```

## Commands

### Authentication
```bash
vigil client login                    # Interactive authentication
vigil client logout                   # Clear credentials
vigil client whoami                   # Show current user info
```

### Artifact Management
```bash
vigil client artifacts                    # List artifacts
vigil client artifacts-get <id>          # Get artifact details
vigil client artifacts-search <query>   # Search artifacts
vigil client pull <artifact-id>         # Download artifact
vigil client push                       # Upload receipts/artifacts
```

### Provenance
```bash
vigil client link <from> <to> --relation <type>  # Create relationship
```

### Configuration
```bash
vigil client config                        # Show current config
vigil client config-set-project <id>      # Set default project
vigil client config-set-remote <url>      # Set remote URL
```

## Python API

```python
from vigil_client import VigilClient
from vigil_client.auth import auth_manager
from vigil_client.models import Artifact, ArtifactType

# Get authenticated client
config = auth_manager.get_client_config()
client = VigilClient(config.remote)

# Register artifact
artifact = Artifact(
    name="my-dataset",
    type=ArtifactType.DATASET,
    uri="s3://my-bucket/data/",
    description="Training dataset"
)

result = client.create_artifact(artifact)
print(f"Created artifact: {result.id}")

# Create provenance link
from vigil_client.models import Link, LinkType

link = Link(
    from_artifact_id="dataset-123",
    to_artifact_id="run-456",
    type=LinkType.INPUT_OF
)

client.create_link(link)
```

## Plugin System

Extend Vigil with custom integrations:

```python
from vigil_client.plugins import BasePlugin, plugin_manager

class BenchlingPlugin(BasePlugin):
    def on_artifact_push(self, artifact):
        # Custom Benchling integration
        if artifact.type == "dataset":
            self.sync_to_benchling(artifact)

# Install plugin
plugin_manager.install_plugin(
    "benchling",
    "my_plugins.benchling",
    {"api_key": "benchling-token"}
)
```

## Integration with Vigil Core

Vigil Client extends Vigil Core with platform integration through a unified CLI:

```bash
# Core commands (from vigil-core)
vigil run
vigil promote
vigil verify

# Platform commands (from vigil-client)
vigil client login
vigil client push
vigil client pull
```

The unified CLI automatically detects available packages and shows appropriate commands.

## Configuration

Configuration is stored in `~/.vigil/config.json`:

```json
{
  "auth": {
    "token": "jwt-token",
    "username": "user",
    "organization": "org"
  },
  "remote": {
    "base_url": "https://api.vigil.app",
    "timeout": 30
  },
  "default_project": "proj-123"
}
```

## Security

- **Token Storage**: API tokens are stored securely using system keyring
- **HTTPS Only**: All platform communication uses HTTPS
- **Scoped Access**: Platform enforces project and organization boundaries

## Development

```bash
# Install in development mode
pip install -e packages/vigil-core-client

# Run tests
pytest packages/vigil-core-client/tests/

# Type checking
mypy packages/vigil-core-client/src/
```

## Architecture

```
vigil-client/
├── api/           # REST API client
├── auth/          # Authentication & config
├── cli/           # CLI commands
├── models/        # Data models
├── plugins/       # Extension system
└── extension.py   # Integration with vigil-core
```

## See Also

- [Vigil Core Documentation](../vigil/README.md)
- [Platform API Reference](api.md)
- [Plugin Development Guide](plugins.md)
