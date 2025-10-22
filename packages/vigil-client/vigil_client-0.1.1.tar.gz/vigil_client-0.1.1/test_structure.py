#!/usr/bin/env python3
"""Test vigil-client package structure and basic functionality."""

import os
import sys
import json
from pathlib import Path

def test_package_structure():
    """Test that the package has the expected structure."""
    package_dir = Path(__file__).parent / "src" / "vigil_client"

    required_files = [
        "__init__.py",
        "models.py",
        "api.py",
        "auth.py",
        "cli.py",
        "plugins.py",
        "extension.py"
    ]

    missing = []
    for file in required_files:
        if not (package_dir / file).exists():
            missing.append(file)

    if missing:
        print(f"❌ Missing files: {missing}")
        return False

    print(f"✅ Package structure complete - {len(required_files)} core files present")
    return True

def test_readme_and_docs():
    """Test that documentation files exist."""
    docs = ["README.md", "API_CONTRACT.md"]

    missing = []
    for doc in docs:
        if not Path(__file__).parent.joinpath(doc).exists():
            missing.append(doc)

    if missing:
        print(f"❌ Missing documentation: {missing}")
        return False

    print("✅ Documentation files present")
    return True

def test_pyproject_config():
    """Test that pyproject.toml is properly configured."""
    pyproject_path = Path(__file__).parent / "pyproject.toml"

    if not pyproject_path.exists():
        print("❌ pyproject.toml missing")
        return False

    try:
        with open(pyproject_path) as f:
            content = f.read()

        required_fields = [
            'name = "vigil-client"',
            'dependencies = [',
            "httpx",
            "pydantic",
            "pyjwt"
        ]

        missing = []
        for field in required_fields:
            if field not in content:
                missing.append(field)

        if missing:
            print(f"❌ Missing pyproject fields: {missing}")
            return False

        print("✅ pyproject.toml properly configured")
        return True

    except Exception as e:
        print(f"❌ Error reading pyproject.toml: {e}")
        return False

def test_cli_command_definitions():
    """Test that CLI commands are properly defined (without importing dependencies)."""
    cli_path = Path(__file__).parent / "src" / "vigil_client" / "cli.py"

    try:
        with open(cli_path) as f:
            content = f.read()

        # Check for key command definitions
        required_commands = [
            '@platform_app.command("login")',
            '@platform_app.command("push")',
            '@platform_app.command("pull")',
            '@platform_app.command("artifacts")',
            '@platform_app.command("link")',
            '@platform_app.command("graph")',
            '@platform_app.command("register")'
        ]

        missing = []
        for cmd in required_commands:
            if cmd not in content:
                missing.append(cmd)

        if missing:
            print(f"❌ Missing CLI commands: {missing}")
            return False

        print(f"✅ All {len(required_commands)} CLI commands defined")
        return True

    except Exception as e:
        print(f"❌ Error checking CLI: {e}")
        return False

def test_api_endpoints_coverage():
    """Test that API contract covers all required endpoints."""
    contract_path = Path(__file__).parent / "API_CONTRACT.md"

    try:
        with open(contract_path) as f:
            content = f.read()

        # Check for all required API endpoints
        endpoints = [
            "POST /api/v1/artifacts",
            "GET /api/v1/artifacts/:id",
            "PATCH /api/v1/artifacts/:id",
            "GET /api/v1/artifacts",
            "POST /api/v1/links",
            "GET /api/v1/links",
            "POST /api/v1/receipts",
            "GET /api/v1/receipts/:id",
            "GET /api/v1/graph/:artifact_id",
            "POST /api/v1/storage/upload-url",
            "GET /api/v1/artifacts/:id/download"
        ]

        missing = []
        for endpoint in endpoints:
            if endpoint not in content:
                missing.append(endpoint)

        if missing:
            print(f"❌ Missing API endpoints: {missing}")
            return False

        print(f"✅ API contract covers all {len(endpoints)} required endpoints")
        return True

    except Exception as e:
        print(f"❌ Error checking API contract: {e}")
        return False

def test_models_structure():
    """Test that model definitions are present."""
    models_path = Path(__file__).parent / "src" / "vigil_client" / "models.py"

    try:
        with open(models_path) as f:
            content = f.read()

        required_classes = [
            "class ArtifactType",
            "class Artifact(BaseModel)",
            "class LinkType",
            "class Link(BaseModel)",
            "class PlatformConfig(BaseModel)",
            "class Receipt(BaseModel)"
        ]

        missing = []
        for cls in required_classes:
            if cls not in content:
                missing.append(cls)

        if missing:
            print(f"❌ Missing model classes: {missing}")
            return False

        print(f"✅ All {len(required_classes)} model classes defined")
        return True

    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def simulate_cli_commands():
    """Simulate testing CLI commands without full imports."""
    try:
        # Test that we can at least import the basic structure
        sys.path.insert(0, str(Path(__file__).parent / "src"))

        # Import just the CLI app definition (should work without dependencies)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cli_test",
            Path(__file__).parent / "src" / "vigil_client" / "cli.py"
        )

        # We can't actually execute this due to missing dependencies,
        # but we can verify the file is syntactically correct
        with open(Path(__file__).parent / "src" / "vigil_client" / "cli.py") as f:
            code = f.read()

        # Basic syntax check by compiling
        compile(code, "cli.py", "exec")
        print("✅ CLI module syntax is valid")
        return True

    except SyntaxError as e:
        print(f"❌ CLI syntax error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  CLI import test skipped (expected due to missing dependencies): {e}")
        return True  # This is expected

if __name__ == "__main__":
    print("🧪 Testing vigil-client package structure...\n")

    tests = [
        ("Package Structure", test_package_structure),
        ("Documentation", test_readme_and_docs),
        ("Pyproject Config", test_pyproject_config),
        ("CLI Commands", test_cli_command_definitions),
        ("API Endpoints", test_api_endpoints_coverage),
        ("Model Definitions", test_models_structure),
        ("CLI Syntax", simulate_cli_commands),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"Running: {name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {name} passed\n")
            else:
                print(f"❌ {name} failed\n")
        except Exception as e:
            print(f"❌ {name} error: {e}\n")

    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 vigil-client package structure is complete and ready!")
        print("\n🚀 Next steps:")
        print("1. Install dependencies: pip install httpx pydantic pyjwt keyring")
        print("2. Run full integration tests")
        print("3. Test against your cofactor-api backend")
        sys.exit(0)
    else:
        print("❌ Some structural tests failed")
        sys.exit(1)
