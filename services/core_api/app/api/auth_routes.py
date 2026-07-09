from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

try:
    from app.models.models import User, UserCreate, UserRead
    from app.core.auth import (
        get_password_hash,
        verify_password,
        create_access_token,
    )
    from app.core.db import get_session
except ImportError:
    from models.models import User, UserCreate, UserRead
    from core.auth import (
        get_password_hash,
        verify_password,
        create_access_token,
    )
    from core.db import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead)
async def signup(
    user: UserCreate,
    session: Session = Depends(get_session)
) -> User:
    """Register a new user in the database.

    Args:
        user: User registration data.
        session: Database session.

    Returns:
        User: Created user instance.
    """
    # Check if user already exists
    statement = select(User).where(User.email == user.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash the password and save
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        hashed_password=hashed_password,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> dict:
    """Authenticate user and return a JWT access token.

    Args:
        form_data: OAuth2 password request form.
        session: Database session.

    Returns:
        dict: Access token and token type.
    """
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()

    if not user or not verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}
