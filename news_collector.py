# ============================================
# RECOLECTOR DE NOTICIAS
# ============================================
# Este módulo busca noticias financieras y analiza su sentimiento

import requests
from datetime import datetime, timedelta
from config import FINNHUB_API_KEY, NASDAQ_STOCKS

class NewsCollector:
    """
    Esta clase se encarga de:
    1. Buscar noticias sobre las acciones del NASDAQ
    2. Analizar si son positivas o negativas
    3. Devolver un puntaje de -100 a +100
    """
    
    def __init__(self):
        self.api_key = FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
    
    def get_news(self, symbol, days=7):
        """
        Busca noticias de una acción específica
        
        Parámetros:
        - symbol: El símbolo de la acción (ej: "AAPL")
        - days: Cuántos días hacia atrás buscar
        
        Retorna:
        - Lista de noticias con su sentimiento
        """
        # Calcular fechas
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Formato de fecha que pide Finnhub
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        # Hacer la petición a la API
        url = f"{self.base_url}/company-news"
        params = {
            "symbol": symbol,
            "from": from_date,
            "to": to_date,
            "token": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            news = response.json()
            return news
        except Exception as e:
            print(f"Error obteniendo noticias de {symbol}: {e}")
            return []
    
    def analyze_headline(self, headline):
        """
        Analiza el sentimiento de un titular de noticia
        
        Este es un análisis SIMPLE basado en palabras clave.
        Para producción, usaríamos un modelo de IA más avanzado.
        
        Retorna un número de -1 (muy negativo) a +1 (muy positivo)
        """
        headline_lower = headline.lower()
        
        # Palabras positivas y su peso
        positive_words = {
            "surge": 0.8, "surges": 0.8, "soar": 0.8, "soars": 0.8,
            "jump": 0.6, "jumps": 0.6, "gain": 0.5, "gains": 0.5,
            "rise": 0.5, "rises": 0.5, "rally": 0.7, "rallies": 0.7,
            "bull": 0.6, "bullish": 0.7, "boom": 0.7,
            "record": 0.5, "high": 0.4, "growth": 0.5,
            "beat": 0.6, "beats": 0.6, "exceed": 0.6, "exceeds": 0.6,
            "upgrade": 0.7, "upgraded": 0.7, "buy": 0.5,
            "profit": 0.5, "profits": 0.5, "revenue": 0.3,
            "success": 0.6, "successful": 0.6, "win": 0.5, "wins": 0.5,
            "positive": 0.5, "optimism": 0.6, "optimistic": 0.6,
            "strong": 0.4, "strength": 0.4, "recover": 0.5, "recovery": 0.5,
            "breakout": 0.6, "momentum": 0.4, "outperform": 0.6,
        }
        
        # Palabras negativas y su peso
        negative_words = {
            "crash": -0.9, "crashes": -0.9, "plunge": -0.8, "plunges": -0.8,
            "drop": -0.6, "drops": -0.6, "fall": -0.5, "falls": -0.5,
            "decline": -0.5, "declines": -0.5, "sink": -0.6, "sinks": -0.6,
            "bear": -0.6, "bearish": -0.7, "bust": -0.7,
            "low": -0.4, "loss": -0.6, "losses": -0.6,
            "miss": -0.6, "misses": -0.6, "missed": -0.6,
            "downgrade": -0.7, "downgraded": -0.7, "sell": -0.5,
            "fear": -0.6, "fears": -0.6, "concern": -0.4, "concerns": -0.4,
            "risk": -0.4, "risks": -0.4, "warning": -0.5, "warn": -0.5,
            "negative": -0.5, "pessimism": -0.6, "pessimistic": -0.6,
            "weak": -0.4, "weakness": -0.4, "trouble": -0.5,
            "crisis": -0.8, "recession": -0.7, "inflation": -0.4,
            "layoff": -0.6, "layoffs": -0.6, "cut": -0.4, "cuts": -0.4,
            "lawsuit": -0.5, "investigation": -0.5, "fraud": -0.8,
        }
        
        score = 0
        word_count = 0
        
        # Buscar palabras positivas
        for word, weight in positive_words.items():
            if word in headline_lower:
                score += weight
                word_count += 1
        
        # Buscar palabras negativas
        for word, weight in negative_words.items():
            if word in headline_lower:
                score += weight  # weight ya es negativo
                word_count += 1
        
        # Si no encontramos palabras clave, es neutral
        if word_count == 0:
            return 0
        
        # Normalizar el score
        normalized_score = max(-1, min(1, score / max(word_count, 1)))
        return normalized_score
    
    def get_news_sentiment(self):
        """
        Obtiene el sentimiento general de las noticias del NASDAQ
        
        Retorna:
        - score: Número de -100 a +100
        - details: Diccionario con detalles por acción
        """
        all_scores = []
        details = {}
        
        print("📰 Recolectando noticias...")
        
        for symbol in NASDAQ_STOCKS:
            news_list = self.get_news(symbol)
            
            if not news_list:
                continue
            
            symbol_scores = []
            for news in news_list[:10]:  # Máximo 10 noticias por acción
                headline = news.get("headline", "")
                sentiment = self.analyze_headline(headline)
                symbol_scores.append(sentiment)
                all_scores.append(sentiment)
            
            if symbol_scores:
                avg_score = sum(symbol_scores) / len(symbol_scores)
                details[symbol] = {
                    "score": round(avg_score * 100, 2),
                    "news_count": len(symbol_scores)
                }
                print(f"  {symbol}: {len(symbol_scores)} noticias, score: {avg_score*100:.1f}")
        
        # Calcular score general
        if all_scores:
            final_score = (sum(all_scores) / len(all_scores)) * 100
        else:
            final_score = 0
        
        return {
            "score": round(final_score, 2),
            "total_news": len(all_scores),
            "details": details
        }


# ============================================
# PRUEBA DEL MÓDULO
# ============================================
if __name__ == "__main__":
    # Esto se ejecuta solo si corres este archivo directamente
    collector = NewsCollector()
    result = collector.get_news_sentiment()
    
    print("\n" + "="*50)
    print(f"📊 SENTIMENT DE NOTICIAS: {result['score']}")
    print(f"📰 Total de noticias analizadas: {result['total_news']}")
    print("="*50)
