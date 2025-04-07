"""
Data Loader Script for Space Cargo System

This script loads data from CSV files in the data folder into the database.
It ensures existing database entries are cleared before loading new data.
"""

import os
import csv
import sys
import pathlib
import sqlite3
import django

# Add Django project to path and set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spacecargo.settings')
django.setup()

# Import Django models after setup
from placement.models import Container, Item, PlacementHistory

# Path to data directory
DATA_DIR = pathlib.Path(__file__).parent.parent / "data"

def reset_database():
    """Clear all existing data in the database and recreate tables."""
    # In Django, we'll just delete all records
    Container.objects.all().delete()
    Item.objects.all().delete()
    PlacementHistory.objects.all().delete()
    print("Database reset complete.")

def load_containers(session=None):
    """Load containers from CSV files in the data folder."""
    container_count = 0
    
    # First, process containers.csv
    containers_file = DATA_DIR / "containers.csv"
    if containers_file.exists():
        with open(containers_file, 'r', newline='') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    # Create container from CSV data - using the correct model attributes
                    container = Container(
                        name=row["container_id"],
                        width_cm=int(float(row["width_cm"])),
                        height_cm=int(float(row["height_cm"])),
                        depth_cm=int(float(row["depth_cm"])),
                        max_weight_kg=1000.0,  # Default max weight
                        zone="General",  # Default zone
                        used_volume=0.0,
                        used_weight=0.0,
                        is_full=False
                    )
                    container.save()
                    container_count += 1
                except Exception as e:
                    print(f"Error loading container {row.get('container_id', 'unknown')}: {e}")
        
        print(f"Loaded {container_count} containers from {containers_file}")
    
    # Then process any additional container CSV files
    for file_path in DATA_DIR.glob("*container*.csv"):
        if file_path != containers_file:  # Skip if it's the main containers.csv we already processed
            with open(file_path, 'r', newline='') as file:
                csv_reader = csv.DictReader(file)
                file_container_count = 0
                for row in csv_reader:
                    try:
                        # Create container from CSV data - using the correct model attributes
                        container = Container(
                            name=row["container_id"],
                            width_cm=int(float(row["width_cm"])),
                            height_cm=int(float(row["height_cm"])),
                            depth_cm=int(float(row["depth_cm"])),
                            max_weight_kg=1000.0,  # Default max weight
                            zone="General",  # Default zone
                            used_volume=0.0,
                            used_weight=0.0,
                            is_full=False
                        )
                        container.save()
                        container_count += 1
                        file_container_count += 1
                    except Exception as e:
                        print(f"Error loading container {row.get('container_id', 'unknown')} from {file_path}: {e}")
                
                print(f"Loaded {file_container_count} containers from {file_path}")
    
    return container_count

def load_items(session=None):
    """Load items from CSV files in the data folder."""
    item_count = 0
    
    # Process items CSV files
    for file_path in DATA_DIR.glob("*item*.csv"):
        with open(file_path, 'r', newline='') as file:
            csv_reader = csv.DictReader(file)
            file_item_count = 0
            for row in csv_reader:
                try:
                    # Default values for optional fields
                    priority = int(row["priority"]) if "priority" in row and row["priority"] and row["priority"] != "N/A" else 1
                    
                    # Create item from CSV data - using the correct field names that match the Item model
                    item = Item(
                        name=row["item_id"],  # Use item_id as the name
                        width_cm=float(row["width_cm"]),
                        height_cm=float(row["height_cm"]),
                        depth_cm=float(row["depth_cm"]),
                        weight_kg=float(row["mass_kg"]),
                        priority=priority,
                        preferred_zone="General",  # Default zone
                        is_placed=False,
                        sensitive=False  # Default value
                    )
                    item.save()
                    item_count += 1
                    file_item_count += 1
                except Exception as e:
                    print(f"Error loading item {row.get('name', 'unknown')} ({row.get('item_id', 'unknown')}) from {file_path}: {e}")
            
            print(f"Loaded {file_item_count} items from {file_path}")
    
    return item_count

def main():
    """Main function to load all data."""
    print(f"Loading data from {DATA_DIR}")
    
    # Check if data directory exists
    if not DATA_DIR.exists():
        print(f"Error: Data directory {DATA_DIR} does not exist.")
        return
    
    # Reset database (clear existing data)
    reset_database()
    
    try:
        # Load containers first
        container_count = load_containers()
        
        # Load items
        item_count = load_items()
        
        print(f"\nData loading complete:")
        print(f"- {container_count} containers loaded")
        print(f"- {item_count} items loaded")
        
    except Exception as e:
        print(f"Error loading data: {e}")

if __name__ == "__main__":
    main() 