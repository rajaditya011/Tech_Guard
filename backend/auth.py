"""
HomeGuardian AI — Authentication
JWT token management for both portal types.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
import fastapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer(auto_error=False)

from config import settings
from database import get_db
from models import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str, role: str) -> str:
    expires = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_EXPIRY_MINUTES)
    payload = {
        "sub": user_id, "role": role, "type": "access",
        "exp": expires, "iat": datetime.utcnow(), "jti": str(uuid.uuid4())
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: str, role: str) -> str:
    expires = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRY_DAYS)
    payload = {
        "sub": user_id, "role": role, "type": "refresh",
        "exp": expires, "iat": datetime.utcnow(), "jti": str(uuid.uuid4())
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})

async def get_current_user(request: fastapi.Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    token = request.query_params.get("token")
    if not token and credentials:
        token = credentials.credentials
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    with get_db() as conn:
        user = conn.execute("SELECT id, role, device_name FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return dict(user)

def require_role(required_role: UserRole):
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] != required_role.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"This endpoint requires {required_role.value} role")
        return user
    return role_checker

def register_user(device_name: str, password: str, role: str, fcm_token: Optional[str] = None) -> dict:
    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE device_name = ? AND role = ?", (device_name, role)).fetchone()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device name already registered for this role")
        conn.execute("INSERT INTO users (id, role, device_name, password_hash, fcm_token) VALUES (?, ?, ?, ?, ?)",
                     (user_id, role, device_name, password_hash, fcm_token))
    return {"id": user_id, "role": role, "device_name": device_name}

def authenticate_user(device_name: str, password: str) -> Optional[dict]:
    with get_db() as conn:
        user = conn.execute("SELECT id, role, device_name, password_hash FROM users WHERE device_name = ?",
                            (device_name,)).fetchone()
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return {"id": user["id"], "role": user["role"], "device_name": user["device_name"]}
