"""
Modelos de datos para la API de Detección de Noticias Falsas
============================================================
"""

from django.db import models
from django.contrib.auth.models import User
import uuid


class NewsAnalysis(models.Model):
    """
    Modelo para almacenar análisis de noticias
    """
    PREDICTION_CHOICES = [
        ('VERDADERA', 'Noticia Verdadera'),
        ('FALSA', 'Noticia Falsa'),
    ]
    
    # Identificador único
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Contenido de la noticia
    text = models.TextField(
        verbose_name="Texto de la noticia",
        help_text="Texto completo de la noticia a analizar"
    )
    
    # Resultados de la predicción
    prediction = models.CharField(
        max_length=10,
        choices=PREDICTION_CHOICES,
        verbose_name="Predicción"
    )
    
    confidence = models.FloatField(
        verbose_name="Confianza",
        help_text="Nivel de confianza de la predicción (0.0 - 1.0)"
    )
    
    probability_fake = models.FloatField(
        verbose_name="Probabilidad de ser falsa",
        help_text="Probabilidad de que la noticia sea falsa"
    )
    
    probability_real = models.FloatField(
        verbose_name="Probabilidad de ser verdadera", 
        help_text="Probabilidad de que la noticia sea verdadera"
    )
    
    # Metadatos
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name="Dirección IP"
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="User Agent"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    
    class Meta:
        verbose_name = "Análisis de Noticia"
        verbose_name_plural = "Análisis de Noticias"
        ordering = ['-created_at']
        
    def __str__(self):
        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"{self.prediction} - {text_preview}"
    
    @property
    def text_length(self):
        """Retorna la longitud del texto"""
        return len(self.text)
    
    @property
    def is_fake(self):
        """Retorna True si la noticia es predicha como falsa"""
        return self.prediction == 'FALSA'


class APIUsage(models.Model):
    """
    Modelo para rastrear el uso de la API
    """
    endpoint = models.CharField(
        max_length=100,
        verbose_name="Endpoint"
    )
    
    method = models.CharField(
        max_length=10,
        verbose_name="Método HTTP"
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name="Dirección IP"
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="User Agent"
    )
    
    response_status = models.IntegerField(
        verbose_name="Estado de respuesta"
    )
    
    response_time = models.FloatField(
        verbose_name="Tiempo de respuesta (ms)"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp"
    )
    
    class Meta:
        verbose_name = "Uso de API"
        verbose_name_plural = "Uso de API"
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.response_status}"


class ModelInfo(models.Model):
    """
    Información sobre el modelo ML en uso
    """
    model_name = models.CharField(
        max_length=100,
        verbose_name="Nombre del modelo"
    )
    
    version = models.CharField(
        max_length=20,
        verbose_name="Versión"
    )
    
    accuracy = models.FloatField(
        verbose_name="Precisión"
    )
    
    f1_score = models.FloatField(
        verbose_name="F1-Score"
    )
    
    training_date = models.DateTimeField(
        verbose_name="Fecha de entrenamiento"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    class Meta:
        verbose_name = "Información del Modelo"
        verbose_name_plural = "Información de Modelos"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.model_name} v{self.version}"
