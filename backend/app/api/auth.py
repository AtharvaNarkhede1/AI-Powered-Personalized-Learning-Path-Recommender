from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError
from app.core.security import (
    create_access_token, get_current_user, hash_password, verify_password,
)
from app.db import repository
from app.models.schemas import (
    MeResponse, PasswordResetRequest, TokenResponse, UserCreate, UserLogin,
)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
@router.post("/register", response_model=TokenResponse)
def register_user(payload: UserCreate):
    email = (payload.email or "").lower().strip()
    password = payload.password or ""
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if repository.get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        user = repository.create_user(email, hash_password(password),
                                      payload.full_name or "Learner")
    except DuplicateKeyError:
        # Lost a race with a concurrent signup for the same email.
        raise HTTPException(status_code=400, detail="Email already registered")
    repository.create_empty_profile(user["_id"])
    return TokenResponse(
        access_token=create_access_token(user["_id"]),
        user_id=user["_id"], email=user["email"], full_name=user["full_name"],
    )
@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin):
    email = (payload.email or "").lower().strip()
    user = repository.get_user_by_email(email)
    if not user or not verify_password(payload.password or "", user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(
        access_token=create_access_token(user["_id"]),
        user_id=user["_id"], email=user["email"], full_name=user.get("full_name"),
    )
@router.post("/reset-password", response_model=TokenResponse)
def reset_password(payload: PasswordResetRequest):
    """Set a new password for an existing account (no email verification -- this
    app has no mail transport). Recovers accounts locked out by a mistyped
    password at signup."""
    email = (payload.email or "").lower().strip()
    new_password = payload.new_password or ""
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    user = repository.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="No account found for that email")
    repository.update_user_password(user["_id"], hash_password(new_password))
    return TokenResponse(
        access_token=create_access_token(user["_id"]),
        user_id=user["_id"], email=user["email"], full_name=user.get("full_name"),
    )
@router.get("/me", response_model=MeResponse)
def me(user=Depends(get_current_user)):
    return MeResponse(user_id=user["_id"], email=user["email"], full_name=user.get("full_name"))
