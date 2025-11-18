from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import re
import crud.user as crud_user
from models.user import User
from schemas.user import UserCreate, Token
from core.database import get_db
from core.security import verify_password, create_access_token
from core.config import settings

router = APIRouter()

def validate_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if len(password) > 50:
        return False, "Password must not exceed 50 characters"
    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, ""

@router.post("/register", response_model=dict)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    if not validate_email(user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    is_valid_password, password_error = validate_password(user_in.password)
    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error
        )
    
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        user = crud_user.create_user(
            db=db,
            username=user_in.email.split("@")[0],
            password=user_in.password,
            email=user_in.email,
            full_name=None
        )
        return {"message": "User created successfully", "email": user.email}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login
    Use your email as username
    """
    # form_data.username sẽ chứa email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}