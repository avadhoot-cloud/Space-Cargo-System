from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models

router = APIRouter()

@router.get("/items")
def search_items(
    name: Optional[str] = None,
    container_id: Optional[int] = None,
    is_placed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search for items based on various criteria"""
    query = db.query(models.Item)
    
    if name:
        query = query.filter(models.Item.name.ilike(f"%{name}%"))
    
    if container_id is not None:
        query = query.filter(models.Item.container_id == container_id)
    
    if is_placed is not None:
        if is_placed:
            query = query.filter(models.Item.container_id.isnot(None))
        else:
            query = query.filter(models.Item.container_id.is_(None))
    
    items = query.offset(skip).limit(limit).all()
    return items

@router.get("/containers")
def search_containers(
    name: Optional[str] = None,
    is_active: Optional[bool] = True,
    has_space: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search for containers based on various criteria"""
    query = db.query(models.Container)
    
    if name:
        query = query.filter(models.Container.name.ilike(f"%{name}%"))
    
    if is_active is not None:
        query = query.filter(models.Container.is_active == is_active)
    
    containers = query.offset(skip).limit(limit).all()
    
    # Filter for containers with available space (if requested)
    if has_space is not None and has_space:
        containers = [c for c in containers if c.current_weight < c.max_weight]
    
    return containers 