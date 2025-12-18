"""CRUD operations for User model."""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Convert password to bytes
    password_bytes = plain_password.encode('utf-8')
    # Truncate to 72 bytes if necessary
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Verify against hash
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    # Truncate to 72 bytes if necessary (bcrypt limit)
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update a user."""
    user = get_user(db, user_id)
    if not user:
        return None
    
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(user)
    return user


def get_all_users(db: Session, skip: int = 0, limit: int = 1000) -> List[User]:
    """Get all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    user = get_user(db, user_id)
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True

