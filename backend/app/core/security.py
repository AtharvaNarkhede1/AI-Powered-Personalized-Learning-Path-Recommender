from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from app.db import mongo
_bearer = HTTPBearer(auto_error=False)
def _pw_bytes(plain: str) -> bytes:
    # bcrypt only uses the first 72 bytes; truncate explicitly so hashing and
    # verification always agree regardless of the installed bcrypt version.
    return (plain or "").encode("utf-8")[:72]
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_pw_bytes(plain), bcrypt.gensalt()).decode("utf-8")
def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_pw_bytes(plain), (hashed or "").encode("utf-8"))
    except (ValueError, TypeError):
        return False
def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM],
            leeway=30,  # tolerate minor server clock skew
        )
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
_CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)
def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Dict[str, Any]:
    if creds is None or not creds.credentials:
        raise _CREDENTIALS_EXC
    user_id = decode_token(creds.credentials)
    if not user_id:
        raise _CREDENTIALS_EXC
    user = mongo.users.find_one({"_id": user_id})
    if not user:
        raise _CREDENTIALS_EXC
    return user