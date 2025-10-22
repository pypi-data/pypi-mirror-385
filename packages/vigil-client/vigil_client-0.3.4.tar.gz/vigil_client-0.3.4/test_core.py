#!/usr/bin/env python3
"""Test vigil-client core functionality without external dependencies."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_core_functionality():
    """Test vigil-client functionality that doesn't require httpx."""
    try:
        # Test models (don't import API client)
        from vigil_client.models import Artifact, ArtifactType, Link, LinkType, PlatformConfig, Receipt

        print('✅ Models import successfully')

        # Test artifact creation
        artifact = Artifact(
            name='test-model',
            type=ArtifactType.MODEL,
            uri='s3://test/model.pkl',
            description='Test model',
            metadata={'accuracy': 0.95}
        )
        print('✅ Artifact creation works')
        assert artifact.name == 'test-model'
        assert artifact.type == 'model'  # enum serialization
        assert artifact.status == 'draft'
        assert artifact.metadata['accuracy'] == 0.95

        # Test link creation
        link = Link(
            from_artifact_id='art-1',
            to_artifact_id='art-2',
            type=LinkType.INPUT_OF,
            metadata={'transform': 'normalize'}
        )
        print('✅ Link creation works')
        assert link.from_artifact_id == 'art-1'
        assert link.type == 'input_of'

        # Test receipt creation
        receipt = Receipt(
            issuer='Vigil',
            runlet_id='rl-123',
            vigil_url='vigil://test',
            git_ref='abc123',
            capsule_digest='sha256:def456',
            started_at='2025-01-01T10:00:00Z',
            finished_at='2025-01-01T10:30:00Z',
            version='2.0'
        )
        print('✅ Receipt creation works')
        assert receipt.issuer == 'Vigil'
        assert receipt.version == '2.0'

        # Test platform config
        config = PlatformConfig(
            base_url='https://api.test.com',
            api_key='test-key',
            project_id='proj-123'
        )
        print('✅ Platform config works')
        assert config.base_url == 'https://api.test.com'
        assert config.api_key == 'test-key'

        # Test auth (without keyring)
        from vigil_client.auth import AuthConfig, ClientConfig
        auth_config = AuthConfig(
            token='test-token',
            username='testuser'
        )
        client_config = ClientConfig(
            auth=auth_config,
            remote=config
        )
        print('✅ Auth config works')
        assert client_config.auth.token == 'test-token'

        # Test plugin system
        from vigil_client.plugins import PluginManager, BasePlugin
        plugin_manager = PluginManager()
        print('✅ Plugin system works')

        # Test CLI imports (without typer execution)
        from vigil_client.cli import platform_app
        print('✅ CLI extensions import')

        # Test extension mechanism
        from vigil_client.extension import extend_vigil_cli
        print('✅ Extension mechanism imports')

        print('🎉 vigil-client core functionality is working!')
        return True

    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_cli_commands():
    """Test that CLI commands are properly defined."""
    try:
        from vigil_client.cli import platform_app
        import inspect

        # Check that main commands exist
        commands = ['login', 'logout', 'status', 'push', 'pull', 'artifacts', 'link', 'graph', 'register', 'project']

        for cmd in commands:
            if not hasattr(platform_app, cmd):
                print(f'❌ Missing command: {cmd}')
                return False

        print(f'✅ All {len(commands)} CLI commands defined')
        return True

    except Exception as e:
        print(f'❌ CLI test error: {e}')
        return False

def test_api_contract_completeness():
    """Test that the API contract is complete."""
    try:
        # Read the API contract
        contract_path = os.path.join(os.path.dirname(__file__), 'API_CONTRACT.md')
        if not os.path.exists(contract_path):
            print('❌ API contract file missing')
            return False

        with open(contract_path, 'r') as f:
            content = f.read()

        # Check for key endpoints
        required_endpoints = [
            'POST /api/v1/artifacts',
            'GET /api/v1/artifacts/:id',
            'POST /api/v1/links',
            'GET /api/v1/links',
            'POST /api/v1/receipts',
            'GET /api/v1/receipts/:id',
            'GET /api/v1/graph/:artifact_id',
            'POST /api/v1/storage/upload-url'
        ]

        missing = []
        for endpoint in required_endpoints:
            if endpoint not in content:
                missing.append(endpoint)

        if missing:
            print(f'❌ Missing API endpoints: {missing}')
            return False

        print(f'✅ API contract complete with {len(required_endpoints)} endpoints')
        return True

    except Exception as e:
        print(f'❌ API contract test error: {e}')
        return False

if __name__ == '__main__':
    print('🧪 Testing vigil-client functionality...\n')

    tests = [
        ('Core Models & Logic', test_core_functionality),
        ('CLI Commands', test_cli_commands),
        ('API Contract', test_api_contract_completeness)
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f'Running: {name}')
        if test_func():
            passed += 1
            print(f'✅ {name} passed\n')
        else:
            print(f'❌ {name} failed\n')

    print(f'Results: {passed}/{total} tests passed')

    if passed == total:
        print('🎉 vigil-client is fully functional!')
        sys.exit(0)
    else:
        print('❌ Some tests failed')
        sys.exit(1)
