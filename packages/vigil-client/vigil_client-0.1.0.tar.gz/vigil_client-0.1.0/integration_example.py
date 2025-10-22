#!/usr/bin/env python3
"""Example integration script showing how vigil-client works with platform backend."""

from pathlib import Path
from vigil_client import VigilClient
from vigil_client.auth import auth_manager
from vigil_client.models import Artifact, ArtifactType, Link, LinkType

def demonstrate_integration():
    """Demonstrate complete integration workflow."""

    print("🔬 Vigil Client Integration Example")
    print("=" * 50)

    # 1. Authentication
    print("\n1. Authentication")
    config = auth_manager.get_client_config()
    print(f"✅ Connected to: {config.remote.base_url}")
    print(f"✅ User: {config.auth.username}")
    print(f"✅ Organization: {config.auth.organization}")

    # 2. Create API client
    print("\n2. API Client Setup")
    client = VigilClient(config.remote)
    print("✅ API client initialized")

    # 3. Register artifacts
    print("\n3. Artifact Registration")

    # Dataset artifact
    dataset = Artifact(
        name="breast_cancer_dataset",
        type=ArtifactType.DATASET,
        uri="s3://medical-data/breast-cancer/features.csv",
        description="Breast cancer diagnostic features dataset",
        metadata={
            "rows": 569,
            "features": 30,
            "source": "UCI Machine Learning Repository"
        },
        project_id=config.default_project
    )

    # Model artifact
    model = Artifact(
        name="cancer_classifier_v2",
        type=ArtifactType.MODEL,
        uri="s3://models/cancer/classifier.pkl",
        description="Random Forest classifier for breast cancer diagnosis",
        metadata={
            "algorithm": "RandomForest",
            "accuracy": 0.967,
            "features": 30
        },
        project_id=config.default_project
    )

    print("✅ Dataset artifact created")
    print("✅ Model artifact created")

    # 4. Upload artifacts (simulated)
    print("\n4. Artifact Upload")
    # In real usage:
    # dataset_result = client.push_artifact_with_file(dataset, Path("data.csv"))
    # model_result = client.push_artifact_with_file(model, Path("model.pkl"))
    print("✅ Artifacts would be uploaded via presigned URLs")

    # 5. Create provenance links
    print("\n5. Provenance Links")

    # Link dataset -> run (input)
    data_to_run = Link(
        from_artifact_id="dataset-123",  # Would be real IDs from upload
        to_artifact_id="run-456",
        type=LinkType.INPUT_OF
    )

    # Link run -> model (output)
    run_to_model = Link(
        from_artifact_id="run-456",
        to_artifact_id="model-789",
        type=LinkType.OUTPUT_OF
    )

    print("✅ Provenance links defined")

    # 6. Push receipt
    print("\n6. Receipt Synchronization")

    # Load a receipt from vigil-core
    receipt_path = Path("app/code/receipts/receipt_latest.json")
    if receipt_path.exists():
        # result = client.register_local_receipt(receipt_path)
        print("✅ Receipt would be pushed to platform")
    else:
        print("ℹ️  No local receipt found (run 'vigil run && vigil promote' first)")

    # 7. Query artifacts
    print("\n7. Artifact Discovery")

    # List all artifacts
    # artifacts = client.list_artifacts(project_id=config.default_project)
    # print(f"✅ Found {len(artifacts)} artifacts")

    # Get specific artifact
    # artifact = client.get_artifact("art-123")
    # print(f"✅ Retrieved artifact: {artifact.name}")

    # 8. Provenance queries
    print("\n8. Provenance Graph")

    # Get full lineage
    # graph = client.get_provenance_graph("model-789")
    # print(f"✅ Retrieved provenance graph with {len(graph.get('nodes', []))} nodes")

    print("\n🎉 Integration demonstration complete!")
    print("\nNext steps:")
    print("1. Set VIGIL_API_URL environment variable to your backend")
    print("2. Run 'vigil platform login' to authenticate")
    print("3. Use the API client in your scientific workflows")


if __name__ == "__main__":
    demonstrate_integration()
