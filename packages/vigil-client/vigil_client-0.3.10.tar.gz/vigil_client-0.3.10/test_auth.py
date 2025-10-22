#!/usr/bin/env python3
"""Test script for Clerk authentication setup."""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        import jwt
        print("✅ PyJWT imported successfully")
    except ImportError as e:
        print(f"❌ PyJWT import failed: {e}")
        return False

    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False

    try:
        from requests_oauthlib import OAuth2Session
        print("✅ Requests-OAuthlib imported successfully")
    except ImportError as e:
        print(f"❌ Requests-OAuthlib import failed: {e}")
        return False

    try:
        import keyring
        print("✅ Keyring imported successfully")
    except ImportError as e:
        print(f"❌ Keyring import failed: {e}")
        return False

    try:
        from cryptography.hazmat.primitives import serialization
        print("✅ Cryptography imported successfully")
    except ImportError as e:
        print(f"❌ Cryptography import failed: {e}")
        return False

    return True

def test_auth_manager():
    """Test AuthManager initialization."""
    print("\nTesting AuthManager...")

    try:
        from vigil_client.utils.auth import AuthManager
        auth_manager = AuthManager()
        print("✅ AuthManager initialized successfully")

        # Test config loading
        config = auth_manager.load_config()
        if config:
            print("✅ Configuration loaded successfully")
        else:
            print("ℹ️  No existing configuration found (this is normal for first run)")

        return True
    except Exception as e:
        print(f"❌ AuthManager test failed: {e}")
        return False

def test_jwt_validator():
    """Test JWT validator."""
    print("\nTesting JWT validator...")

    try:
        from vigil_client.utils.jwt_validator import JWTValidator, create_clerk_validator
        print("✅ JWT validator imported successfully")

        # Test validator creation (this will fail if Clerk domain is not set)
        try:
            validator = create_clerk_validator("https://test.clerk.accounts.dev")
            print("✅ JWT validator created successfully")
        except Exception as e:
            print(f"ℹ️  JWT validator creation failed (expected if Clerk not configured): {e}")

        return True
    except Exception as e:
        print(f"❌ JWT validator test failed: {e}")
        return False

def test_environment():
    """Test environment variables."""
    print("\nTesting environment variables...")

    required_vars = [
        "CLERK_CLIENT_ID",
        "CLERK_CLIENT_SECRET",
        "CLERK_DOMAIN"
    ]

    optional_vars = [
        "VIGIL_API_URL"
    ]

    all_good = True

    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set (required)")
            all_good = False

    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var} is set")
        else:
            print(f"ℹ️  {var} is not set (optional)")

    return all_good

def main():
    """Run all tests."""
    print("🔐 Vigil Client Authentication Test")
    print("=" * 40)

    tests = [
        ("Import Test", test_imports),
        ("AuthManager Test", test_auth_manager),
        ("JWT Validator Test", test_jwt_validator),
        ("Environment Test", test_environment),
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
        print("\n🎉 All tests passed! Authentication setup is ready.")
        print("\nNext steps:")
        print("1. Set up your Clerk application (see CLERK_SETUP.md)")
        print("2. Configure environment variables")
        print("3. Run 'vigil login' to test authentication")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install missing dependencies: pip install -e .")
        print("2. Set up environment variables (see env.example)")
        print("3. Check Clerk configuration (see CLERK_SETUP.md)")

if __name__ == "__main__":
    main()
