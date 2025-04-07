# Place this in your backend/placement/views.py file

from django.shortcuts import render
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
import pandas as pd
import logging
from datetime import datetime
import os
from pathlib import Path

from .models import Container, Item, PlacementHistory
from .serializers import (ContainerSerializer, ItemSerializer, PlacementHistorySerializer, 
                          PlacementResponseSerializer, PlacementRecommendationSerializer,
                          PlacementStatisticsSerializer)
from .algorithms import PlacementManager

logger = logging.getLogger(__name__)
placement_manager = PlacementManager()

class ContainerViewSet(viewsets.ModelViewSet):
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

@api_view(['GET'])
def get_statistics(request):
    """Get statistics about placement algorithm performance."""
    try:
        # Use the placement manager to get efficiency metrics
        statistics = placement_manager.get_placement_efficiency()
        return Response(statistics)
    except Exception as e:
        logger.error(f"Error in get_statistics: {str(e)}")
        return Response(
            {"detail": f"Error fetching placement statistics: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def process_data(request):
    """Process placement data using the placement algorithm."""
    try:
        # Use the placement manager to process data
        placements_df, unplaced_df = placement_manager.place_items()
        
        if placements_df is None:
            return Response(
                {"success": False, "message": "Failed to process data. Please check CSV files."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate summary statistics
        statistics = placement_manager.get_placement_efficiency()
        
        return Response({
            "success": True,
            "message": "Placement processing completed successfully",
            "statistics": statistics,
            "placed_count": len(placements_df) if placements_df is not None else 0,
            "unplaced_count": len(unplaced_df) if unplaced_df is not None else 0
        })
    except Exception as e:
        logger.error(f"Error in process_data: {str(e)}")
        return Response(
            {"success": False, "message": f"Error processing data: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_results(request):
    """Get the results of placement processing."""
    try:
        # Load results from CSV files
        placements_df, unplaced_df = placement_manager.load_results()
        
        if placements_df is None and unplaced_df is None:
            return Response(
                {"detail": "Placement results not found. Please process the data first."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Load container data
        items_df, containers_df = placement_manager.load_from_csv()
        
        # Convert DataFrames to lists of dictionaries
        placed_items = placements_df.to_dict(orient='records') if placements_df is not None else []
        unplaced_items = unplaced_df.to_dict(orient='records') if unplaced_df is not None else []
        containers = containers_df.to_dict(orient='records') if containers_df is not None else []
        
        # Calculate statistics
        total_items = len(placed_items) + len(unplaced_items)
        
        return Response({
            "placed_items": placed_items,
            "unplaced_items": unplaced_items,
            "containers": containers,
            "statistics": {
                "total_items": total_items,
                "placed_items": len(placed_items),
                "unplaced_items": len(unplaced_items)
            }
        })
    except Exception as e:
        logger.error(f"Error in get_results: {str(e)}")
        return Response(
            {"detail": f"Error fetching placement results: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_recommendations(request):
    """Get placement recommendations for unplaced items."""
    try:
        # Use the placement manager to get recommendations
        recommendations = placement_manager.get_recommendations()
        return Response(recommendations)
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}")
        return Response(
            {"detail": f"Error generating recommendations: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def place_item(request):
    """Place an item in a container."""
    try:
        item_id = request.data.get('item_id')
        container_id = request.data.get('container_id')
        user_id = request.data.get('user_id', 'anonymous')
        
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Load data
        items_df, containers_df = placement_manager.load_from_csv()
        placements_df, _ = placement_manager.load_results()
        
        if items_df is None or containers_df is None:
            return Response(
                {"success": False, "message": "Data not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find the item
        item_row = items_df[items_df['item_id'] == item_id]
        if item_row.empty:
            return Response(
                {"success": False, "message": f"Item {item_id} not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find the container
        if container_id:
            container_row = containers_df[containers_df['container_id'] == container_id]
            if container_row.empty:
                return Response(
                    {"success": False, "message": f"Container {container_id} not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Get recommendations and use the best one
            recommendations = placement_manager.get_recommendations()
            recommendation = next((r for r in recommendations if r['item_id'] == item_id), None)
            
            if recommendation:
                container_id = recommendation['container_id']
                container_row = containers_df[containers_df['container_id'] == container_id]
                if container_row.empty:
                    return Response(
                        {"success": False, "message": f"Recommended container {container_id} not found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {"success": False, "message": "No suitable container found"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get item dimensions
        item = item_row.iloc[0]
        item_volume = item['width_cm'] * item['depth_cm'] * item['height_cm']
        
        # Get container dimensions
        container = container_row.iloc[0]
        container_volume = container['volume'] if 'volume' in container else container['width_cm'] * container['depth_cm'] * container['height_cm']
        
        # Calculate position (simple placement for now)
        position = (0, 0, 0)
        
        if placements_df is not None and not placements_df.empty:
            # Find items already in this container
            container_items = placements_df[placements_df['container_id'] == container_id]
            
            if not container_items.empty:
                # Simple stacking: place on top of the highest item
                max_height = 0
                for _, placement in container_items.iterrows():
                    if placement['z_cm'] + placement['height_cm'] > max_height:
                        max_height = placement['z_cm'] + placement['height_cm']
                position = (0, 0, max_height)
        
        # Add to placements
        new_placement = {
            'item_id': item_id,
            'container_id': container_id,
            'x_cm': position[0],
            'y_cm': position[1],
            'z_cm': position[2],
            'width_cm': item['width_cm'],
            'depth_cm': item['depth_cm'],
            'height_cm': item['height_cm']
        }
        
        if placements_df is None:
            placements_df = pd.DataFrame([new_placement])
        else:
            # Remove any existing placement for this item
            placements_df = placements_df[placements_df['item_id'] != item_id]
            # Add new placement
            placements_df = pd.concat([placements_df, pd.DataFrame([new_placement])], ignore_index=True)
        
        # Save back to CSV
        placements_df.to_csv(placement_manager.data_dir / 'placed_items.csv', index=False)
        
        # Generate log
        placement_manager.generate_log('placement', user_id, item_id, {
            'container_id': container_id,
            'position': position
        })
        
        return Response({
            "success": True,
            "message": f"Item {item_id} placed in container {container_id}",
            "position": {
                "x": position[0],
                "y": position[1],
                "z": position[2]
            }
        })
    except Exception as e:
        logger.error(f"Error in place_item: {str(e)}")
        return Response(
            {"success": False, "message": f"Error placing item: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def search_item(request):
    """Search for an item by ID or name."""
    try:
        item_id = request.query_params.get('item_id')
        item_name = request.query_params.get('item_name')
        
        if not item_id and not item_name:
            return Response(
                {"success": False, "message": "Item ID or name is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Load data
        items_df, _ = placement_manager.load_from_csv()
        placements_df, _ = placement_manager.load_results()
        
        if items_df is None:
            return Response(
                {"success": False, "message": "Items data not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find the item
        if item_id:
            item_row = items_df[items_df['item_id'] == item_id]
        else:
            item_row = items_df[items_df['name'].str.contains(item_name, case=False, na=False)]
        
        if item_row.empty:
            return Response(
                {"success": False, "found": False, "message": f"Item not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get the first matching item
        item = item_row.iloc[0].to_dict()
        item_id = item['item_id']
        
        # Check if item is placed
        placement = None
        if placements_df is not None and not placements_df.empty:
            placement_row = placements_df[placements_df['item_id'] == item_id]
            if not placement_row.empty:
                placement = placement_row.iloc[0].to_dict()
        
        # Determine retrieval steps (simplified)
        retrieval_steps = []
        
        if placement:
            # In a real implementation, you would calculate actual retrieval steps
            # This is a simplified version
            retrieval_steps.append({
                "step": 1,
                "action": "retrieve",
                "itemId": item_id,
                "itemName": item['name']
            })
        
        return Response({
            "success": True,
            "found": True,
            "item": {
                "itemId": item_id,
                "name": item['name'],
                "containerId": placement['container_id'] if placement else None,
                "position": {
                    "startCoordinates": {
                        "width": placement['x_cm'] if placement else 0,
                        "depth": placement['y_cm'] if placement else 0,
                        "height": placement['z_cm'] if placement else 0
                    },
                    "endCoordinates": {
                        "width": placement['x_cm'] + placement['width_cm'] if placement else 0,
                        "depth": placement['y_cm'] + placement['depth_cm'] if placement else 0,
                        "height": placement['z_cm'] + placement['height_cm'] if placement else 0
                    }
                }
            },
            "retrievalSteps": retrieval_steps
        })
    except Exception as e:
        logger.error(f"Error in search_item: {str(e)}")
        return Response(
            {"success": False, "message": f"Error searching item: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def retrieve_item(request):
    """Mark an item as retrieved."""
    try:
        item_id = request.data.get('item_id')
        user_id = request.data.get('user_id', 'anonymous')
        
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Load data
        items_df, _ = placement_manager.load_from_csv()
        
        if items_df is None:
            return Response(
                {"success": False, "message": "Items data not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find the item
        item_idx = items_df[items_df['item_id'] == item_id].index
        
        if len(item_idx) == 0:
            return Response(
                {"success": False, "message": f"Item {item_id} not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update usage count if available
        idx = item_idx[0]
        if 'usage_limit' in items_df.columns:
            current_uses = items_df.at[idx, 'usage_limit']
            
            if pd.notna(current_uses) and current_uses > 0:
                items_df.at[idx, 'usage_limit'] = current_uses - 1
        
        # Save back to CSV
        items_df.to_csv(placement_manager.data_dir / 'input_items.csv', index=False)
        
        # Generate log
        placement_manager.generate_log('retrieval', user_id, item_id)
        
        return Response({
            "success": True,
            "message": f"Item {item_id} retrieved"
        })
    except Exception as e:
        logger.error(f"Error in retrieve_item: {str(e)}")
        return Response(
            {"success": False, "message": f"Error retrieving item: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def identify_waste(request):
    """Identify expired items and items with zero uses left."""
    try:
        waste_items = placement_manager.identify_waste()
        
        return Response({
            "success": True,
            "wasteItems": waste_items
        })
    except Exception as e:
        logger.error(f"Error in identify_waste: {str(e)}")
        return Response(
            {"success": False, "message": f"Error identifying waste: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def return_plan(request):
    """Generate a plan for returning waste items."""
    try:
        undocking_container_id = request.data.get('undockingContainerId')
        undocking_date = request.data.get('undockingDate')
        max_weight = request.data.get('maxWeight', float('inf'))
        
        if not undocking_container_id:
            return Response(
                {"success": False, "message": "Undocking container ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get waste items
        waste_items = placement_manager.identify_waste()
        
        if not waste_items:
            return Response({
                "success": True,
                "returnPlan": [],
                "retrievalSteps": [],
                "returnManifest": {
                    "undockingContainerId": undocking_container_id,
                    "undockingDate": undocking_date,
                    "returnItems": [],
                    "totalVolume": 0,
                    "totalWeight": 0
                }
            })
        
        # Load data
        items_df, containers_df = placement_manager.load_from_csv()
        
        if items_df is None or containers_df is None:
            return Response(
                {"success": False, "message": "Data not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create return plan
        return_plan = []
        retrieval_steps = []
        return_items = []
        total_volume = 0
        total_weight = 0
        
        for i, waste_item in enumerate(waste_items):
            item_id = waste_item['item_id']
            
            # Find item details
            item_row = items_df[items_df['item_id'] == item_id]
            if item_row.empty:
                continue
            
            item = item_row.iloc[0]
            item_weight = item.get('weight_kg', 0)
            
            # Check if adding this item would exceed max weight
            if total_weight + item_weight > max_weight:
                continue
            
            # Add to return plan
            return_plan.append({
                "step": i + 1,
                "itemId": item_id,
                "itemName": waste_item['name'],
                "fromContainer": waste_item['containerId'],
                "toContainer": undocking_container_id
            })
            
            # Add retrieval step
            retrieval_steps.append({
                "step": i + 1,
                "action": "retrieve",
                "itemId": item_id,
                "itemName": waste_item['name']
            })
            
            # Add to return items
            return_items.append({
                "itemId": item_id,
                "name": waste_item['name'],
                "reason": waste_item['reason']
            })
            
            # Update totals
            total_weight += item_weight
            item_volume = item['width_cm'] * item['depth_cm'] * item['height_cm']
            total_volume += item_volume
        
        return Response({
            "success": True,
            "returnPlan": return_plan,
            "retrievalSteps": retrieval_steps,
            "returnManifest": {
                "undockingContainerId": undocking_container_id,
                "undockingDate": undocking_date,
                "returnItems": return_items,
                "totalVolume": total_volume,
                "totalWeight": total_weight
            }
        })
    except Exception as e:
        logger.error(f"Error in return_plan: {str(e)}")
        return Response(
            {"success": False, "message": f"Error generating return plan: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def complete_undocking(request):
    """Remove waste items after undocking."""
    try:
        undocking_container_id = request.data.get('undockingContainerId')
        user_id = request.data.get('user_id', 'anonymous')
        
        if not undocking_container_id:
            return Response(
                {"success": False, "message": "Undocking container ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get waste items
        waste_items = placement_manager.identify_waste()
        
        if not waste_items:
            return Response({
                "success": True,
                "itemsRemoved": 0
            })
        
        # Load data
        items_df, _ = placement_manager.load_from_csv()
        placements_df, _ = placement_manager.load_results()
        
        if items_df is None or placements_df is None:
            return Response(
                {"success": False, "message": "Data not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Remove waste items
        items_removed = 0
        
        for waste_item in waste_items:
            item_id = waste_item['item_id']
            
            # Remove from placements
            if not placements_df.empty:
                placements_df = placements_df[placements_df['item_id'] != item_id]
            
            # Generate log
            placement_manager.generate_log('disposal', user_id, item_id, {
                'reason': waste_item['reason']
            })
            
            items_removed += 1
        
        # Save back to CSV
        if not placements_df.empty:
            placements_df.to_csv(placement_manager.data_dir / 'placed_items.csv', index=False)
        
        return Response({
            "success": True,
            "itemsRemoved": items_removed
        })
    except Exception as e:
        logger.error(f"Error in complete_undocking: {str(e)}")
        return Response(
            {"success": False, "message": f"Error completing undocking: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def simulate_day(request):
    """Simulate the passage of time."""
    try:
        num_days = request.data.get('numOfDays')
        to_timestamp = request.data.get('toTimestamp')
        items_to_be_used = request.data.get('itemsToBeUsedPerDay', [])
        
        if not num_days and not to_timestamp:
            return Response(
                {"success": False, "message": "Number of days or target date is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate num_days if to_timestamp is provided
        if not num_days and to_timestamp:
            try:
                target_date = datetime.strptime(to_timestamp, '%Y-%m-%d')
                today = datetime.now()
                num_days = (target_date - today).days
            except:
                return Response(
                    {"success": False, "message": "Invalid target date format"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Simulate days
        result = placement_manager.simulate_days(num_days, items_to_be_used)
        
        return Response(result)
    except Exception as e:
        logger.error(f"Error in simulate_day: {str(e)}")
        return Response(
            {"success": False, "message": f"Error simulating days: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def import_items(request):
    """Import items from a CSV file."""
    parser_classes = (MultiPartParser, FileUploadParser)
    
    try:
        if 'file' not in request.FILES:
            return Response(
                {"success": False, "message": "No file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # Check file type
        if not uploaded_file.name.endswith('.csv'):
            return Response(
                {"success": False, "message": "Only CSV files are supported"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Read the file
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            return Response(
                {"success": False, "message": f"Error reading CSV file: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate required columns for items
        required_columns = ['item_id', 'name', 'width_cm', 'depth_cm', 'height_cm']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return Response(
                {"success": False, "message": f"Missing required columns: {', '.join(missing_columns)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if this is an items file
        is_items_file = all(col in df.columns for col in required_columns)
        
        if is_items_file:
            # Check for existing file
            items_path = placement_manager.data_dir / 'input_items.csv'
            
            if items_path.exists():
                # Load existing data
                existing_df = pd.read_csv(items_path)
                
                # Check for duplicates
                common_ids = set(df['item_id']).intersection(set(existing_df['item_id']))
                
                if common_ids:
                    # Update existing items and add new ones
                    for item_id in df['item_id']:
                        existing_idx = existing_df[existing_df['item_id'] == item_id].index
                        if len(existing_idx) > 0:
                            # Update existing item
                            existing_df.loc[existing_idx[0]] = df[df['item_id'] == item_id].iloc[0]
                        else:
                            # Add new item
                            existing_df = pd.concat([existing_df, df[df['item_id'] == item_id]], ignore_index=True)
                else:
                    # Append new items
                    existing_df = pd.concat([existing_df, df], ignore_index=True)
                
                # Save merged data
                existing_df.to_csv(items_path, index=False)
                
                return Response({
                    "success": True,
                    "message": "Items merged with existing data",
                    "itemsImported": len(df),
                    "errors": []
                })
            else:
                # Save new file
                df.to_csv(items_path, index=False)
                
                return Response({
                    "success": True,
                    "message": "Items imported successfully",
                    "itemsImported": len(df),
                    "errors": []
                })
        else:
            return Response(
                {"success": False, "message": "Invalid items file format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Error in import_items: {str(e)}")
        return Response(
            {"success": False, "message": f"Error importing items: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def import_containers(request):
    """Import containers from a CSV file."""
    parser_classes = (MultiPartParser, FileUploadParser)
    
    try:
        if 'file' not in request.FILES:
            return Response(
                {"success": False, "message": "No file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # Check file type
        if not uploaded_file.name.endswith('.csv'):
            return Response(
                {"success": False, "message": "Only CSV files are supported"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Read the file
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            return Response(
                {"success": False, "message": f"Error reading CSV file: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate required columns for containers
        required_columns = ['container_id', 'width_cm', 'depth_cm', 'height_cm', 'zone']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return Response(
                {"success": False, "message": f"Missing required columns: {', '.join(missing_columns)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if this is a containers file
        is_containers_file = all(col in df.columns for col in required_columns)
        
        if is_containers_file:
            # Check for existing file
            containers_path = placement_manager.data_dir / 'containers.csv'
            
            if containers_path.exists():
                # Load existing data
                existing_df = pd.read_csv(containers_path)
                
                # Check for duplicates
                common_ids = set(df['container_id']).intersection(set(existing_df['container_id']))
                
                if common_ids:
                    # Update existing containers and add new ones
                    for container_id in df['container_id']:
                        existing_idx = existing_df[existing_df['container_id'] == container_id].index
                        if len(existing_idx) > 0:
                            # Update existing container
                            existing_df.loc[existing_idx[0]] = df[df['container_id'] == container_id].iloc[0]
                        else:
                            # Add new container
                            existing_df = pd.concat([existing_df, df[df['container_id'] == container_id]], ignore_index=True)
                else:
                    # Append new containers
                    existing_df = pd.concat([existing_df, df], ignore_index=True)
                
                # Save merged data
                existing_df.to_csv(containers_path, index=False)
                
                return Response({
                    "success": True,
                    "message": "Containers merged with existing data",
                    "containersImported": len(df),
                    "errors": []
                })
            else:
                # Save new file
                df.to_csv(containers_path, index=False)
                
                return Response({
                    "success": True,
                    "message": "Containers imported successfully",
                    "containersImported": len(df),
                    "errors": []
                })
        else:
            return Response(
                {"success": False, "message": "Invalid containers file format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Error in import_containers: {str(e)}")
        return Response(
            {"success": False, "message": f"Error importing containers: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def export_arrangement(request):
    """Export the current arrangement to a CSV file."""
    try:
        # Load placement data
        placements_df, _ = placement_manager.load_results()
        
        if placements_df is None or placements_df.empty:
            return Response(
                {"success": False, "message": "No placement data found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create arrangement CSV
        arrangement_data = []
        
        for _, placement in placements_df.iterrows():
            item_id = placement['item_id']
            container_id = placement['container_id']
            start_coords = (placement['x_cm'], placement['y_cm'], placement['z_cm'])
            end_coords = (
                placement['x_cm'] + placement['width_cm'],
                placement['y_cm'] + placement['depth_cm'],
                placement['z_cm'] + placement['height_cm']
            )
            
            arrangement_data.append({
                'Item ID': item_id,
                'Container ID': container_id,
                'Coordinates': f"({start_coords[0]},{start_coords[1]},{start_coords[2]}),({end_coords[0]},{end_coords[1]},{end_coords[2]})"
            })
        
        arrangement_df = pd.DataFrame(arrangement_data)
        
        # Save to CSV
        csv_path = placement_manager.data_dir / 'arrangement.csv'
        arrangement_df.to_csv(csv_path, index=False)
        
        # Return file path (in a real system, you would serve the file directly)
        return Response({
            "success": True,
            "message": "Arrangement exported successfully",
            "file_path": str(csv_path)
        })
    except Exception as e:
        logger.error(f"Error in export_arrangement: {str(e)}")
        return Response(
            {"success": False, "message": f"Error exporting arrangement: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_logs(request):
    """Get logs filtered by various criteria."""
    try:
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        item_id = request.query_params.get('itemId')
        user_id = request.query_params.get('userId')
        action_type = request.query_params.get('actionType')
        
        logs = placement_manager.get_logs(start_date, end_date, item_id, user_id, action_type)
        
        return Response({
            "logs": logs
        })
    except Exception as e:
        logger.error(f"Error in get_logs: {str(e)}")
        return Response(
            {"success": False, "message": f"Error getting logs: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )