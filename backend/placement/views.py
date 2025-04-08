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
    manager = PlacementManager()
    stats = manager.get_placement_efficiency()
    
    # If no stats found, try to load from CSV and recalculate
    if stats is None or not stats.get('success', False):
        _, placement_df = manager.load_from_csv()
        if placement_df is not None:
            stats = manager.get_placement_efficiency()
    
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
    manager = PlacementManager()
    recommendations = manager.get_recommendations()
    if not recommendations:
        # If no recommendations, try to generate them from unplaced items
        _, unplaced_df = manager.load_results()
        if unplaced_df is not None and not unplaced_df.empty:
            recommendations = manager.get_recommendations()
    serializer = PlacementRecommendationSerializer(recommendations, many=True)
    return Response(serializer.data)

# API view to retrieve placement results from CSV files
@api_view(['GET'])
def get_results(request):
    manager = PlacementManager()
    placements_df, unplaced_df = manager.load_results()
    
    # If no results found, try to process the data
    if placements_df is None or unplaced_df is None:
        items_df, containers_df = manager.load_from_csv()
        if items_df is not None and containers_df is not None:
            placements_df, unplaced_df = manager.place_items(items_df, containers_df)
    
    # Convert DataFrames to dictionaries
    placements = placements_df.to_dict(orient='records') if placements_df is not None else []
    unplaced = unplaced_df.to_dict(orient='records') if unplaced_df is not None else []
    
    # Load items and containers data
    items_df, containers_df = manager.load_from_csv()
    items = items_df.to_dict(orient='records') if items_df is not None else []
    containers = containers_df.to_dict(orient='records') if containers_df is not None else []
    
    # Calculate container utilization
    container_utilization = {}
    for container in containers:
        container_items = [p for p in placements if p['container_id'] == container['container_id']]
        used_volume = sum(item['width_cm'] * item['height_cm'] * item['depth_cm'] for item in container_items)
        total_volume = container['width_cm'] * container['height_cm'] * container['depth_cm']
        utilization = (used_volume / total_volume * 100) if total_volume > 0 else 0
        
        container_utilization[container['container_id']] = {
            'utilization': round(utilization, 2),
            'used_volume': round(used_volume, 2),
            'total_volume': round(total_volume, 2)
        }
    
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
    item_id = request.query_params.get('item_id')
    item_name = request.query_params.get('item_name')
    
    manager = PlacementManager()
    items_df, _ = manager.load_from_csv()
    
    if items_df is None:
        return Response({
            'success': False,
            'message': 'No items data found'
        })
    
    # Search by ID or name
    if item_id:
        item = items_df[items_df['item_id'] == item_id]
    elif item_name:
        item = items_df[items_df['name'].str.contains(item_name, case=False, na=False)]
    else:
        return Response({
            'success': False,
            'message': 'Please provide either item_id or item_name'
        })
    
    if item.empty:
        return Response({
            'success': False,
            'message': 'Item not found'
        })
    
    # Get placement information
    placements_df, _ = manager.load_results()
    placement = None
    if placements_df is not None:
        placement = placements_df[placements_df['item_id'] == item.iloc[0]['item_id']]
    
    # Format response
    item_data = item.iloc[0].to_dict()
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
    
    return Response(response_data)

# API view for retrieving an item from its container
@api_view(['POST'])
def retrieve_item(request):
    """Retrieve an item from its container."""
    item_id = request.data.get('item_id')
    user_id = request.data.get('user_id', 'system')
    
    if not item_id:
        return Response({
            'success': False,
            'message': 'Item ID is required'
        })
    
    manager = PlacementManager()
    items_df, _ = manager.load_from_csv()
    placements_df, _ = manager.load_results()
    
    if items_df is None or placements_df is None:
        return Response({
            'success': False,
            'message': 'No data found'
        })
    
    # Find item and its placement
    item = items_df[items_df['item_id'] == item_id]
    placement = placements_df[placements_df['item_id'] == item_id]
    
    if item.empty or placement.empty:
        return Response({
            'success': False,
            'message': 'Item not found or not placed'
        })
    
    # Generate log entry
    log_entry = manager.generate_log(
        action_type='retrieve',
        user_id=user_id,
        item_id=item_id,
        details=f"Item retrieved from container {placement.iloc[0]['container_id']}"
    )
    
    return Response({
        'success': True,
        'message': f"Item {item_id} has been retrieved successfully",
        'log': log_entry
    })

# Dummy view for waste identification (to be implemented)
@api_view(['GET'])
def identify_waste(request):
    manager = PlacementManager()
    waste_items = manager.identify_waste()
    return Response({
        'success': True,
        'waste_items': waste_items
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
        'containers': containers
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
