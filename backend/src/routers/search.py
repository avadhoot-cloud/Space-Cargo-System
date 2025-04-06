from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..database import get_db
from ..crud import container_crud, item_crud
from .. import models

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["search"],
    responses={404: {"description": "Not found"}}
)

@router.get("/items")
def search_items(
    query: str = "",
    category: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Search for items based on query and filters
    """
    logger.info(f"Searching items with query: {query}, category: {category}, status: {status}")
    
    try:
        # Get all items matching the filters
        items = item_crud.get_items(db, skip=skip, limit=limit, category=category, status=status)
        
        # Filter by search query if provided
        if query:
            query = query.lower()
            filtered_items = [
                item for item in items
                if query in item.name.lower() or 
                   (item.description and query in item.description.lower()) or
                   (item.category and query in item.category.lower())
            ]
        else:
            filtered_items = items
            
        # Convert to dictionaries
        result = [item.to_dict() for item in filtered_items]
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching items: {str(e)}")

@router.get("/containers")
def search_containers(
    query: str = "",
    zone: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Search for containers based on query and filters
    """
    logger.info(f"Searching containers with query: {query}, zone: {zone}")
    
    try:
        # Get all containers matching the filters
        containers = container_crud.get_containers(db, skip=skip, limit=limit, zone=zone)
        
        # Filter by search query if provided
        if query:
            query = query.lower()
            filtered_containers = [
                container for container in containers
                if query in container.name.lower() or 
                   (container.zone and query in container.zone.lower())
            ]
        else:
            filtered_containers = containers
            
        # Convert to dictionaries
        result = [container.to_dict() for container in filtered_containers]
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching containers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching containers: {str(e)}") 