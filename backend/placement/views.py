from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Container, Item
from .serializers import (
    ContainerSerializer, 
    ItemSerializer, 
    PlacementResponseSerializer,
    PlacementStatisticsSerializer,
    PlacementRecommendationSerializer
)
from .algorithms import PlacementManager
import pandas as pd

# Model ViewSets for basic CRUD operations
class ContainerViewSet(viewsets.ModelViewSet):
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

# API view for getting placement statistics
@api_view(['GET'])
def get_placement_stats(request):
    print("DEBUG: get_placement_stats called")
    manager = PlacementManager()
    stats = manager.get_placement_efficiency()
    print(f"DEBUG: Stats: {stats}")
    
    # If no stats found, try to load from CSV and recalculate
    if stats is None or not stats.get('success', False):
        print("DEBUG: No stats found, trying to load from CSV")
        _, placement_df = manager.load_from_csv()
        if placement_df is not None:
            print("DEBUG: Loaded placement data, recalculating stats")
            stats = manager.get_placement_efficiency()
    
    print(f"DEBUG: Final stats: {stats}")
    return Response({
        'success': True,
        'stats': stats.get('statistics', {}) if stats else {}
    })

# API view to process and place items
@api_view(['GET', 'POST'])
def process_data(request):
    manager = PlacementManager()
    items_df, containers_df = manager.load_from_csv()
    if items_df is None or containers_df is None:
         return Response({'success': False, 'message': 'CSV files not found'})
    
    placements_df, unplaced_df = manager.place_items(items_df, containers_df)
    placements = placements_df.to_dict(orient='records') if placements_df is not None else []
    unplaced = unplaced_df.to_dict(orient='records') if unplaced_df is not None else []
    return Response({
         'success': True,
         'placements': placements,
         'unplaced': unplaced
    })

# API view for getting placement recommendations for unplaced items
@api_view(['GET'])
def get_recommendations(request):
    print("DEBUG: get_recommendations called")
    manager = PlacementManager()
    
    # First try to load data from CSV files
    items_df, containers_df = manager.load_from_csv()
    
    if items_df is None or containers_df is None:
        print("DEBUG: No data found")
        return Response({
            'success': False,
            'message': 'No data found'
        })
    
    # Try to load results directly from CSV files
    try:
        placed_path = manager.data_dir / 'placed_items.csv'
        unplaced_path = manager.data_dir / 'unplaced_items.csv'
        
        print(f"DEBUG: Looking for placement files at {placed_path} and {unplaced_path}")
        
        placements_df = None
        unplaced_df = None
        
        if placed_path.exists():
            try:
                placements_df = pd.read_csv(placed_path)
                print(f"DEBUG: Loaded placed items: {len(placements_df)} items")
            except Exception as e:
                print(f"DEBUG: Error loading placed items: {str(e)}")
        else:
            print(f"DEBUG: Placed items file not found at {placed_path}")
            
        if unplaced_path.exists():
            try:
                unplaced_df = pd.read_csv(unplaced_path)
                print(f"DEBUG: Loaded unplaced items: {len(unplaced_df)} items")
            except Exception as e:
                print(f"DEBUG: Error loading unplaced items: {str(e)}")
        else:
            print(f"DEBUG: Unplaced items file not found at {unplaced_path}")
    except Exception as e:
        print(f"DEBUG: Error loading placement data: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error loading placement data: {str(e)}'
        })
    
    # If no unplaced items found, return empty list
    if unplaced_df is None or unplaced_df.empty:
        print("DEBUG: No unplaced items found")
        return Response([])
    
    # Calculate recommendations
    recommendations = []
    print(f"DEBUG: Calculating recommendations for {len(unplaced_df)} unplaced items")
    
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
    print(f"DEBUG: Generated {len(recommendations)} recommendations")
    
    return Response(recommendations)

# API view to retrieve placement results from CSV files
@api_view(['GET'])
def get_results(request):
    print("DEBUG: get_results called")
    manager = PlacementManager()
    
    # The error is here - load_results is in the class but views.py is trying to use it incorrectly
    print("DEBUG: Loading placement results")
    items_df, containers_df = manager.load_from_csv()
    
    try:
        # Try to load results directly from CSV files
        placed_path = manager.data_dir / 'placed_items.csv'
        unplaced_path = manager.data_dir / 'unplaced_items.csv'
        
        print(f"DEBUG: Looking for placement files at {placed_path} and {unplaced_path}")
        
        placements_df = None
        unplaced_df = None
        
        if placed_path.exists():
            try:
                placements_df = pd.read_csv(placed_path)
                print(f"DEBUG: Loaded placed items: {len(placements_df)} items")
            except Exception as e:
                print(f"DEBUG: Error loading placed items: {str(e)}")
        else:
            print(f"DEBUG: Placed items file not found at {placed_path}")
            
        if unplaced_path.exists():
            try:
                unplaced_df = pd.read_csv(unplaced_path)
                print(f"DEBUG: Loaded unplaced items: {len(unplaced_df)} items")
            except Exception as e:
                print(f"DEBUG: Error loading unplaced items: {str(e)}")
        else:
            print(f"DEBUG: Unplaced items file not found at {unplaced_path}")
    
    except Exception as e:
        print(f"DEBUG: Error in get_results: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error loading results: {str(e)}'
        })
    
    # If no results found or loading failed, try to process the data
    if placements_df is None or unplaced_df is None:
        print("DEBUG: No placement results found, trying to process data")
        items_df, containers_df = manager.load_from_csv()
        if items_df is not None and containers_df is not None:
            placements_df, unplaced_df = manager.place_items(items_df, containers_df)
    
    # Convert DataFrames to dictionaries
    placements = placements_df.to_dict(orient='records') if placements_df is not None else []
    unplaced = unplaced_df.to_dict(orient='records') if unplaced_df is not None else []
    
    # Load items and containers data
    items = items_df.to_dict(orient='records') if items_df is not None else []
    containers = containers_df.to_dict(orient='records') if containers_df is not None else []
    
    # Calculate container utilization
    container_utilization = {}
    try:
        for container in containers:
            container_id = container['container_id']
            container_items = [p for p in placements if p['container_id'] == container_id]
            used_volume = sum(item['width_cm'] * item['height_cm'] * item['depth_cm'] for item in container_items)
            total_volume = container['width_cm'] * container['height_cm'] * container['depth_cm']
            utilization = (used_volume / total_volume * 100) if total_volume > 0 else 0
            
            container_utilization[container_id] = {
                'utilization': round(utilization, 2),
                'used_volume': round(used_volume, 2),
                'total_volume': round(total_volume, 2)
            }
    except Exception as e:
        print(f"DEBUG: Error calculating utilization: {str(e)}")
    
    print("DEBUG: Successfully processed results")
    return Response({
        'success': True,
        'placed_items': placements,
        'unplaced_items': unplaced,
        'items': items,
        'containers': containers,
        'container_utilization': container_utilization
    })

# Dummy view for placing an individual item (extend as needed)
@api_view(['POST'])
def place_item(request):
    # In production, extract and validate the request data,
    # then call the placement logic and update models as needed.
    return Response({
        'success': True,
        'message': 'Item placed successfully.'
    })

# API view for searching for an item
@api_view(['GET'])
def search_item(request):
    """Search for items by ID or name."""
    print("DEBUG: search_item called")
    item_id = request.query_params.get('item_id')
    item_name = request.query_params.get('item_name')
    print(f"DEBUG: Search params - item_id: {item_id}, item_name: {item_name}")
    
    manager = PlacementManager()
    items_df, _ = manager.load_from_csv()
    
    if items_df is None:
        print("DEBUG: No items data found")
        return Response({
            'success': False,
            'message': 'No items data found'
        })
    
    # Search by ID or name
    if item_id:
        print(f"DEBUG: Searching by item_id: {item_id}")
        item = items_df[items_df['item_id'] == item_id]
    elif item_name:
        print(f"DEBUG: Searching by item_name: {item_name}")
        item = items_df[items_df['name'].str.contains(item_name, case=False, na=False)]
    else:
        print("DEBUG: No search parameters provided")
        return Response({
            'success': False,
            'message': 'Please provide either item_id or item_name'
        })
    
    if item.empty:
        print("DEBUG: Item not found")
        return Response({
            'success': False,
            'message': 'Item not found'
        })
    
    # Get placement information
    print("DEBUG: Loading placement results")
    try:
        # Try to load results directly from CSV files
        placed_path = manager.data_dir / 'placed_items.csv'
        print(f"DEBUG: Looking for placement file at {placed_path}")
        
        placements_df = None
        
        if placed_path.exists():
            try:
                placements_df = pd.read_csv(placed_path)
                print(f"DEBUG: Loaded placed items: {len(placements_df)} items")
            except Exception as e:
                print(f"DEBUG: Error loading placed items: {str(e)}")
        else:
            print(f"DEBUG: Placed items file not found at {placed_path}")
            
        placement = None
        if placements_df is not None:
            placement = placements_df[placements_df['item_id'] == item.iloc[0]['item_id']]
            print(f"DEBUG: Placement found: {not placement.empty if not placement.empty else False}")
    except Exception as e:
        print(f"DEBUG: Error loading placement data: {str(e)}")
        placement = None
    
    # Format response
    item_data = item.iloc[0].to_dict()
    print(f"DEBUG: Item data: {item_data}")
    
    response_data = {
        'success': True,
        'found': True,
        'item': {
            'itemId': item_data['item_id'],
            'name': item_data['name'],
            'containerId': placement.iloc[0]['container_id'] if placement is not None and not placement.empty else None,
            'position': {
                'startCoordinates': {
                    'width': placement.iloc[0]['x_cm'] if placement is not None and not placement.empty else None,
                    'depth': placement.iloc[0]['y_cm'] if placement is not None and not placement.empty else None,
                    'height': placement.iloc[0]['z_cm'] if placement is not None and not placement.empty else None
                }
            }
        }
    }
    
    print(f"DEBUG: Response data: {response_data}")
    return Response(response_data)

# API view for retrieving an item from its container
@api_view(['POST'])
def retrieve_item(request):
    """Retrieve an item from its container."""
    print("DEBUG: retrieve_item called")
    item_id = request.data.get('item_id')
    user_id = request.data.get('user_id', 'system')
    print(f"DEBUG: Retrieve params - item_id: {item_id}, user_id: {user_id}")
    
    if not item_id:
        print("DEBUG: Item ID is required")
        return Response({
            'success': False,
            'message': 'Item ID is required'
        })
    
    manager = PlacementManager()
    print("DEBUG: Loading items and placements")
    items_df, _ = manager.load_from_csv()
    
    try:
        # Try to load results directly from CSV files
        placed_path = manager.data_dir / 'placed_items.csv'
        print(f"DEBUG: Looking for placement file at {placed_path}")
        
        placements_df = None
        
        if placed_path.exists():
            try:
                placements_df = pd.read_csv(placed_path)
                print(f"DEBUG: Loaded placed items: {len(placements_df)} items")
            except Exception as e:
                print(f"DEBUG: Error loading placed items: {str(e)}")
        else:
            print(f"DEBUG: Placed items file not found at {placed_path}")
    except Exception as e:
        print(f"DEBUG: Error loading placement data: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error loading placement data: {str(e)}'
        })
    
    if items_df is None or placements_df is None:
        print("DEBUG: No data found")
        return Response({
            'success': False,
            'message': 'No data found'
        })
    
    # Find item and its placement
    print(f"DEBUG: Finding item {item_id}")
    item = items_df[items_df['item_id'] == item_id]
    placement = placements_df[placements_df['item_id'] == item_id]
    
    if item.empty or placement.empty:
        print("DEBUG: Item not found or not placed")
        return Response({
            'success': False,
            'message': 'Item not found or not placed'
        })
    
    # Generate log entry
    print("DEBUG: Generating log entry")
    log_entry = manager.generate_log(
        action_type='retrieve',
        user_id=user_id,
        item_id=item_id,
        details=f"Item retrieved from container {placement.iloc[0]['container_id']}"
    )
    
    print(f"DEBUG: Log entry: {log_entry}")
    return Response({
        'success': True,
        'message': f"Item {item_id} has been retrieved successfully",
        'log': log_entry
    })

# Dummy view for waste identification (to be implemented)
@api_view(['GET'])
def identify_waste(request):
    """Identify expired items or items with zero uses left."""
    print("DEBUG: identify_waste view called")
    manager = PlacementManager()
    
    try:
        waste_items = manager.identify_waste()
        print(f"DEBUG: Retrieved {len(waste_items)} waste items")
        return Response({
            'success': True,
            'waste_items': waste_items,
            'wasteItems': waste_items  # Add camelCase version for compatibility
        })
    except Exception as e:
        print(f"DEBUG: Error in identify_waste view: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return Response({
            'success': False,
            'message': f"Error identifying waste items: {str(e)}",
            'waste_items': [],
            'wasteItems': []  # Add camelCase version for compatibility
        })

# Dummy view for returning undocking plan (to be implemented)
@api_view(['POST'])
def return_plan(request):
    # Implement your undocking plan logic here
    return Response({
        'success': True,
        'plan': {}
    })

# Dummy view for completing undocking (to be implemented)
@api_view(['POST'])
def complete_undocking(request):
    # Implement your undocking completion logic here
    return Response({
        'success': True,
        'message': 'Undocking completed.'
    })

# Dummy view for simulation of day (to be implemented)
@api_view(['POST'])
def simulate_day(request):
    # Extract parameters from request.data
    num_days = request.data.get('num_of_days', 1)
    items_to_use = request.data.get('items_to_use', [])
    manager = PlacementManager()
    result = manager.simulate_days(num_days, items_to_use)
    return Response(result)

# Dummy view for import_items (to be implemented)
@api_view(['POST'])
def import_items(request):
    # Implement your import logic here
    return Response({
        'success': True,
        'message': 'Items imported successfully.'
    })

# Dummy view for import_containers (to be implemented)
@api_view(['POST'])
def import_containers(request):
    # Implement your import logic here
    return Response({
        'success': True,
        'message': 'Containers imported successfully.'
    })

# Dummy view for export_arrangement (to be implemented)
@api_view(['GET'])
def export_arrangement(request):
    # Implement your export logic here
    return Response({
        'success': True,
        'arrangement': {}
    })

# Dummy view for logs (to be implemented)
@api_view(['GET'])
def get_logs(request):
    manager = PlacementManager()
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    item_id = request.query_params.get('item_id')
    user_id = request.query_params.get('user_id')
    action_type = request.query_params.get('action_type')
    logs = manager.get_logs(start_date, end_date, item_id, user_id, action_type)
    return Response({
        'success': True,
        'logs': logs
    })

@api_view(['GET'])
def get_containers(request):
    manager = PlacementManager()
    containers_df = manager.load_containers()
    
    # If no containers found, try to load from CSV
    if containers_df is None:
        _, containers_df = manager.load_from_csv()
    
    containers = containers_df.to_dict(orient='records') if containers_df is not None else []
    return Response({
        'success': True,
        'containers': containers,
        'containersData': containers  # Add camelCase version for compatibility
    })

@api_view(['GET'])
def get_items(request):
    manager = PlacementManager()
    items_df = manager.load_items()
    
    # If no items found, try to load from CSV
    if items_df is None:
        items_df, _ = manager.load_from_csv()
    
    items = items_df.to_dict(orient='records') if items_df is not None else []
    return Response({
        'success': True,
        'items': items
    })

@api_view(['GET'])
def get_placement(request):
    manager = PlacementManager()
    placement_df = manager.load_placement()
    
    # If no placement found, try to load from CSV
    if placement_df is None:
        _, placement_df = manager.load_from_csv()
    
    placement = placement_df.to_dict(orient='records') if placement_df is not None else []
    return Response({
        'success': True,
        'placement': placement
    })



# backend/placement/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# views.py (updated placement_view)
@csrf_exempt
def placement_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if "items" not in data or "containers" not in data:
                return JsonResponse({"success": False, "error": "Missing required keys"}, status=400)
            
            # Process items and containers into DataFrames
            items_data = data['items']
            containers_data = data['containers']
            
            # Convert input keys to DataFrame columns (camelCase to snake_case)
            for item in items_data:
                item['item_id'] = item.pop('itemId')
                item['width_cm'] = item.pop('width')
                item['depth_cm'] = item.pop('depth')
                item['height_cm'] = item.pop('height')
                item['preferred_zone'] = item.get('preferredZone', '')
            
            for container in containers_data:
                container['container_id'] = container.pop('containerId')
                container['width_cm'] = container.pop('width')
                container['depth_cm'] = container.pop('depth')
                container['height_cm'] = container.pop('height')
                container['zone'] = container.get('zone', '')
                container['volume'] = container['width_cm'] * container['depth_cm'] * container['height_cm']
                container['name'] = container.get('name', f"Container {container['container_id']}")
            
            items_df = pd.DataFrame(items_data)
            containers_df = pd.DataFrame(containers_data)
            
            manager = PlacementManager()
            placements_df, unplaced_df = manager.place_items(items_df, containers_df)
            
            # Format placements
            placements = []
            if placements_df is not None and not placements_df.empty:
                for _, row in placements_df.iterrows():
                    start_width = row['x_cm']
                    start_depth = row['y_cm']
                    start_height = row['z_cm']
                    
                    end_width = start_width + row['width_cm']
                    end_depth = start_depth + row['depth_cm']
                    end_height = start_height + row['height_cm']
                    
                    placements.append({
                        "itemId": row['item_id'],
                        "containerId": row['container_id'],
                        "position": {
                            "startCoordinates": {
                                "width": start_width,
                                "depth": start_depth,
                                "height": start_height
                            },
                            "endCoordinates": {
                                "width": end_width,
                                "depth": end_depth,
                                "height": end_height
                            }
                        }
                    })
            
            # Return response with empty rearrangements (not implemented)
            return JsonResponse({
                "success": True,
                "placements": placements,
                "rearrangements": []
            })
            
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    else:
        return JsonResponse({"success": False, "error": "Only POST method is allowed"}, status=405)