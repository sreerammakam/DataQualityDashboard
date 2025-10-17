from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

from .config import get_settings


PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 200_000
PBKDF2_SALT_BYTES = 16


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def _b64decode(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


def hash_password(plain_password: str) -> str:
    salt = os.urandom(PBKDF2_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM, plain_password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"pbkdf2_{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${_b64encode(salt)}${_b64encode(dk)}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        scheme, iter_str, b64_salt, b64_hash = hashed_password.split("$")
        assert scheme.startswith("pbkdf2_")
        iterations = int(iter_str)
        salt = _b64decode(b64_salt)
        expected = _b64decode(b64_hash)
    except Exception:
        return False
    candidate = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM, plain_password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(candidate, expected)


def create_access_token(subject: str, expires_minutes: Optional[int] = None, extra: Optional[Dict[str, Any]] = None) -> str:
    settings = get_settings()
    expire_delta = timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {"sub": subject, "iat": int(now.timestamp()), "exp": int((now + expire_delta).timestamp())}
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_token(token: str) -> Dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
