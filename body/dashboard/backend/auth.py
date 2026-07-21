# Copyright Entropy Hackers. Licensed under the Apache License, Version 2.0.
"""Single shared admin credential (same posture as v0 — no per-Vater
accounts yet, see docs' Non-Goals). A signed, timestamped cookie replaces
Flask's server-side session so the FastAPI backend stays stateless; no
session table needed for a single-operator tool.
"""

from __future__ import annotations

import bcrypt
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

COOKIE_NAME = "dashboard_session"
MAX_AGE_SECONDS = 7 * 24 * 3600  # 7 days, matches v0


def make_serializer(secret_key: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret_key, salt="dashboard-auth")


def check_password(password: str, password_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash)


def make_session_cookie(serializer: URLSafeTimedSerializer) -> str:
    return serializer.dumps({"authenticated": True})


def verify_session_cookie(serializer: URLSafeTimedSerializer, cookie_value: str | None) -> bool:
    if not cookie_value:
        return False
    try:
        data = serializer.loads(cookie_value, max_age=MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return False
    return bool(data.get("authenticated"))
