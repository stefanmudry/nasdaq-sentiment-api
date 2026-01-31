# ============================================
# SERVIDOR API - NASDAQ SENTIMENT TRACKER
# ============================================
# Este servidor expone endpoints para que tu frontend
# pueda obtener los datos de sentimiento

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import threading
import time

# Importar el calculador
from sentiment_calculator import SentimentCalculator

# ==========================================
# CONFIGURACIÓN DEL SERVIDOR
# ==========================================
app = Flask(__name__)

# Permitir peticiones desde tu frontend (Netlify)
CORS(app, origins=[
    "https://nasdaqsentimenttracker.netlify.app",
    "https://splendid-sherbet-00da96.netlify.app",   
    "http://127.0.0.1:3000",
    "*"  # Para desarrollo (quitar en producción)
])

# Cache para no hacer demasiadas peticiones a las APIs
sentiment_cache = {
    "data": None,
    "last_updated": None,
    "updating": False
}

# El sentimiento se actualiza cada 15 minutos
CACHE_DURATION_MINUTES = 15


# ==========================================
# ENDPOINTS DE LA API
# ==========================================

@app.route("/")
def home():
    """
    Página principal - muestra info básica
    """
    return jsonify({
        "name": "NASDAQ Sentiment Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "/api/sentiment": "GET - Obtener el sentiment score actual",
            "/api/sentiment/refresh": "POST - Forzar actualización del score",
            "/api/health": "GET - Estado del servidor"
        },
        "documentation": "https://nasdaqsentimenttracker.netlify.app"
    })


@app.route("/api/health")
def health():
    """
    Endpoint para verificar que el servidor está funcionando
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache": {
            "has_data": sentiment_cache["data"] is not None,
            "last_updated": sentiment_cache["last_updated"],
            "updating": sentiment_cache["updating"]
        }
    })


@app.route("/api/sentiment")
def get_sentiment():
    """
    Endpoint principal - devuelve el sentiment score
    
    Usa cache para no sobrecargar las APIs
    """
    # Verificar si necesitamos actualizar el cache
    needs_update = False
    
    if sentiment_cache["data"] is None:
        needs_update = True
    elif sentiment_cache["last_updated"]:
        time_since_update = (datetime.now() - sentiment_cache["last_updated"]).total_seconds()
        if time_since_update > CACHE_DURATION_MINUTES * 60:
            needs_update = True
    
    # Si necesitamos actualizar y no está ya actualizando
    if needs_update and not sentiment_cache["updating"]:
        # Actualizar en background
        thread = threading.Thread(target=update_sentiment_cache)
        thread.start()
        
        # Si no hay datos previos, esperar a que termine
        if sentiment_cache["data"] is None:
            thread.join(timeout=60)  # Esperar máximo 60 segundos
    
    # Devolver datos del cache
    if sentiment_cache["data"]:
        return jsonify({
            "success": True,
            "data": sentiment_cache["data"],
            "cached": True,
            "last_updated": sentiment_cache["last_updated"].isoformat() if sentiment_cache["last_updated"] else None
        })
    else:
        return jsonify({
            "success": False,
            "error": "No data available yet. Please try again in a moment.",
            "updating": sentiment_cache["updating"]
        }), 503


@app.route("/api/sentiment/refresh", methods=["POST"])
def refresh_sentiment():
    """
    Forzar actualización del sentiment (con rate limiting)
    """
    # Verificar si ya está actualizando
    if sentiment_cache["updating"]:
        return jsonify({
            "success": False,
            "message": "Update already in progress"
        }), 429
    
    # Verificar rate limit (mínimo 5 minutos entre actualizaciones forzadas)
    if sentiment_cache["last_updated"]:
        time_since_update = (datetime.now() - sentiment_cache["last_updated"]).total_seconds()
        if time_since_update < 300:  # 5 minutos
            return jsonify({
                "success": False,
                "message": f"Please wait {int(300 - time_since_update)} seconds before refreshing again"
            }), 429
    
    # Iniciar actualización
    thread = threading.Thread(target=update_sentiment_cache)
    thread.start()
    
    return jsonify({
        "success": True,
        "message": "Update started. Check /api/sentiment for results."
    })


@app.route("/api/sentiment/components")
def get_components():
    """
    Devuelve solo los componentes individuales (para el dashboard)
    """
    if sentiment_cache["data"]:
        components = sentiment_cache["data"].get("components", {})
        
        # Formatear para el frontend
        formatted = []
        for name, data in components.items():
            formatted.append({
                "name": name.replace("_", " ").title(),
                "score": data.get("score", 0),
                "weight": data.get("weight", 0)
            })
        
        return jsonify({
            "success": True,
            "components": formatted,
            "final_score": sentiment_cache["data"].get("final_score", 0)
        })
    
    return jsonify({
        "success": False,
        "error": "No data available"
    }), 503


# ==========================================
# FUNCIÓN PARA ACTUALIZAR EL CACHE
# ==========================================
def update_sentiment_cache():
    """
    Actualiza el cache con datos frescos
    """
    global sentiment_cache
    
    if sentiment_cache["updating"]:
        return
    
    sentiment_cache["updating"] = True
    
    try:
        print("\n🔄 Actualizando sentiment cache...")
        calculator = SentimentCalculator()
        result = calculator.calculate_sentiment()
        
        sentiment_cache["data"] = result
        sentiment_cache["last_updated"] = datetime.now()
        print("✅ Cache actualizado exitosamente")
        
    except Exception as e:
        print(f"❌ Error actualizando cache: {e}")
    finally:
        sentiment_cache["updating"] = False


# ==========================================
# INICIAR SERVIDOR
# ==========================================
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║     NASDAQ SENTIMENT TRACKER - API SERVER         ║
    ╠═══════════════════════════════════════════════════╣
    ║  Endpoints:                                       ║
    ║    GET  /api/sentiment     - Get sentiment score  ║
    ║    POST /api/sentiment/refresh - Force refresh    ║
    ║    GET  /api/health        - Server health        ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # Pre-cargar datos al iniciar
    print("📊 Pre-cargando datos iniciales...")
    update_sentiment_cache()
    
    # Iniciar servidor
    # Para producción usar: gunicorn server:app
    app.run(host="0.0.0.0", port=5000, debug=True)
