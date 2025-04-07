from rest_framework import serializers
from .models import Container, Item, PlacementHistory

class ContainerSerializer(serializers.ModelSerializer):
    """
    Serializer for Container model with included calculated fields.
    """
    utilization_percentage = serializers.FloatField(read_only=True)
    total_volume = serializers.FloatField(read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Container
        fields = [
            'id', 'name', 'width_cm', 'height_cm', 'depth_cm', 
            'max_weight_kg', 'zone', 'used_volume', 'used_weight', 
            'is_full', 'utilization_percentage', 'total_volume', 'item_count'
        ]
    
    def get_item_count(self, obj):
        """Return the number of items in this container."""
        return obj.items.count()


class ItemSerializer(serializers.ModelSerializer):
    """
    Serializer for Item model with calculated volume field.
    """
    volume = serializers.FloatField(read_only=True)
    container_name = serializers.SerializerMethodField(read_only=True)
    container_zone = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Item
        fields = [
            'id', 'name', 'width_cm', 'height_cm', 'depth_cm', 
            'weight_kg', 'priority', 'preferred_zone', 'is_placed',
            'container', 'container_name', 'container_zone',
            'position_x', 'position_y', 'position_z',
            'rotation', 'placement_date', 'sensitive', 'volume'
        ]
    
    def get_container_name(self, obj):
        """Return the container name if available."""
        if obj.container:
            return obj.container.name
        return None
    
    def get_container_zone(self, obj):
        """Return the container zone if available."""
        if obj.container:
            return obj.container.zone
        return None


class PlacementHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for PlacementHistory model with detailed item and container info.
    """
    item_name = serializers.SerializerMethodField()
    container_name = serializers.SerializerMethodField()
    container_zone = serializers.SerializerMethodField()
    
    class Meta:
        model = PlacementHistory
        fields = [
            'id', 'item', 'item_name', 'container', 'container_name', 
            'container_zone', 'placement_date', 'success', 'reason'
        ]
    
    def get_item_name(self, obj):
        return obj.item.name
    
    def get_container_name(self, obj):
        return obj.container.name
    
    def get_container_zone(self, obj):
        return obj.container.zone


class PlacementResponseSerializer(serializers.Serializer):
    """
    Serializer for API responses from placement operations.
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    container_id = serializers.IntegerField(required=False)
    position_x = serializers.FloatField(required=False)
    position_y = serializers.FloatField(required=False)
    position_z = serializers.FloatField(required=False)


class PlacementRecommendationSerializer(serializers.Serializer):
    """
    Serializer for placement recommendations.
    """
    item_id = serializers.IntegerField()
    item_name = serializers.CharField()
    container_id = serializers.IntegerField()
    container_name = serializers.CharField()
    reasoning = serializers.CharField()
    score = serializers.FloatField()


class PlacementStatisticsSerializer(serializers.Serializer):
    """
    Serializer for placement statistics.
    """
    total_items_placed = serializers.IntegerField()
    space_utilization = serializers.FloatField()
    success_rate = serializers.FloatField()
    efficiency = serializers.FloatField()
    priority_satisfaction = serializers.FloatField(required=False)
    zone_match_rate = serializers.FloatField(required=False)
    container_utilization = serializers.ListField(child=serializers.DictField())


class ItemPositionSerializer(serializers.Serializer):
    """
    Serializer for item position coordinates in a container.
    """
    start_coordinates = serializers.DictField(child=serializers.FloatField())
    end_coordinates = serializers.DictField(child=serializers.FloatField())


class ItemPlacementSerializer(serializers.Serializer):
    """
    Serializer for item placement requests.
    """
    item_id = serializers.IntegerField()
    container_id = serializers.IntegerField()
    position = ItemPositionSerializer(required=False)
    user_id = serializers.CharField(required=False)


class ItemRetrievalSerializer(serializers.Serializer):
    """
    Serializer for item retrieval requests.
    """
    item_id = serializers.CharField()
    user_id = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField(required=False)


class WasteIdentificationSerializer(serializers.Serializer):
    """
    Serializer for identified waste items.
    """
    item_id = serializers.IntegerField()
    name = serializers.CharField()
    reason = serializers.CharField()
    container_id = serializers.IntegerField()
    position = ItemPositionSerializer()


class UndockingPlanSerializer(serializers.Serializer):
    """
    Serializer for undocking plan requests.
    """
    undocking_container_id = serializers.CharField()
    undocking_date = serializers.DateTimeField()
    max_weight = serializers.FloatField()


class SimulationRequestSerializer(serializers.Serializer):
    """
    Serializer for time simulation requests.
    """
    num_of_days = serializers.IntegerField(required=False)
    to_timestamp = serializers.DateTimeField(required=False)
    items_to_be_used_per_day = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )