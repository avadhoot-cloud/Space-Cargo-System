"""
Database Summary Script for Space Cargo System

This script connects to the database and prints a summary of the data.
"""

import os
import sys
from sqlalchemy import func

# Add the parent directory to sys.path to import from src
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from src.models import Container, Item
from src.database import SessionLocal

def summarize_database():
    """Connect to the database and print a summary of the data."""
    session = SessionLocal()
    
    try:
        # Count containers
        container_count = session.query(func.count(Container.id)).scalar()
        print(f"Total containers: {container_count}")
        
        # Count items
        item_count = session.query(func.count(Item.id)).scalar()
        print(f"Total items: {item_count}")
        
        # Sample containers
        print("\n--- Sample Containers ---")
        containers = session.query(Container).limit(5).all()
        for container in containers:
            print(f"ID: {container.id}, Name: {container.name}, Dimensions: {container.width}x{container.height}x{container.depth} cm")
        
        # Sample items
        print("\n--- Sample Items ---")
        items = session.query(Item).limit(5).all()
        for item in items:
            print(f"ID: {item.id}, Name: {item.name}, Weight: {item.weight} kg, Volume: {item.volume} m³")
        
        # Items per container
        print("\n--- Items per Container ---")
        container_with_items = session.query(
            Container.id, 
            Container.name, 
            func.count(Item.id).label('item_count')
        ).outerjoin(Item, Container.id == Item.container_id)\
         .group_by(Container.id)\
         .order_by(func.count(Item.id).desc())\
         .limit(5)\
         .all()
        
        for container_id, container_name, item_count in container_with_items:
            print(f"Container {container_name} (ID: {container_id}) has {item_count} items")
        
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    summarize_database() 