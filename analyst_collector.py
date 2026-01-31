# ============================================
# RECOLECTOR DE RECOMENDACIONES DE ANALISTAS
# ============================================
# Este módulo obtiene las recomendaciones de analistas
# (upgrades, downgrades, price targets) usando Finnhub

import requests
from datetime import datetime, timedelta
from config import FINNHUB_API_KEY, NASDAQ_STOCKS

class AnalystCollector:
    """
    Esta clase obtiene:
    1. Recomendaciones de analistas (Buy, Hold, Sell)
    2. Cambios recientes (Upgrades/Downgrades)
    3. Price targets
    """
    
    def __init__(self):
        self.api_key = FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
    
    def get_recommendations(self, symbol):
        """
        Obtiene las recomendaciones actuales de analistas
        
        Retorna el consenso: Strong Buy, Buy, Hold, Sell, Strong Sell
        """
        url = f"{self.base_url}/stock/recommendation"
        params = {
            "symbol": symbol,
            "token": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data:
                # Tomamos la recomendación más reciente
                return data[0] if data else None
            return None
        except Exception as e:
            print(f"Error obteniendo recomendaciones de {symbol}: {e}")
            return None
    
    def get_price_target(self, symbol):
        """
        Obtiene el price target promedio de los analistas
        """
        url = f"{self.base_url}/stock/price-target"
        params = {
            "symbol": symbol,
            "token": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error obteniendo price target de {symbol}: {e}")
            return None
    
    def calculate_recommendation_score(self, rec_data):
        """
        Convierte las recomendaciones a un score
        
        Finnhub devuelve:
        - strongBuy: Número de analistas con Strong Buy
        - buy: Número con Buy
        - hold: Número con Hold
        - sell: Número con Sell
        - strongSell: Número con Strong Sell
        
        Convertimos esto a un score de -100 a +100
        """
        if not rec_data:
            return 0
        
        strong_buy = rec_data.get("strongBuy", 0)
        buy = rec_data.get("buy", 0)
        hold = rec_data.get("hold", 0)
        sell = rec_data.get("sell", 0)
        strong_sell = rec_data.get("strongSell", 0)
        
        total = strong_buy + buy + hold + sell + strong_sell
        
        if total == 0:
            return 0
        
        # Ponderamos cada categoría
        # Strong Buy = +2, Buy = +1, Hold = 0, Sell = -1, Strong Sell = -2
        weighted_score = (
            strong_buy * 2 +
            buy * 1 +
            hold * 0 +
            sell * -1 +
            strong_sell * -2
        )
        
        # Normalizar a -100 a +100
        # El máximo teórico es 2 * total, el mínimo es -2 * total
        max_score = 2 * total
        normalized = (weighted_score / max_score) * 100
        
        return normalized
    
    def calculate_price_target_score(self, target_data, current_price):
        """
        Compara el price target con el precio actual
        
        Si el target es mucho mayor que el precio actual = Bullish
        Si el target es menor que el precio actual = Bearish
        """
        if not target_data or not current_price:
            return 0
        
        target_mean = target_data.get("targetMean", 0)
        
        if target_mean == 0 or current_price == 0:
            return 0
        
        # Calcular el upside/downside potencial
        potential = ((target_mean - current_price) / current_price) * 100
        
        # Convertir a score
        # +20% upside = +50 score
        # -10% downside = -25 score
        score = potential * 2.5
        
        # Limitar a -50 a +50 (dejamos espacio para otros factores)
        return max(-50, min(50, score))
    
    def get_analyst_sentiment(self):
        """
        Obtiene el sentimiento general basado en recomendaciones de analistas
        """
        print("🎯 Obteniendo recomendaciones de analistas...")
        
        all_rec_scores = []
        all_target_scores = []
        details = {}
        
        for symbol in NASDAQ_STOCKS:
            # Obtener recomendaciones
            rec_data = self.get_recommendations(symbol)
            rec_score = self.calculate_recommendation_score(rec_data)
            
            if rec_score != 0:
                all_rec_scores.append(rec_score)
            
            # Obtener price target
            target_data = self.get_price_target(symbol)
            
            # Para el price target necesitamos el precio actual
            # Por simplicidad, usamos el targetMean como referencia
            if target_data:
                current = target_data.get("targetMean", 0) * 0.9  # Aproximación
                target_score = self.calculate_price_target_score(target_data, current)
                if target_score != 0:
                    all_target_scores.append(target_score)
            
            # Guardar detalles
            if rec_data or target_data:
                details[symbol] = {
                    "recommendation_score": round(rec_score, 2),
                    "recommendations": {
                        "strongBuy": rec_data.get("strongBuy", 0) if rec_data else 0,
                        "buy": rec_data.get("buy", 0) if rec_data else 0,
                        "hold": rec_data.get("hold", 0) if rec_data else 0,
                        "sell": rec_data.get("sell", 0) if rec_data else 0,
                        "strongSell": rec_data.get("strongSell", 0) if rec_data else 0,
                    },
                    "price_target": target_data.get("targetMean", 0) if target_data else 0
                }
                
                print(f"  {symbol}: Rec Score: {rec_score:.1f}")
        
        # Calcular scores finales
        avg_rec_score = sum(all_rec_scores) / len(all_rec_scores) if all_rec_scores else 0
        avg_target_score = sum(all_target_scores) / len(all_target_scores) if all_target_scores else 0
        
        # Combinar ambos scores (60% recomendaciones, 40% price targets)
        final_score = avg_rec_score * 0.6 + avg_target_score * 0.4
        
        return {
            "score": round(final_score, 2),
            "recommendation_score": round(avg_rec_score, 2),
            "price_target_score": round(avg_target_score, 2),
            "stocks_analyzed": len(details),
            "details": details
        }


# ============================================
# PRUEBA DEL MÓDULO
# ============================================
if __name__ == "__main__":
    collector = AnalystCollector()
    result = collector.get_analyst_sentiment()
    
    print("\n" + "="*50)
    print(f"🎯 SENTIMENT DE ANALISTAS: {result['score']}")
    print(f"📊 Score de recomendaciones: {result['recommendation_score']}")
    print(f"💰 Score de price targets: {result['price_target_score']}")
    print(f"📈 Acciones analizadas: {result['stocks_analyzed']}")
    print("="*50)
