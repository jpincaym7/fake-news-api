"""
fakenews_api URL Configuration
==============================
Configuración principal de URLs del proyecto
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET


@require_GET
def root_endpoint(request):
    """
    Endpoint raíz con información básica de la API
    """
    return JsonResponse({
        'message': 'Fake News Detection API',
        'version': '1.0.0',
        'status': 'active',
        'endpoints': {
            'analyze': '/api/analyze/',
            'health': '/api/health/',
            'stats': '/api/stats/',
            'model_info': '/api/model/info/',
            'documentation': '/api/docs/',
            'admin': '/admin/'
        }
    })


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('api.urls')),
    
    # Root endpoint
    path('', root_endpoint, name='root'),
]

# Configuración para archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
