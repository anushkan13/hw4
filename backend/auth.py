"""Password hashing and session tokens for Campus Customs.

The three seeded users were created with PBKDF2-HMAC-SHA256 and stored as

    pbkdf2_sha256$<salt>$<hex digest>

with 120,000 iterations and the salt used as raw UTF-8 bytes. New accounts are
written in exactly that format with the same parameters, so the seeded users keep
working and every row in the table verifies through one code path.

Plain passwords exist only as a local variable inside hash_password() and
verify_password(). They are never stored, never returned by a route, and never
logged.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path

# --- password hashing --------------------------------------------------------
ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000
SALT_BYTES = 8  # 8 bytes -> 16 hex chars, matching the seeded users' salts


def hash_password(password: str) -> str:
    """Return a storable `pbkdf2_sha256$salt$digest` string for a plain password."""
    salt = secrets.token_hex(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS
    )
    return f"{ALGORITHM}${salt}${digest.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    """Check a plain password against a stored hash, in constant time."""
    if not stored:
        return False
    try:
        algorithm, salt, expected = stored.split("$")
    except ValueError:
        return False
    if algorithm != ALGORITHM:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS
    )
    # compare_digest avoids leaking how much of the hash matched via timing.
    return hmac.compare_digest(digest.hex(), expected)


# --- session tokens ----------------------------------------------------------
# Stateless HMAC-signed tokens: "<user_id>.<expiry>.<signature>". Nothing about the
# password is in the token, and a tampered id or expiry fails the signature check.
TOKEN_TTL_SECONDS = 14 * 24 * 60 * 60  # 14 days
_SECRET_FILE = Path(__file__).resolve().parent / ".session_secret"


def _load_secret() -> bytes:
    """Secret for signing tokens, from the environment or a local gitignored file.

    Persisting it means a backend restart does not log everyone out, which matters
    during development.
    """
    from_env = os.environ.get("CAMPUS_CUSTOMS_SECRET")
    if from_env:
        return from_env.encode("utf-8")
    if _SECRET_FILE.exists():
        return _SECRET_FILE.read_text().strip().encode("utf-8")
    generated = secrets.token_hex(32)
    _SECRET_FILE.write_text(generated)
    _SECRET_FILE.chmod(0o600)
    return generated.encode("utf-8")


_SECRET = _load_secret()


def _sign(payload: str) -> str:
    mac = hmac.new(_SECRET, payload.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode("ascii").rstrip("=")


def create_token(user_id: int, ttl: int = TOKEN_TTL_SECONDS) -> str:
    payload = f"{user_id}.{int(time.time()) + ttl}"
    return f"{payload}.{_sign(payload)}"


def read_token(token: str | None) -> int | None:
    """Return the user id for a valid, unexpired token, else None."""
    if not token:
        return None
    try:
        user_id, expiry, signature = token.split(".")
    except ValueError:
        return None
    if not hmac.compare_digest(_sign(f"{user_id}.{expiry}"), signature):
        return None
    try:
        if int(expiry) < time.time():
            return None
        return int(user_id)
    except ValueError:
        return None
