from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import logging
import traceback

from ..crud import container_crud, item_crud
from ..algorithms import placement_manager

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["simulation"],
    responses={404: {"description": "Not found"}}
)

@router.post("/run")
def run_simulation(
    days: int = Query(7, description="Number of days to simulate"),
    items_per_day: int = Query(5, description="Average number of items to process per day"),
    random_seed: Optional[int] = Query(None, description="Random seed for reproducibility"),
    db: Session = Depends(get_db)
):
    """
    Run a simulation of the space cargo system over a specified period
    
    Simulates:
    - New items arriving
    - Items being placed in containers
    - Items being consumed
    """
    logger.info(f"Starting simulation: {days} days, {items_per_day} items/day, seed: {random_seed}")
    
    # Set random seed if provided
    if random_seed is not None:
        random.seed(random_seed)
    
    try:
        # Get all containers and items
        containers = container_crud.get_containers(db)
        items = item_crud.get_items(db, status="available")
        
        if not containers:
            raise HTTPException(status_code=400, detail="No containers available for simulation")
        
        # Statistics to track
        stats = {
            "days_simulated": days,
            "items_processed": 0,
            "items_placed": 0,
            "items_failed": 0,
            "items_consumed": 0,
            "space_utilization": 0.0,
            "daily_activity": []
        }
        
        # Simulation loop
        start_date = datetime.now()
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            daily_stats = {
                "day": day + 1,
                "date": current_date.strftime("%Y-%m-%d"),
                "items_processed": 0,
                "items_placed": 0,
                "items_failed": 0,
                "items_consumed": 0
            }
            
            # Generate random number of items for the day
            day_items_count = max(1, int(random.gauss(items_per_day, items_per_day/3)))
            
            # Process items
            for _ in range(day_items_count):
                # Get available items or create new ones if needed
                if not items or random.random() > 0.7:  # 30% chance to generate new item
                    new_item_data = generate_random_item()
                    new_item = item_crud.create_item(db, new_item_data)
                    items.append(new_item)
                
                # Select a random item to process
                item_index = random.randint(0, len(items) - 1)
                item = items[item_index]
                
                daily_stats["items_processed"] += 1
                stats["items_processed"] += 1
                
                # Try to place the item
                try:
                    # Choose a container or let the algorithm find the best one
                    use_specific_container = random.random() > 0.5
                    container_id = None
                    
                    if use_specific_container and containers:
                        container_id = random.choice(containers).id
                    
                    # Try to place the item using placement algorithm
                    placement_result = placement_manager.place_item(db, item.id, container_id)
                    
                    if placement_result.get("success", False):
                        daily_stats["items_placed"] += 1
                        stats["items_placed"] += 1
                        # Remove from available items
                        items.pop(item_index)
                    else:
                        daily_stats["items_failed"] += 1
                        stats["items_failed"] += 1
                        
                except Exception as e:
                    logger.error(f"Error placing item in simulation: {str(e)}")
                    daily_stats["items_failed"] += 1
                    stats["items_failed"] += 1
            
            # Randomly consume some items
            placed_items = item_crud.get_items(db, status="placed")
            if placed_items:
                consumed_count = random.randint(0, min(3, len(placed_items)))
                for _ in range(consumed_count):
                    item_to_consume = random.choice(placed_items)
                    item_crud.mark_item_consumed(db, item_to_consume.id)
                    placed_items.remove(item_to_consume)
                    
                    daily_stats["items_consumed"] += 1
                    stats["items_consumed"] += 1
            
            # Add daily stats to overall record
            stats["daily_activity"].append(daily_stats)
        
        # Calculate final space utilization
        placement_statistics = placement_manager.get_placement_statistics(db)
        stats["space_utilization"] = placement_statistics.get("space_utilization", 0.0)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error running simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running simulation: {str(e)}")

def generate_random_item() -> Dict[str, Any]:
    """Generate random item data for simulation"""
    categories = ["Food", "Equipment", "Medical", "Science", "Personal"]
    zones = ["A", "B", "C", "D", "E"]
    
    # Random dimensions between 0.1 and 1.0 meters
    length = round(random.uniform(0.1, 1.0), 2)
    width = round(random.uniform(0.1, 1.0), 2)
    height = round(random.uniform(0.1, 1.0), 2)
    
    # Random weight between 0.5 and 10 kg
    weight = round(random.uniform(0.5, 10.0), 2)
    
    return {
        "name": f"Sim-Item-{random.randint(1000, 9999)}",
        "length": length,
        "width": width,
        "height": height,
        "weight": weight,
        "category": random.choice(categories),
        "priority": random.randint(1, 5),
        "preferred_zone": random.choice(zones),
        "status": "available"
    }

@router.post("/day")
def simulate_next_day(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Simulate the passage of one day in the space cargo system.
    Updates item statuses, simulates usage, and handles expiry dates.
    """
    try:
        # Get the current simulated date (from db or use default)
        current_date = get_simulation_date(db)
        
        # Set next date (add one day)
        next_date = current_date + timedelta(days=1)
        
        # Process simulation for one day
        simulation_results = process_day_simulation(db, current_date, next_date)
        
        # Update the simulation date in the database
        update_simulation_date(db, next_date)
        
        return {
            "success": True,
            "daysSimulated": 1,
            "previousDate": current_date.isoformat(),
            "currentDate": next_date.isoformat(),
            "itemsConsumed": simulation_results["items_consumed"],
            "newExpiredItems": simulation_results["new_expired_items"],
            "alerts": simulation_results["alerts"]
        }
    except Exception as e:
        logging.error(f"Error simulating next day: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error simulating next day: {str(e)}")


@router.post("/days")
def simulate_multiple_days(days: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Simulate the passage of multiple days in the space cargo system.
    Updates item statuses, simulates usage, and handles expiry dates.
    """
    if days < 1 or days > 90:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 90")
    
    try:
        # Get the current simulated date
        current_date = get_simulation_date(db)
        
        # Set end date after simulating multiple days
        end_date = current_date + timedelta(days=days)
        
        # Collect aggregated results
        total_consumed = 0
        total_expired = 0
        all_alerts = []
        
        # Process each day in the simulation
        temp_date = current_date
        for _ in range(days):
            next_date = temp_date + timedelta(days=1)
            daily_results = process_day_simulation(db, temp_date, next_date)
            
            total_consumed += daily_results["items_consumed"]
            total_expired += daily_results["new_expired_items"]
            all_alerts.extend(daily_results["alerts"])
            
            temp_date = next_date
        
        # Update the simulation date in the database
        update_simulation_date(db, end_date)
        
        return {
            "success": True,
            "daysSimulated": days,
            "startDate": current_date.isoformat(),
            "currentDate": end_date.isoformat(),
            "itemsConsumed": total_consumed,
            "newExpiredItems": total_expired,
            "alerts": all_alerts[-10:] if len(all_alerts) > 10 else all_alerts
        }
    except Exception as e:
        logging.error(f"Error simulating multiple days: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error simulating multiple days: {str(e)}")


def get_simulation_date(db: Session) -> datetime:
    """Get the current simulation date from the database or create one if it doesn't exist"""
    try:
        sim_config = db.query(models.SystemConfig).filter(models.SystemConfig.key == "simulation_date").first()
        
        if not sim_config:
            # Start with today's date if not set
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            sim_config = models.SystemConfig(key="simulation_date", value=today.isoformat())
            db.add(sim_config)
            db.commit()
            return today
        
        return datetime.fromisoformat(sim_config.value)
    except Exception as e:
        logger.error(f"Error getting simulation date: {str(e)}")
        logger.error(traceback.format_exc())
        # Fall back to today's date if there's an error
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def update_simulation_date(db: Session, new_date: datetime) -> None:
    """Update the simulation date in the database"""
    try:
        sim_config = db.query(models.SystemConfig).filter(models.SystemConfig.key == "simulation_date").first()
        
        if not sim_config:
            sim_config = models.SystemConfig(key="simulation_date", value=new_date.isoformat())
            db.add(sim_config)
        else:
            sim_config.value = new_date.isoformat()
        
        db.commit()
    except Exception as e:
        logger.error(f"Error updating simulation date: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()


def process_day_simulation(db: Session, current_date: datetime, next_date: datetime) -> Dict[str, Any]:
    """
    Process a single day of simulation.
    This simulates:
    1. Item consumption based on priority
    2. Item expiry
    3. Generates alerts for critical situations
    
    Returns stats about the simulation day.
    """
    items_consumed = 0
    new_expired_items = 0
    alerts = []
    
    # Get all items
    items = db.query(models.Item).all()
    
    # Consume items based on priority (higher priority = more likely to be consumed)
    for item in items:
        # Skip already consumed items
        if item.status == "CONSUMED":
            continue
            
        # Check for expiry
        if item.expiry_date and datetime.fromisoformat(str(item.expiry_date)) <= next_date:
            if item.status != "EXPIRED":
                item.status = "EXPIRED"
                new_expired_items += 1
                
                # Generate alert for expired items
                alerts.append({
                    "severity": "warning",
                    "message": f"Item '{item.name}' has expired on {item.expiry_date}"
                })
        
        # Simulate consumption based on priority
        # Higher priority = less likely to be consumed
        consumption_chance = 0.05 - (item.priority * 0.01)  # Base 5% chance, reduced by priority
        
        if item.status == "AVAILABLE" and random.random() < consumption_chance:
            item.status = "CONSUMED"
            item.consumed_date = next_date.isoformat()
            items_consumed += 1
    
    # Generate alerts for low stock
    item_categories = {}
    for item in items:
        if item.category not in item_categories:
            item_categories[item.category] = {
                "total": 0,
                "available": 0
            }
        
        item_categories[item.category]["total"] += 1
        if item.status == "AVAILABLE":
            item_categories[item.category]["available"] += 1
    
    # Check if any category is running low
    for category, counts in item_categories.items():
        if counts["total"] > 0:
            available_percentage = counts["available"] / counts["total"] * 100
            
            if available_percentage <= 10:
                alerts.append({
                    "severity": "critical",
                    "message": f"Critical shortage of {category}: only {counts['available']} items left ({available_percentage:.1f}%)"
                })
            elif available_percentage <= 25:
                alerts.append({
                    "severity": "warning", 
                    "message": f"Low stock of {category}: only {counts['available']} items left ({available_percentage:.1f}%)"
                })
    
    # Commit all changes
    db.commit()
    
    return {
        "items_consumed": items_consumed,
        "new_expired_items": new_expired_items,
        "alerts": alerts
    } 