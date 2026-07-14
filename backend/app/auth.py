"""
auth.py — Benutzer-Auth für ein Familien-Deployment: bcrypt-Passwörter + signierte
Tokens (JWT, 30 Tage gültig). Der Admin legt Nutzer an — kein Self-Signup, kein OAuth.
AUTH_SECRET kommt aus der Umgebung (.env), wie alle Secrets.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Header, HTTPException

TOKEN_DAYS = 30


def _secret() -> str:
    secret = os.environ.get("AUTH_SECRET")
    if not secret:
        raise RuntimeError("AUTH_SECRET fehlt in .env — langen Zufallsstring setzen.")
    return secret


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def make_token(user_id: str) -> str:
    return jwt.encode(
        {"sub": user_id,
         "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_DAYS)},
        _secret(), algorithm="HS256",
    )


def user_id_from_token(authorization: str | None = Header(None)) -> str:
    """FastAPI dependency: Bearer-Token → user_id (401 bei allem anderen)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "No autenticado.")
    try:
        return jwt.decode(authorization[7:], _secret(), algorithms=["HS256"])["sub"]
    except jwt.PyJWTError:
        raise HTTPException(401, "Sesión caducada — vuelve a entrar.")
