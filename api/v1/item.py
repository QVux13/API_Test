from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.item import Item
from models.user import User
from schemas.item import ItemCreate, Item as ItemSchema
from core.database import get_db
from core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new item for current user"""
    db_item = Item(
        title=item.title,
        description=item.description,
        owner_id=current_user.id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=List[ItemSchema])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all items of current user"""
    items = db.query(Item).filter(Item.owner_id == current_user.id).offset(skip).limit(limit).all()
    return items

@router.get("/{item_id}", response_model=ItemSchema)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific item by ID"""
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemSchema)
async def update_item(
    item_id: int,
    item_update: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update item"""
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.title = item_update.title
    db_item.description = item_update.description
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete item"""
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return None