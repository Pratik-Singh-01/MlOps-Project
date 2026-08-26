import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

import config


bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class TokenRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = "viewer"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str


class UserInfo(BaseModel):
    username: str
    role: str


USERS_DB = {
    config.ADMIN_USERNAME: {
        "password": config.ADMIN_PASSWORD,
        "role": "admin",
    },
    config.VIEWER_USERNAME: {
        "password": config.VIEWER_PASSWORD,
        "role": "viewer",
    },
}


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_access_token(username: str, role: str, expires_delta: Optional[int] = None) -> str:
    expires_in = expires_delta or (config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    payload = {
        "sub": username,
        "role": role,
        "exp": int(time.time()) + expires_in,
    }
    payload_part = _b64_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(
        config.SECRET_KEY.encode("utf-8"),
        payload_part.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{payload_part}.{_b64_encode(signature)}"


def verify_token(token: str) -> UserInfo:
    try:
        payload_part, signature_part = token.split(".", 1)
        actual_signature = _b64_decode(signature_part)
        expected_signature = hmac.new(
            config.SECRET_KEY.encode("utf-8"),
            payload_part.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(expected_signature, actual_signature):
            raise ValueError("Signature mismatch")

        payload = json.loads(_b64_decode(payload_part).decode("utf-8"))
        if payload.get("exp", 0) < int(time.time()):
            raise ValueError("Token expired")

        username = payload.get("sub")
        role = payload.get("role")
        if not username or not role:
            raise ValueError("Missing subject or role")

        return UserInfo(username=username, role=role)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = USERS_DB.get(username)
    if user is None:
        return None
    if not secrets.compare_digest(password, user["password"]):
        return None
    return {"username": username, "role": user["role"]}


def register_user(username: str, password: str, role: str = "viewer") -> dict:
    clean_username = username.strip()
    if not clean_username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )
    target_role = (role or "viewer").lower().strip()
    if target_role not in ("admin", "viewer"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'admin' or 'viewer'",
        )
    if clean_username in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    USERS_DB[clean_username] = {
        "password": password,
        "role": target_role,
    }
    return {"username": clean_username, "role": target_role}


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
) -> UserInfo:
    if credentials and credentials.credentials:
        return verify_token(credentials.credentials)
    if api_key and api_key in config.API_KEYS:
        return UserInfo(username="api-key-user", role="viewer")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def require_admin(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
