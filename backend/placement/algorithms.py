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
        
        if not items_path.exists() or not containers_path.exists():
            logger.warning(f"CSV files not found: {items_path} or {containers_path}")
            return None, None
            
        try:
            items_df = pd.read_csv(items_path)
            containers_df = pd.read_csv(containers_path)
            return items_df, containers_df
        except Exception as e:
            logger.error(f"Error loading CSV files: {str(e)}")
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
        items_df['expiry_date'] = pd.to_datetime(items_df['expiry_date'], errors='coerce')
        
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
                    # In a real implementation, you would use a 3D packing algorithm
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
        """Calculate efficiency metrics for the current placement."""
        items_df, containers_df = self.load_from_csv()
        placements_df, unplaced_df = self.load_results()
        
        if items_df is None or containers_df is None or placements_df is None:
            return {
                "efficiency": 0,
                "space_utilization": 0,
                "success_rate": 0,
                "priority_satisfaction": 0,
                "zone_match_rate": 0
            }
        
        # Calculate metrics
        total_items = len(items_df)
        placed_items = len(placements_df)
        
        # Space utilization
        total_container_volume = containers_df['volume'].sum()
        total_item_volume = 0
        
        for _, placement in placements_df.iterrows():
            total_item_volume += placement['width_cm'] * placement['depth_cm'] * placement['height_cm']
        
        space_utilization = (total_item_volume / total_container_volume * 100) if total_container_volume > 0 else 0
        
        # Success rate
        success_rate = (placed_items / total_items * 100) if total_items > 0 else 0
        
        # Priority satisfaction (higher priority items should be placed first)
        priority_satisfied = 80  # Placeholder - would need to calculate based on placement order
        
        # Zone match rate (items should be in preferred zones)
        zone_matches = 0
        zone_match_rate = 0
        
        if placed_items > 0:
            for _, placement in placements_df.iterrows():
                item_id = placement['item_id']
                container_id = placement['container_id']
                
                # Get item's preferred zone
                item_row = items_df[items_df['item_id'] == item_id]
                if not item_row.empty and 'preferred_zone' in item_row.columns:
                    preferred_zone = item_row['preferred_zone'].iloc[0]
                    
                    # Get container's zone
                    container_row = containers_df[containers_df['container_id'] == container_id]
                    if not container_row.empty:
                        container_zone = container_row['zone'].iloc[0]
                        
                        if preferred_zone == container_zone:
                            zone_matches += 1
            
            zone_match_rate = (zone_matches / placed_items * 100)
        
        # Overall efficiency (weighted average)
        efficiency = (space_utilization * 0.4 + success_rate * 0.3 + priority_satisfied * 0.15 + zone_match_rate * 0.15)
        
        # Container utilization details
        container_utilization = []
        for _, container in containers_df.iterrows():
            container_id = container['container_id']
            container_volume = container['volume']
            
            # Calculate used volume for this container
            used_volume = 0
            container_placements = placements_df[placements_df['container_id'] == container_id]
            
            for _, placement in container_placements.iterrows():
                used_volume += placement['width_cm'] * placement['depth_cm'] * placement['height_cm']
            
            utilization_percentage = (used_volume / container_volume * 100) if container_volume > 0 else 0
            
            container_utilization.append({
                "id": container_id,
                "name": container.get('name', f"Container {container_id}"),
                "utilization_percentage": utilization_percentage
            })
        
        return {
            "efficiency": round(efficiency, 2),
            "space_utilization": round(space_utilization, 2),
            "success_rate": round(success_rate, 2),
            "priority_satisfaction": round(priority_satisfied, 2),
            "zone_match_rate": round(zone_match_rate, 2),
            "container_utilization": container_utilization
        }
    
    def load_results(self):
        """Load placement results from CSV files."""
        placed_path = self.data_dir / 'placed_items.csv'
        unplaced_path = self.data_dir / 'unplaced_items.csv'
        
        placements_df = None
        unplaced_df = None
        
        if placed_path.exists():
            try:
                placements_df = pd.read_csv(placed_path)
            except Exception as e:
                logger.error(f"Error loading placed items: {str(e)}")
        
        if unplaced_path.exists():
            try:
                unplaced_df = pd.read_csv(unplaced_path)
            except Exception as e:
                logger.error(f"Error loading unplaced items: {str(e)}")
        
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
                    best_reasoning = f"No containers available in preferred zone ({preferred_zone}). " + \
                                    f"Selected container in zone {best_container['zone']} with sufficient space."
            
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
        items_df, _ = self.load_from_csv()
        placements_df, _ = self.load_results()
        
        if items_df is None or placements_df is None:
            return []
        
        waste_items = []
        today = datetime.now().date()
        
        for _, item in items_df.iterrows():
            item_id = item['item_id']
            
            # Check if item is placed
            if placements_df is not None and item_id in placements_df['item_id'].values:
                placement = placements_df[placements_df['item_id'] == item_id].iloc[0]
                container_id = placement['container_id']
                position = (placement['x_cm'], placement['y_cm'], placement['z_cm'])
                
                # Check expiry date
                if 'expiry_date' in item and pd.notna(item['expiry_date']):
                    try:
                        expiry_date = pd.to_datetime(item['expiry_date']).date()
                        if expiry_date <= today:
                            waste_items.append({
                                "item_id": item_id,
                                "name": item['name'],
                                "reason": "Expired",
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
                    except:
                        pass
                
                # Check usage limit
                if 'usage_limit' in item and pd.notna(item['usage_limit']):
                    if int(item['usage_limit']) <= 0:
                        waste_items.append({
                            "item_id": item_id,
                            "name": item['name'],
                            "reason": "Out of Uses",
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