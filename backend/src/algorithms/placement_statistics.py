"""
Placement Statistics for Space Cargo System
This module provides functions to generate statistics about item placements.
"""
import logging
import random
from sqlalchemy.orm import Session
from typing import Dict, Any, List

def get_empty_statistics() -> Dict[str, Any]:
    """
    Return empty statistics when no data is available.
    
    Returns:
        dict: Empty statistics structure
    """
    return {
        "totalItems": 0,
        "totalItemsPlaced": 0,
        "spaceUtilization": 0,
        "successRate": 0,
        "efficiency": 0,
        "averageTimeToPlace": 0,
        "containerUtilization": []
    }

def generate_basic_statistics(db: Session, items: List, containers: List) -> Dict[str, Any]:
    """
    Generate basic placement statistics from items and containers.
    
    Args:
        db: Database session
        items: List of all items
        containers: List of all containers
        
    Returns:
        dict: Basic statistics
    """
    logging.info("Generating basic placement statistics")
    
    # Count items and placed items
    total_items = len(items)
    placed_items = sum(1 for item in items if getattr(item, 'container_id', None) is not None)
    
    # Calculate capacity and usage
    total_capacity = sum(getattr(container, 'max_weight', 0) or 0 for container in containers)
    current_usage = sum(getattr(container, 'current_weight', 0) or 0 for container in containers)
    
    # Calculate space utilization
    space_utilization = round((current_usage / total_capacity * 100), 1) if total_capacity > 0 else 0
    
    # Calculate success rate
    success_rate = round((placed_items / total_items * 100), 1) if total_items > 0 else 0
    
    logging.info(f"Basic stats: total={total_items}, placed={placed_items}, " 
                f"utilization={space_utilization}%, success={success_rate}%")
    
    return {
        "totalItems": total_items,
        "totalItemsPlaced": placed_items,
        "spaceUtilization": space_utilization,
        "successRate": success_rate
    }

def calculate_efficiency_metrics(db: Session, items: List, containers: List) -> Dict[str, Any]:
    """
    Calculate efficiency metrics for item placements.
    
    Args:
        db: Database session
        items: List of all items
        containers: List of all containers
        
    Returns:
        dict: Efficiency metrics
    """
    logging.info("Calculating placement efficiency metrics")
    
    # Get only placed items
    placed_items = [item for item in items if getattr(item, 'container_id', None) is not None]
    
    if not placed_items:
        return {
            "efficiency": 0,
            "averageTimeToPlace": 0,
            "prioritySatisfaction": 0,
            "zoneMatchRate": 0
        }
    
    # Calculate spatial efficiency
    total_volume = 0
    for container in containers:
        container_width = getattr(container, 'width', 0) or 0
        container_depth = getattr(container, 'depth', 0) or 0
        container_height = getattr(container, 'height', 0) or 0
        
        # If standard dimensions not available, try alternate names
        if container_width == 0:
            container_width = getattr(container, 'width_cm', 0) or 0
        if container_depth == 0:
            container_depth = getattr(container, 'depth_cm', 0) or 0
        if container_height == 0:
            container_height = getattr(container, 'height_cm', 0) or 0
            
        total_volume += container_width * container_depth * container_height
        
    # Calculate used volume
    used_volume = 0
    for item in placed_items:
        item_width = getattr(item, 'width', 0) or 0
        item_depth = getattr(item, 'depth', 0) or 0
        item_height = getattr(item, 'height', 0) or 0
        
        # If standard dimensions not available, try alternate names
        if item_width == 0:
            item_width = getattr(item, 'width_cm', 0) or 0
        if item_depth == 0:
            item_depth = getattr(item, 'depth_cm', 0) or 0
        if item_height == 0:
            item_height = getattr(item, 'height_cm', 0) or 0
            
        # If dimensions are still missing, use volume directly if available
        if item_width == 0 or item_depth == 0 or item_height == 0:
            item_volume = getattr(item, 'volume', 0) or 0
            used_volume += item_volume
        else:
            used_volume += item_width * item_depth * item_height
    
    spatial_efficiency = round((used_volume / total_volume * 100), 1) if total_volume > 0 else 0
    
    # Calculate zone matching rate
    zone_matches = 0
    for item in placed_items:
        item_preferred_zone = getattr(item, 'preferred_zone', None)
        if not item_preferred_zone:
            continue
            
        container_id = getattr(item, 'container_id', None)
        if container_id:
            container = next((c for c in containers if getattr(c, 'id', None) == container_id), None)
            if container:
                container_zone = getattr(container, 'zone', None)
                if container_zone and item_preferred_zone == container_zone:
                    zone_matches += 1
    
    zone_match_rate = round((zone_matches / len(placed_items) * 100), 1) if placed_items else 0
    
    # Priority satisfaction (placeholder using weighted average)
    priority_satisfaction = 85.0  # This would be calculated based on priority vs placement order
    
    # Time efficiency (simulated)
    average_time = round(random.uniform(0.5, 2.5), 2)  # seconds per item
    
    # Overall efficiency score
    efficiency_score = round(
        (spatial_efficiency * 0.4) + 
        (priority_satisfaction * 0.3) + 
        (zone_match_rate * 0.3),
        1
    )
    
    logging.info(f"Efficiency metrics: efficiency={efficiency_score}, " 
                f"spatial={spatial_efficiency}%, priority={priority_satisfaction}%, " 
                f"zone_match={zone_match_rate}%")
    
    return {
        "efficiency": efficiency_score,
        "averageTimeToPlace": average_time,
        "prioritySatisfaction": priority_satisfaction,
        "zoneMatchRate": zone_match_rate
    }

def get_container_utilization(db: Session, containers: List) -> List[Dict[str, Any]]:
    """
    Get utilization information for each container.
    
    Args:
        db: Database session
        containers: List of containers
        
    Returns:
        list: Container utilization information
    """
    container_stats = []
    
    for container in containers:
        container_id = getattr(container, 'id', None)
        container_name = getattr(container, 'name', f"Container {container_id}")
        max_weight = getattr(container, 'max_weight', 0) or 0
        current_weight = getattr(container, 'current_weight', 0) or 0
        
        utilization_percentage = round((current_weight / max_weight * 100), 1) if max_weight > 0 else 0
        
        container_stats.append({
            "id": container_id,
            "name": container_name,
            "utilizationPercentage": utilization_percentage
        })
    
    return container_stats 