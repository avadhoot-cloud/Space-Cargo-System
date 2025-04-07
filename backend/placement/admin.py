from django.contrib import admin
from .models import Container, Item, PlacementHistory

@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'zone', 'width_cm', 'height_cm', 'depth_cm', 'max_weight_kg', 'is_full')
    list_filter = ('zone', 'is_full')
    search_fields = ('name', 'zone')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'priority', 'preferred_zone', 'is_placed', 'container')
    list_filter = ('is_placed', 'preferred_zone', 'priority')
    search_fields = ('name',)

@admin.register(PlacementHistory)
class PlacementHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'container', 'placement_date', 'success')
    list_filter = ('success', 'placement_date')
    date_hierarchy = 'placement_date'
