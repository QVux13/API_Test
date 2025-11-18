from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import User as UserSchema
from core.database import get_db
from core.security import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current logged-in user information
    Requires: Bearer token in Authorization header
    """
    return current_user

@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user by ID
    Requires: Bearer token in Authorization header
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=UserSchema)
async def update_current_user(
    full_name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's information
    Requires: Bearer token in Authorization header
    """
    if full_name is not None:
        current_user.full_name = full_name
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete current user account
    Requires: Bearer token in Authorization header
    """
    db.delete(current_user)
    db.commit()
    return None