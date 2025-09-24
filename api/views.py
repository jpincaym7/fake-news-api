"""
Vistas de la API REST para Detección de Noticias Falsas
========================================================
Endpoints para la predicción y gestión del servicio de ML
"""

from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import json
import logging
from datetime import datetime

from .models import NewsAnalysis, APIUsage, ModelInfo
from .serializers import (
    NewsAnalysisRequestSerializer,
    NewsAnalysisResponseSerializer,
    ModelInfoSerializer,
    HealthCheckSerializer
)
from .ml_service import ml_service

logger = logging.getLogger(__name__)


class APIHomeView(TemplateView):
    """
    Vista principal de la API (página de documentación)
    """
    template_name = 'api/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_name'] = 'Fake News Detection API'
        context['version'] = '1.0.0'
        context['model_status'] = ml_service.is_ready()
        return context


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_news(request):
    """
    Endpoint principal para analizar noticias
    
    POST /api/analyze/
    {
        "text": "Texto de la noticia a analizar",
        "metadata": {
            "source": "opcional",
            "category": "opcional"
        }
    }
    """
    try:
        # Registrar uso de la API
        api_usage = APIUsage.objects.create(
            endpoint='/api/analyze/',
            method='POST',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            response_status=500,  # Default, will be updated
            response_time=0.0,    # Default, will be updated
            timestamp=datetime.now()
        )
        
        # Validar datos de entrada
        serializer = NewsAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            api_usage.response_status = 400
            api_usage.save()
            
            return Response({
                'status': 'error',
                'message': 'Datos de entrada inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener texto validado
        text = serializer.validated_data['text']
        metadata = serializer.validated_data.get('metadata', {})
        
        # Verificar que el servicio ML esté listo
        if not ml_service.is_ready():
            api_usage.response_status = 503
            api_usage.save()
            
            return Response({
                'status': 'error',
                'message': 'El servicio de análisis no está disponible temporalmente',
                'code': 'SERVICE_UNAVAILABLE'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Validar el texto con el servicio ML
        is_valid, error_message = ml_service.validate_text(text)
        if not is_valid:
            api_usage.response_status = 400
            api_usage.save()
            
            return Response({
                'status': 'error',
                'message': error_message,
                'code': 'INVALID_TEXT'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Realizar predicción
        try:
            prediction_result = ml_service.predict(text)
            
            # Guardar análisis en la base de datos
            news_analysis = NewsAnalysis.objects.create(
                text=text[:1000],  # Limitar texto guardado
                prediction=prediction_result['prediction'],
                confidence=prediction_result['confidence'],
                probability_real=prediction_result['probability_real'],
                probability_fake=prediction_result['probability_fake'],
                ip_address=get_client_ip(request)
            )
            
            # Preparar respuesta
            response_data = {
                'analysis_id': str(news_analysis.id),
                'prediction': prediction_result['prediction'],
                'confidence': round(prediction_result['confidence'], 3),
                'probabilities': {
                    'real': round(prediction_result['probability_real'], 3),
                    'fake': round(prediction_result['probability_fake'], 3)
                },
                'text_info': {
                    'length': prediction_result['text_length'],
                    'processed_length': prediction_result['processed_text_length']
                },
                'timestamp': prediction_result['timestamp'],
                'status': 'success'
            }
            
            # Finalizar registro de uso de API
            api_usage.response_status = 200
            api_usage.save()
            
            logger.info(f"Análisis exitoso: {news_analysis.id}")
            return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            api_usage.response_status = 500
            api_usage.save()
            
            logger.error(f"Error en predicción: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Error interno en el análisis',
                'code': 'PREDICTION_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error general en analyze_news: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Error interno del servidor',
            'code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_analysis(request, analysis_id):
    """
    Obtener resultado de un análisis específico
    
    GET /api/analysis/{analysis_id}/
    """
    try:
        analysis = NewsAnalysis.objects.get(id=analysis_id)
        
        response_data = {
            'analysis_id': str(analysis.id),
            'prediction': analysis.prediction,
            'confidence': analysis.confidence,
            'probabilities': {
                'real': analysis.probability_real,
                'fake': analysis.probability_fake
            },
            'created_at': analysis.created_at.isoformat(),
            'status': 'success'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except NewsAnalysis.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Análisis no encontrado',
            'code': 'NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error al obtener análisis: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Error interno del servidor',
            'code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def model_info(request):
    """
    Obtener información del modelo ML
    
    GET /api/model/info/
    """
    try:
        model_data = ml_service.get_model_info()
        
        # Actualizar o crear información del modelo en BD
        model_info_obj, created = ModelInfo.objects.get_or_create(
            model_name=model_data.get('model_name', 'default'),
            defaults={
                'version': '1.0.0',
                'accuracy': model_data.get('metrics', {}).get('accuracy', 0.0),
                'f1_score': model_data.get('metrics', {}).get('f1_score', 0.0),
                'training_date': datetime.now(),
                'is_active': model_data.get('model_loaded', False)
            }
        )
        
        serializer = ModelInfoSerializer(model_info_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error al obtener info del modelo: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Error al obtener información del modelo',
            'code': 'MODEL_INFO_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint de salud del servicio
    
    GET /api/health/
    """
    try:
        health_data = ml_service.get_health_status()
        
        # Añadir información adicional
        health_data.update({
            'database_connected': True,  # Si llega aquí, la BD está conectada
            'api_version': '1.0.0',
            'environment': 'production' if not settings.DEBUG else 'development'
        })
        
        # Determinar código de estado HTTP
        http_status = status.HTTP_200_OK if health_data['service_status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(health_data, status=http_status)
        
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return Response({
            'service_status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_stats(request):
    """
    Estadísticas de uso de la API
    
    GET /api/stats/
    """
    try:
        from django.db.models import Count, Q
        from datetime import timedelta
        from django.utils import timezone
        
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        
        stats = {
            'total_analyses': NewsAnalysis.objects.count(),
            'total_api_calls': APIUsage.objects.count(),
            'analyses_today': NewsAnalysis.objects.filter(created_at__date=today).count(),
            'analyses_last_week': NewsAnalysis.objects.filter(created_at__gte=week_ago).count(),
            'predictions_by_result': {
                'fake': NewsAnalysis.objects.filter(prediction='FALSA').count(),
                'real': NewsAnalysis.objects.filter(prediction='VERDADERA').count()
            },
            'api_calls_by_status': {
                'success': APIUsage.objects.filter(response_status=200).count(),
                'client_error': APIUsage.objects.filter(response_status__gte=400, response_status__lt=500).count(),
                'server_error': APIUsage.objects.filter(response_status__gte=500).count()
            },
            'model_status': ml_service.is_ready(),
            'timestamp': now.isoformat()
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Error al obtener estadísticas',
            'code': 'STATS_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_client_ip(request):
    """
    Obtener la IP del cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Vistas adicionales para la interfaz web (opcional)
def api_documentation(request):
    """
    Página de documentación de la API
    """
    context = {
        'endpoints': [
            {
                'url': '/api/analyze/',
                'method': 'POST',
                'description': 'Analizar una noticia para detectar si es falsa',
                'example': {
                    'text': 'Texto de la noticia...',
                    'metadata': {'source': 'ejemplo'}
                }
            },
            {
                'url': '/api/analysis/{id}/',
                'method': 'GET',
                'description': 'Obtener resultado de un análisis específico'
            },
            {
                'url': '/api/model/info/',
                'method': 'GET',
                'description': 'Información del modelo de ML'
            },
            {
                'url': '/api/health/',
                'method': 'GET',
                'description': 'Estado de salud del servicio'
            },
            {
                'url': '/api/stats/',
                'method': 'GET',
                'description': 'Estadísticas de uso'
            }
        ],
        'model_status': ml_service.is_ready()
    }
    return render(request, 'api/documentation.html', context)
