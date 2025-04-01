from ..models import Item, Container
from sqlalchemy.orm import Session

def find_optimal_position(item: Item, container: Container, db: Session):
    """
    Find the optimal position for an item in a container.
    This is a simple implementation - in a real system, you'd implement more
    sophisticated 3D bin packing algorithms.
    
    Returns:
        Dict with x, y, z coordinates or None if item cannot fit
    """
    # Check if item weight would exceed container capacity
    if container.current_weight + item.weight > container.max_weight:
        return None
    
    # Get all items already in the container
    existing_items = db.query(Item).filter(Item.container_id == container.id).all()
    
    # Simple 3D grid representation of the container (1 = occupied, 0 = free)
    grid = [[[0 for z in range(container.depth)] 
             for y in range(container.height)] 
             for x in range(container.width)]
    
    # Mark occupied positions
    for existing_item in existing_items:
        if all(coord is not None for coord in [existing_item.position_x, 
                                              existing_item.position_y, 
                                              existing_item.position_z]):
            # Approximate the item as a cube for simplicity
            # In a real system, you'd handle actual item dimensions
            size = int(existing_item.volume ** (1/3))  # Approximate cube size
            
            for dx in range(size):
                for dy in range(size):
                    for dz in range(size):
                        x, y, z = existing_item.position_x + dx, existing_item.position_y + dy, existing_item.position_z + dz
                        if 0 <= x < container.width and 0 <= y < container.height and 0 <= z < container.depth:
                            grid[x][y][z] = 1
    
    # Calculate approximate size of the current item (simplified as a cube)
    item_size = int(item.volume ** (1/3))
    
    # Find first available position where the item can fit
    for x in range(container.width - item_size + 1):
        for y in range(container.height - item_size + 1):
            for z in range(container.depth - item_size + 1):
                # Check if the space is free
                can_fit = True
                for dx in range(item_size):
                    for dy in range(item_size):
                        for dz in range(item_size):
                            if grid[x + dx][y + dy][z + dz] == 1:
                                can_fit = False
                                break
                    if not can_fit:
                        break
                if can_fit:
                    return {"x": x, "y": y, "z": z}
    
    # If we get here, the item couldn't fit
    return None 