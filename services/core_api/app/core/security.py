"""Firebase authentication dependency for FastAPI routes.

This module provides:
- ``get_current_user``: FastAPI dependency that verifies an incoming
  Firebase ID token and resolves the caller's profile (including
  ``is_lawyer``) from Firestore.
- ``require_lawyer``: convenience dependency that additionally enforces
  the caller is a verified advocate.
- ``check_bypass_guard``: called at startup to refuse boot in production
  when DEV_BYPASS_AUTH is True.

Environment variables
---------------------
FIREBASE_PROJECT_ID  : Required — the Firebase project ID (e.g. "lexai-3fd1a").
DEV_BYPASS_AUTH      : Optional — set to "true" to skip token verification
                       during local development.
ENV                  : Optional — set to "production" to enable the hard
                       boot guard against DEV_BYPASS_AUTH.
"""

import json
import logging
import os
import time
from functools import lru_cache
from typing import Any, Optional

import httpx
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FIREBASE_PROJECT_ID: str = os.getenv(
    "FIREBASE_PROJECT_ID", "lexai-3fd1a"
)
DEV_BYPASS_AUTH: bool = (
    os.getenv("DEV_BYPASS_AUTH", "false").lower() == "true"
)
ENV: str = os.getenv("ENV", "development")

GOOGLE_CERTS_URL = (
    "https://www.googleapis.com/robot/v1/metadata/x509/"
    "securetoken-system@system.gserviceaccount.com"
)
FIREBASE_ISSUER = (
    f"https://securetoken.google.com/{FIREBASE_PROJECT_ID}"
)

# In-memory Firestore profile cache: uid -> (profile_dict, expires_at)
_PROFILE_CACHE: dict[str, tuple[dict[str, Any], float]] = {}
_PROFILE_TTL_SECONDS = 300  # 5 minutes

# Cached public certs: (certs_dict, expiry_epoch)
_certs_cache: tuple[dict[str, str], float] = ({}, 0.0)

bearer_scheme = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Production boot guard
# ---------------------------------------------------------------------------

def check_bypass_guard() -> None:
    """Refuse to start if DEV_BYPASS_AUTH is active in production.

    Reads ENV and DEV_BYPASS_AUTH fresh from os.environ each time so
    that test patches applied after module import are respected.

    Raises:
        RuntimeError: When ENV is "production" and DEV_BYPASS_AUTH is True.
    """
    env = os.getenv("ENV", "development")
    bypass = os.getenv("DEV_BYPASS_AUTH", "false").lower() == "true"
    if env == "production" and bypass:
        raise RuntimeError(
            "FATAL: DEV_BYPASS_AUTH=True is not allowed when "
            "ENV=production. Refusing to start to prevent "
            "unauthenticated access in a production environment."
        )


# ---------------------------------------------------------------------------
# Google public certificate fetching
# ---------------------------------------------------------------------------

def _get_google_public_keys() -> dict[str, Any]:
    """Fetch and cache Google's Firebase signing public keys.

    Returns:
        dict: Mapping of key IDs to RSA public key objects.
    """
    global _certs_cache
    certs_dict, expiry = _certs_cache

    if time.time() < expiry and certs_dict:
        return certs_dict

    response = httpx.get(GOOGLE_CERTS_URL, timeout=5.0)
    response.raise_for_status()
    raw: dict[str, str] = response.json()

    # Parse PEM certificates into public key objects
    keys: dict[str, Any] = {}
    for kid, pem in raw.items():
        cert = x509.load_pem_x509_certificate(
            pem.encode("utf-8"), default_backend()
        )
        keys[kid] = cert.public_key()

    # Honour the Cache-Control max-age if provided
    cache_control = response.headers.get("Cache-Control", "")
    max_age = 3600
    for part in cache_control.split(","):
        part = part.strip()
        if part.startswith("max-age="):
            try:
                max_age = int(part.split("=", 1)[1])
            except ValueError:
                pass

    _certs_cache = (keys, time.time() + max_age)
    return keys


# ---------------------------------------------------------------------------
# Token verification
# ---------------------------------------------------------------------------

def _verify_firebase_token(token: str) -> dict[str, Any]:
    """Verify a Firebase ID token and return its decoded claims.

    Args:
        token: The raw JWT string from the Authorization header.

    Returns:
        dict: Decoded JWT claims including ``uid``, ``email``, etc.

    Raises:
        HTTPException: 401 if the token is invalid, expired, or untrusted.
    """
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Malformed token header: {exc}",
        ) from exc

    kid = header.get("kid")
    public_keys = _get_google_public_keys()

    if kid not in public_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown signing key — try refreshing your ID token.",
        )

    try:
        claims = jwt.decode(
            token,
            public_keys[kid],
            algorithms=["RS256"],
            audience=FIREBASE_PROJECT_ID,
            issuer=FIREBASE_ISSUER,
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {exc}",
        ) from exc

    return claims


# ---------------------------------------------------------------------------
# Firestore profile resolution
# ---------------------------------------------------------------------------

def _resolve_profile(uid: str) -> dict[str, Any]:
    """Fetch the user's Firestore profile with a 5-minute TTL cache.

    Args:
        uid: Firebase user UID.

    Returns:
        dict: Firestore user document data including ``is_lawyer``.
    """
    now = time.time()
    cached = _PROFILE_CACHE.get(uid)
    if cached and now < cached[1]:
        return cached[0]

    # Lazy import to avoid hard dependency when DEV_BYPASS_AUTH is set
    try:
        import firebase_admin  # type: ignore[import]
        from firebase_admin import firestore  # type: ignore[import]

        if not firebase_admin._apps:
            firebase_admin.initialize_app()

        db = firestore.client()
        doc = db.collection("users").document(uid).get()
        profile: dict[str, Any] = doc.to_dict() if doc.exists else {}
    except Exception as exc:  # pragma: no cover
        logger.warning(
            "Firestore profile fetch failed for uid=%s: %s", uid, exc
        )
        profile = {}

    _PROFILE_CACHE[uid] = (profile, now + _PROFILE_TTL_SECONDS)
    return profile


# ---------------------------------------------------------------------------
# Pydantic schema returned by get_current_user
# ---------------------------------------------------------------------------

class FirebaseUser(BaseModel):
    """Resolved caller identity with role flags.

    Attributes:
        uid: Firebase user UID.
        email: Verified email address from the token.
        full_name: Display name from Firestore (may be empty).
        is_lawyer: True if the Firestore user document flags the caller as
            a verified advocate. This value is always fetched from
            Firestore — never trusted from the request body.
        bar_registration_number: Bar Council number from Firestore.
    """

    uid: str
    email: str
    full_name: str = ""
    is_lawyer: bool = False
    bar_registration_number: str = ""


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        bearer_scheme
    ),
) -> FirebaseUser:
    """Verify the caller's Firebase ID token and resolve their profile.

    Args:
        credentials: Bearer token extracted from the Authorization header.

    Returns:
        FirebaseUser: Resolved caller identity with role information.

    Raises:
        HTTPException: 401 if credentials are absent or invalid.
    """
    if os.getenv("DEV_BYPASS_AUTH", "false").lower() == "true":
        logger.warning(
            "DEV_BYPASS_AUTH is active — skipping token verification. "
            "This MUST NOT be enabled in production."
        )
        # Return a hard-coded dev identity so tests can set a known uid
        return FirebaseUser(
            uid=os.getenv("DEV_USER_UID", "dev-uid-000"),
            email=os.getenv("DEV_USER_EMAIL", "dev@lexai.local"),
            full_name=os.getenv("DEV_USER_NAME", "Dev User"),
            is_lawyer=(
                os.getenv("DEV_USER_IS_LAWYER", "false").lower() == "true"
            ),
        )

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header with Bearer token is required.",
        )

    claims = _verify_firebase_token(credentials.credentials)
    uid: str = claims.get("sub", claims.get("uid", ""))
    email: str = claims.get("email", "")

    profile = _resolve_profile(uid)

    return FirebaseUser(
        uid=uid,
        email=email,
        full_name=profile.get("full_name", ""),
        is_lawyer=bool(profile.get("is_lawyer", False)),
        bar_registration_number=profile.get(
            "bar_registration_number", ""
        ),
    )


async def require_lawyer(
    current_user: FirebaseUser = Depends(get_current_user),
) -> FirebaseUser:
    """Dependency that additionally enforces the caller is a verified advocate.

    Args:
        current_user: Resolved FirebaseUser from get_current_user.

    Returns:
        FirebaseUser: Verified lawyer identity.

    Raises:
        HTTPException: 403 if the caller is not flagged as is_lawyer.
    """
    if not current_user.is_lawyer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "This endpoint is restricted to verified advocates. "
                "Your account is not flagged as is_lawyer."
            ),
        )
    return current_user
