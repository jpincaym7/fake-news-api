"""
URLs de la aplicación API
========================
Configuración de rutas para los endpoints de la API
"""

from django.urls import path, include
from . import views

urlpatterns = [
    # Endpoint principal para análisis
    path('analyze/', views.analyze_news, name='analyze_news'),
    
    # Obtener análisis específico
    path('analysis/<uuid:analysis_id>/', views.get_analysis, name='get_analysis'),
    
    # Información del modelo
    path('model/info/', views.model_info, name='model_info'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
    
    # Estadísticas
    path('stats/', views.api_stats, name='api_stats'),
    
    # Documentación
    path('docs/', views.api_documentation, name='api_documentation'),
    path('', views.APIHomeView.as_view(), name='api_home'),
]