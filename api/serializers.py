"""
Serializers para la API de Detección de Noticias Falsas
======================================================
Convierte objetos Django en JSON y viceversa
"""

from rest_framework import serializers
from .models import NewsAnalysis, APIUsage, ModelInfo


class NewsAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer para el análisis de noticias
    """
    text_length = serializers.ReadOnlyField()
    is_fake = serializers.ReadOnlyField()
    
    class Meta:
        model = NewsAnalysis
        fields = [
            'id',
            'text',
            'prediction',
            'confidence',
            'probability_fake',
            'probability_real',
            'text_length',
            'is_fake',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'prediction',
            'confidence',
            'probability_fake',
            'probability_real',
            'text_length',
            'is_fake',
            'created_at'
        ]
    
    def validate_text(self, value):
        """
        Validar el texto de entrada
        """
        if not value or not value.strip():
            raise serializers.ValidationError("El texto no puede estar vacío.")
        
        if len(value) < 10:
            raise serializers.ValidationError("El texto debe tener al menos 10 caracteres.")
        
        if len(value) > 5000:
            raise serializers.ValidationError("El texto no puede exceder los 5000 caracteres.")
        
        return value.strip()


class NewsAnalysisRequestSerializer(serializers.Serializer):
    """
    Serializer para las peticiones de análisis
    """
    text = serializers.CharField(
        max_length=5000,
        min_length=10,
        help_text="Texto de la noticia a analizar"
    )
    
    def validate_text(self, value):
        """
        Validar el texto de entrada
        """
        if not value or not value.strip():
            raise serializers.ValidationError("El texto no puede estar vacío.")
        
        return value.strip()


class NewsAnalysisResponseSerializer(serializers.Serializer):
    """
    Serializer para las respuestas de análisis
    """
    success = serializers.BooleanField()
    data = serializers.DictField()
    message = serializers.CharField(allow_blank=True)
    timestamp = serializers.DateTimeField()


class ModelInfoSerializer(serializers.ModelSerializer):
    """
    Serializer para información del modelo
    """
    class Meta:
        model = ModelInfo
        fields = [
            'model_name',
            'version',
            'accuracy',
            'f1_score',
            'training_date',
            'is_active',
            'created_at'
        ]


class APIStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de la API
    """
    total_analyses = serializers.IntegerField()
    fake_news_detected = serializers.IntegerField()
    real_news_detected = serializers.IntegerField()
    fake_news_percentage = serializers.FloatField()
    average_confidence = serializers.FloatField()
    total_api_calls = serializers.IntegerField()
    
    
class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer para el health check
    """
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    version = serializers.CharField()
    model_loaded = serializers.BooleanField()
    database_status = serializers.CharField()
    uptime = serializers.CharField()