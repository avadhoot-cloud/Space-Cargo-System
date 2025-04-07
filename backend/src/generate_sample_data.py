import pandas as pd
import numpy as np
from pathlib import Path

# Create data directory if it doesn't exist
data_dir = Path(__file__).parent.parent.parent / "data"
data_dir.mkdir(exist_ok=True)

# Generate sample containers
containers = [
    {"container_id": 1, "name": "Storage Container 1", "width_cm": 100, "height_cm": 80, "depth_cm": 120, "max_weight_kg": 50, "zone": "storage"},
    {"container_id": 2, "name": "Lab Storage", "width_cm": 90, "height_cm": 70, "depth_cm": 110, "max_weight_kg": 40, "zone": "lab"},
    {"container_id": 3, "name": "Medical Cabinet", "width_cm": 80, "height_cm": 60, "depth_cm": 100, "max_weight_kg": 30, "zone": "medical"},
    {"container_id": 4, "name": "Tool Storage", "width_cm": 95, "height_cm": 75, "depth_cm": 115, "max_weight_kg": 45, "zone": "maintenance"}
]

# Generate sample items
items = [
    {"item_id": 1, "name": "Box A", "width_cm": 30, "height_cm": 20, "depth_cm": 40, "weight_kg": 5.5, "priority": 1, "preferred_zone": "storage"},
    {"item_id": 2, "name": "Box B", "width_cm": 25, "height_cm": 15, "depth_cm": 35, "weight_kg": 4.2, "priority": 2, "preferred_zone": "storage"},
    {"item_id": 3, "name": "Lab Equipment", "width_cm": 40, "height_cm": 30, "depth_cm": 50, "weight_kg": 8.0, "priority": 3, "preferred_zone": "lab"},
    {"item_id": 4, "name": "Medical Supplies", "width_cm": 20, "height_cm": 15, "depth_cm": 25, "weight_kg": 2.5, "priority": 4, "preferred_zone": "medical"},
    {"item_id": 5, "name": "Tools", "width_cm": 35, "height_cm": 25, "depth_cm": 45, "weight_kg": 6.0, "priority": 2, "preferred_zone": "maintenance"}
]

# Create DataFrames
containers_df = pd.DataFrame(containers)
items_df = pd.DataFrame(items)

# Save to CSV
containers_df.to_csv(data_dir / "containers.csv", index=False)
items_df.to_csv(data_dir / "input_items.csv", index=False)

# Generate sample placement results
placed_items = [
    {"item_id": 1, "container_id": 1, "x_cm": 10, "y_cm": 10, "z_cm": 10, "width": 30, "height": 20, "depth": 40, "priority": 1, "sensitive": "No", "expiry_days": 36500},
    {"item_id": 2, "container_id": 1, "x_cm": 50, "y_cm": 10, "z_cm": 10, "width": 25, "height": 15, "depth": 35, "priority": 2, "sensitive": "No", "expiry_days": 36500},
    {"item_id": 3, "container_id": 2, "x_cm": 10, "y_cm": 10, "z_cm": 10, "width": 40, "height": 30, "depth": 50, "priority": 3, "sensitive": "No", "expiry_days": 36500},
    {"item_id": 4, "container_id": 3, "x_cm": 10, "y_cm": 10, "z_cm": 10, "width": 20, "height": 15, "depth": 25, "priority": 4, "sensitive": "No", "expiry_days": 36500},
    {"item_id": 5, "container_id": 4, "x_cm": 10, "y_cm": 10, "z_cm": 10, "width": 35, "height": 25, "depth": 45, "priority": 2, "sensitive": "No", "expiry_days": 36500}
]

unplaced_items = []

# Create DataFrames for results
placed_df = pd.DataFrame(placed_items)
unplaced_df = pd.DataFrame(unplaced_items)

# Save to CSV
placed_df.to_csv(data_dir / "placed_items.csv", index=False)
unplaced_df.to_csv(data_dir / "unplaced_items.csv", index=False)

print(f"Generated sample data in {data_dir}")
print(f"Containers: {len(containers_df)}")
print(f"Items: {len(items_df)}")
print(f"Placed items: {len(placed_df)}")
print(f"Unplaced items: {len(unplaced_df)}") 