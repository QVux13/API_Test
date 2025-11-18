from sqlalchemy.orm import Session
from models.item import Item
from schemas.item import ItemCreate

def create_item(db: Session, item: ItemCreate, owner_id: int) -> Item:
    db_item = Item(
        title=item.title,
        description=item.description,
        owner_id=owner_id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item