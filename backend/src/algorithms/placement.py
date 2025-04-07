import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from py3dbp import Packer, Bin, Item
from datetime import datetime
import math

def calculate_sensitivity(items_df):
    """Calculate item sensitivity based on name similarity using TF-IDF and cosine similarity."""
    item_names = items_df['name'].astype(str).values
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(item_names)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    sensitive_flags = (similarity_matrix < 0.2).sum(axis=1) > 0
    items_df['sensitive'] = sensitive_flags.astype(int)
    return items_df

def load_and_preprocess_data(items_path, containers_path):
    """Load and preprocess items and containers data with auto-handling of missing fields."""
    # Load data with clean column names
    items_df = pd.read_csv(items_path).rename(columns={
        'mass_kg': 'weight_kg',
        'usage_limit': 'usage_limit'
    })
    containers_df = pd.read_csv(containers_path)
    
    # Auto-calculate missing container weights if needed
    if 'max_weight_kg' not in containers_df:
        # Estimate max weight as 500kg/m³ density * volume (cm³ to m³ conversion factor 1/1e6)
        containers_df['max_weight_kg'] = containers_df.apply(
            lambda x: (x['width_cm'] * x['height_cm'] * x['depth_cm']) / 1e6 * 500,
            axis=1
        )
    
    # Calculate volumes
    items_df['item_volume'] = items_df['width_cm'] * items_df['depth_cm'] * items_df['height_cm']
    containers_df['container_volume'] = containers_df['width_cm'] * containers_df['depth_cm'] * containers_df['height_cm']
    
    # Handle missing priority values
    if 'priority' not in items_df:
        items_df['priority'] = 1  # Default to lowest priority
    
    # Calculate sensitivity
    items_df = calculate_sensitivity(items_df)
    
    # Handle expiry dates: keep as pandas datetime objects so .dt accessor works
    today = pd.Timestamp.today()
    items_df['expiry_date'] = pd.to_datetime(items_df['expiry_date'], errors='coerce')
    items_df['days_before_expiry'] = (items_df['expiry_date'] - today).dt.days
    items_df['days_before_expiry'] = items_df['days_before_expiry'].apply(
        lambda x: x if pd.notnull(x) and x >= 0 else 36500
    )
    
    return items_df, containers_df

def pack_items(items_df, containers_df):
    """Pack items into containers considering zones, priority, and sensitivity."""
    # Sort items by priority (desc), days before expiry (asc), sensitivity (desc)
    sorted_items = items_df.sort_values(
        by=['priority', 'days_before_expiry', 'sensitive'],
        ascending=[False, True, False]
    )
    
    # Group containers by zone
    zones = containers_df['zone'].unique()
    zone_containers = {zone: containers_df[containers_df['zone'] == zone] for zone in zones}
    
    all_placements = []
    remaining_items = sorted_items.copy()
    
    # Pack items into preferred zone containers first
    for zone in zones:
        containers = zone_containers[zone]
        if containers.empty:
            continue
        
        # Get items preferring this zone
        zone_items = remaining_items[remaining_items['preferred_zone'] == zone]
        if zone_items.empty:
            continue
        
        # Initialize packer
        packer = Packer()
        for _, container in containers.iterrows():
            # Create a Bin with required positional arguments only
            bin_obj = Bin(
                container['container_id'],
                container['width_cm'],
                container['height_cm'],
                container['depth_cm'],
                container['max_weight_kg']
            )
            packer.add_bin(bin_obj)
        
        # Add items to packer
        for _, item in zone_items.iterrows():
            # Create an Item with required positional arguments
            item_obj = Item(
                item['name'],
                item['width_cm'],
                item['height_cm'],
                item['depth_cm'],
                item['weight_kg']
            )
            # Set additional attributes as needed
            item_obj.partno = item['item_id']
            item_obj.level = item['priority']
            item_obj.put_type = 1  # if needed for later use
            item_obj.color = 'red' if item['sensitive'] else 'green'
            packer.add_item(item_obj)
        
        # Pack items
        packer.pack(bigger_first=True, distribute_items=False, fix_point=True)
        
        # Record placements
        for bin_obj in packer.bins:
            for item_obj in bin_obj.items:
                all_placements.append({
                    'item_id': item_obj.partno,
                    'container_id': bin_obj.identifier,  # or use bin_obj.partno if set manually
                    'x_cm': round(item_obj.position[0], 1),
                    'y_cm': round(item_obj.position[1], 1),
                    'z_cm': round(item_obj.position[2], 1),
                    'rotation': item_obj.rotation_type,
                    'width': item_obj.width,
                    'depth': item_obj.depth,
                    'height': item_obj.height,
                    'priority': item_obj.level,
                    'sensitive': 'Yes' if item_obj.color == 'red' else 'No',
                    'expiry_days': item_obj.userdata.get('expiry_days', 36500)
                })
        
        # Update remaining items
        placed_ids = [p['item_id'] for p in all_placements]
        remaining_items = remaining_items[~remaining_items['item_id'].isin(placed_ids)]
    
    # Pack remaining items into any container
    if not remaining_items.empty:
        packer = Packer()
        for _, container in containers_df.iterrows():
            bin_obj = Bin(
                container['container_id'],
                container['width_cm'],
                container['height_cm'],
                container['depth_cm'],
                container['max_weight_kg']
            )
            packer.add_bin(bin_obj)
        
        for _, item in remaining_items.iterrows():
            item_obj = Item(
                item['name'],
                item['width_cm'],
                item['height_cm'],
                item['depth_cm'],
                item['weight_kg']
            )
            item_obj.partno = item['item_id']
            item_obj.level = item['priority']
            item_obj.put_type = 1
            item_obj.color = 'red' if item['sensitive'] else 'green'
            packer.add_item(item_obj)
        
        packer.pack(bigger_first=True, distribute_items=False, fix_point=True)
        
        for bin_obj in packer.bins:
            for item_obj in bin_obj.items:
                all_placements.append({
                    'item_id': item_obj.partno,
                    'container_id': bin_obj.identifier,
                    'x_cm': round(item_obj.position[0], 1),
                    'y_cm': round(item_obj.position[1], 1),
                    'z_cm': round(item_obj.position[2], 1),
                    'rotation': item_obj.rotation_type,
                    'width': item_obj.width,
                    'depth': item_obj.depth,
                    'height': item_obj.height,
                    'priority': item_obj.level,
                    'sensitive': 'Yes' if item_obj.color == 'red' else 'No',
                    'expiry_days': item_obj.userdata.get('expiry_days', 36500)
                })
        
        placed_ids = [p['item_id'] for p in all_placements]
        remaining_items = remaining_items[~remaining_items['item_id'].isin(placed_ids)]
    
    return pd.DataFrame(all_placements), remaining_items

def generate_output(placed_df, unplaced_df):
    """Generate CSV outputs with placement details."""
    # Save placed items with full details
    placed_output = placed_df[[
        'item_id', 'container_id', 'x_cm', 'y_cm', 'z_cm',
        'rotation', 'width', 'depth', 'height', 'priority',
        'sensitive', 'expiry_days'
    ]]
    placed_output.to_csv('placed_items.csv', index=False)
    
    # Save unplaced items with reasons
    if not unplaced_df.empty:
        unplaced_output = unplaced_df[[
            'item_id', 'name', 'width_cm', 'depth_cm', 'height_cm',
            'weight_kg', 'priority', 'preferred_zone', 'sensitive'
        ]]
        unplaced_output['reason'] = 'No suitable container found'
        unplaced_output.to_csv('unplaced_items.csv', index=False)
    
    # Print summary
    print(f"\n📦 Placement Summary:")
    print(f"✅ Successfully placed: {len(placed_df)} items")
    print(f"🚫 Failed to place: {len(unplaced_df)} items")
    print(f"📊 Placement rate: {len(placed_df)/(len(placed_df)+len(unplaced_df)):.1%}")

if __name__ == "__main__":
    # Load and preprocess data
    items_df, containers_df = load_and_preprocess_data('input_items.csv', 'containers.csv')
    
    # Pack items into containers
    placed_df, unplaced_df = pack_items(items_df, containers_df)
    
    # Generate output files
    generate_output(placed_df, unplaced_df)
