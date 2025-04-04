from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
import csv
import io
import os
import pathlib
import shutil
from typing import List, Dict, Any
import hashlib

router = APIRouter()

# Path to data directory relative to the project root
DATA_DIR = pathlib.Path(__file__).parent.parent.parent.parent / "data"

def parse_csv(file: UploadFile) -> List[Dict[str, Any]]:
    """Parse CSV file into a list of dictionaries."""
    content = file.file.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(content))
    
    records = []
    for row in csv_reader:
        # Convert empty strings to None
        cleaned_row = {k: (v if v else None) for k, v in row.items()}
        records.append(cleaned_row)
    
    # Reset file cursor for potential reuse
    file.file.seek(0)
    return records

def parse_csv_file(file_path: pathlib.Path) -> List[Dict[str, Any]]:
    """Parse a CSV file from disk into a list of dictionaries."""
    with open(file_path, 'r', newline='') as file:
        csv_reader = csv.DictReader(file)
        return [{k: (v if v else None) for k, v in row.items()} for row in csv_reader]

def detect_csv_type(headers: List[str]) -> str:
    """Detect if the CSV is for containers or items."""
    container_headers = ["zone", "container_id", "width_cm", "depth_cm", "height_cm"]
    item_headers = ["item_id", "name", "width_cm", "depth_cm", "height_cm", "mass_kg", "priority"]
    
    if all(header in headers for header in container_headers):
        return "container"
    elif all(header in headers for header in item_headers):
        return "item"
    else:
        return "unknown"

def calculate_file_hash(file_path: pathlib.Path) -> str:
    """Calculate MD5 hash of a file to check for duplicates."""
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def is_duplicate_file(file: UploadFile) -> bool:
    """Check if the uploaded file already exists in the data folder."""
    try:
        # Ensure data directory exists
        DATA_DIR.mkdir(exist_ok=True)
        
        # Get the original file content for hashing
        content = file.file.read()
        file_hash = hashlib.md5(content).hexdigest()
        file.file.seek(0)  # Reset cursor for reuse
        
        # Check against all existing files
        for existing_file in DATA_DIR.glob("*.csv"):
            if calculate_file_hash(existing_file) == file_hash:
                return True
        
        return False
    except Exception as e:
        print(f"Error checking for duplicate file: {e}")
        return False

def save_csv_to_data_folder(file: UploadFile) -> pathlib.Path:
    """Save uploaded CSV file to the data folder."""
    try:
        # Ensure data directory exists
        DATA_DIR.mkdir(exist_ok=True)
        
        # Create a unique filename based on current timestamp and original name
        destination = DATA_DIR / file.filename
        
        # Use a counter for cases where the file might exist
        counter = 1
        while destination.exists():
            name_parts = file.filename.rsplit('.', 1)
            new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}" if len(name_parts) > 1 else f"{file.filename}_{counter}"
            destination = DATA_DIR / new_name
            counter += 1
        
        # Save the file
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file.file.seek(0)  # Reset cursor for reuse
        return destination
    except Exception as e:
        print(f"Error saving file to data folder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {str(e)}"
        )

def load_data_from_folder(db: Session):
    """Load data from the data folder if database is empty."""
    # Check if we have any data in the database
    container_count = db.query(models.Container).count()
    item_count = db.query(models.Item).count()
    
    if container_count == 0 and item_count == 0:
        try:
            # Create data directory if it doesn't exist
            DATA_DIR.mkdir(exist_ok=True)
            
            # Process all CSV files in the data directory
            for file_path in DATA_DIR.glob("*.csv"):
                try:
                    records = parse_csv_file(file_path)
                    if records:
                        csv_type = detect_csv_type(records[0].keys())
                        process_records(records, csv_type, db)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    
        except Exception as e:
            print(f"Error loading data from folder: {e}")

def process_records(records: List[Dict[str, Any]], csv_type: str, db: Session):
    """Process records based on CSV type."""
    if csv_type == "container":
        for data in records:
            container = models.Container(
                name=data.get("container_id", "Container"),
                width=int(data["width_cm"]),
                height=int(data["height_cm"]),
                depth=int(data["depth_cm"]),
                max_weight=1000.0,  # Default value
                current_weight=0.0,
                zone=data.get("zone", ""),
                is_active=True
            )
            db.add(container)
            
    elif csv_type == "item":
        for data in records:
            item = models.Item(
                name=data["name"],
                description=data.get("item_id", ""),
                weight=float(data["mass_kg"]),
                width=float(data["width_cm"]),
                height=float(data["height_cm"]),
                depth=float(data["depth_cm"]),
                volume=float(data["width_cm"]) * float(data["height_cm"]) * float(data["depth_cm"]) / 1000000,  # Convert to m³
                priority=int(data["priority"]) if data["priority"] else 1,
                expiry_date=data.get("expiry_date"),
                usage_limit=int(data.get("usage_limit", 0)) if data.get("usage_limit") else None,
                preferred_zone=data.get("preferred_zone"),
                is_fragile=False  # Default value
            )
            db.add(item)
    
    db.commit()

@router.post("/csv", status_code=status.HTTP_201_CREATED)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed."
        )
    
    try:
        records = parse_csv(file)
        if not records:
            raise HTTPException(
                status_code=400,
                detail="The CSV file is empty."
            )
        
        # Detect CSV type
        csv_type = detect_csv_type(records[0].keys())
        if csv_type == "unknown":
            raise HTTPException(
                status_code=400,
                detail="Invalid CSV format. Please check the required headers for items or containers."
            )
        
        # Check for duplicates
        if is_duplicate_file(file):
            return {
                "message": "This file already exists in the database",
                "items": [{"name": record.get("name", record.get("container_id", "Unknown"))} for record in records[:5]],
                "duplicate": True
            }
        
        # Save file to data folder
        saved_path = save_csv_to_data_folder(file)
        
        # Process the records
        process_records(records, csv_type, db)
        
        if csv_type == "container":
            return {
                "message": f"Successfully imported {len(records)} containers",
                "items": [{"name": data.get("container_id", f"Container {i+1}")} for i, data in enumerate(records[:5])],
                "file_path": str(saved_path)
            }
        else:
            return {
                "message": f"Successfully imported {len(records)} items",
                "items": [{"name": data.get("name", f"Item {i+1}")} for i, data in enumerate(records[:5])],
                "file_path": str(saved_path)
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing the CSV file: {str(e)}"
        )

@router.get("/containers")
def get_containers(db: Session = Depends(get_db)):
    """Get all containers."""
    # Ensure data is loaded from data folder if DB is empty
    load_data_from_folder(db)
    containers = db.query(models.Container).all()
    return containers

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    """Get all items."""
    # Ensure data is loaded from data folder if DB is empty
    load_data_from_folder(db)
    items = db.query(models.Item).all()
    return items 