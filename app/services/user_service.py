"""User service - Business logic for user operations."""
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserResponse, UserUpdate


def create_user(
    db: Session,
    user_data: UserCreate
) -> UserResponse:
    """
    Create a new user with validation.
    
    Args:
        db: Database session
        user_data: User data to create
    
    Returns:
        UserResponse
    
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    if user_crud.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if user_crud.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user (password hashing is done in CRUD)
    db_user = user_crud.create_user(db, user_data)
    return UserResponse.model_validate(db_user)


def authenticate_user(
    db: Session,
    username: str,
    password: str
) -> Optional[UserResponse]:
    """
    Authenticate a user by username and password.
    
    Args:
        db: Database session
        username: Username
        password: Plain text password
    
    Returns:
        UserResponse if authentication successful, None otherwise
    """
    user = user_crud.authenticate_user(db, username, password)
    if not user:
        return None
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return UserResponse.model_validate(user)


def get_user_by_id(
    db: Session,
    user_id: int
) -> Optional[UserResponse]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        UserResponse if found, None otherwise
    """
    user = user_crud.get_user(db, user_id)
    if not user:
        return None
    return UserResponse.model_validate(user)


def update_user(
    db: Session,
    user_id: int,
    user_update: UserUpdate
) -> Optional[UserResponse]:
    """
    Update a user with validation.
    
    Args:
        db: Database session
        user_id: User ID
        user_update: User update data
    
    Returns:
        UserResponse if updated, None if user not found
    
    Raises:
        HTTPException: If new username or email already exists
    """
    # Check if username is being changed and already exists
    if user_update.username is not None:
        existing_user = user_crud.get_user_by_username(db, user_update.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
    
    # Check if email is being changed and already exists
    if user_update.email is not None:
        existing_user = user_crud.get_user_by_email(db, user_update.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update user (password hashing is done in CRUD)
    updated_user = user_crud.update_user(db, user_id, user_update)
    if not updated_user:
        return None
    
    return UserResponse.model_validate(updated_user)

