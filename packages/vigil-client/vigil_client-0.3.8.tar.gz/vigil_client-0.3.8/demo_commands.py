#!/usr/bin/env python3
"""Demonstrate all vigil-client CLI commands and their expected behavior."""

import sys
from pathlib import Path

def show_command_demo():
    """Show examples of all vigil-client commands."""
    print("🔬 Vigil Client CLI Commands Demo")
    print("=" * 50)

    commands = [
        {
            "cmd": "vigil platform login",
            "desc": "Authenticate with Vigil platform",
            "output": """🔐 Logging into Vigil platform...

Opening browser for authentication: https://api.vigil.app/auth/login?client=vigil-cli

After authenticating, paste your API token:
API token: *****

✅ Successfully logged in!"""
        },
        {
            "cmd": "vigil platform status",
            "desc": "Show authentication and configuration status",
            "output": """Vigil Platform Status
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Setting     ┃ Value                         ┃
├─────────────┼───────────────────────────────┤
│ Authenticated │ ✅ Yes                        │
│ Platform URL  │ https://api.vigil.app         │
│ User         │ researcher@example.com        │
│ Organization │ acme-labs                     │
│ Default Project │ cancer-research             │
└─────────────┴───────────────────────────────┘"""
        },
        {
            "cmd": "vigil platform register 'breast-cancer-model' model 's3://models/cancer/rf.pkl' --description 'Random Forest classifier'",
            "desc": "Register a new artifact",
            "output": """✅ Artifact registered: art-123456
   Name: breast-cancer-model
   Type: model
   URI: s3://models/cancer/rf.pkl"""
        },
        {
            "cmd": "vigil platform artifacts",
            "desc": "List artifacts in the platform",
            "output": """Platform Artifacts
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID            ┃ Name                      ┃ Type   ┃ Status   ┃ Updated    ┃
├───────────────┼───────────────────────────┼────────┼──────────┼────────────┤
│ art-123456    │ breast-cancer-model       │ model  │ published│ 2025-01-01 │
│ art-789012    │ training-dataset          │ dataset│ published│ 2025-01-01 │
│ art-345678    │ evaluation-metrics        │ receipt │ draft    │ 2025-01-01 │
└───────────────┴───────────────────────────┴────────┴──────────┴────────────┘"""
        },
        {
            "cmd": "vigil platform link art-789012 art-123456 input_of",
            "desc": "Create provenance link between artifacts",
            "output": """✅ Link created: link-456789
   art-789012 --[input_of]--> art-123456"""
        },
        {
            "cmd": "vigil platform graph art-123456",
            "desc": "Show provenance graph for an artifact",
            "output": """Provenance Graph for art-123456
{
  "nodes": [
    {
      "id": "art-789012",
      "type": "Artifact",
      "data": {
        "name": "training-dataset",
        "type": "dataset",
        "uri": "s3://data/cancer/features.csv"
      }
    },
    {
      "id": "art-123456",
      "type": "Artifact",
      "data": {
        "name": "breast-cancer-model",
        "type": "model",
        "uri": "s3://models/cancer/rf.pkl"
      }
    }
  ],
  "edges": [
    {
      "id": "link-456789",
      "source": "art-789012",
      "target": "art-123456",
      "type": "input_of"
    }
  ]
}"""
        },
        {
            "cmd": "vigil platform push app/code/receipts/receipt_latest.json",
            "desc": "Push a receipt to the platform",
            "output": """✅ Receipt pushed: receipt-789012"""
        },
        {
            "cmd": "vigil platform pull art-123456 --output ./downloaded-model.pkl",
            "desc": "Download an artifact from the platform",
            "output": """✅ Downloaded: ./downloaded-model.pkl"""
        },
        {
            "cmd": "vigil platform project --set-default cancer-research",
            "desc": "Set default project for operations",
            "output": """✅ Default project set to: cancer-research"""
        }
    ]

    for i, cmd_info in enumerate(commands, 1):
        print(f"\n{i}. {cmd_info['desc']}")
        print(f"   Command: {cmd_info['cmd']}")
        print("   Expected Output:")
        for line in cmd_info['output'].split('\n'):
            if line.strip():
                print(f"   {line}")
        print()

def show_integration_workflow():
    """Show the complete integration workflow."""
    print("\n🔄 Complete Integration Workflow")
    print("=" * 40)

    workflow = [
        "# 1. Set up environment",
        "export VIGIL_API_URL=https://your-cofactor-api.com",

        "# 2. Authenticate",
        "vigil platform login",

        "# 3. Run your scientific workflow",
        "vigil run && vigil promote",

        "# 4. Push results to platform",
        "vigil platform push receipt.json",

        "# 5. Register artifacts",
        "vigil platform register 'my-model' model 's3://models/model.pkl'",
        "vigil platform register 'my-data' dataset 's3://data/dataset.csv'",

        "# 6. Create provenance links",
        "vigil platform link data-123 model-456 input_of",

        "# 7. Explore in platform UI",
        "# Open cofactor-app to see the provenance graph",

        "# 8. Collaborate with team",
        "vigil platform artifacts  # See all team artifacts",
        "vigil platform graph model-456  # Explore lineage"
    ]

    for step in workflow:
        if step.startswith("#"):
            print(f"\n{step}")
        else:
            print(f"   {step}")

    print("\n🎯 Result: End-to-end cryptographic provenance with collaborative platform!")

if __name__ == "__main__":
    show_command_demo()
    show_integration_workflow()
