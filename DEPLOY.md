# 🚀 Guía de Despliegue en Render

Esta guía te ayudará a desplegar tu API de Detección de Noticias Falsas en Render.

## 📋 Prerrequisitos

1. **Cuenta en Render**: [render.com](https://render.com)
2. **Repositorio en GitHub**: Tu código debe estar en un repositorio público o privado
3. **Archivos del modelo ML**: Asegúrate de que estén en `backend/ml_models/`

## 🔧 Preparación del Proyecto

### 1. Verificar Archivos Necesarios

Asegúrate de que estos archivos estén en tu directorio `backend/`:

```
backend/
├── build.sh              ✅ Script de construcción
├── Procfile              ✅ Comando de inicio
├── runtime.txt           ✅ Versión de Python  
├── requirements.txt      ✅ Dependencias
├── .env.example          ✅ Variables de entorno
├── ml_models/
│   ├── mejor_modelo_fake_news.pkl     ✅ Modelo entrenado
│   └── info_mejor_modelo.json         ✅ Info del modelo
└── manage.py             ✅ Django management
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` local (para testing) basado en `.env.example`:

```bash
# Configuración para producción en Render
DEBUG=False
SECRET_KEY=tu-clave-super-secreta-aqui
ALLOWED_HOSTS=tu-app-name.onrender.com
DATABASE_URL=postgresql://...  # Se configurará automáticamente
```

## 🌐 Despliegue en Render

### Paso 1: Crear Web Service

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click en **"New"** → **"Web Service"**
3. Conecta tu repositorio de GitHub
4. Selecciona el repositorio con tu código

### Paso 2: Configurar el Servicio

**Configuración Básica:**
- **Name**: `fake-news-api` (o el nombre que prefieras)
- **Environment**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn fakenews_api.wsgi:application`
- **Root Directory**: `backend` (¡IMPORTANTE!)

### Paso 3: Variables de Entorno

En la sección "Environment Variables", añade:

```bash
# Obligatorias
SECRET_KEY=tu-clave-super-secreta-de-50-caracteres-minimo
DEBUG=False
PYTHON_VERSION=3.11.5

# Opcional - Render las configurará automáticamente
# DATABASE_URL  (se auto-genera con PostgreSQL)
# ALLOWED_HOSTS (se auto-configura)
```

**Generar SECRET_KEY segura:**
```python
# Ejecuta este código en Python para generar una clave
import secrets
print(secrets.token_urlsafe(50))
```

### Paso 4: Base de Datos PostgreSQL

1. En el Dashboard, click **"New"** → **"PostgreSQL"**
2. Configuración:
   - **Name**: `fake-news-db`
   - **Database Name**: `fakenews`
   - **User**: `fakenews_user`
3. **Importante**: Copia la **Internal Database URL** 
4. En tu Web Service, añade la variable de entorno:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

### Paso 5: Deploy

1. Click **"Create Web Service"**
2. Render comenzará el proceso de construcción automáticamente
3. Monitorea los logs en tiempo real

## 📊 Verificar el Despliegue

### 1. Health Check
```bash
curl https://tu-app-name.onrender.com/api/health/
```

**Respuesta esperada:**
```json
{
    "service_status": "healthy",
    "model_loaded": true,
    "database_connected": true,
    "api_version": "1.0.0"
}
```

### 2. Test del Endpoint Principal
```bash
curl -X POST https://tu-app-name.onrender.com/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Esta es una noticia de prueba para verificar que funciona correctamente"}'
```

### 3. Verificar Documentación
Visita: `https://tu-app-name.onrender.com/api/docs/`

## 🔧 Configuración Avanzada

### Custom Domain (Opcional)
1. En Render Dashboard → Settings → Custom Domains
2. Añade tu dominio personalizado
3. Configura DNS según las instrucciones de Render
4. Actualiza `ALLOWED_HOSTS` en las variables de entorno

### Monitoring y Logs
- **Logs en tiempo real**: Dashboard → Logs
- **Métricas**: Dashboard → Metrics  
- **Health checks**: Render los ejecuta automáticamente

## 🚨 Solución de Problemas

### Error: "Application failed to respond"

1. **Verificar logs**: Dashboard → Logs
2. **Común**: Error de migración de base de datos
   ```bash
   # En los logs, busca errores como:
   # "relation does not exist"
   # "no such table"
   ```
3. **Solución**: Re-deploy para ejecutar migraciones

### Error: "Model file not found"

1. **Verificar** que `ml_models/mejor_modelo_fake_news.pkl` esté en el repo
2. **Check paths** en `settings.py`:
   ```python
   ML_CONFIG = {
       'MODEL_PATH': os.path.join(BASE_DIR, 'ml_models', 'mejor_modelo_fake_news.pkl')
   }
   ```

### Error: "Build failed"

1. **Verificar** `requirements.txt` - todas las dependencias correctas
2. **Python version** en `runtime.txt` debe ser válida
3. **Permisos** en `build.sh`:
   ```bash
   chmod +x build.sh  # Ejecutar localmente antes de push
   ```

### Error: "Static files not found"

1. Verificar `STATIC_ROOT` en `settings.py`
2. El `build.sh` debe ejecutar `collectstatic`

### Base de datos no conecta

1. **Verificar DATABASE_URL** esté configurada
2. **PostgreSQL service** debe estar activo
3. **Internal URL** vs External URL - usar la Internal

## 🔄 Updates y Redeploy

### Actualizar el Código
1. Haz push a tu repositorio de GitHub
2. Render detectará automáticamente los cambios
3. Se iniciará un nuevo deploy automáticamente

### Actualizar Solo el Modelo
1. Reemplaza archivos en `ml_models/`
2. Push al repositorio
3. Auto-deploy ejecutará

### Manual Redeploy
1. Dashboard → Manual Deploy → "Deploy latest commit"

## 📈 Monitoreo de Producción

### Endpoints de Monitoreo
- **Health**: `/api/health/`  
- **Stats**: `/api/stats/`
- **Model Info**: `/api/model/info/`

### Logs Importantes
```bash
# Busca en los logs:
[INFO] Modelo cargado exitosamente
[INFO] Análisis exitoso: uuid
[ERROR] Error en predicción: ...
```

### Métricas a Monitorear
- Response time
- Error rate
- Database connections
- Memory usage

## 🔒 Seguridad

### Variables de Entorno Seguras
- ❌ Nunca hagas commit de archivos `.env`
- ✅ Usa Render Environment Variables
- ✅ `DEBUG=False` en producción
- ✅ SECRET_KEY única y fuerte

### HTTPS
- Render provee HTTPS automáticamente
- Certificados SSL renovación automática

## 📝 URL Final

Una vez completado el despliegue, tu API estará disponible en:

```
https://tu-app-name.onrender.com
```

### Endpoints Disponibles:
- `GET /` - Información de la API
- `POST /api/analyze/` - Analizar noticia
- `GET /api/health/` - Health check
- `GET /api/stats/` - Estadísticas
- `GET /api/docs/` - Documentación
- `GET /admin/` - Panel de administración Django

## 🎉 ¡Listo!

Tu API de Detección de Noticias Falsas está ahora desplegada profesionalmente en Render con:

- ✅ **Base de datos PostgreSQL**
- ✅ **Modelo ML integrado**
- ✅ **HTTPS automático**
- ✅ **Logs y monitoreo**
- ✅ **Auto-deploy desde GitHub**
- ✅ **Documentación web**

---

**¿Problemas?** Revisa los logs en Render Dashboard o consulta la documentación completa en tu API desplegada.