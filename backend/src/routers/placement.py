from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
from fastapi.responses import JSONResponse

from ..database import get_db
from ..models import Container, Item, PlacementHistory
from ..schemas.placement import (
    ContainerCreate, Container,
    ItemCreate, Item,
    PlacementHistoryCreate, PlacementHistory,
    PlacementRecommendation, PlacementStatistics,
    PlacementResponse
)
from ..algorithms.placement_manager import PlacementManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/placement",
    tags=["placement"],
    responses={404: {"description": "Not found"}}
)

# Initialize placement manager
placement_manager = PlacementManager()

# Container endpoints
@router.post("/containers/", response_model=Container)
def create_container(container: ContainerCreate, db: Session = Depends(get_db)):
    db_container = Container(**container.model_dump())
    db.add(db_container)
    db.commit()
    db.refresh(db_container)
    return db_container

@router.get("/containers/", response_model=List[Container])
def read_containers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    containers = db.query(Container).offset(skip).limit(limit).all()
    return containers

@router.get("/containers/{container_id}", response_model=Container)
def read_container(container_id: int, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.id == container_id).first()
    if container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    return container

# Item endpoints
@router.post("/items/", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items

@router.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Placement endpoints
@router.post("/place", response_model=PlacementResponse)
def place_item(item_id: int, container_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        logger.info(f"Processing placement request for item_id={item_id}, container_id={container_id}")
        
        # Get item and container
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
            
        if container_id:
            container = db.query(Container).filter(Container.id == container_id).first()
            if not container:
                raise HTTPException(status_code=404, detail="Container not found")
        else:
            # Find optimal container if not specified
            containers = db.query(Container).all()
            if not containers:
                raise HTTPException(status_code=404, detail="No containers available")
                
            container = placement_manager.find_optimal_container(item, containers)
            if not container:
                raise HTTPException(status_code=400, detail="No suitable container found")
        
        # Place the item
        result = placement_manager.place_item(db, item, container)
        
        if result["success"]:
            # Update item status
            item.is_placed = True
            item.container_id = container.id
            item.position_x = result["position_x"]
            item.position_y = result["position_y"]
            item.position_z = result["position_z"]
            item.placement_date = datetime.now()
            
            # Update container usage
            container.used_volume += item.width * item.height * item.depth
            container.used_weight += item.weight
            container.is_full = container.used_volume >= (container.width * container.height * container.depth * 0.95)
            
            # Record in history
            history = PlacementHistory(
                item_id=item.id,
                container_id=container.id,
                placement_date=datetime.now(),
                success=True,
                reason="Successfully placed item"
            )
            db.add(history)
            
            db.commit()
            
            return PlacementResponse(
                success=True,
                message="Item placed successfully",
                container_id=container.id,
                position_x=result["position_x"],
                position_y=result["position_y"],
                position_z=result["position_z"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in place_item: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error placing item: {str(e)}")

@router.get("/recommendations", response_model=List[PlacementRecommendation])
async def get_recommendations(db: Session = Depends(get_db)):
    """Get placement recommendations for unplaced items."""
    try:
        logger.info("Fetching placement recommendations")
        
        # Get unplaced items
        unplaced_items = db.query(Item).filter(Item.is_placed == False).all()
        if not unplaced_items:
            return []
            
        # Get available containers
        containers = db.query(Container).filter(Container.is_full == False).all()
        if not containers:
            raise HTTPException(status_code=404, detail="No containers available")
            
        recommendations = []
        for item in unplaced_items:
            # Find optimal container for the item
            optimal_container = placement_manager.find_optimal_container(item, containers)
            if optimal_container:
                # Calculate compatibility score
                score = placement_manager.calculate_compatibility_score(item, optimal_container)
                
                recommendations.append(PlacementRecommendation(
                    item_id=item.id,
                    item_name=item.name,
                    container_id=optimal_container.id,
                    container_name=optimal_container.name,
                    reasoning=placement_manager.generate_reasoning(item, optimal_container, score),
                    score=score
                ))
        
        # Sort recommendations by score (highest first)
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"Generated {len(recommendations)} placement recommendations")
        return recommendations
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.get("/statistics", response_model=PlacementStatistics)
async def get_placement_statistics(db: Session = Depends(get_db)):
    """Get statistics about placement algorithm performance."""
    try:
        logger.info("Fetching placement statistics")
        
        # Get total items and placed items
        total_items = db.query(Item).count()
        placed_items = db.query(Item).filter(Item.is_placed == True).count()
        
        # Calculate success rate
        successful_placements = db.query(PlacementHistory).filter(PlacementHistory.success == True).count()
        total_placements = db.query(PlacementHistory).count()
        success_rate = (successful_placements / total_placements * 100) if total_placements > 0 else 0
        
        # Calculate space utilization
        containers = db.query(Container).all()
        total_volume = sum(c.width * c.height * c.depth for c in containers)
        used_volume = sum(c.used_volume for c in containers)
        space_utilization = (used_volume / total_volume * 100) if total_volume > 0 else 0
        
        # Calculate priority satisfaction
        high_priority_items = db.query(Item).filter(Item.priority >= 70).count()
        placed_high_priority = db.query(Item).filter(Item.priority >= 70, Item.is_placed == True).count()
        priority_satisfaction = (placed_high_priority / high_priority_items * 100) if high_priority_items > 0 else 0
        
        # Calculate zone match rate
        zone_matches = db.query(Item).filter(
            Item.is_placed == True,
            Item.preferred_zone == Container.zone
        ).join(Container).count()
        zone_match_rate = (zone_matches / placed_items * 100) if placed_items > 0 else 0
        
        # Calculate efficiency
        efficiency = (success_rate + priority_satisfaction + zone_match_rate) / 3
        
        # Get container utilization details
        container_utilization = []
        for container in containers:
            utilization = (container.used_volume / (container.width * container.height * container.depth)) * 100
            container_utilization.append({
                "id": container.id,
                "name": container.name,
                "utilization_percentage": utilization
            })
        
        return PlacementStatistics(
            total_items_placed=placed_items,
            space_utilization=space_utilization,
            success_rate=success_rate,
            efficiency=efficiency,
            priority_satisfaction=priority_satisfaction,
            zone_match_rate=zone_match_rate,
            container_utilization=container_utilization
        )
        
    except Exception as e:
        logger.error(f"Error in get_placement_statistics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching placement statistics: {str(e)}") 