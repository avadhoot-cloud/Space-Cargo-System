"""
Placement Utilities for Space Cargo System
This module provides utility functions for the placement algorithm system.
"""
import logging
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Tuple

def get_items_and_containers_from_db(db: Session) -> Tuple[List, List]:
    """
    Get all items and containers from the database.
    
    Args:
        db: Database session
        
    Returns:
        tuple: (items, containers) lists
    """
    try:
        from .. import models
        
        # Get all items
        items = db.query(models.Item).all()
        logging.info(f"Retrieved {len(items)} items from database")
        
        # Get all containers
        containers = db.query(models.Container).all()
        logging.info(f"Retrieved {len(containers)} containers from database")
        
        return items, containers
    except Exception as e:
        logging.error(f"Error getting items and containers: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return [], []

def get_item_and_container(db: Session, item_id: int, container_id: int) -> Tuple[Any, Any]:
    """
    Get an item and container by their IDs.
    
    Args:
        db: Database session
        item_id: ID of the item to retrieve
        container_id: ID of the container to retrieve
        
    Returns:
        tuple: (item, container) objects
    """
    try:
        from .. import models
        
        # Get item
        item = db.query(models.Item).filter(models.Item.id == item_id).first()
        if not item:
            raise ValueError(f"Item with ID {item_id} not found")
        
        # Get container
        container = db.query(models.Container).filter(models.Container.id == container_id).first()
        if not container:
            raise ValueError(f"Container with ID {container_id} not found")
        
        return item, container
    except Exception as e:
        logging.error(f"Error getting item and container: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        raise

def update_placement_in_db(db: Session, item: Any, container: Any, position: Dict[str, int]) -> None:
    """
    Update the database with placement information.
    
    Args:
        db: Database session
        item: The item being placed
        container: The container the item is placed in
        position: The position coordinates
    """
    try:
        # Update item with container ID and position
        item.container_id = container.id
        item.position_x = position["x"]
        item.position_y = position["y"]
        item.position_z = position["z"]
        
        # Get item weight
        item_weight = getattr(item, 'weight', 0) or 0
        
        # Update container's current weight
        current_weight = getattr(container, 'current_weight', 0) or 0
        container.current_weight = current_weight + item_weight
        
        # Commit changes to database
        db.commit()
        db.refresh(item)
        db.refresh(container)
        
        logging.info(f"Updated placement in database: Item {item.id} placed in Container {container.id}")
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating placement in database: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        raise

def get_safe_attribute(obj, attr_name, default=0):
    """
    Safely get an attribute from an object, with fallbacks.
    
    Args:
        obj: The object to get the attribute from
        attr_name: The name of the attribute
        default: Default value if attribute doesn't exist
        
    Returns:
        The attribute value or default
    """
    value = getattr(obj, attr_name, None)
    if value is None:
        return default
    return value 