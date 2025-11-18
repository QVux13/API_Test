from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate
from core.security import hash_password

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str, email: str, full_name: str | None = None) -> User:
    """Create new user"""
    hashed_password = hash_password(password)
    db_user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user