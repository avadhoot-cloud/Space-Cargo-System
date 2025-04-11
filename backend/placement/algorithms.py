# Place this in your backend/placement/algorithms.py file

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

class PlacementManager:
    def __init__(self):
        self.data_dir = getattr(settings, 'DATA_DIR', Path(__file__).resolve().parent.parent.parent / 'data')
        self.data_dir.mkdir(exist_ok=True)
        
    def load_from_csv(self, items_path=None, containers_path=None):
        """Load data from CSV files in the data directory."""
        if not items_path:
            items_path = self.data_dir / 'input_items.csv'
        if not containers_path:
            containers_path = self.data_dir / 'containers.csv'
        
        print(f"DEBUG: Looking for items at {items_path}")
        print(f"DEBUG: Looking for containers at {containers_path}")
        
        if not items_path.exists() or not containers_path.exists():
            logger.warning(f"CSV files not found: {items_path} or {containers_path}")
            print(f"DEBUG: CSV files not found: {items_path} or {containers_path}")
            return None, None
        
        try:
            # Load items data
            items_df = pd.read_csv(items_path)
            print(f"DEBUG: Loaded items: {len(items_df)} items")
            print(f"DEBUG: Items columns: {items_df.columns.tolist()}")
            print(f"DEBUG: First few items: {items_df.head().to_dict()}")
            
            # Check if mass_kg exists but weight_kg doesn't, and rename if needed
            if 'mass_kg' in items_df.columns and 'weight_kg' not in items_df.columns:
                print(f"DEBUG: Renaming mass_kg to weight_kg")
                items_df = items_df.rename(columns={'mass_kg': 'weight_kg'})
            
            # Ensure required columns exist
            required_item_columns = ['item_id', 'name', 'width_cm', 'height_cm', 'depth_cm', 'weight_kg']
            for col in required_item_columns:
                if col not in items_df.columns:
                    logger.error(f"Missing required column in items CSV: {col}")
                    print(f"DEBUG: Missing required column in items CSV: {col}")
                    return None, None
            
            # Load containers data
            containers_df = pd.read_csv(containers_path)
            print(f"DEBUG: Loaded containers: {len(containers_df)} containers")
            print(f"DEBUG: Containers columns: {containers_df.columns.tolist()}")
            print(f"DEBUG: First few containers: {containers_df.head().to_dict()}")
            
            # Ensure required columns exist
            required_container_columns = ['container_id', 'width_cm', 'height_cm', 'depth_cm', 'zone']
            for col in required_container_columns:
                if col not in containers_df.columns:
                    logger.error(f"Missing required column in containers CSV: {col}")
                    print(f"DEBUG: Missing required column in containers CSV: {col}")
                    return None, None
            
            # Add max_weight_kg if missing
            if 'max_weight_kg' not in containers_df.columns:
                print(f"DEBUG: Adding max_weight_kg column with default value 1000")
                containers_df['max_weight_kg'] = 1000
            
            # Add container name if missing
            if 'name' not in containers_df.columns:
                print(f"DEBUG: Adding name column based on container_id")
                containers_df['name'] = containers_df['container_id'].apply(lambda x: f"Container {x}")
            
            # Calculate volumes
            items_df['volume'] = items_df['width_cm'] * items_df['height_cm'] * items_df['depth_cm']
            containers_df['volume'] = containers_df['width_cm'] * containers_df['height_cm'] * containers_df['depth_cm']
            
            # Add remaining_volume to containers
            containers_df['remaining_volume'] = containers_df['volume']
            
            # Handle missing expiry dates and convert to datetime
            if 'expiry_date' in items_df.columns:
                items_df['expiry_date'] = pd.to_datetime(items_df['expiry_date'], errors='coerce')
            
            # Calculate sensitivity based on name similarity if not present
            if 'sensitive' not in items_df.columns:
                items_df = self.calculate_sensitivity(items_df)
            
            return items_df, containers_df
        except Exception as e:
            logger.error(f"Error loading CSV files: {str(e)}")
            print(f"DEBUG: Error loading CSV files: {str(e)}")
            return None, None
    
    def preprocess_data(self, items_df, containers_df):
        """Preprocess items and containers data."""
        # Standardize column names
        if 'mass_kg' in items_df.columns and 'weight_kg' not in items_df.columns:
            items_df = items_df.rename(columns={'mass_kg': 'weight_kg'})
        
        # Calculate volumes
        items_df['volume'] = items_df['width_cm'] * items_df['depth_cm'] * items_df['height_cm']
        containers_df['volume'] = containers_df['width_cm'] * containers_df['depth_cm'] * containers_df['height_cm']
        
        # Add remaining_volume to containers
        containers_df['remaining_volume'] = containers_df['volume']
        
        # Handle missing expiry dates and convert to datetime
        if 'expiry_date' in items_df.columns:
            items_df['expiry_date'] = pd.to_datetime(items_df['expiry_date'], errors='coerce')
        else:
            items_df['expiry_date'] = pd.NaT  # Add empty expiry date column
        
        # Calculate sensitivity based on name similarity
        items_df = self.calculate_sensitivity(items_df)
        
        return items_df, containers_df
    
    def calculate_sensitivity(self, items_df):
        """Calculate item sensitivity based on name similarity."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        item_names = items_df['name'].astype(str).values
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(item_names)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        sensitive_flags = (similarity_matrix < 0.2).sum(axis=1) > 0
        items_df['sensitive'] = sensitive_flags.astype(int)
        return items_df
    
    def place_items(self, items_df=None, containers_df=None):
        """Place items into containers using the efficient placement algorithm."""
        # If dataframes not provided, load from CSV
        if items_df is None or containers_df is None:
            items_df, containers_df = self.load_from_csv()
            
        if items_df is None or containers_df is None:
            return None, None
        
        # Preprocess data
        items_df, containers_df = self.preprocess_data(items_df, containers_df)
        
        # Sort items by priority (highest first), then by expiry date (closest first)
        sorted_items = items_df.copy()
        if 'priority' in sorted_items.columns:
            sorted_items = sorted_items.sort_values(by='priority', ascending=False)
        
        # Initialize containers and results
        container_data = {c_id: {'items': [], 'volume_used': 0, 'weight_used': 0} 
                         for c_id in containers_df['container_id']}
        
        placements = []
        unplaced_items = []
        
        # First pass: place items in their preferred zones
        for _, item in sorted_items.iterrows():
            item_id = item.get('item_id')
            preferred_zone = item.get('preferred_zone')
            
            # Skip if no preferred zone
            if pd.isna(preferred_zone):
                continue
                
            # Get containers in the preferred zone
            zone_containers = containers_df[containers_df['zone'] == preferred_zone]
            
            placed = False
            for _, container in zone_containers.iterrows():
                container_id = container['container_id']
                container_data_entry = container_data[container_id]
                
                # Check if item can fit (volume and weight)
                item_volume = item['width_cm'] * item['depth_cm'] * item['height_cm']
                item_weight = item.get('weight_kg', 0)
                
                if (container['volume'] - container_data_entry['volume_used'] >= item_volume and
                    container.get('max_weight_kg', float('inf')) - container_data_entry['weight_used'] >= item_weight):
                    
                    # Calculate position (simple stacking for now)
                    current_items = container_data_entry['items']
                    position = (0, 0, 0)  # Default position at origin
                    
                    if current_items:
                        # Simple stacking: place on top of the highest item
                        max_height = 0
                        for prev_item in current_items:
                            if prev_item['position'][2] + prev_item['height'] > max_height:
                                max_height = prev_item['position'][2] + prev_item['height']
                        position = (0, 0, max_height)
                    
                    # Add item to container
                    container_data_entry['items'].append({
                        'item_id': item_id,
                        'width': item['width_cm'],
                        'depth': item['depth_cm'],
                        'height': item['height_cm'],
                        'weight': item_weight,
                        'priority': item.get('priority', 0),
                        'position': position
                    })
                    
                    container_data_entry['volume_used'] += item_volume
                    container_data_entry['weight_used'] += item_weight
                    
                    # Record placement
                    placements.append({
                        'item_id': item_id,
                        'container_id': container_id,
                        'x_cm': position[0],
                        'y_cm': position[1],
                        'z_cm': position[2],
                        'width_cm': item['width_cm'],
                        'depth_cm': item['depth_cm'],
                        'height_cm': item['height_cm']
                    })
                    
                    placed = True
                    break
            
            if not placed:
                unplaced_items.append(item_id)
        
        # Second pass: place remaining items in any container
        remaining_items = sorted_items[sorted_items['item_id'].isin(unplaced_items)]
        unplaced_items = []  # Reset for second pass
        
        for _, item in remaining_items.iterrows():
            item_id = item.get('item_id')
            
            placed = False
            for _, container in containers_df.iterrows():
                container_id = container['container_id']
                container_data_entry = container_data[container_id]
                
                # Check if item can fit
                item_volume = item['width_cm'] * item['depth_cm'] * item['height_cm']
                item_weight = item.get('weight_kg', 0)
                
                if (container['volume'] - container_data_entry['volume_used'] >= item_volume and
                    container.get('max_weight_kg', float('inf')) - container_data_entry['weight_used'] >= item_weight):
                    
                    # Calculate position
                    current_items = container_data_entry['items']
                    position = (0, 0, 0)
                    
                    if current_items:
                        max_height = 0
                        for prev_item in current_items:
                            if prev_item['position'][2] + prev_item['height'] > max_height:
                                max_height = prev_item['position'][2] + prev_item['height']
                        position = (0, 0, max_height)
                    
                    # Add item to container
                    container_data_entry['items'].append({
                        'item_id': item_id,
                        'width': item['width_cm'],
                        'depth': item['depth_cm'],
                        'height': item['height_cm'],
                        'weight': item_weight,
                        'priority': item.get('priority', 0),
                        'position': position
                    })
                    
                    container_data_entry['volume_used'] += item_volume
                    container_data_entry['weight_used'] += item_weight
                    
                    # Record placement
                    placements.append({
                        'item_id': item_id,
                        'container_id': container_id,
                        'x_cm': position[0],
                        'y_cm': position[1],
                        'z_cm': position[2],
                        'width_cm': item['width_cm'],
                        'depth_cm': item['depth_cm'],
                        'height_cm': item['height_cm']
                    })
                    
                    placed = True
                    break
            
            if not placed:
                unplaced_items.append(item_id)
        
        # Create DataFrames from results
        placements_df = pd.DataFrame(placements)
        unplaced_df = sorted_items[sorted_items['item_id'].isin(unplaced_items)]
        
        # Save results to CSV
        if not placements_df.empty:
            placements_df.to_csv(self.data_dir / 'placed_items.csv', index=False)
        
        if not unplaced_df.empty:
            unplaced_df.to_csv(self.data_dir / 'unplaced_items.csv', index=False)
        
        return placements_df, unplaced_df
    
    def get_placement_efficiency(self):
        """Calculate the efficiency metrics of current placement arrangement."""
        try:
            print("DEBUG: Starting get_placement_efficiency")
            # Load data
            items_df, containers_df = self.load_from_csv()
            if items_df is None or containers_df is None:
                print("DEBUG: Failed to load items or containers data")
                return {
                    "success": False,
                    "message": "Failed to load data from CSV files",
                    "statistics": {}
                }
            
            # Load placement results
            placements_df, unplaced_df = self.load_results()
            print(f"DEBUG: Placements: {placements_df}")
            # Calculate basic metrics
            total_items = len(items_df)
            print(f"DEBUG: Total items: {total_items}")
            placed_items = len(placements_df) if placements_df is not None else 0
            print(f"DEBUG: Placed items: {placed_items}")
            unplaced_items = total_items - placed_items
            print(f"DEBUG: Unplaced items: {unplaced_items}")
            
            # Calculate placement rate
            placement_rate = (placed_items / total_items * 100) if total_items > 0 else 0
            print(f"DEBUG: Placement rate: {placement_rate}%")
            
            # Calculate volume utilization
            total_container_volume = containers_df['volume'].sum()
            print(f"DEBUG: Total container volume: {total_container_volume}")
            used_volume = 0
            container_utilization = []
            
            if placements_df is not None and not placements_df.empty:
                # Fix: Convert container_id to string if needed to ensure type matching
                if 'container_id' in placements_df.columns:
                    placements_df['container_id'] = placements_df['container_id'].astype(str)
                
                # Calculate the total volume used by all placed items
                for _, item in placements_df.iterrows():
                    item_volume = item['width_cm'] * item['depth_cm'] * item['height_cm']
                    used_volume += item_volume
                    print(f"DEBUG: Added item volume: {item_volume}, total used volume now: {used_volume}")
                
                # Process each container
                for _, container in containers_df.iterrows():
                    container_id = str(container['container_id'])
                    container_volume = container['volume']
                    print(f"DEBUG: Processing container {container_id} with volume {container_volume}")
                    
                    # Find items in this container
                    container_items = placements_df[placements_df['container_id'].astype(str) == container_id]
                    print(f"DEBUG: Container {container_id} has {len(container_items)} items")
                    
                    # Calculate volume used in this container
                    container_used_volume = 0
                    for _, item in container_items.iterrows():
                        item_volume = item['width_cm'] * item['depth_cm'] * item['height_cm']
                        container_used_volume += item_volume
                        print(f"DEBUG: Item volume: {item_volume}, container used volume now: {container_used_volume}")
                    
                    # Calculate utilization for this container
                    container_util = (container_used_volume / container_volume * 100) if container_volume > 0 else 0
                    print(f"DEBUG: Container {container_id} used volume: {container_used_volume}")
                    print(f"DEBUG: Container {container_id} utilization: {container_util}%")
                    
                    container_utilization.append({
                        "container_id": container_id,
                        "name": container.get('name', f"Container {container_id}"),
                        "zone": container['zone'],
                        "volume_cm3": float(container_volume),
                        "used_volume_cm3": float(container_used_volume),
                        "utilization_percent": float(container_util)
                    })
            else:
                # If no placements, set all containers to 0 utilization
                for _, container in containers_df.iterrows():
                    container_id = str(container['container_id'])
                    container_volume = container['volume']
                    container_utilization.append({
                        "container_id": container_id,
                        "name": container.get('name', f"Container {container_id}"),
                        "zone": container['zone'],
                        "volume_cm3": float(container_volume),
                        "used_volume_cm3": 0.0,
                        "utilization_percent": 0.0
                    })
            
            # Calculate overall volume utilization
            volume_utilization = (used_volume / total_container_volume * 100) if total_container_volume > 0 else 0
            print(f"DEBUG: Overall volume utilization: {volume_utilization}%")
            
            result = {
                "success": True,
                "statistics": {
                    "total_items": int(total_items),
                    "placed_items": int(placed_items),
                    "unplaced_items": int(unplaced_items),
                    "placement_rate_percent": float(placement_rate),
                    "volume_utilization_percent": float(volume_utilization),
                    "total_container_volume_cm3": float(total_container_volume),
                    "used_volume_cm3": float(used_volume),
                    "container_utilization": container_utilization
                }
            }
            print(f"DEBUG: Returning result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error calculating placement efficiency: {str(e)}")
            print(f"DEBUG: Error calculating placement efficiency: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Error calculating statistics: {str(e)}",
                "statistics": {}
            }
    
    def load_results(self):
        """Load placement results from CSV files."""
        # Check both possible filenames for placements
        placed_path = self.data_dir / 'placed_items.csv'
        alt_placed_path = self.data_dir / 'placement_results.csv'
        unplaced_path = self.data_dir / 'unplaced_items.csv'
        
        print(f"DEBUG: Looking for placed items at {placed_path} or {alt_placed_path}")
        print(f"DEBUG: Looking for unplaced items at {unplaced_path}")
        
        placements_df = None
        unplaced_df = None
        
        # First try the original filename
        if placed_path.exists():
            try:
                placements_df = pd.read_csv(placed_path)
                print(f"DEBUG: Loaded placed items from {placed_path}: {len(placements_df)} items")
                print(f"DEBUG: Placed items columns: {placements_df.columns.tolist()}")
                print(f"DEBUG: First few placed items: {placements_df.head().to_dict()}")
            except Exception as e:
                logger.error(f"Error loading placed items from {placed_path}: {str(e)}")
                print(f"DEBUG: Error loading placed items from {placed_path}: {str(e)}")
        
        # If not found, try the alternative filename
        elif alt_placed_path.exists():
            try:
                placements_df = pd.read_csv(alt_placed_path)
                print(f"DEBUG: Loaded placed items from {alt_placed_path}: {len(placements_df)} items")
                print(f"DEBUG: Placed items columns: {placements_df.columns.tolist()}")
                print(f"DEBUG: First few placed items: {placements_df.head().to_dict()}")
            except Exception as e:
                logger.error(f"Error loading placed items from {alt_placed_path}: {str(e)}")
                print(f"DEBUG: Error loading placed items from {alt_placed_path}: {str(e)}")
        else:
            print(f"DEBUG: Placed items file not found at {placed_path} or {alt_placed_path}")
        
        if unplaced_path.exists():
            try:
                unplaced_df = pd.read_csv(unplaced_path)
                print(f"DEBUG: Loaded unplaced items: {len(unplaced_df)} items")
                print(f"DEBUG: Unplaced items columns: {unplaced_df.columns.tolist()}")
                print(f"DEBUG: First few unplaced items: {unplaced_df.head().to_dict()}")
            except Exception as e:
                logger.error(f"Error loading unplaced items: {str(e)}")
                print(f"DEBUG: Error loading unplaced items: {str(e)}")
        else:
            print(f"DEBUG: Unplaced items file not found at {unplaced_path}")
        
        return placements_df, unplaced_df
    
    def get_recommendations(self):
        """Get placement recommendations for unplaced items."""
        items_df, containers_df = self.load_from_csv()
        placements_df, unplaced_df = self.load_results()
        
        if items_df is None or containers_df is None or unplaced_df is None or unplaced_df.empty:
            return []
        
        recommendations = []
        
        for _, item in unplaced_df.iterrows():
            item_id = item['item_id']
            item_volume = item['width_cm'] * item['depth_cm'] * item['height_cm']
            preferred_zone = item.get('preferred_zone')
            
            # First try preferred zone
            best_container_id = None
            best_utilization = float('inf')
            best_reasoning = ""
            zone_match = False
            
            # Filter containers that can fit the item
            valid_containers = []
            
            for _, container in containers_df.iterrows():
                container_id = container['container_id']
                container_volume = container['volume']
                container_zone = container['zone']
                
                # Calculate current utilization
                current_utilization = 0
                if placements_df is not None:
                    container_placements = placements_df[placements_df['container_id'] == container_id]
                    for _, placement in container_placements.iterrows():
                        current_utilization += placement['width_cm'] * placement['depth_cm'] * placement['height_cm']
                
                remaining_volume = container_volume - current_utilization
                
                if remaining_volume >= item_volume:
                    valid_containers.append({
                        'container_id': container_id,
                        'container_name': container.get('name', f"Container {container_id}"),
                        'zone': container_zone,
                        'remaining_volume': remaining_volume,
                        'utilization': current_utilization / container_volume if container_volume > 0 else 0
                    })
            
            # Find best container
            if valid_containers:
                # First try preferred zone
                preferred_containers = [c for c in valid_containers if c['zone'] == preferred_zone]
                
                if preferred_containers:
                    # Sort by utilization (choose one with highest utilization to maximize space efficiency)
                    preferred_containers.sort(key=lambda x: x['utilization'], reverse=True)
                    best_container = preferred_containers[0]
                    best_container_id = best_container['container_id']
                    best_reasoning = f"Container is in the preferred zone ({preferred_zone})"
                    zone_match = True
                else:
                    # Sort all containers by remaining volume (choose smallest that can fit)
                    valid_containers.sort(key=lambda x: x['remaining_volume'])
                    best_container = valid_containers[0]
                    best_container_id = best_container['container_id']
                    best_reasoning = f"No containers available in preferred zone ({preferred_zone}). Selected container in zone {best_container['zone']} with sufficient space."
            
            if best_container_id:
                score = 100 if zone_match else 70
                recommendations.append({
                    "item_id": item_id,
                    "item_name": item['name'],
                    "container_id": best_container_id,
                    "container_name": next((c['container_name'] for c in valid_containers if c['container_id'] == best_container_id), ""),
                    "reasoning": best_reasoning,
                    "score": score
                })
        
        # Sort recommendations by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
    
    def identify_waste(self):
        """Identify expired items and items with zero uses left."""
        print("DEBUG: identify_waste called")
        items_df, _ = self.load_from_csv()
        
        # Try to load placement data directly from CSV files
        placed_path = self.data_dir / 'placed_items.csv'
        print(f"DEBUG: Looking for placed items at {placed_path}")
        
        placements_df = None
        if placed_path.exists():
            try:
                placements_df = pd.read_csv(placed_path)
                print(f"DEBUG: Loaded placed items: {len(placements_df)} items")
            except Exception as e:
                print(f"DEBUG: Error loading placed items: {str(e)}")
                logger.error(f"Error loading placed items: {str(e)}")
        
        if items_df is None or placements_df is None:
            print("DEBUG: No items or placements data found")
            return []
        
        waste_items = []
        today = datetime.now().date()
        print(f"DEBUG: Today's date: {today}")
        
        for _, item in items_df.iterrows():
            item_id = item['item_id']
            
            # Check if item is placed
            if placements_df is not None and item_id in placements_df['item_id'].values:
                placement = placements_df[placements_df['item_id'] == item_id].iloc[0]
                container_id = placement['container_id']
                position = (placement['x_cm'], placement['y_cm'], placement['z_cm'])
                
                should_add = False
                reason = ""
                
                # Check expiry date if column exists
                if 'expiry_date' in items_df.columns and pd.notna(item.get('expiry_date')):
                    try:
                        expiry_date = pd.to_datetime(item['expiry_date']).date()
                        print(f"DEBUG: Item {item_id} expiry date: {expiry_date}")
                        if expiry_date <= today:
                            should_add = True
                            reason = "Expired"
                    except Exception as e:
                        print(f"DEBUG: Error processing expiry date for item {item_id}: {str(e)}")
                
                # Check usage limit if column exists
                if 'usage_limit' in items_df.columns and pd.notna(item.get('usage_limit')):
                    if int(item['usage_limit']) <= 0:
                        should_add = True
                        reason = "Out of Uses"
                
                if should_add:
                    print(f"DEBUG: Adding item {item_id} as waste with reason: {reason}")
                    waste_items.append({
                        "item_id": item_id,
                        "name": item['name'],
                        "reason": reason,
                        "containerId": container_id,
                        "position": {
                            "startCoordinates": {
                                "width": position[0],
                                "depth": position[1],
                                "height": position[2]
                            },
                            "endCoordinates": {
                                "width": position[0] + item['width_cm'],
                                "depth": position[1] + item['depth_cm'],
                                "height": position[2] + item['height_cm']
                            }
                        }
                    })
        
        print(f"DEBUG: Found {len(waste_items)} waste items")
        return waste_items
    
    def simulate_days(self, num_days, items_to_use=None):
        """Simulate the passage of time and track expiration and usage."""
        items_df, _ = self.load_from_csv()
        
        if items_df is None:
            return {
                "success": False,
                "message": "No items data found"
            }
        
        # Convert today's date
        today = datetime.now()
        new_date = today + timedelta(days=num_days)
        
        # Track changes
        items_used = []
        items_expired = []
        items_depleted = []
        
        # Get copies to modify
        modified_items = items_df.copy()
        
        # Process item usage
        if items_to_use:
            for item_to_use in items_to_use:
                item_id = item_to_use.get('item_id')
                if item_id:
                    # Find the item in the dataframe
                    item_idx = modified_items[modified_items['item_id'] == item_id].index
                    
                    if not item_idx.empty:
                        idx = item_idx[0]
                        # Reduce usage limit if it exists
                        if 'usage_limit' in modified_items.columns:
                            current_uses = modified_items.at[idx, 'usage_limit']
                            
                            if pd.notna(current_uses) and current_uses > 0:
                                # Decrement usage
                                modified_items.at[idx, 'usage_limit'] = current_uses - 1
                                
                                items_used.append({
                                    "item_id": item_id,
                                    "name": modified_items.at[idx, 'name'],
                                    "remaining_uses": current_uses - 1
                                })
                                
                                # Check if depleted
                                if current_uses - 1 == 0:
                                    items_depleted.append({
                                        "item_id": item_id,
                                        "name": modified_items.at[idx, 'name']
                                    })
        
        # Process expirations
        for idx, item in modified_items.iterrows():
            if 'expiry_date' in item and pd.notna(item['expiry_date']):
                try:
                    expiry_date = pd.to_datetime(item['expiry_date']).date()
                    new_date_only = new_date.date()
                    
                    # Today < expiry date <= new date
                    if today.date() < expiry_date <= new_date_only:
                        items_expired.append({
                            "item_id": item['item_id'],
                            "name": item['name']
                        })
                except:
                    pass
        
        # Save modified items back to CSV
        modified_items.to_csv(self.data_dir / 'input_items.csv', index=False)
        
        return {
            "success": True,
            "newDate": new_date.strftime('%Y-%m-%d'),
            "changes": {
                "itemsUsed": items_used,
                "itemsExpired": items_expired,
                "itemsDepletedToday": items_depleted
            }
        }
    
    def generate_log(self, action_type, user_id, item_id, details=None):
        """Generate a log entry for an action."""
        log_path = self.data_dir / 'action_logs.csv'
        
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': user_id,
            'action_type': action_type,
            'item_id': item_id,
            'details': str(details) if details else ''
        }
        
        # Create or append to log file
        if not log_path.exists():
            log_df = pd.DataFrame([log_entry])
            log_df.to_csv(log_path, index=False)
        else:
            log_df = pd.read_csv(log_path)
            log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
            log_df.to_csv(log_path, index=False)
        
        return log_entry
    
    def get_logs(self, start_date=None, end_date=None, item_id=None, user_id=None, action_type=None):
        """Get logs filtered by various criteria."""
        log_path = self.data_dir / 'action_logs.csv'
        
        if not log_path.exists():
            return []
        
        try:
            log_df = pd.read_csv(log_path)
            
            # Apply filters
            if start_date:
                log_df = log_df[log_df['timestamp'] >= start_date]
            
            if end_date:
                log_df = log_df[log_df['timestamp'] <= end_date]
            
            if item_id:
                log_df = log_df[log_df['item_id'] == item_id]
            
            if user_id:
                log_df = log_df[log_df['user_id'] == user_id]
            
            if action_type:
                log_df = log_df[log_df['action_type'] == action_type]
            
            return log_df.to_dict(orient='records')
            
        except Exception as e:
            logger.error(f"Error loading logs: {str(e)}")
            return []
    
    def load_containers(self):
        """Load containers data from CSV."""
        try:
            containers_path = self.data_dir / 'containers.csv'
            
            if not containers_path.exists():
                logger.warning(f"Containers file not found: {containers_path}")
                print(f"DEBUG: Containers file not found: {containers_path}")
                return None
            
            containers_df = pd.read_csv(containers_path)
            print(f"DEBUG: Loaded containers: {len(containers_df)} containers")
            
            return containers_df
        except Exception as e:
            logger.error(f"Error loading containers: {str(e)}")
            print(f"DEBUG: Error loading containers: {str(e)}")
            return None
    
    def load_items(self):
        """Load items data from CSV."""
        try:
            items_path = self.data_dir / 'input_items.csv'
            
            if not items_path.exists():
                logger.warning(f"Items file not found: {items_path}")
                print(f"DEBUG: Items file not found: {items_path}")
                return None
            
            items_df = pd.read_csv(items_path)
            print(f"DEBUG: Loaded items: {len(items_df)} items")
            
            return items_df
        except Exception as e:
            logger.error(f"Error loading items: {str(e)}")
            print(f"DEBUG: Error loading items: {str(e)}")
            return None
    
    def load_placement(self):
        """Load placement data from CSV."""
        try:
            # Check both possible filenames for placements
            placed_path = self.data_dir / 'placed_items.csv'
            alt_placed_path = self.data_dir / 'placement_results.csv'
            
            print(f"DEBUG: Looking for placed items at {placed_path} or {alt_placed_path}")
            
            # First try the original filename
            if placed_path.exists():
                try:
                    placements_df = pd.read_csv(placed_path)
                    print(f"DEBUG: Loaded placed items from {placed_path}: {len(placements_df)} items")
                    return placements_df
                except Exception as e:
                    logger.error(f"Error loading placed items from {placed_path}: {str(e)}")
                    print(f"DEBUG: Error loading placed items from {placed_path}: {str(e)}")
            
            # If not found, try the alternative filename
            elif alt_placed_path.exists():
                try:
                    placements_df = pd.read_csv(alt_placed_path)
                    print(f"DEBUG: Loaded placed items from {alt_placed_path}: {len(placements_df)} items")
                    return placements_df
                except Exception as e:
                    logger.error(f"Error loading placed items from {alt_placed_path}: {str(e)}")
                    print(f"DEBUG: Error loading placed items from {alt_placed_path}: {str(e)}")
            else:
                print(f"DEBUG: Placed items file not found at {placed_path} or {alt_placed_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading placement: {str(e)}")
            print(f"DEBUG: Error loading placement: {str(e)}")
            return None
