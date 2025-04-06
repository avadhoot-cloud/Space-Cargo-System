"""
Placement Manager for Space Cargo System
This module orchestrates the placement algorithm process and provides main functions
for the API to interact with.
"""
from sqlalchemy.orm import Session
import logging
from . import placement_algorithm, placement_statistics, placement_utils
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PlacementManager:
    """
    Manages the placement of items in containers with improved algorithms
    for space optimization and priority-based allocation.
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
    
    def process_placement_data(self, containers, items):
        """
        Process container and item data to prepare for placement operations
        
        Args:
            containers: List of container data from CSV or database
            items: List of item data from CSV or database
            
        Returns:
            Processed containers and items ready for placement
        """
        processed_containers = []
        for container in containers:
            # Convert string dimensions to float if needed
            processed_container = self._process_container(container)
            processed_containers.append(processed_container)
        
        processed_items = []
        for item in items:
            # Convert string dimensions to float if needed
            processed_item = self._process_item(item)
            processed_items.append(processed_item)
            
        return processed_containers, processed_items
    
    def _process_container(self, container):
        """Process and normalize container data"""
        processed = container.copy()
        
        # Ensure numeric values for dimensions
        for field in ['width', 'height', 'depth', 'maxWeight']:
            if field in processed and isinstance(processed[field], str):
                try:
                    processed[field] = float(processed[field])
                except (ValueError, TypeError):
                    processed[field] = 0.0
            elif field not in processed:
                processed[field] = 0.0
                
        # Calculate volume if not present
        if 'volume' not in processed:
            processed['volume'] = processed['width'] * processed['height'] * processed['depth']
            
        # Initialize usage tracking
        processed['used_volume'] = 0.0
        processed['remainingWeight'] = processed.get('maxWeight', float('inf'))
        
        return processed
    
    def _process_item(self, item):
        """Process and normalize item data"""
        processed = item.copy()
        
        # Ensure numeric values for dimensions
        for field in ['width', 'height', 'depth', 'weight', 'priority']:
            if field in processed and isinstance(processed[field], str):
                try:
                    processed[field] = float(processed[field])
                except (ValueError, TypeError):
                    processed[field] = 0.0
            elif field not in processed:
                processed[field] = 0.0
                
        # Calculate volume if not present
        if 'volume' not in processed:
            processed['volume'] = processed['width'] * processed['height'] * processed['depth']
            
        # Set default priority if not present
        if 'priority' not in processed:
            processed['priority'] = 50.0  # Medium priority
            
        return processed
    
    def place_items_in_containers(self, containers, items):
        """
        Place items in containers using an improved algorithm
        
        Args:
            containers: List of processed container data
            items: List of processed item data
            
        Returns:
            Placement results and statistics
        """
        logger.info(f"Starting placement of {len(items)} items in {len(containers)} containers")
        
        # Sort items by priority (highest first)
        sorted_items = sorted(items, key=lambda x: -(x.get('priority', 0)))
        
        placement_results = []
        failed_placements = []
        
        # Keep track of container space usage
        container_space = {container['id']: {'container': container, 'used_volume': 0, 'positions': []} 
                         for container in containers}
        
        for item in sorted_items:
            placement = self._find_optimal_container(item, containers, container_space)
            
            if placement:
                placement_results.append(placement)
                
                # Update container space usage
                container_id = placement['container_id']
                container_space[container_id]['used_volume'] += item.get('volume', 0)
                container_space[container_id]['positions'].append({
                    'item_id': item['id'],
                    'x': placement['position_x'],
                    'y': placement['position_y'],
                    'z': placement['position_z']
                })
            else:
                failed_placements.append({
                    'item_id': item['id'],
                    'reason': 'No suitable container found'
                })
        
        # Calculate statistics
        self._calculate_placement_statistics(containers, items, placement_results, failed_placements)
        
        return {
            'placements': placement_results,
            'failed': failed_placements,
            'statistics': self.stats
        }
    
    def _find_optimal_container(self, item, containers, container_space):
        """
        Find the optimal container for an item
        
        Args:
            item: Item to place
            containers: Available containers
            container_space: Current space usage in containers
            
        Returns:
            Placement data if a container is found, None otherwise
        """
        compatible_containers = []
        
        for container in containers:
            # Skip if container is full
            if container_space[container['id']]['used_volume'] + item.get('volume', 0) > container.get('volume', 0):
                continue
                
            # Check if item dimensions fit in container
            if not self._item_fits_container(item, container):
                continue
                
            # Calculate compatibility score
            score = self._calculate_compatibility_score(item, container, container_space[container['id']])
            compatible_containers.append({
                'container': container,
                'score': score
            })
        
        if not compatible_containers:
            logger.warning(f"No compatible container found for item {item.get('name', 'unknown')}")
            return None
            
        # Choose the container with the highest score
        compatible_containers.sort(key=lambda x: x['score'], reverse=True)
        best_container = compatible_containers[0]['container']
        
        # Calculate position in container
        position = self._calculate_position(item, best_container, container_space[best_container['id']]['positions'])
        
        return {
            'item_id': item['id'],
            'container_id': best_container['id'],
            'position_x': position[0],
            'position_y': position[1],
            'position_z': position[2],
            'placement_date': datetime.now().isoformat(),
            'score': compatible_containers[0]['score']
        }
    
    def _item_fits_container(self, item, container):
        """Check if item dimensions fit in container"""
        # Check if each dimension fits (allowing for rotation)
        item_dims = [item.get('width', 0), item.get('height', 0), item.get('depth', 0)]
        container_dims = [container.get('width', 0), container.get('height', 0), container.get('depth', 0)]
        
        # Try all possible orientations
        for perm in self._get_permutations(item_dims):
            if all(perm[i] <= container_dims[i] for i in range(3)):
                return True
                
        return False
    
    def _get_permutations(self, dims):
        """Get all possible orientations of an item"""
        return [
            [dims[0], dims[1], dims[2]],
            [dims[0], dims[2], dims[1]],
            [dims[1], dims[0], dims[2]],
            [dims[1], dims[2], dims[0]],
            [dims[2], dims[0], dims[1]],
            [dims[2], dims[1], dims[0]]
        ]
    
    def _calculate_compatibility_score(self, item, container, space_info):
        """Calculate how suitable a container is for an item"""
        score = 0
        
        # 1. Space utilization (30%)
        remaining_volume = container.get('volume', 0) - space_info['used_volume']
        volume_ratio = item.get('volume', 0) / max(remaining_volume, 0.001)  # Avoid division by zero
        
        # Prefer containers where the item uses more of the available space
        # but not too much to leave some buffer
        space_score = 30 * (1 - abs(volume_ratio - 0.7))
        score += space_score
        
        # 2. Zone preference (25%)
        if 'preferredZone' in item and item['preferredZone'] == container.get('zone'):
            score += 25
        
        # 3. Accessibility (20%)
        # Items in less filled containers are more accessible
        fill_ratio = space_info['used_volume'] / max(container.get('volume', 0.001), 0.001)
        accessibility_score = 20 * (1 - fill_ratio)
        score += accessibility_score
        
        # 4. Priority alignment (15%)
        # High priority items should be placed in more accessible containers
        priority_score = 15 * (item.get('priority', 50) / 100) * (1 - fill_ratio)
        score += priority_score
        
        # 5. Item expiration consideration (10%)
        # If the item has an expiry date, prefer containers with better accessibility
        if 'expiryDate' in item and item['expiryDate']:
            score += 10 * (1 - fill_ratio)
        
        return score
    
    def _calculate_position(self, item, container, existing_positions):
        """
        Calculate the optimal position for the item in the container
        
        Uses a simplified First-Fit Decreasing (FFD) approach for 3D bin packing
        """
        # This is a simplified implementation - real production code would 
        # use a proper 3D bin packing algorithm
        
        # For simplicity, assume items are stacked from the bottom up
        # Using the existing positions to avoid overlaps
        
        container_dims = [
            container.get('width', 0),
            container.get('height', 0),
            container.get('depth', 0)
        ]
        
        item_dims = [
            item.get('width', 0),
            item.get('height', 0),
            item.get('depth', 0)
        ]
        
        # If no existing positions, place at the bottom corner
        if not existing_positions:
            return (0, 0, 0)
        
        # Simple stacking strategy: place item at the "highest" point
        # In a real implementation, this would be much more sophisticated
        highest_y = max([pos['y'] + item_dims[1] for pos in existing_positions])
        
        # Make sure the item is within container bounds
        highest_y = min(highest_y, container_dims[1] - item_dims[1])
        
        # Random x,z position (keeping item within container bounds)
        max_x = container_dims[0] - item_dims[0]
        max_z = container_dims[2] - item_dims[2]
        
        x = np.random.uniform(0, max(max_x, 0))
        z = np.random.uniform(0, max(max_z, 0))
        
        return (float(x), float(highest_y), float(z))
    
    def _calculate_placement_statistics(self, containers, items, placements, failed_placements):
        """Calculate comprehensive statistics about the placement process"""
        # Total items and placement success rate
        total_items = len(items)
        placed_items = len(placements)
        
        if total_items > 0:
            success_rate = (placed_items / total_items) * 100
        else:
            success_rate = 0
            
        # Space utilization
        total_container_volume = sum(container.get('volume', 0) for container in containers)
        total_item_volume = sum(item.get('volume', 0) for item in items 
                               if item['id'] in [p['item_id'] for p in placements])
        
        if total_container_volume > 0:
            space_utilization = (total_item_volume / total_container_volume) * 100
        else:
            space_utilization = 0
            
        # Zone match rate
        zone_matches = 0
        for placement in placements:
            item = next((i for i in items if i['id'] == placement['item_id']), None)
            container = next((c for c in containers if c['id'] == placement['container_id']), None)
            
            if item and container and 'preferredZone' in item and container.get('zone') == item['preferredZone']:
                zone_matches += 1
                
        if placed_items > 0:
            zone_match_rate = (zone_matches / placed_items) * 100
        else:
            zone_match_rate = 0
            
        # Priority satisfaction (how well high-priority items were placed)
        priority_satisfaction = 0
        if placed_items > 0:
            placed_item_objects = [next((i for i in items if i['id'] == p['item_id']), None) for p in placements]
            placed_item_objects = [i for i in placed_item_objects if i is not None]
            
            if placed_item_objects:
                # Average priority of placed items compared to all items
                avg_placed_priority = sum(item.get('priority', 0) for item in placed_item_objects) / len(placed_item_objects)
                avg_all_priority = sum(item.get('priority', 0) for item in items) / len(items)
                
                # Higher is better (1.0 means all high priority items were placed first)
                priority_ratio = avg_placed_priority / max(avg_all_priority, 1)
                priority_satisfaction = min(priority_ratio * 100, 100)
        
        # Calculate overall efficiency
        efficiency = (
            (success_rate * 0.3) +
            (space_utilization * 0.3) +
            (zone_match_rate * 0.2) +
            (priority_satisfaction * 0.2)
        )
        
        # Update statistics
        self.stats = {
            "totalItemsPlaced": placed_items,
            "spaceUtilization": round(space_utilization, 2),
            "successRate": round(success_rate, 2),
            "efficiency": round(efficiency, 2),
            "prioritySatisfaction": round(priority_satisfaction, 2),
            "zoneMatchRate": round(zone_match_rate, 2)
        }
        
        return self.stats
    
    def get_placement_statistics(self):
        """Get current placement statistics"""
        return self.stats

# Singleton instance for use in routers and other modules
placement_manager = PlacementManager()

def process_placement_data(db: Session):
    """
    Process placement data in the database and generate statistics.
    
    Args:
        db (Session): Database session
        
    Returns:
        dict: Combined placement statistics
    """
    try:
        logging.info("Processing placement data")
        
        # Get items and containers from the database
        items, containers = placement_utils.get_items_and_containers_from_db(db)
        
        if not items or not containers:
            logging.warning("No items or containers found in database")
            return placement_statistics.get_empty_statistics()
        
        # Generate statistics about placements
        basic_stats = placement_statistics.generate_basic_statistics(db, items, containers)
        efficiency_stats = placement_statistics.calculate_efficiency_metrics(db, items, containers)
        
        # Combine all statistics
        combined_stats = {**basic_stats, **efficiency_stats}
        
        # Get container utilization information
        container_stats = placement_statistics.get_container_utilization(db, containers)
        combined_stats["containerUtilization"] = container_stats
        
        logging.info(f"Successfully processed placement data: {combined_stats}")
        return combined_stats
        
    except Exception as e:
        logging.error(f"Error in process_placement_data: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        raise

def place_item(db: Session, item_id: int, container_id: int):
    """
    Place an item in a container using the placement algorithm.
    
    Args:
        db (Session): Database session
        item_id (int): ID of the item to place
        container_id (int): ID of the target container
        
    Returns:
        dict: Placement result containing position information
    """
    try:
        # Get item and container
        item, container = placement_utils.get_item_and_container(db, item_id, container_id)
        
        # Use placement algorithm to find optimal position
        position = placement_algorithm.find_optimal_position(item, container, db)
        
        # Update database with placement information
        placement_utils.update_placement_in_db(db, item, container, position)
        
        return {
            "success": True,
            "item": item,
            "position": position
        }
        
    except Exception as e:
        logging.error(f"Error in place_item: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        raise

def get_placement_statistics(db: Session) -> Dict[str, Any]:
    """
    Get statistics about placement algorithm performance.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        Dictionary with placement statistics
    """
    try:
        logging.info("Getting placement statistics")
        
        # Get all containers and items from the database
        from ..crud import container_crud, item_crud
        
        containers = container_crud.get_containers(db)
        items = item_crud.get_items(db)
        
        # If there's no data, return empty statistics
        if not containers or not items:
            logging.warning("No containers or items found, returning empty statistics")
            return placement_statistics.get_empty_statistics()
        
        # Generate basic statistics
        basic_stats = placement_statistics.generate_basic_statistics(db, items, containers)
        
        # Calculate efficiency metrics
        efficiency_metrics = placement_statistics.calculate_efficiency_metrics(db, items, containers)
        
        # Get container utilization
        container_utilization = placement_statistics.get_container_utilization(db, containers)
        
        # Combine all statistics
        stats = {**basic_stats, **efficiency_metrics, "containerUtilization": container_utilization}
        
        logging.info(f"Placement statistics: {stats}")
        return stats
        
    except Exception as e:
        logging.error(f"Error getting placement statistics: {str(e)}", exc_info=True)
        # Return empty statistics on error
        return placement_statistics.get_empty_statistics() 