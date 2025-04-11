from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def api_root(request):
    return JsonResponse({
        'message': 'Welcome to Space Cargo System API',
        'status': 'online',
        'endpoints': {
            'placement': '/placement/',
            'fastapi': '/api/'
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api_root'),

    # ✅ Add this line to support /api/placement/
    path('api/placement/', include('placement.urls')),

    # existing route still valid
    path('placement/', include('placement.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
