# 🚀 NASDAQ Sentiment Tracker - Backend

## 📋 ¿Qué es esto?

Este es el **backend** (servidor) para tu aplicación NASDAQ Sentiment Tracker.

Calcula un **Sentiment Score de -100 a +100** basado en 6 factores:

| Factor | Peso | Fuente |
|--------|------|--------|
| 📰 News Sentiment | 25% | Finnhub API |
| 💬 Social Media | 15% | Reddit API |
| 📊 Technical Indicators | 20% | Yahoo Finance |
| 😱 VIX | 15% | Yahoo Finance |
| 📈 Put/Call Ratio | 10% | Estimado del VIX |
| 🎯 Analyst Recommendations | 15% | Finnhub API |

---

## 🛠️ PASO 1: Obtener las API Keys (GRATIS)

### 1.1 Finnhub (Noticias y Recomendaciones)
1. Ve a https://finnhub.io/
2. Click en "Get free API key"
3. Regístrate con tu email
4. Copia tu API key

### 1.2 Alpha Vantage (Datos adicionales)
1. Ve a https://www.alphavantage.co/support/#api-key
2. Llena el formulario
3. Copia tu API key

### 1.3 Reddit (Sentimiento Social)
1. Ve a https://www.reddit.com/prefs/apps
2. Inicia sesión en Reddit
3. Scroll hasta abajo y click "create another app..."
4. Llena así:
   - **name**: NasdaqSentiment
   - **type**: script
   - **redirect uri**: http://localhost:8000
5. Click "create app"
6. Copia:
   - **client_id**: El código debajo de "personal use script"
   - **client_secret**: El código al lado de "secret"

---

## 💻 PASO 2: Configurar el Proyecto

### 2.1 Instalar Python
Si no tienes Python instalado:
- Windows: https://www.python.org/downloads/
- Mac: `brew install python`

### 2.2 Descargar el proyecto
```bash
# Crear carpeta y entrar
mkdir nasdaq_sentiment
cd nasdaq_sentiment
```

### 2.3 Copiar los archivos
Copia todos los archivos `.py` a esta carpeta.

### 2.4 Configurar las API Keys
Abre el archivo `config.py` y reemplaza:

```python
FINNHUB_API_KEY = "TU_LLAVE_REAL_AQUI"
ALPHA_VANTAGE_API_KEY = "TU_LLAVE_REAL_AQUI"
REDDIT_CLIENT_ID = "TU_CLIENT_ID_AQUI"
REDDIT_CLIENT_SECRET = "TU_SECRET_AQUI"
```

### 2.5 Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## ▶️ PASO 3: Ejecutar el Servidor

### Para probar localmente:
```bash
python server.py
```

Verás algo así:
```
╔═══════════════════════════════════════════════════╗
║     NASDAQ SENTIMENT TRACKER - API SERVER         ║
╚═══════════════════════════════════════════════════╝

📊 Pre-cargando datos iniciales...
🚀 CALCULANDO NASDAQ SENTIMENT SCORE
...
* Running on http://0.0.0.0:5000
```

### Probar que funciona:
Abre en tu navegador: http://localhost:5000/api/sentiment

Deberías ver un JSON con el sentiment score.

---

## 🌐 PASO 4: Desplegar en la Nube (GRATIS)

### Opción A: Railway.app (Recomendado)

1. Ve a https://railway.app/
2. Regístrate con GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Sube tu código a GitHub primero
5. Railway lo detectará automáticamente
6. Agrega las variables de entorno (tus API keys)
7. ¡Listo! Te dará una URL como `https://tu-app.up.railway.app`

### Opción B: Render.com

1. Ve a https://render.com/
2. Regístrate gratis
3. New → Web Service
4. Conecta tu repositorio de GitHub
5. Configura:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn server:app`
6. Agrega las variables de entorno
7. Deploy

### Opción C: PythonAnywhere

1. Ve a https://www.pythonanywhere.com/
2. Plan gratuito
3. Sube tus archivos
4. Configura un Web App con Flask

---

## 🔗 PASO 5: Conectar con tu Frontend

Una vez tengas tu servidor corriendo (ej: `https://tu-api.railway.app`), 
necesitas actualizar tu frontend en Netlify para que use esta URL.

En tu código JavaScript del frontend, cambia:
```javascript
const API_URL = "https://tu-api.railway.app/api/sentiment";

// Obtener el sentiment
fetch(API_URL)
  .then(response => response.json())
  .then(data => {
    console.log("Sentiment Score:", data.data.final_score);
    // Actualizar tu UI aquí
  });
```

---

## 📊 Endpoints de la API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Info del servidor |
| `/api/health` | GET | Estado del servidor |
| `/api/sentiment` | GET | Obtener el sentiment score |
| `/api/sentiment/refresh` | POST | Forzar actualización |
| `/api/sentiment/components` | GET | Desglose por componente |

### Ejemplo de respuesta `/api/sentiment`:
```json
{
  "success": true,
  "data": {
    "final_score": 42.5,
    "interpretation": "Bullish 🟢",
    "components": {
      "news_sentiment": {"score": 35.2, "weight": 25},
      "social_sentiment": {"score": 28.1, "weight": 15},
      "technical": {"score": 45.0, "weight": 20},
      "vix": {"score": 60.0, "weight": 15},
      "put_call_ratio": {"score": 30.0, "weight": 10},
      "analyst_recommendations": {"score": 55.3, "weight": 15}
    },
    "timestamp": "2025-01-30T10:30:00"
  },
  "cached": true,
  "last_updated": "2025-01-30T10:30:00"
}
```

---

## ⚠️ Limitaciones de las APIs Gratuitas

| API | Límite Gratis | Consecuencia |
|-----|---------------|--------------|
| Finnhub | 60 calls/minuto | El sistema usa cache de 15 min |
| Reddit | 60 calls/minuto | Analizamos menos posts |
| Yahoo Finance | Sin límite claro | Puede bloquearte si abusas |

Por eso el sistema usa **cache**: calcula el sentiment cada 15 minutos
y guarda el resultado para no sobrecargar las APIs.

---

## 🐛 Solución de Problemas

### "API key inválida"
- Verifica que copiaste bien la key en `config.py`
- Algunas APIs tardan unos minutos en activarse

### "No hay datos de noticias"
- Finnhub tiene límites. Espera unos minutos.
- Verifica tu key en https://finnhub.io/dashboard

### "Error de Reddit"
- Verifica que tu app de Reddit esté configurada como "script"
- El client_id es el código DEBAJO de "personal use script"

### "El servidor no inicia"
- ¿Instalaste las dependencias? `pip install -r requirements.txt`
- ¿Estás en la carpeta correcta?

---

## 📈 Mejoras Futuras

Para mejorar el indicador podrías:

1. **Usar APIs de pago** para más datos de noticias
2. **Agregar más fuentes** (Twitter/X, StockTwits)
3. **Usar modelos de IA** para mejor análisis de sentimiento
4. **Agregar alertas** cuando el sentimiento cambie drásticamente
5. **Crear el oscilador** para Sierra Chart

---

## 📞 ¿Necesitas Ayuda?

Si tienes problemas:
1. Revisa que las API keys estén correctas
2. Lee los mensajes de error en la consola
3. Verifica los límites de las APIs

¡Buena suerte con tu proyecto! 🚀📈
