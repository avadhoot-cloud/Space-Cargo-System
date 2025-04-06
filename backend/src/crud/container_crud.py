from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from .. import models

logger = logging.getLogger(__name__)

def get_container(db: Session, container_id: int) -> Optional[models.Container]:
    """
    Get a container by ID
    
    Args:
        db: Database session
        container_id: ID of the container to retrieve
        
    Returns:
        Container object or None if not found
    """
    logger.info(f"Getting container with id {container_id}")
    return db.query(models.Container).filter(models.Container.id == container_id).first()

def get_containers(db: Session, skip: int = 0, limit: int = 100, 
                   zone: Optional[str] = None) -> List[models.Container]:
    """
    Get a list of containers, optionally filtered by zone
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        zone: Optional zone to filter by
        
    Returns:
        List of Container objects
    """
    logger.info(f"Getting containers (skip={skip}, limit={limit}, zone={zone})")
    query = db.query(models.Container)
    
    if zone:
        query = query.filter(models.Container.zone == zone)
    
    return query.offset(skip).limit(limit).all()

def create_container(db: Session, container_data: Dict[str, Any]) -> models.Container:
    """
    Create a new container
    
    Args:
        db: Database session
        container_data: Dictionary with container attributes
        
    Returns:
        Created Container object
    """
    logger.info(f"Creating container with data: {container_data}")
    
    db_container = models.Container(
        name=container_data.get("name", ""),
        width=container_data.get("width", 0),
        height=container_data.get("height", 0),
        depth=container_data.get("depth", 0),
        max_weight=container_data.get("max_weight", 0),
        zone=container_data.get("zone", "general"),
        is_active=container_data.get("is_active", True)
    )
    
    db.add(db_container)
    db.commit()
    db.refresh(db_container)
    return db_container

def update_container(db: Session, container_id: int, 
                    container_data: Dict[str, Any]) -> Optional[models.Container]:
    """
    Update an existing container
    
    Args:
        db: Database session
        container_id: ID of the container to update
        container_data: Dictionary with container attributes to update
        
    Returns:
        Updated Container object or None if not found
    """
    logger.info(f"Updating container {container_id} with data: {container_data}")
    
    db_container = get_container(db, container_id)
    if not db_container:
        logger.warning(f"Container with id {container_id} not found")
        return None
    
    # Update container attributes
    for key, value in container_data.items():
        if hasattr(db_container, key):
            setattr(db_container, key, value)
    
    db.commit()
    db.refresh(db_container)
    return db_container

def update_container_usage(db: Session, container_id: int, 
                          used_volume: float) -> Optional[models.Container]:
    """
    Update a container's used volume
    
    Args:
        db: Database session
        container_id: ID of the container to update
        used_volume: New used volume value
        
    Returns:
        Updated Container object or None if not found
    """
    logger.info(f"Updating container {container_id} used volume to {used_volume}")
    
    db_container = get_container(db, container_id)
    if not db_container:
        logger.warning(f"Container with id {container_id} not found")
        return None
    
    db_container.used_volume = used_volume
    
    db.commit()
    db.refresh(db_container)
    return db_container

def delete_container(db: Session, container_id: int) -> bool:
    """
    Delete a container
    
    Args:
        db: Database session
        container_id: ID of the container to delete
        
    Returns:
        True if deleted, False if not found
    """
    logger.info(f"Deleting container {container_id}")
    
    db_container = get_container(db, container_id)
    if not db_container:
        logger.warning(f"Container with id {container_id} not found")
        return False
    
    db.delete(db_container)
    db.commit()
    return True 