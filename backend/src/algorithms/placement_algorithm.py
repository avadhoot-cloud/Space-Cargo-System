"""
Core Placement Algorithm for Space Cargo System
This module contains the main logic for determining optimal placement of items in containers.
"""
import numpy as np
import logging
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PlacementAlgorithm:
    """
    An improved algorithm for optimal placement of items in containers
    with sophisticated space optimization and priority handling.
    """
    
    def __init__(self):
        self.stats = {
            "totalItemsPlaced": 0,
            "spaceUtilization": 0,
            "successRate": 0,
            "efficiency": 0,
            "prioritySatisfaction": 0,
            "zoneMatchRate": 0,
        }
    
    def find_optimal_placement(self, item: Dict[str, Any], containers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the optimal container for an item based on multiple factors:
        - Available space
        - Zone preferences
        - Priority of the item
        - Container accessibility
        - Expiry date considerations
        
        Args:
            item: The item to place
            containers: List of available containers
            
        Returns:
            Dictionary with placement information or None if no suitable placement found
        """
        logger.info(f"Finding optimal placement for item: {item.get('name')} (ID: {item.get('id')})")
        
        # Check if item can fit in any container
        compatible_containers = []
        for container in containers:
            # Skip containers that are already full
            if self._is_container_full(container):
                continue
                
            # Check physical constraints (dimensions)
            if self._can_fit_physically(item, container):
                compatibility_score = self._calculate_compatibility_score(item, container)
                compatible_containers.append({
                    "container": container,
                    "score": compatibility_score
                })
        
        # If no compatible containers found
        if not compatible_containers:
            logger.warning(f"No compatible containers found for item {item.get('name')}")
            return None
            
        # Sort by compatibility score (higher is better)
        compatible_containers.sort(key=lambda x: x["score"], reverse=True)
        best_container = compatible_containers[0]["container"]
        
        # Calculate optimal position within the container
        position = self._find_optimal_position(item, best_container)
        
        if not position:
            logger.warning(f"Could not find position in container {best_container.get('name')}")
            return None
            
        # Update statistics
        self.stats["totalItemsPlaced"] += 1
        
        # Create placement result
        placement_result = {
            "item_id": item.get("id"),
            "container_id": best_container.get("id"),
            "container_name": best_container.get("name"),
            "position_x": position[0],
            "position_y": position[1],
            "position_z": position[2],
            "rotation": self._calculate_optimal_rotation(item),
            "placement_date": datetime.now().isoformat(),
            "placement_score": compatible_containers[0]["score"]
        }
        
        logger.info(f"Optimal placement found: {placement_result}")
        return placement_result
    
    def place_batch(self, items: List[Dict[str, Any]], containers: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Place a batch of items optimally across available containers
        
        Args:
            items: List of items to place
            containers: List of available containers
            
        Returns:
            Tuple of (successful_placements, failed_placements)
        """
        logger.info(f"Starting batch placement for {len(items)} items across {len(containers)} containers")
        
        # Sort items by priority (high to low) and then by expiry date (sooner first)
        sorted_items = sorted(items, 
                             key=lambda x: (-(x.get("priority") or 0), 
                                           x.get("expiry_date") or "9999-12-31"))
        
        successful_placements = []
        failed_placements = []
        
        # Track container space usage for this batch
        container_usage = {container.get("id"): {"used_volume": 0, "total_volume": self._calculate_container_volume(container)} 
                          for container in containers}
        
        for item in sorted_items:
            # Deep copy of containers with updated usage for accurate placement
            current_containers = []
            for container in containers:
                container_copy = container.copy()
                container_copy["used_volume"] = container_usage[container.get("id")]["used_volume"]
                current_containers.append(container_copy)
            
            placement = self.find_optimal_placement(item, current_containers)
            
            if placement:
                successful_placements.append(placement)
                # Update container usage
                container_id = placement["container_id"]
                item_volume = self._calculate_item_volume(item)
                container_usage[container_id]["used_volume"] += item_volume
            else:
                failed_placements.append({
                    "item_id": item.get("id"),
                    "item_name": item.get("name"),
                    "reason": "No suitable container found"
                })
        
        # Calculate final statistics
        self._calculate_statistics(successful_placements, failed_placements, container_usage, items, containers)
        
        logger.info(f"Batch placement completed: {len(successful_placements)} successful, {len(failed_placements)} failed")
        return successful_placements, failed_placements
    
    def get_placement_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about placement operations
        
        Returns:
            Dictionary of statistics
        """
        return self.stats
    
    def _calculate_statistics(self, successful_placements, failed_placements, container_usage, items, containers):
        """Calculate comprehensive statistics about the placement operations"""
        total_items = len(items)
        placed_items = len(successful_placements)
        
        # Update success rate
        self.stats["successRate"] = round((placed_items / max(total_items, 1)) * 100, 2)
        
        # Calculate space utilization
        total_container_volume = sum(usage["total_volume"] for usage in container_usage.values())
        total_used_volume = sum(usage["used_volume"] for usage in container_usage.values())
        
        if total_container_volume > 0:
            self.stats["spaceUtilization"] = round((total_used_volume / total_container_volume) * 100, 2)
        
        # Calculate priority satisfaction
        if successful_placements:
            priority_scores = []
            for placement in successful_placements:
                item = next((i for i in items if i.get("id") == placement["item_id"]), None)
                if item and "priority" in item:
                    placement_score = placement["placement_score"]
                    # Higher priority items with better placement scores contribute more
                    weighted_score = (item["priority"] / 100) * placement_score
                    priority_scores.append(weighted_score)
            
            if priority_scores:
                avg_priority_satisfaction = sum(priority_scores) / len(priority_scores)
                self.stats["prioritySatisfaction"] = round(avg_priority_satisfaction * 100, 2)
        
        # Calculate zone matching rate
        zone_matches = 0
        for placement in successful_placements:
            item = next((i for i in items if i.get("id") == placement["item_id"]), None)
            container = next((c for c in containers if c.get("id") == placement["container_id"]), None)
            
            if item and container and "preferredZone" in item and "zone" in container:
                if item["preferredZone"] == container["zone"]:
                    zone_matches += 1
        
        if successful_placements:
            self.stats["zoneMatchRate"] = round((zone_matches / len(successful_placements)) * 100, 2)
        
        # Calculate efficiency (considers packing density, item priorities, and zone matching)
        efficiency_score = (
            (self.stats["spaceUtilization"] / 100) * 0.4 +
            (self.stats["successRate"] / 100) * 0.3 +
            (self.stats["prioritySatisfaction"] / 100) * 0.2 +
            (self.stats["zoneMatchRate"] / 100) * 0.1
        ) * 100
        
        self.stats["efficiency"] = round(efficiency_score, 2)
        self.stats["totalItemsPlaced"] = placed_items
    
    def _calculate_compatibility_score(self, item: Dict[str, Any], container: Dict[str, Any]) -> float:
        """Calculate a compatibility score between an item and a container"""
        score = 0.0
        
        # Space fit (how well the item fits - smaller containers preferred if it fits well)
        item_volume = self._calculate_item_volume(item)
        container_remaining_volume = self._calculate_container_volume(container) - container.get("used_volume", 0)
        
        # If item is too big, return 0
        if item_volume > container_remaining_volume:
            return 0.0
            
        # Calculate space fit score - we want to maximize usage without wasting space
        # Higher score for containers where item fits well but doesn't waste space
        volume_ratio = item_volume / max(container_remaining_volume, 0.001)  # Avoid division by zero
        space_fit_score = 0.8 * volume_ratio + 0.2 * (1 - abs(0.7 - volume_ratio))
        score += space_fit_score * 40  # Space fit contributes 40% of score
        
        # Zone preference match (30% of score)
        if item.get("preferredZone") and item.get("preferredZone") == container.get("zone"):
            score += 30
        
        # Accessibility score (20% of score)
        # Lower position values typically mean more accessible locations
        accessibility = 1.0 - (container.get("used_volume", 0) / 
                              max(self._calculate_container_volume(container), 0.001))
        score += accessibility * 20
        
        # Weight capacity check (10% of score)
        if "weight" in item and "maxWeight" in container:
            if item["weight"] <= container.get("remainingWeight", container["maxWeight"]):
                weight_ratio = 1.0 - (item["weight"] / max(container["maxWeight"], 0.001))
                score += weight_ratio * 10
        else:
            score += 5  # Add partial score if weight constraints aren't specified
        
        return score
    
    def _calculate_item_volume(self, item: Dict[str, Any]) -> float:
        """Calculate the volume of an item in cubic units"""
        if "volume" in item:
            return item["volume"]
        
        # If volume not provided, calculate from dimensions
        width = item.get("width", 0)
        height = item.get("height", 0)
        depth = item.get("depth", 0)
        
        return width * height * depth
    
    def _calculate_container_volume(self, container: Dict[str, Any]) -> float:
        """Calculate the volume of a container in cubic units"""
        if "volume" in container:
            return container["volume"]
        
        # If volume not provided, calculate from dimensions
        width = container.get("width", 0)
        height = container.get("height", 0)
        depth = container.get("depth", 0)
        
        return width * height * depth
    
    def _is_container_full(self, container: Dict[str, Any]) -> bool:
        """Check if a container is already full"""
        used_volume = container.get("used_volume", 0)
        total_volume = self._calculate_container_volume(container)
        
        # Consider container full if it's at 95% capacity or more
        return used_volume >= (total_volume * 0.95)
    
    def _can_fit_physically(self, item: Dict[str, Any], container: Dict[str, Any]) -> bool:
        """Check if an item can physically fit in a container based on dimensions"""
        # Check dimensions
        item_width = item.get("width", 0)
        item_height = item.get("height", 0)
        item_depth = item.get("depth", 0)
        
        container_width = container.get("width", 0)
        container_height = container.get("height", 0)
        container_depth = container.get("depth", 0)
        
        # Check volume
        item_volume = self._calculate_item_volume(item)
        container_remaining_volume = self._calculate_container_volume(container) - container.get("used_volume", 0)
        
        # Check weight if data is available
        weight_check = True
        if "weight" in item and "maxWeight" in container:
            remaining_weight = container.get("remainingWeight", container["maxWeight"])
            weight_check = item["weight"] <= remaining_weight
        
        # Each dimension must fit, considering possible rotations
        dimensions_check = (
            (item_width <= container_width and item_height <= container_height and item_depth <= container_depth) or
            (item_width <= container_width and item_depth <= container_height and item_height <= container_depth) or
            (item_height <= container_width and item_width <= container_height and item_depth <= container_depth) or
            (item_height <= container_width and item_depth <= container_height and item_width <= container_depth) or
            (item_depth <= container_width and item_width <= container_height and item_height <= container_depth) or
            (item_depth <= container_width and item_height <= container_height and item_width <= container_depth)
        )
        
        return dimensions_check and item_volume <= container_remaining_volume and weight_check
    
    def _find_optimal_position(self, item: Dict[str, Any], container: Dict[str, Any]) -> Optional[Tuple[float, float, float]]:
        """
        Find the optimal position for an item in a container.
        Implements a simplistic gravity-based placement.
        
        In a real implementation, this could use a 3D bin packing algorithm.
        """
        # Simple implementation - place at first available position
        # For a real application, a 3D bin packing algorithm would be used here
        
        # Simulate a simplistic placement: put the item at the bottom
        # with some existing items in the way
        
        # Let's pretend the container has some items in it at various
        # heights, calculated based on used_volume
        container_width = container.get("width", 100)
        container_depth = container.get("depth", 100)
        
        # Proportional to how full the container is
        used_ratio = min(container.get("used_volume", 0) / 
                        max(self._calculate_container_volume(container), 0.001), 0.95)
        
        # Simplified: assume items are evenly distributed at the bottom
        # and the average height is proportional to the used volume ratio
        item_height = item.get("height", 10)
        
        # Randomly generate a position, avoiding the edges
        margin = 5
        x = margin + (np.random.random() * (container_width - 2 * margin - item.get("width", 0)))
        z = margin + (np.random.random() * (container_depth - 2 * margin - item.get("depth", 0)))
        
        # Place on top of existing items
        y = used_ratio * container.get("height", 100)
        
        return (float(x), float(y), float(z))
    
    def _calculate_optimal_rotation(self, item: Dict[str, Any]) -> Dict[str, float]:
        """Calculate the optimal rotation for an item to minimize space usage"""
        # Simple implementation, for a real application this could involve 
        # more complex orientation calculations
        return {"x": 0, "y": 0, "z": 0}


# Singleton instance
placement_algorithm = PlacementAlgorithm()

def find_optimal_position(item, container, db: Session) -> Dict[str, int]:
    """
    Find the optimal position to place an item in a container.
    
    Args:
        item: The item to place
        container: The container to place the item in
        db: Database session
        
    Returns:
        dict: Position information with x, y, z coordinates
    """
    logging.info(f"Finding optimal position for item {item.id} in container {container.id}")
    
    # Get item dimensions
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
    
    # Get container dimensions
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
    
    # Get items already in this container
    existing_items = db.query(db.query(type(item)).get(1).__class__).filter_by(
        container_id=container.id
    ).all()
    
    # Find optimal position (simplified for demonstration)
    position = calculate_position(
        item_width, item_depth, item_height,
        container_width, container_depth, container_height,
        existing_items
    )
    
    logging.info(f"Found position at x={position['x']}, y={position['y']}, z={position['z']}")
    return position

def calculate_position(
    item_width: int, item_depth: int, item_height: int,
    container_width: int, container_depth: int, container_height: int,
    existing_items: List
) -> Dict[str, int]:
    """
    Calculate the position for an item based on existing items in the container.
    
    This is a simplified version of the algorithm. In a real system, this would
    implement more complex 3D bin packing logic from the notebook.
    
    Args:
        item_width: Width of the item
        item_depth: Depth of the item
        item_height: Height of the item
        container_width: Width of the container
        container_depth: Depth of the container
        container_height: Height of the container
        existing_items: List of items already in the container
        
    Returns:
        dict: Position with x, y, z coordinates
    """
    # Start with default position at origin
    position = {"x": 0, "y": 0, "z": 0}
    
    # If there are existing items, find a spot that doesn't overlap
    if existing_items:
        # Find maximum x, y, z used by existing items
        max_x = max([getattr(item, 'position_x', 0) or 0 + 
                    getattr(item, 'width', 0) or getattr(item, 'width_cm', 0) or 0 
                    for item in existing_items], default=0)
        
        # Option 1: Try stacking on top (z-axis)
        # Find item directly below the potential position
        items_below = [item for item in existing_items 
                      if (getattr(item, 'position_x', 0) or 0) <= position["x"] < 
                         (getattr(item, 'position_x', 0) or 0) + (getattr(item, 'width', 0) or getattr(item, 'width_cm', 0) or 0) and
                         (getattr(item, 'position_y', 0) or 0) <= position["y"] < 
                         (getattr(item, 'position_y', 0) or 0) + (getattr(item, 'depth', 0) or getattr(item, 'depth_cm', 0) or 0)]
        
        if items_below:
            # Get the highest item below
            highest_item = max(items_below, key=lambda item: 
                              (getattr(item, 'position_z', 0) or 0) + 
                              (getattr(item, 'height', 0) or getattr(item, 'height_cm', 0) or 0))
            
            highest_z = (getattr(highest_item, 'position_z', 0) or 0) + \
                        (getattr(highest_item, 'height', 0) or getattr(highest_item, 'height_cm', 0) or 0)
            
            position["z"] = highest_z
        
        # Option 2: If stacking would exceed container height, place beside
        if position["z"] + item_height > container_height:
            position["x"] = max_x
            position["z"] = 0
            
            # If placing beside would exceed container width, place in next row
            if position["x"] + item_width > container_width:
                position["x"] = 0
                position["y"] = max([getattr(item, 'position_y', 0) or 0 + 
                                   getattr(item, 'depth', 0) or getattr(item, 'depth_cm', 0) or 0 
                                   for item in existing_items], default=0)
                
                # If placing in next row would exceed container depth, cannot place
                if position["y"] + item_depth > container_depth:
                    raise ValueError("Cannot fit item in container - no space available")
    
    # Check if the item fits at the calculated position
    if (position["x"] + item_width > container_width or
        position["y"] + item_depth > container_depth or
        position["z"] + item_height > container_height):
        raise ValueError("Cannot fit item in container - dimensions exceed container size")
    
    return position

def evaluate_placement_quality(item, container, position, db: Session) -> float:
    """
    Evaluate the quality of a placement decision.
    
    Args:
        item: The item being placed
        container: The container it's placed in
        position: The position coordinates
        db: Database session
        
    Returns:
        float: Quality score between 0.0 and 1.0
    """
    # This would implement a scoring function from the notebook
    # For now, return a placeholder score
    return 0.8 