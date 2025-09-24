"""
Servicio de Machine Learning para Detección de Noticias Falsas
==============================================================
Maneja la carga del modelo y las predicciones
"""

import os
import json
import joblib
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from django.conf import settings
import numpy as np

logger = logging.getLogger(__name__)


class FakeNewsDetectorService:
    """
    Servicio principal para la detección de noticias falsas
    """
    
    def __init__(self):
        self.model = None
        self.model_info = {}
        self.model_loaded = False
        self.load_model()
    
    def load_model(self) -> bool:
        """
        Cargar el modelo de machine learning
        """
        try:
            model_path = settings.ML_CONFIG['MODEL_PATH']
            model_info_path = settings.ML_CONFIG['MODEL_INFO_PATH']
            
            # Verificar que existan los archivos
            if not os.path.exists(model_path):
                logger.error(f"Archivo del modelo no encontrado: {model_path}")
                return False
            
            # Cargar el modelo
            self.model = joblib.load(model_path)
            logger.info(f"Modelo cargado exitosamente desde: {model_path}")
            
            # Cargar información del modelo si existe
            if os.path.exists(model_info_path):
                with open(model_info_path, 'r', encoding='utf-8') as f:
                    self.model_info = json.load(f)
                logger.info("Información del modelo cargada exitosamente")
            else:
                logger.warning(f"Archivo de información del modelo no encontrado: {model_info_path}")
                self.model_info = {
                    'nombre': 'Modelo de Detección de Noticias Falsas',
                    'fecha_entrenamiento': 'Desconocida',
                    'metricas_validacion': {
                        'accuracy': 0.0,
                        'f1': 0.0,
                        'auc': 0.0
                    }
                }
            
            self.model_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {str(e)}")
            self.model_loaded = False
            return False
    
    def is_ready(self) -> bool:
        """
        Verificar si el servicio está listo para hacer predicciones
        """
        return self.model_loaded and self.model is not None
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocesar el texto antes de la predicción
        """
        # Limpieza básica del texto
        text = text.strip()
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres extra
        import re
        text = re.sub(r'\s+', ' ', text)  # Espacios múltiples
        text = re.sub(r'[^\w\sáéíóúüñ]', ' ', text)  # Caracteres especiales
        
        return text
    
    def predict(self, text: str) -> Dict:
        """
        Hacer predicción sobre un texto
        
        Args:
            text (str): Texto de la noticia a analizar
            
        Returns:
            Dict: Resultado de la predicción con probabilidades y confianza
        """
        if not self.is_ready():
            raise Exception("El modelo no está disponible")
        
        try:
            # Preprocesar el texto
            processed_text = self.preprocess_text(text)
            
            if len(processed_text) < 5:
                raise Exception("El texto procesado es demasiado corto")
            
            # Hacer predicción
            prediction = self.model.predict([processed_text])[0]
            probabilities = self.model.predict_proba([processed_text])[0]
            
            # Extraer probabilidades
            prob_real = float(probabilities[0])
            prob_fake = float(probabilities[1])
            confidence = float(max(probabilities))
            
            # Determinar la etiqueta
            prediction_label = "FALSA" if prediction == 1 else "VERDADERA"
            
            result = {
                'prediction': prediction_label,
                'confidence': confidence,
                'probability_real': prob_real,
                'probability_fake': prob_fake,
                'text_length': len(text),
                'processed_text_length': len(processed_text),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Predicción realizada: {prediction_label} (confianza: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Error en la predicción: {str(e)}")
            raise Exception(f"Error al procesar el texto: {str(e)}")
    
    def get_model_info(self) -> Dict:
        """
        Obtener información del modelo
        """
        if not self.model_info:
            return {
                'status': 'error',
                'message': 'Información del modelo no disponible'
            }
        
        return {
            'status': 'success',
            'model_loaded': self.model_loaded,
            'model_name': self.model_info.get('nombre', 'Desconocido'),
            'training_date': self.model_info.get('fecha_entrenamiento', 'Desconocida'),
            'metrics': self.model_info.get('metricas_validacion', {}),
            'parameters': self.model_info.get('parametros', {})
        }
    
    def validate_text(self, text: str) -> Tuple[bool, str]:
        """
        Validar el texto de entrada
        
        Args:
            text (str): Texto a validar
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not text or not text.strip():
            return False, "El texto no puede estar vacío"
        
        text = text.strip()
        
        if len(text) < 10:
            return False, "El texto debe tener al menos 10 caracteres"
        
        max_length = settings.ML_CONFIG.get('MAX_TEXT_LENGTH', 5000)
        if len(text) > max_length:
            return False, f"El texto no puede exceder los {max_length} caracteres"
        
        # Verificar que el texto contenga palabras
        words = text.split()
        if len(words) < 3:
            return False, "El texto debe contener al menos 3 palabras"
        
        return True, ""
    
    def get_health_status(self) -> Dict:
        """
        Obtener el estado de salud del servicio
        """
        return {
            'service_status': 'healthy' if self.is_ready() else 'unhealthy',
            'model_loaded': self.model_loaded,
            'model_path_exists': os.path.exists(settings.ML_CONFIG['MODEL_PATH']),
            'model_info_available': bool(self.model_info),
            'timestamp': datetime.now().isoformat()
        }


# Instancia global del servicio
ml_service = FakeNewsDetectorService()