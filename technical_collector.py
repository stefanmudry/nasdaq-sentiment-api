# ============================================
# RECOLECTOR DE DATOS TÉCNICOS
# ============================================
# Este módulo obtiene:
# - VIX (índice de miedo)
# - Indicadores técnicos (RSI, MACD)
# - Put/Call Ratio
# - Datos de precio

import requests
from datetime import datetime, timedelta

class TechnicalCollector:
    """
    Esta clase obtiene datos técnicos del mercado
    que no requieren análisis de texto
    """
    
    def __init__(self):
        # Usamos Yahoo Finance (no requiere API key)
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    def get_stock_data(self, symbol, period="1mo", interval="1d"):
        """
        Obtiene datos históricos de una acción
        
        Parámetros:
        - symbol: Símbolo (ej: "AAPL", "^VIX", "QQQ")
        - period: Período (1d, 5d, 1mo, 3mo, 6mo, 1y)
        - interval: Intervalo (1m, 5m, 15m, 1h, 1d)
        """
        url = f"{self.base_url}/{symbol}"
        params = {
            "period1": int((datetime.now() - timedelta(days=30)).timestamp()),
            "period2": int(datetime.now().timestamp()),
            "interval": interval
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            result = data.get("chart", {}).get("result", [{}])[0]
            timestamps = result.get("timestamp", [])
            quotes = result.get("indicators", {}).get("quote", [{}])[0]
            
            return {
                "timestamps": timestamps,
                "open": quotes.get("open", []),
                "high": quotes.get("high", []),
                "low": quotes.get("low", []),
                "close": quotes.get("close", []),
                "volume": quotes.get("volume", [])
            }
        except Exception as e:
            print(f"Error obteniendo datos de {symbol}: {e}")
            return None
    
    # ==========================================
    # VIX - ÍNDICE DE MIEDO
    # ==========================================
    def get_vix_sentiment(self):
        """
        Obtiene el VIX y lo convierte a un score de sentimiento
        
        VIX alto = miedo = sentimiento negativo
        VIX bajo = calma = sentimiento positivo
        
        Niveles típicos:
        - VIX < 15: Muy bajo (complacencia) → +50 a +100
        - VIX 15-20: Normal → 0 a +50
        - VIX 20-25: Elevado → -25 a 0
        - VIX 25-30: Alto → -50 a -25
        - VIX > 30: Muy alto (pánico) → -100 a -50
        """
        print("😱 Obteniendo VIX...")
        
        data = self.get_stock_data("^VIX")
        
        if not data or not data["close"]:
            return {"score": 0, "vix_value": None, "error": "No data"}
        
        # Obtener el último valor del VIX
        vix_value = data["close"][-1]
        
        # Convertir VIX a sentimiento (-100 a +100)
        # Fórmula: invertimos la escala porque VIX alto = malo
        if vix_value < 12:
            score = 80  # Muy bullish (quizás demasiado complaciente)
        elif vix_value < 15:
            score = 60
        elif vix_value < 18:
            score = 40
        elif vix_value < 20:
            score = 20
        elif vix_value < 22:
            score = 0
        elif vix_value < 25:
            score = -20
        elif vix_value < 30:
            score = -40
        elif vix_value < 35:
            score = -60
        elif vix_value < 40:
            score = -80
        else:
            score = -95  # Pánico extremo
        
        print(f"  VIX actual: {vix_value:.2f} → Score: {score}")
        
        return {
            "score": score,
            "vix_value": round(vix_value, 2),
            "interpretation": self._interpret_vix(vix_value)
        }
    
    def _interpret_vix(self, vix):
        """Interpreta el nivel del VIX en texto"""
        if vix < 15:
            return "Muy bajo - Mercado complaciente"
        elif vix < 20:
            return "Normal - Mercado estable"
        elif vix < 25:
            return "Elevado - Algo de preocupación"
        elif vix < 30:
            return "Alto - Miedo en el mercado"
        else:
            return "Muy alto - Pánico"
    
    # ==========================================
    # INDICADORES TÉCNICOS
    # ==========================================
    def calculate_rsi(self, prices, period=14):
        """
        Calcula el RSI (Relative Strength Index)
        
        RSI > 70 = Sobrecompra (bearish)
        RSI < 30 = Sobreventa (bullish)
        RSI 30-70 = Neutral
        """
        if len(prices) < period + 1:
            return None
        
        # Calcular cambios
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separar ganancias y pérdidas
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        # Promedio de ganancias y pérdidas
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, prices):
        """
        Calcula el MACD (Moving Average Convergence Divergence)
        
        MACD positivo y subiendo = Bullish
        MACD negativo y bajando = Bearish
        """
        if len(prices) < 26:
            return None, None
        
        # EMA de 12 períodos
        ema12 = self._calculate_ema(prices, 12)
        # EMA de 26 períodos
        ema26 = self._calculate_ema(prices, 26)
        
        # MACD Line
        macd_line = ema12 - ema26
        
        # Para simplificar, calculamos la señal como EMA de 9 del MACD histórico
        # Aquí solo devolvemos el MACD line actual
        return macd_line, None
    
    def _calculate_ema(self, prices, period):
        """Calcula EMA (Exponential Moving Average)"""
        if len(prices) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period  # SMA inicial
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def get_technical_sentiment(self):
        """
        Obtiene indicadores técnicos del NASDAQ (QQQ) y los convierte a sentimiento
        """
        print("📊 Calculando indicadores técnicos...")
        
        data = self.get_stock_data("QQQ")
        
        if not data or not data["close"]:
            return {"score": 0, "error": "No data"}
        
        prices = [p for p in data["close"] if p is not None]
        
        # Calcular RSI
        rsi = self.calculate_rsi(prices)
        
        # Calcular MACD
        macd, _ = self.calculate_macd(prices)
        
        # Convertir RSI a sentimiento
        if rsi is not None:
            if rsi > 70:
                rsi_score = -30  # Sobrecompra = bearish
            elif rsi > 60:
                rsi_score = -10
            elif rsi < 30:
                rsi_score = 30   # Sobreventa = bullish (oportunidad de compra)
            elif rsi < 40:
                rsi_score = 10
            else:
                rsi_score = 0   # Neutral
        else:
            rsi_score = 0
        
        # Convertir MACD a sentimiento
        if macd is not None:
            if macd > 2:
                macd_score = 30
            elif macd > 0:
                macd_score = 15
            elif macd > -2:
                macd_score = -15
            else:
                macd_score = -30
        else:
            macd_score = 0
        
        # Calcular tendencia de precio (últimos 5 días vs 20 días)
        if len(prices) >= 20:
            sma5 = sum(prices[-5:]) / 5
            sma20 = sum(prices[-20:]) / 20
            trend_score = 20 if sma5 > sma20 else -20
        else:
            trend_score = 0
        
        # Score final técnico
        final_score = (rsi_score + macd_score + trend_score) / 3 * 1.5
        final_score = max(-100, min(100, final_score))
        
        print(f"  RSI: {rsi:.1f if rsi else 'N/A'} → Score: {rsi_score}")
        print(f"  MACD: {macd:.2f if macd else 'N/A'} → Score: {macd_score}")
        print(f"  Tendencia → Score: {trend_score}")
        
        return {
            "score": round(final_score, 2),
            "rsi": round(rsi, 2) if rsi else None,
            "macd": round(macd, 2) if macd else None,
            "details": {
                "rsi_score": rsi_score,
                "macd_score": macd_score,
                "trend_score": trend_score
            }
        }
    
    # ==========================================
    # PUT/CALL RATIO
    # ==========================================
    def get_put_call_sentiment(self):
        """
        El Put/Call Ratio indica el sentimiento de los traders de opciones
        
        Ratio alto (>1.0) = Más puts = Bearish
        Ratio bajo (<0.7) = Más calls = Bullish
        
        NOTA: Obtener datos reales de Put/Call ratio requiere APIs de pago
        Por ahora, usamos una estimación basada en el VIX
        """
        print("📈 Estimando Put/Call Ratio...")
        
        # Como no tenemos acceso gratuito al Put/Call real,
        # lo estimamos basándonos en el VIX (están correlacionados)
        vix_data = self.get_vix_sentiment()
        vix_value = vix_data.get("vix_value", 20)
        
        if vix_value is None:
            return {"score": 0, "ratio": None, "estimated": True}
        
        # Estimar Put/Call basado en VIX
        # VIX 15 ≈ PC Ratio 0.7
        # VIX 25 ≈ PC Ratio 1.0
        # VIX 35 ≈ PC Ratio 1.3
        estimated_ratio = 0.5 + (vix_value / 50)
        
        # Convertir a sentimiento
        # Ratio < 0.7 es muy bullish, > 1.0 es bearish
        if estimated_ratio < 0.6:
            score = 50
        elif estimated_ratio < 0.7:
            score = 30
        elif estimated_ratio < 0.8:
            score = 15
        elif estimated_ratio < 0.9:
            score = 0
        elif estimated_ratio < 1.0:
            score = -15
        elif estimated_ratio < 1.1:
            score = -30
        else:
            score = -50
        
        print(f"  Put/Call Ratio estimado: {estimated_ratio:.2f} → Score: {score}")
        
        return {
            "score": score,
            "ratio": round(estimated_ratio, 2),
            "estimated": True,
            "note": "Basado en correlación con VIX (APIs de opciones requieren suscripción)"
        }


# ============================================
# PRUEBA DEL MÓDULO
# ============================================
if __name__ == "__main__":
    collector = TechnicalCollector()
    
    print("\n" + "="*50)
    print("PRUEBA DE DATOS TÉCNICOS")
    print("="*50)
    
    vix = collector.get_vix_sentiment()
    print(f"\n😱 VIX Score: {vix['score']}")
    
    technical = collector.get_technical_sentiment()
    print(f"\n📊 Technical Score: {technical['score']}")
    
    putcall = collector.get_put_call_sentiment()
    print(f"\n📈 Put/Call Score: {putcall['score']}")
