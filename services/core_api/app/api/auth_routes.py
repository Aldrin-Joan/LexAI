from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.models import User, UserCreate, UserRead, UserRole
from app.core.auth import get_password_hash, verify_password, create_access_token
from sqlmodel import Session, select

# Assuming a database engine setup - for now we'll use a placeholder for dependency injection
# In a real app, engine would be initialized in app/core/db.py

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead)
async def signup(user: UserCreate):
    # This is a placeholder since we haven't initialized the DB session yet in main.py
    # In a real implementation, we'd use a DB session
    print(f"Signing up user: {user.email} with role {user.role}")

    # Simulate DB check
    if user.email == "exists@example.com":
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    # Return a mock user for now to test the structure
    return {
        "id": 1,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": True,
        "created_at": "2023-10-27T10:00:00",
    }


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Mock validation
    if form_data.username == "test@example.com" and form_data.password == "password":
        access_token = create_access_token(subject=form_data.username)
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
