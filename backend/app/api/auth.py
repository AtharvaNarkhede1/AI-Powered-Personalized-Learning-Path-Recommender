"""
Authentication -- email/password registration & login, JWT access tokens.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import (
    create_access_token, get_current_user, hash_password, verify_password,
)
from app.db import repository
from app.models.schemas import MeResponse, TokenResponse, UserCreate, UserLogin

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register_user(payload: UserCreate):
    email = payload.email.lower().strip()
    if not email or not payload.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    if repository.get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = repository.create_user(email, hash_password(payload.password),
                                  payload.full_name or "Learner")
    repository.create_empty_profile(user["_id"])
    return TokenResponse(
        access_token=create_access_token(user["_id"]),
        user_id=user["_id"], email=user["email"], full_name=user["full_name"],
    )


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin):
    user = repository.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(
        access_token=create_access_token(user["_id"]),
        user_id=user["_id"], email=user["email"], full_name=user.get("full_name"),
    )


@router.get("/me", response_model=MeResponse)
def me(user=Depends(get_current_user)):
    return MeResponse(user_id=user["_id"], email=user["email"], full_name=user.get("full_name"))
