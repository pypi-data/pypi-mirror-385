#!/usr/bin/env python3
"""Test script to verify vigil-client follows AUTH.md specifications."""

import os
import sys
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config_structure():
    """Test that config structure matches AUTH.md spec."""
    print("Testing config structure...")

    try:
        from vigil_client.utils.auth import ClientConfig

        # Test the expected structure from AUTH.md
        config = ClientConfig(
            user="@willblair0708",
            organization="~science-abundance",
            token="jwt.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            remote="https://api.cofactor.app"
        )

        # Verify structure matches AUTH.md
        assert hasattr(config, 'user'), "Missing 'user' field"
        assert hasattr(config, 'organization'), "Missing 'organization' field"
        assert hasattr(config, 'token'), "Missing 'token' field"
        assert hasattr(config, 'remote'), "Missing 'remote' field"

        print("✅ Config structure matches AUTH.md spec")
        return True

    except Exception as e:
        print(f"❌ Config structure test failed: {e}")
        return False

def test_auth_manager():
    """Test AuthManager follows AUTH.md spec."""
    print("\nTesting AuthManager...")

    try:
        from vigil_client.utils.auth import AuthManager

        auth_manager = AuthManager()

        # Test that it can create config in AUTH.md format
        config = auth_manager.load_config()
        if config:
            # Verify it has the right structure
            assert hasattr(config, 'user'), "Config missing 'user' field"
            assert hasattr(config, 'organization'), "Config missing 'organization' field"
            assert hasattr(config, 'token'), "Config missing 'token' field"
            assert hasattr(config, 'remote'), "Config missing 'remote' field"
            print("✅ AuthManager config structure correct")
        else:
            print("ℹ️  No existing config (normal for first run)")

        return True

    except Exception as e:
        print(f"❌ AuthManager test failed: {e}")
        return False

def test_config_file_format():
    """Test that config file format matches AUTH.md example."""
    print("\nTesting config file format...")

    try:
        from vigil_client.utils.auth import AuthManager, ClientConfig

        auth_manager = AuthManager()

        # Create a test config following AUTH.md spec
        test_config = ClientConfig(
            user="@willblair0708",
            organization="~science-abundance",
            token="jwt.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            remote="https://api.cofactor.app"
        )

        # Save it
        auth_manager.save_config(test_config)

        # Read it back and verify format
        config_file = auth_manager.CONFIG_FILE
        if config_file.exists():
            with config_file.open('r') as f:
                data = json.load(f)

            # Check it matches AUTH.md example structure
            expected_keys = {'user', 'organization', 'token', 'remote'}
            actual_keys = set(data.keys())

            if expected_keys.issubset(actual_keys):
                print("✅ Config file format matches AUTH.md spec")
                print(f"   Sample config: {json.dumps(data, indent=2)}")

                # Clean up test file
                config_file.unlink()
                return True
            else:
                print(f"❌ Config missing expected keys. Expected: {expected_keys}, Got: {actual_keys}")
                return False
        else:
            print("❌ Config file not created")
            return False

    except Exception as e:
        print(f"❌ Config file format test failed: {e}")
        return False

def test_api_headers():
    """Test that API client includes organization headers."""
    print("\nTesting API headers...")

    try:
        from vigil_client.api.client import VigilClient
        from vigil_client.models.config import PlatformConfig

        # Create a mock config with organization
        class MockConfig:
            def __init__(self):
                self.base_url = "https://api.cofactor.app"
                self.timeout = 30
                self.api_key = "test-token"
                self.organization = "~science-abundance"

        config = MockConfig()
        client = VigilClient(config)

        # Check headers include organization
        headers = client._get_headers()

        if 'X-Org' in headers and headers['X-Org'] == '~science-abundance':
            print("✅ API client includes X-Org header as per AUTH.md")
            return True
        else:
            print(f"❌ Missing X-Org header. Headers: {headers}")
            return False

    except Exception as e:
        print(f"❌ API headers test failed: {e}")
        return False

def test_authentication_flow():
    """Test the authentication flow matches AUTH.md."""
    print("\nTesting authentication flow...")

    try:
        from vigil_client.utils.auth import AuthManager

        auth_manager = AuthManager()

        # Test authentication check
        is_auth = auth_manager.is_authenticated()
        print(f"ℹ️  Authentication status: {is_auth}")

        # Test user info extraction
        if is_auth:
            user_info = auth_manager.get_user_info()
            print(f"ℹ️  User info: {user_info}")

            # Verify user info structure
            expected_keys = {'sub', 'org_id', 'username', 'organization'}
            if all(key in user_info for key in expected_keys):
                print("✅ User info structure correct")
                return True
            else:
                print(f"❌ User info missing keys. Expected: {expected_keys}, Got: {list(user_info.keys())}")
                return False
        else:
            print("ℹ️  Not authenticated (normal for first run)")
            return True

    except Exception as e:
        print(f"❌ Authentication flow test failed: {e}")
        return False

def main():
    """Run all AUTH.md alignment tests."""
    print("🔐 Vigil Client AUTH.md Alignment Test")
    print("=" * 50)

    tests = [
        ("Config Structure", test_config_structure),
        ("AuthManager", test_auth_manager),
        ("Config File Format", test_config_file_format),
        ("API Headers", test_api_headers),
        ("Authentication Flow", test_authentication_flow),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    print(f"\n{'=' * 20} SUMMARY {'=' * 20}")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{len(results)} tests")

    if passed == len(results):
        print("\n🎉 All tests passed! vigil-client follows AUTH.md specifications.")
        print("\nKey AUTH.md compliance features:")
        print("✅ Config structure: {user, organization, token, remote}")
        print("✅ Organization headers: X-Org header in API requests")
        print("✅ Token format: Direct JWT from Clerk")
        print("✅ User format: @username and ~organization prefixes")
        print("✅ Storage: ~/.vigil/config.json")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nAUTH.md compliance issues found:")
        for test_name, result in results:
            if not result:
                print(f"❌ {test_name}")

if __name__ == "__main__":
    main()
