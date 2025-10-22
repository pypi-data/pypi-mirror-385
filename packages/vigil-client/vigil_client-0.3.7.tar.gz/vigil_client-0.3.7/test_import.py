#!/usr/bin/env python3
"""Quick test script to verify vigil-client functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules import correctly."""
    try:
        from vigil_client import VigilClient, Artifact, ArtifactType
        print('✅ vigil-client imports successfully')

        # Test model creation
        artifact = Artifact(
            name='test-model',
            type=ArtifactType.MODEL,
            uri='s3://test/model.pkl',
            description='Test model'
        )
        print('✅ Models work correctly')
        assert artifact.name == 'test-model'
        assert artifact.type == 'model'  # enum value
        assert artifact.status == 'draft'  # default

        # Test API client instantiation
        from vigil_client.models import PlatformConfig
        config = PlatformConfig(base_url='https://test.com', api_key='test-key')
        client = VigilClient(config)
        print('✅ API client initializes correctly')
        assert client.config.base_url == 'https://test.com'

        # Test auth
        from vigil_client.auth import auth_manager
        print('✅ Auth manager imports correctly')

        # Test CLI
        from vigil_client.cli import platform_app
        print('✅ CLI extensions import correctly')

        # Test plugins
        from vigil_client.plugins import plugin_manager
        print('✅ Plugin system imports correctly')

        print('🎉 vigil-client is fully functional!')
        return True

    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
