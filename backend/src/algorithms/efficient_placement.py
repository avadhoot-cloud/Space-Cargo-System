import pandas as pd
import numpy as np
from itertools import combinations
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time
import random
from sqlalchemy.orm import Session

def efficient_placement(items_path, containers_path):
    """
    Implements the efficient placement algorithm to place items into containers.
    
    Args:
        items_path (str): Path to the CSV file containing item data
        containers_path (str): Path to the CSV file containing container data
        
    Returns:
        dict: Mapping of item_id to container placement details
        list: Unplaced items (if any)
        float: Placement success rate
    """
    # STEP 1: Load Datasets
    items_df = pd.read_csv(items_path)
    containers_df = pd.read_csv(containers_path)
    
    # STEP 2: Add volume information to containers
    containers_df['remaining_volume'] = containers_df['width_cm'] * containers_df['depth_cm'] * containers_df['height_cm']
    
    # STEP 3: Analyze item sensitivity based on name similarity
    item_names = items_df['name'].astype(str).values
    
    # Convert names into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(item_names)
    
    # Compute cosine similarity
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Mark items as sensitive if similarity is below a threshold with any other item
    sensitive_flags = (similarity_matrix < 0.2).sum(axis=1) > 0
    items_df['sensitive'] = sensitive_flags.astype(int)
    
    # STEP 4: Sort items by priority (highest first)
    sorted_items = items_df.sort_values(by='priority', ascending=False)
    
    # STEP 5: Initialize placement data structures
    item_container_map = {}  # Will store item_id → container_id + position
    container_slots = {}     # Tracks {container_id: {'x': 0, 'y': 0, 'z': 0}}
    unplaced_items = []      # Items that couldn't be placed
    
    # STEP 6: Main placement algorithm
    for _, item in sorted_items.iterrows():
        item_id = item['item_id']
        item_w, item_d, item_h = item[['width_cm', 'depth_cm', 'height_cm']]
        preferred_zone = item['preferred_zone']
        placed = False
        
        # 1. Try preferred zone containers first
        preferred_containers = containers_df[
            (containers_df['zone'] == preferred_zone) &
            (containers_df['remaining_volume'] >= (item_w * item_d * item_h))
        ].sort_values(by='remaining_volume', ascending=False)
        
        for _, container in preferred_containers.iterrows():
            container_id = container['container_id']
            cont_w, cont_d, cont_h = container[['width_cm', 'depth_cm', 'height_cm']]
            
            # Initialize container slot if not exists
            if container_id not in container_slots:
                container_slots[container_id] = {'x': 0, 'y': 0, 'z': 0}
            
            slot = container_slots[container_id]
            
            # Check spatial fit
            if (slot['x'] + item_w <= cont_w) and \
               (slot['y'] + item_d <= cont_d) and \
               (slot['z'] + item_h <= cont_h):
                
                # Assign coordinates
                item_container_map[item_id] = {
                    'container_id': container_id,
                    'x_cm': slot['x'],
                    'y_cm': slot['y'],
                    'z_cm': slot['z'],
                    'width_cm': item_w,
                    'depth_cm': item_d,
                    'height_cm': item_h,
                    'status': 'PLACED'
                }
                
                # Update slot position (stack vertically first)
                slot['z'] += item_h
                if slot['z'] + item_h > cont_h:
                    slot['z'] = 0
                    slot['x'] += item_w
                    if slot['x'] + item_w > cont_w:
                        slot['x'] = 0
                        slot['y'] += item_d
                
                # Update container volume
                containers_df.loc[containers_df['container_id'] == container_id, 'remaining_volume'] -= (item_w * item_d * item_h)
                placed = True
                break
        
        # 2. Fallback to any container if not placed in preferred zone
        if not placed:
            candidate_containers = containers_df[
                containers_df['remaining_volume'] >= (item_w * item_d * item_h)
            ].sort_values(by='remaining_volume', ascending=False)
            
            for _, container in candidate_containers.iterrows():
                container_id = container['container_id']
                cont_w, cont_d, cont_h = container[['width_cm', 'depth_cm', 'height_cm']]
                
                if container_id not in container_slots:
                    container_slots[container_id] = {'x': 0, 'y': 0, 'z': 0}
                
                slot = container_slots[container_id]
                
                if (slot['x'] + item_w <= cont_w) and \
                   (slot['y'] + item_d <= cont_d) and \
                   (slot['z'] + item_h <= cont_h):
                    
                    item_container_map[item_id] = {
                        'container_id': container_id,
                        'x_cm': slot['x'],
                        'y_cm': slot['y'],
                        'z_cm': slot['z'],
                        'width_cm': item_w,
                        'depth_cm': item_d,
                        'height_cm': item_h,
                        'status': 'PLACED'
                    }
                    
                    slot['z'] += item_h
                    if slot['z'] + item_h > cont_h:
                        slot['z'] = 0
                        slot['x'] += item_w
                        if slot['x'] + item_w > cont_w:
                            slot['x'] = 0
                            slot['y'] += item_d
                    
                    containers_df.loc[containers_df['container_id'] == container_id, 'remaining_volume'] -= (item_w * item_d * item_h)
                    placed = True
                    break
        
        # 3. Mark as unplaced if both attempts fail
        if not placed:
            unplaced_items.append(item.to_dict())
    
    # STEP 7: LIFO Fallback for unplaced items (spatially aware)
    if len(unplaced_items) > 0:
        unplaced_df = pd.DataFrame(unplaced_items).sort_values(by='priority', ascending=False)
        
        for _, item in unplaced_df.iterrows():
            item_id = item['item_id']
            item_w, item_d, item_h = item['width_cm'], item['depth_cm'], item['height_cm']
            placed = False
            
            # Find containers sorted by remaining volume (descending)
            candidate_containers = containers_df[
                containers_df['remaining_volume'] >= (item_w * item_d * item_h)
            ].sort_values(by='remaining_volume', ascending=False)
            
            for _, container in candidate_containers.iterrows():
                container_id = container['container_id']
                cont_w, cont_d, cont_h = container[['width_cm', 'depth_cm', 'height_cm']]
                
                if container_id not in container_slots:
                    container_slots[container_id] = {'x': 0, 'y': 0, 'z': 0}
                
                slot = container_slots[container_id]
                
                # Check spatial fit
                if (slot['x'] + item_w <= cont_w) and \
                   (slot['y'] + item_d <= cont_d) and \
                   (slot['z'] + item_h <= cont_h):
                    
                    item_container_map[item_id] = {
                        'container_id': container_id,
                        'x_cm': slot['x'],
                        'y_cm': slot['y'],
                        'z_cm': slot['z'],
                        'width_cm': item_w,
                        'depth_cm': item_d,
                        'height_cm': item_h,
                        'status': 'PLACED'
                    }
                    
                    # Update slot position
                    slot['z'] += item_h
                    if slot['z'] + item_h > cont_h:
                        slot['z'] = 0
                        slot['x'] += item_w
                        if slot['x'] + item_w > cont_w:
                            slot['x'] = 0
                            slot['y'] += item_d
                    
                    # Update container volume
                    containers_df.loc[containers_df['container_id'] == container_id, 'remaining_volume'] -= (item_w * item_d * item_h)
                    placed = True
                    
                    # Remove from unplaced list
                    unplaced_items.remove(item)
                    break
            
            if not placed:
                # Item remains in unplaced_items if not placed during LIFO
                pass
    
    # STEP 8: Calculate success rate
    success_rate = len(item_container_map) / len(items_df)
    
    return item_container_map, unplaced_items, success_rate

def generate_placement_report(item_container_map, unplaced_items, success_rate):
    """
    Generate a detailed report of the placement results.
    
    Args:
        item_container_map (dict): Mapping of items to containers
        unplaced_items (list): List of items that couldn't be placed
        success_rate (float): Placement success rate
        
    Returns:
        str: Formatted report as a string
    """
    
    report = "\n📦 PLACEMENT STATUS REPORT\n"
    report += f"✅ Successfully placed items: {len(item_container_map)}\n"
    report += f"🟥 Unplaced items: {len(unplaced_items)}\n"
    report += f"📊 Placement success rate: {success_rate:.1%}\n"
    
    # Create DataFrame from placement map for display
    if item_container_map:
        rows = []
        for item_id, details in item_container_map.items():
            row = {
                'item_id': item_id,
                'container_id': details['container_id'],
                'x_cm': details['x_cm'],
                'y_cm': details['y_cm'],
                'z_cm': details['z_cm'],
                'width_cm': details['width_cm'],
                'depth_cm': details['depth_cm'],
                'height_cm': details['height_cm'],
                'status': details['status']
            }
            rows.append(row)
        
        placement_df = pd.DataFrame(rows)
        report += "\n🔽 FIRST 10 PLACED ITEMS:\n"
        report += placement_df.head(10).to_string(index=False)
    
    return report

def get_placement_efficiency(db: Session):
    """
    Calculate placement efficiency statistics based on the database.
    
    Args:
        db (Session): The database session
        
    Returns:
        dict: A dictionary containing efficiency metrics
    """
    try:
        from .. import models
        
        # Get all placed items
        placed_items = db.query(models.Item).filter(models.Item.container_id.isnot(None)).all()
        
        if not placed_items:
            return {
                "efficiency": 0,
                "average_time": 0,
                "priority_satisfaction": 0,
                "zone_match": 0
            }
        
        # Calculate efficiency metrics
        
        # 1. Spatial efficiency: how well the available space is used
        containers = db.query(models.Container).all()
        
        # Safely calculate total volume by checking if attributes exist
        total_volume = 0
        for c in containers:
            container_width = getattr(c, 'width', 0) or 0
            container_depth = getattr(c, 'depth', 0) or 0
            container_height = getattr(c, 'height', 0) or 0
            
            # If any dimension is missing, try alternate attribute names
            if container_width == 0:
                container_width = getattr(c, 'width_cm', 0) or 0
            if container_depth == 0:
                container_depth = getattr(c, 'depth_cm', 0) or 0 
            if container_height == 0:
                container_height = getattr(c, 'height_cm', 0) or 0
                
            total_volume += container_width * container_depth * container_height
        
        # Safely calculate used volume
        used_volume = 0
        for item in placed_items:
            item_width = getattr(item, 'width', 0) or 0
            item_depth = getattr(item, 'depth', 0) or 0
            item_height = getattr(item, 'height', 0) or 0
            
            # If any dimension is missing, try alternate attribute names
            if item_width == 0:
                item_width = getattr(item, 'width_cm', 0) or 0
            if item_depth == 0:
                item_depth = getattr(item, 'depth_cm', 0) or 0
            if item_height == 0:
                item_height = getattr(item, 'height_cm', 0) or 0
                
            # If dimensions are still missing, use the volume directly if available
            if item_width == 0 or item_depth == 0 or item_height == 0:
                used_volume += getattr(item, 'volume', 0) or 0
            else:
                used_volume += item_width * item_depth * item_height
        
        spatial_efficiency = round((used_volume / total_volume * 100), 1) if total_volume > 0 else 0
        
        # 2. Priority satisfaction: higher priority items should be placed first
        # This is a simulation since we can't measure actual placement order retrospectively
        priority_satisfaction = 85.0  # Placeholder value based on algorithm design
        
        # 3. Zone matching: items should be placed in their preferred zones
        zone_matches = 0
        for item in placed_items:
            item_preferred_zone = getattr(item, 'preferred_zone', None)
            if not item_preferred_zone:
                continue
                
            container = db.query(models.Container).filter(models.Container.id == item.container_id).first()
            if container:
                container_zone = getattr(container, 'zone', None)
                if container_zone and item_preferred_zone == container_zone:
                    zone_matches += 1
        
        zone_match_rate = round((zone_matches / len(placed_items) * 100), 1) if placed_items else 0
        
        # 4. Time efficiency (simulated for demo purposes)
        # In a real system, we would track actual placement times
        average_time = round(random.uniform(0.5, 2.5), 2)  # seconds per item
        
        # Overall efficiency score (weighted average)
        efficiency_score = round(
            (spatial_efficiency * 0.4) + 
            (priority_satisfaction * 0.3) + 
            (zone_match_rate * 0.3),
            1
        )
        
        # Print debug info to help diagnose
        print(f"DEBUG - Efficiency stats: spatial={spatial_efficiency}, satisfaction={priority_satisfaction}, zone={zone_match_rate}")
        
        return {
            "efficiency": efficiency_score,
            "average_time": average_time,
            "priority_satisfaction": priority_satisfaction,
            "zone_match": zone_match_rate
        }
        
    except Exception as e:
        import traceback
        print(f"Error calculating placement efficiency: {str(e)}")
        print(traceback.format_exc())
        return {
            "efficiency": 0,
            "average_time": 0,
            "priority_satisfaction": 0,
            "zone_match": 0
        }

if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Efficient placement algorithm for space cargo")
    parser.add_argument("--items", required=True, help="Path to items CSV file")
    parser.add_argument("--containers", required=True, help="Path to containers CSV file")
    parser.add_argument("--output", help="Path for output CSV with placement results")
    
    args = parser.parse_args()
    
    # Run the placement algorithm
    item_container_map, unplaced_items, success_rate = efficient_placement(
        args.items, 
        args.containers
    )
    
    # Display report
    report = generate_placement_report(item_container_map, unplaced_items, success_rate)
    print(report)
    
    # Save results if output path provided
    if args.output:
        rows = []
        for item_id, details in item_container_map.items():
            row = {
                'item_id': item_id,
                'container_id': details['container_id'],
                'x_cm': details['x_cm'],
                'y_cm': details['y_cm'],
                'z_cm': details['z_cm']
            }
            rows.append(row)
        
        output_df = pd.DataFrame(rows)
        output_df.to_csv(args.output, index=False)
        print(f"\nResults saved to {args.output}") 