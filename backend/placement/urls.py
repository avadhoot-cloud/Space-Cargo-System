# Place this in your backend/placement/urls.py file

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import placement_view

router = DefaultRouter()
router.register('containers', views.ContainerViewSet)
router.register('items', views.ItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Placement APIs
    path('api/placement', placement_view, name='placement'),
    path('statistics/', views.get_placement_stats, name='get_placement_stats'),
    path('process/', views.process_data, name='process_data'),
    path('results/', views.get_results, name='get_results'),
    path('recommendations/', views.get_recommendations, name='get_recommendations'),
    path('place/', views.place_item, name='place_item'),
    
    # Search and Retrieval APIs
    path('search/', views.search_item, name='search_item'),
    path('retrieve/', views.retrieve_item, name='retrieve_item'),
    
    # Waste Management APIs
    path('waste/identify/', views.identify_waste, name='identify_waste'),
    path('waste/return-plan/', views.return_plan, name='return_plan'),
    path('waste/complete-undocking/', views.complete_undocking, name='complete_undocking'),
    
    # Time Simulation API
    path('simulate/', views.simulate_day, name='simulate_day'),
    
    # Import/Export APIs
    path('import/items/', views.import_items, name='import_items'),
    path('import/containers/', views.import_containers, name='import_containers'),
    path('export/arrangement/', views.export_arrangement, name='export_arrangement'),
    
    # Logging API
    path('logs/', views.get_logs, name='get_logs'),
]
