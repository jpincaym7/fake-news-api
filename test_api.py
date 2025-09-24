#!/usr/bin/env python3
"""
Script de prueba para la API de Detección de Noticias Falsas
============================================================
Este script demuestra cómo usar la API para analizar noticias
"""

import requests
import json
import time
from datetime import datetime


class FakeNewsAPITester:
    """
    Cliente de prueba para la API de detección de noticias falsas
    """
    
    def __init__(self, base_url="http://localhost:8000"):
        """
        Inicializar el cliente de prueba
        
        Args:
            base_url (str): URL base de la API (local o producción)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FakeNewsAPITester/1.0'
        })
    
    def test_health(self):
        """Probar el endpoint de health check"""
        print("🔍 Probando health check...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/health/")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API saludable: {data.get('service_status')}")
                print(f"   📊 Modelo cargado: {data.get('model_loaded')}")
                print(f"   💾 BD conectada: {data.get('database_connected')}")
                return True
            else:
                print(f"❌ Health check falló: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en health check: {e}")
            return False
    
    def test_analyze_news(self, text, metadata=None):
        """
        Probar el análisis de una noticia
        
        Args:
            text (str): Texto de la noticia
            metadata (dict): Metadatos opcionales
            
        Returns:
            dict: Resultado del análisis
        """
        print(f"\n📰 Analizando noticia...")
        print(f"   📝 Texto: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        payload = {"text": text}
        if metadata:
            payload["metadata"] = metadata
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/analyze/",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Análisis exitoso!")
                print(f"   🎯 Predicción: {data.get('prediction')}")
                print(f"   🎲 Confianza: {data.get('confidence', 0):.3f}")
                print(f"   📊 Prob. Real: {data.get('probabilities', {}).get('real', 0):.3f}")
                print(f"   📊 Prob. Falsa: {data.get('probabilities', {}).get('fake', 0):.3f}")
                print(f"   🆔 ID: {data.get('analysis_id')}")
                return data
            else:
                print(f"❌ Error en análisis: {response.status_code}")
                print(f"   📄 Respuesta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error en análisis: {e}")
            return None
    
    def test_get_analysis(self, analysis_id):
        """
        Probar la consulta de un análisis específico
        
        Args:
            analysis_id (str): ID del análisis a consultar
            
        Returns:
            dict: Datos del análisis
        """
        print(f"\n🔍 Consultando análisis {analysis_id}...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/analysis/{analysis_id}/"
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Análisis encontrado!")
                print(f"   🎯 Predicción: {data.get('prediction')}")
                print(f"   🎲 Confianza: {data.get('confidence', 0):.3f}")
                print(f"   📅 Creado: {data.get('created_at')}")
                return data
            else:
                print(f"❌ Error al consultar análisis: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error al consultar análisis: {e}")
            return None
    
    def test_model_info(self):
        """Probar endpoint de información del modelo"""
        print(f"\n🤖 Consultando información del modelo...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/model/info/")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Información del modelo obtenida!")
                print(f"   📛 Nombre: {data.get('model_name')}")
                print(f"   🏷️  Versión: {data.get('version')}")
                print(f"   📊 Activo: {data.get('is_active')}")
                print(f"   📅 Entrenamiento: {data.get('training_date')}")
                
                # Mostrar métricas si están disponibles
                metrics = data.get('metrics', {})
                if metrics:
                    print("   📈 Métricas:")
                    for metric, value in metrics.items():
                        print(f"      {metric}: {value}")
                
                return data
            else:
                print(f"❌ Error al obtener info del modelo: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error al obtener info del modelo: {e}")
            return None
    
    def test_stats(self):
        """Probar endpoint de estadísticas"""
        print(f"\n📊 Consultando estadísticas de la API...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/stats/")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Estadísticas obtenidas!")
                print(f"   📝 Total análisis: {data.get('total_analyses', 0)}")
                print(f"   📞 Total llamadas API: {data.get('total_api_calls', 0)}")
                print(f"   📅 Análisis hoy: {data.get('analyses_today', 0)}")
                print(f"   📊 Modelo activo: {data.get('model_status')}")
                
                # Mostrar distribución de predicciones
                predictions = data.get('predictions_by_result', {})
                if predictions:
                    print("   🎯 Distribución de predicciones:")
                    print(f"      Falsas: {predictions.get('fake', 0)}")
                    print(f"      Reales: {predictions.get('real', 0)}")
                
                return data
            else:
                print(f"❌ Error al obtener estadísticas: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error al obtener estadísticas: {e}")
            return None
    
    def run_comprehensive_test(self):
        """Ejecutar una suite completa de pruebas"""
        print(f"🚀 Iniciando pruebas comprehensivas de la API")
        print(f"🌐 URL base: {self.base_url}")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Test 1: Health Check
        if not self.test_health():
            print("❌ Health check falló. Terminando pruebas.")
            return False
        
        # Test 2: Información del modelo
        self.test_model_info()
        
        # Test 3: Estadísticas iniciales
        self.test_stats()
        
        # Test 4: Análisis de noticias de prueba
        test_news = [
            {
                "text": "El gobierno anunció nuevas medidas económicas para combatir la inflación que afecta a todos los sectores",
                "metadata": {"source": "test", "category": "economía", "type": "neutral"}
            },
            {
                "text": "Científicos descubrieron una nueva especie de dinosaurio en Argentina que revoluciona la paleontología",
                "metadata": {"source": "test", "category": "ciencia", "type": "positive"}
            },
            {
                "text": "El agua del grifo contiene microchips para controlar nuestras mentes según expertos anónimos",
                "metadata": {"source": "test", "category": "conspiración", "type": "suspicious"}
            }
        ]
        
        analysis_ids = []
        
        for i, news in enumerate(test_news, 1):
            print(f"\n{'='*60}")
            print(f"📰 Prueba de noticia {i}/3")
            result = self.test_analyze_news(news["text"], news["metadata"])
            
            if result and result.get("analysis_id"):
                analysis_ids.append(result["analysis_id"])
                
                # Pequeña pausa para evitar rate limiting
                time.sleep(1)
        
        # Test 5: Consultar análisis creados
        print(f"\n{'='*60}")
        print(f"🔍 Consultando análisis creados...")
        
        for analysis_id in analysis_ids:
            self.test_get_analysis(analysis_id)
            time.sleep(0.5)
        
        # Test 6: Estadísticas finales
        print(f"\n{'='*60}")
        self.test_stats()
        
        print(f"\n{'='*60}")
        print(f"✅ Pruebas completadas exitosamente!")
        print(f"📊 Total de análisis realizados: {len(analysis_ids)}")
        print(f"🎉 La API está funcionando correctamente!")
        
        return True


def main():
    """Función principal para ejecutar las pruebas"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Probar API de Detección de Noticias Falsas')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='URL base de la API (default: http://localhost:8000)')
    parser.add_argument('--production', action='store_true',
                       help='Usar URL de producción en Render')
    
    args = parser.parse_args()
    
    # Configurar URL
    if args.production:
        # Reemplaza con tu URL de Render
        base_url = "https://tu-app-name.onrender.com"
        print("🌐 Modo PRODUCCIÓN activado")
    else:
        base_url = args.url
        print("🏠 Modo LOCAL/DESARROLLO")
    
    # Crear cliente y ejecutar pruebas
    tester = FakeNewsAPITester(base_url)
    
    try:
        success = tester.run_comprehensive_test()
        exit_code = 0 if success else 1
        exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        exit(1)


if __name__ == "__main__":
    main()