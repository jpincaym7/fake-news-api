# 🔍 Fake News Detection API Backend

API REST profesional para la detección de noticias falsas usando Machine Learning, desarrollada con Django REST Framework.

## 🚀 Características

- **API REST completa** con endpoints para análisis de noticias
- **Modelo de ML integrado** para clasificación de texto
- **Base de datos** para tracking de análisis y estadísticas
- **Documentación interactiva** con interfaz web
- **Logging completo** para monitoreo y debugging
- **Configuración profesional** lista para producción
- **Despliegue en Render** con configuración automática

## 📋 Endpoints Principales

### 🔍 Análisis de Noticias
```bash
POST /api/analyze/
```
Analiza un texto de noticia y determina si es falsa o verdadera.

**Request:**
```json
{
    "text": "Texto de la noticia a analizar",
    "metadata": {
        "source": "opcional",
        "category": "opcional"
    }
}
```

**Response:**
```json
{
    "analysis_id": "uuid-del-análisis",
    "prediction": "VERDADERA",
    "confidence": 0.87,
    "probabilities": {
        "real": 0.87,
        "fake": 0.13
    },
    "status": "success"
}
```

### 📊 Otros Endpoints

- `GET /api/analysis/{id}/` - Consultar análisis específico
- `GET /api/model/info/` - Información del modelo ML
- `GET /api/health/` - Estado de salud del servicio
- `GET /api/stats/` - Estadísticas de uso
- `GET /api/docs/` - Documentación completa

## 🛠️ Instalación Local

### 1. Configurar el entorno
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env con tus configuraciones
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Ejecutar el servidor
```bash
python manage.py runserver
```

La API estará disponible en: http://localhost:8000

## 🔧 Estructura del Proyecto

```
backend/
├── fakenews_api/          # Configuración principal Django
│   ├── settings.py        # Configuraciones del proyecto
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # WSGI para producción
├── api/                  # Aplicación principal de la API
│   ├── models.py         # Modelos de base de datos
│   ├── serializers.py    # Serializers para la API REST
│   ├── views.py          # Vistas y lógica de endpoints
│   ├── urls.py           # URLs de la API
│   └── ml_service.py     # Servicio de Machine Learning
├── ml_models/            # Modelos de ML y archivos relacionados
│   ├── mejor_modelo_fake_news.pkl    # Modelo entrenado
│   └── info_mejor_modelo.json        # Metadatos del modelo
├── templates/            # Templates HTML para documentación
├── requirements.txt      # Dependencias Python
├── .env.example         # Variables de entorno ejemplo
├── build.sh             # Script para despliegue en Render
├── Procfile             # Configuración para Render
└── runtime.txt          # Versión de Python para Render
```

## 🔍 Modelos de Base de Datos

### NewsAnalysis
Almacena los resultados de análisis de noticias:
- `id` (UUID): Identificador único
- `text`: Texto analizado (primeros 1000 caracteres)
- `prediction`: Resultado (VERDADERA/FALSA)
- `confidence`: Nivel de confianza (0-1)
- `probability_real/fake`: Probabilidades individuales
- `metadata`: Información adicional (JSON)
- `created_at`: Timestamp de creación

### APIUsage
Tracking de uso de la API:
- `endpoint`: Endpoint utilizado
- `method`: Método HTTP
- `ip_address`: IP del cliente
- `status_code`: Código de respuesta HTTP
- `timestamp`: Momento de la solicitud

### ModelInfo
Información del modelo ML:
- `model_name`: Nombre del modelo
- `version`: Versión
- `metrics`: Métricas de rendimiento (JSON)
- `training_date`: Fecha de entrenamiento
- `is_active`: Estado activo/inactivo

## 🧠 Servicio de Machine Learning

El servicio ML (`ml_service.py`) maneja:

- **Carga automática** del modelo al iniciar
- **Preprocesamiento** de texto (limpieza, normalización)
- **Validación** de entrada (longitud, contenido)
- **Predicción** con probabilidades de confianza
- **Logging** detallado para debugging
- **Health checks** para monitoreo

### Validaciones de Entrada
- Mínimo: 10 caracteres, 3 palabras
- Máximo: 5,000 caracteres
- Limpieza automática de caracteres especiales
- Conversión a minúsculas

## 📈 Monitoreo y Logging

### Sistema de Logs
```python
# Configuración en settings.py
LOGGING = {
    'formatters': {
        'detailed': {
            'format': '[{levelname}] {asctime} {name}: {message}',
        }
    },
    'handlers': {
        'console': {...},
        'file': {...}
    }
}
```

### Health Check
```bash
GET /api/health/
```
Respuesta incluye:
- Estado del modelo ML
- Conectividad de base de datos
- Métricas del sistema
- Timestamp actual

## 🌐 Despliegue en Render

### 1. Configuración Automática
El repositorio incluye todos los archivos necesarios:

- `build.sh` - Script de construcción
- `Procfile` - Comando de inicio
- `runtime.txt` - Versión de Python
- `requirements.txt` - Dependencias

### 2. Variables de Entorno en Render
```bash
DEBUG=False
SECRET_KEY=clave-super-secreta-para-producción
DATABASE_URL=postgresql://...  # Automático con Render PostgreSQL
ALLOWED_HOSTS=tu-app.onrender.com
```

### 3. Configuración de Base de Datos
Render PostgreSQL se configura automáticamente. El `build.sh` ejecuta:
```bash
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
```

### 4. URL de Despliegue
Una vez desplegado, tu API estará disponible en:
```
https://tu-app-name.onrender.com
```

## 🔒 Configuraciones de Seguridad

### Producción
- `DEBUG = False`
- `SECURE_SSL_REDIRECT = True`
- CORS configurado para dominios específicos
- Headers de seguridad activados
- Rate limiting (pendiente implementar)

### CORS
```python
CORS_ALLOWED_ORIGINS = [
    "https://tu-frontend.com",
    "https://tu-app.onrender.com"
]
```

## 🧪 Testing

### Ejecutar Tests (TODO)
```bash
python manage.py test
```

### Test Manual con curl
```bash
# Health check
curl https://tu-app.onrender.com/api/health/

# Análisis de noticia
curl -X POST https://tu-app.onrender.com/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Esta es una noticia de prueba"}'
```

## 📊 Estadísticas y Métricas

### Endpoint de Estadísticas
```bash
GET /api/stats/
```

**Respuesta:**
```json
{
    "total_analyses": 1500,
    "analyses_today": 45,
    "analyses_last_week": 320,
    "predictions_by_result": {
        "fake": 680,
        "real": 820
    },
    "api_calls_by_status": {
        "success": 1450,
        "client_error": 35,
        "server_error": 15
    },
    "model_status": true
}
```

## 🚨 Solución de Problemas

### Error: Modelo no encontrado
```bash
# Verificar que el modelo esté en el directorio correcto
ls ml_models/
# Debe mostrar: mejor_modelo_fake_news.pkl
```

### Error: Base de datos bloqueada
```bash
python manage.py migrate
python manage.py collectstatic --no-input
```

### Error: Dependencias faltantes
```bash
pip install -r requirements.txt --upgrade
```

## 📚 Dependencias Principales

- **Django 4.2.7** - Framework web
- **Django REST Framework** - API REST
- **scikit-learn** - Machine Learning
- **pandas** - Procesamiento de datos
- **numpy** - Computación numérica
- **joblib** - Persistencia de modelos
- **gunicorn** - Servidor WSGI para producción
- **psycopg2** - Driver PostgreSQL
- **django-cors-headers** - Manejo de CORS

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

Desarrollado como parte del proyecto de detección de noticias falsas con Machine Learning.

---

¿Necesitas ayuda? Abre un [issue](../../issues) o consulta la [documentación en línea](https://tu-app.onrender.com/api/docs/).

## 🔗 Enlaces Útiles

- [Documentación Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Render Deploy Guide](https://render.com/docs/deploy-django)
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)