from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from .. import models

logger = logging.getLogger(__name__)

def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    """
    Get an item by ID
    
    Args:
        db: Database session
        item_id: ID of the item to retrieve
        
    Returns:
        Item object or None if not found
    """
    logger.info(f"Getting item with id {item_id}")
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 100, 
              category: Optional[str] = None, 
              status: Optional[str] = None,
              container_id: Optional[int] = None) -> List[models.Item]:
    """
    Get a list of items with filtering options
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        category: Optional category to filter by
        status: Optional status to filter by (AVAILABLE, CONSUMED, EXPIRED)
        container_id: Optional container ID to filter by
        
    Returns:
        List of Item objects
    """
    logger.info(f"Getting items (skip={skip}, limit={limit}, category={category}, "
                f"status={status}, container_id={container_id})")
    
    query = db.query(models.Item)
    
    if category:
        query = query.filter(models.Item.category == category)
    
    if status:
        query = query.filter(models.Item.status == status)
    
    if container_id is not None:
        query = query.filter(models.Item.container_id == container_id)
    
    return query.offset(skip).limit(limit).all()

def get_items_by_container(db: Session, container_id: int) -> List[models.Item]:
    """
    Get all items in a specific container
    
    Args:
        db: Database session
        container_id: ID of the container
        
    Returns:
        List of Item objects in the container
    """
    logger.info(f"Getting items in container {container_id}")
    return db.query(models.Item).filter(models.Item.container_id == container_id).all()

def create_item(db: Session, item_data: Dict[str, Any]) -> models.Item:
    """
    Create a new item
    
    Args:
        db: Database session
        item_data: Dictionary with item attributes
        
    Returns:
        Created Item object
    """
    logger.info(f"Creating item with data: {item_data}")
    
    db_item = models.Item(
        name=item_data.get("name", ""),
        description=item_data.get("description", ""),
        weight=item_data.get("weight", 0),
        volume=item_data.get("volume", 0),
        width=item_data.get("width"),
        height=item_data.get("height"),
        depth=item_data.get("depth"),
        priority=item_data.get("priority", 1),
        is_fragile=item_data.get("is_fragile", False),
        preferred_zone=item_data.get("preferred_zone", "general"),
        category=item_data.get("category", "general"),
        status=item_data.get("status", "AVAILABLE"),
        expiry_date=item_data.get("expiry_date"),
        container_id=item_data.get("container_id")
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, 
               item_data: Dict[str, Any]) -> Optional[models.Item]:
    """
    Update an existing item
    
    Args:
        db: Database session
        item_id: ID of the item to update
        item_data: Dictionary with item attributes to update
        
    Returns:
        Updated Item object or None if not found
    """
    logger.info(f"Updating item {item_id} with data: {item_data}")
    
    db_item = get_item(db, item_id)
    if not db_item:
        logger.warning(f"Item with id {item_id} not found")
        return None
    
    # Update item attributes
    for key, value in item_data.items():
        if hasattr(db_item, key):
            setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item_container(db: Session, item_id: int, container_id: int,
                         position_x: float, position_y: float, 
                         position_z: float) -> Optional[models.Item]:
    """
    Update an item's container and position
    
    Args:
        db: Database session
        item_id: ID of the item to update
        container_id: ID of the new container
        position_x: X position within the container
        position_y: Y position within the container
        position_z: Z position within the container
        
    Returns:
        Updated Item object or None if not found
    """
    logger.info(f"Updating item {item_id} container to {container_id} at position "
                f"({position_x}, {position_y}, {position_z})")
    
    db_item = get_item(db, item_id)
    if not db_item:
        logger.warning(f"Item with id {item_id} not found")
        return None
    
    db_item.container_id = container_id
    db_item.position_x = position_x
    db_item.position_y = position_y
    db_item.position_z = position_z
    
    db.commit()
    db.refresh(db_item)
    return db_item

def mark_item_consumed(db: Session, item_id: int) -> Optional[models.Item]:
    """
    Mark an item as consumed
    
    Args:
        db: Database session
        item_id: ID of the item to mark as consumed
        
    Returns:
        Updated Item object or None if not found
    """
    logger.info(f"Marking item {item_id} as consumed")
    
    db_item = get_item(db, item_id)
    if not db_item:
        logger.warning(f"Item with id {item_id} not found")
        return None
    
    db_item.status = "CONSUMED"
    db_item.consumed_date = datetime.now()
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int) -> bool:
    """
    Delete an item
    
    Args:
        db: Database session
        item_id: ID of the item to delete
        
    Returns:
        True if deleted, False if not found
    """
    logger.info(f"Deleting item {item_id}")
    
    db_item = get_item(db, item_id)
    if not db_item:
        logger.warning(f"Item with id {item_id} not found")
        return False
    
    db.delete(db_item)
    db.commit()
    return True 