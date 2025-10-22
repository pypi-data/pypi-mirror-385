"""JWT signature verification utilities for vigil-client."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import jwt
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class JWKS:
    """JSON Web Key Set handler for JWT verification."""

    def __init__(self, jwks_url: str):
        self.jwks_url = jwks_url
        self._keys: List[Dict[str, Any]] = []
        self._last_fetch: Optional[float] = None

    def _fetch_keys(self) -> None:
        """Fetch JWKS from the URL."""
        try:
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            jwks = response.json()
            self._keys = jwks.get('keys', [])
            import time
            self._last_fetch = time.time()
        except Exception as e:
            raise ValueError(f"Failed to fetch JWKS: {e}")

    def get_key(self, kid: str) -> Optional[Dict[str, Any]]:
        """Get a specific key by key ID."""
        import time

        # Refresh keys if older than 1 hour
        if self._last_fetch is None or time.time() - self._last_fetch > 3600:
            self._fetch_keys()

        for key in self._keys:
            if key.get('kid') == kid:
                return key
        return None

    def get_signing_key(self, token: str) -> Optional[str]:
        """Get the signing key for a JWT token."""
        try:
            # Decode header to get key ID
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')

            if not kid:
                return None

            key_data = self.get_key(kid)
            if not key_data:
                return None

            # Convert JWK to PEM format
            if key_data.get('kty') == 'RSA':
                # Extract RSA components
                n = key_data.get('n')
                e = key_data.get('e')

                if n and e:
                    # Convert base64url to integers
                    import base64
                    import struct

                    def base64url_decode(data: str) -> bytes:
                        # Add padding if needed
                        missing_padding = len(data) % 4
                        if missing_padding:
                            data += '=' * (4 - missing_padding)
                        return base64.urlsafe_b64decode(data)

                    n_bytes = base64url_decode(n)
                    e_bytes = base64url_decode(e)

                    # Convert to integers
                    n_int = int.from_bytes(n_bytes, 'big')
                    e_int = int.from_bytes(e_bytes, 'big')

                    # Create RSA public key
                    public_key = rsa.RSAPublicNumbers(e_int, n_int).public_key()

                    # Convert to PEM format
                    pem = public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )

                    return pem.decode('utf-8')

            return None

        except Exception as e:
            print(f"Error getting signing key: {e}")
            return None


class JWTValidator:
    """JWT token validator with signature verification."""

    def __init__(self, jwks_url: str):
        self.jwks = JWKS(jwks_url)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token signature and return payload."""
        try:
            # Get signing key
            signing_key = self.jwks.get_signing_key(token)
            if not signing_key:
                raise ValueError("Could not find signing key")

            # Verify token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=['RS256'],
                options={'verify_exp': True, 'verify_aud': False}
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")
        except Exception as e:
            raise ValueError(f"Token verification failed: {e}")

    def verify_token_without_signature(self, token: str) -> Dict[str, Any]:
        """Verify JWT token without signature verification (for development)."""
        try:
            payload = jwt.decode(
                token,
                options={'verify_signature': False, 'verify_exp': False}
            )
            return payload
        except Exception as e:
            raise ValueError(f"Token parsing failed: {e}")


def create_clerk_validator(clerk_domain: str) -> JWTValidator:
    """Create a JWT validator for Clerk tokens."""
    jwks_url = f"{clerk_domain}/.well-known/jwks.json"
    return JWTValidator(jwks_url)
