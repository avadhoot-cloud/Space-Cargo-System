from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import Dict, List, Any
import json
import numpy as np

from ..database import get_db
from ..crud import container_crud, item_crud
from ..algorithms import placement_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["placement"],
    responses={404: {"description": "Not found"}}
)

@router.post("/place")
def place_item(item_id: int, container_id: int = None, db: Session = Depends(get_db)):
    """
    Place an item in a container, either in a specified container or
    in the best container determined by the placement algorithm
    """
    try:
        logger.info(f"Processing placement request for item_id={item_id}, container_id={container_id}")
        
        # Use the placement_manager to place the item
        result = placement_manager.place_item(db, item_id, container_id)
        
        if result.get("success"):
            logger.info(f"Successfully placed item {item_id} in container {result.get('container_id')}")
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to place item"))
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error in place_item: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error placing item: {str(e)}")

@router.get("/statistics")
def get_placement_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about the placement algorithm performance
    """
    try:
        logger.info("Fetching placement statistics")
        
        # Use the placement_manager to get statistics
        statistics = placement_manager.get_placement_statistics(db)
        
        logger.info(f"Placement statistics: {json.dumps(statistics)}")
        return statistics
        
    except Exception as e:
        logger.error(f"Error in get_placement_statistics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching placement statistics: {str(e)}")

def find_optimal_container(item, containers):
    """
    Find the best container for an item based on multiple factors:
    - Available space
    - Item priority
    - Zone preferences
    - Container accessibility
    """
    compatible_containers = []
    
    for container in containers:
        # Skip containers that are too small
        if not can_fit_physically(item, container):
            continue
            
        # Skip containers that are already full
        container_volume = container.width * container.height * container.depth
        used_volume = container.used_volume or 0
        item_volume = item.width * item.height * item.depth
        
        if used_volume + item_volume > container_volume * 0.95:  # 95% capacity as cutoff
            continue
            
        # Calculate compatibility score
        score = calculate_compatibility_score(item, container)
        compatible_containers.append({
            "container": container,
            "score": score
        })
    
    if not compatible_containers:
        return None
        
    # Sort by compatibility score (higher is better)
    compatible_containers.sort(key=lambda x: x["score"], reverse=True)
    return compatible_containers[0]["container"]

def calculate_compatibility_score(item, container):
    """Calculate a compatibility score between an item and a container"""
    score = 0
    
    # 1. Space fit (30%)
    container_volume = container.width * container.height * container.depth
    used_volume = container.used_volume or 0
    remaining_volume = container_volume - used_volume
    item_volume = item.width * item.height * item.depth
    
    if remaining_volume <= 0:
        return 0
        
    volume_ratio = item_volume / remaining_volume
    # Higher score when the item uses an appropriate amount of the remaining space
    space_score = 30 * (1 - abs(volume_ratio - 0.7))
    score += max(0, space_score)
    
    # 2. Zone preference (25%)
    if item.preferred_zone and container.zone == item.preferred_zone:
        score += 25
    
    # 3. Accessibility (20%)
    # Less filled containers are more accessible
    fill_ratio = used_volume / container_volume if container_volume > 0 else 1
    accessibility_score = 20 * (1 - fill_ratio)
    score += accessibility_score
    
    # 4. Priority consideration (15%)
    # Higher priority items get better placement
    if item.priority:
        priority_score = 15 * (item.priority / 100) * (1 - fill_ratio)
        score += priority_score
    
    # 5. Weight considerations (10%)
    # Check if weight capacity is respected
    if hasattr(container, 'max_weight') and hasattr(item, 'weight'):
        if container.max_weight and item.weight:
            if item.weight <= container.max_weight:
                weight_score = 10 * (1 - (item.weight / container.max_weight))
                score += weight_score
    else:
        # No weight constraints, add partial score
        score += 5
    
    return score

def can_fit_physically(item, container):
    """Check if an item can physically fit in a container based on dimensions"""
    # Get all possible orientations of the item
    item_dims = [item.width, item.height, item.depth]
    container_dims = [container.width, container.height, container.depth]
    
    # Try all possible rotations
    for perm in get_permutations(item_dims):
        if all(perm[i] <= container_dims[i] for i in range(3)):
            return True
            
    return False

def get_permutations(dims):
    """Get all possible orientations of an item"""
    return [
        [dims[0], dims[1], dims[2]],
        [dims[0], dims[2], dims[1]],
        [dims[1], dims[0], dims[2]],
        [dims[1], dims[2], dims[0]],
        [dims[2], dims[0], dims[1]],
        [dims[2], dims[1], dims[0]]
    ]

def calculate_position(item, container):
    """
    Calculate the optimal position for an item in a container
    Uses a simplified gravity-based placement strategy
    """
    # Get items already in this container
    items_in_container = item_crud.get_items_by_container(None, container.id)
    
    # Container dimensions
    container_width = container.width
    container_height = container.height
    container_depth = container.depth
    
    # If no items in container, place at bottom corner
    if not items_in_container:
        return (0, 0, 0)
    
    # Find the highest point in the container for a basic stacking approach
    highest_y = 0
    for existing_item in items_in_container:
        if existing_item.position_y is not None and existing_item.height is not None:
            item_top = existing_item.position_y + existing_item.height
            highest_y = max(highest_y, item_top)
    
    # Place on top of highest point
    # In a real implementation, you would use a more sophisticated 3D bin packing algorithm
    y = highest_y
    
    # Random x,z with margins
    margin = min(5, container_width * 0.05, container_depth * 0.05)
    max_x = max(0, container_width - item.width - 2 * margin)
    max_z = max(0, container_depth - item.depth - 2 * margin)
    
    x = margin + (np.random.random() * max_x if max_x > 0 else 0)
    z = margin + (np.random.random() * max_z if max_z > 0 else 0)
    
    return (float(x), float(y), float(z)) 