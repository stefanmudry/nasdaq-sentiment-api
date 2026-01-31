# ============================================
# NASDAQ SENTIMENT CALCULATOR
# ============================================
# Este es el CEREBRO del sistema
# Combina todos los factores y calcula el Sentiment Score final

from datetime import datetime
from config import PESOS

# Importar todos los recolectores
from news_collector import NewsCollector
from reddit_collector import RedditCollector
from technical_collector import TechnicalCollector
from analyst_collector import AnalystCollector

class SentimentCalculator:
    """
    Esta clase:
    1. Llama a todos los recolectores de datos
    2. Aplica los pesos configurados
    3. Calcula el Sentiment Score final de -100 a +100
    4. Genera un reporte completo
    """
    
    def __init__(self):
        self.news_collector = NewsCollector()
        self.reddit_collector = RedditCollector()
        self.technical_collector = TechnicalCollector()
        self.analyst_collector = AnalystCollector()
        
        self.pesos = PESOS
    
    def calculate_sentiment(self):
        """
        Calcula el Sentiment Score completo
        
        Retorna:
        {
            "final_score": número de -100 a +100,
            "interpretation": "Bullish" / "Bearish" / "Neutral",
            "components": {cada componente con su score},
            "timestamp": cuando se calculó
        }
        """
        print("\n" + "="*60)
        print("🚀 CALCULANDO NASDAQ SENTIMENT SCORE")
        print("="*60 + "\n")
        
        components = {}
        
        # ==========================================
        # 1. NOTICIAS
        # ==========================================
        try:
            news_result = self.news_collector.get_news_sentiment()
            components["news_sentiment"] = {
                "score": news_result["score"],
                "weight": self.pesos["news_sentiment"],
                "details": news_result
            }
        except Exception as e:
            print(f"⚠️ Error en noticias: {e}")
            components["news_sentiment"] = {"score": 0, "weight": self.pesos["news_sentiment"], "error": str(e)}
        
        # ==========================================
        # 2. REDES SOCIALES (Reddit)
        # ==========================================
        try:
            social_result = self.reddit_collector.get_social_sentiment()
            components["social_sentiment"] = {
                "score": social_result["score"],
                "weight": self.pesos["social_sentiment"],
                "details": social_result
            }
        except Exception as e:
            print(f"⚠️ Error en Reddit: {e}")
            components["social_sentiment"] = {"score": 0, "weight": self.pesos["social_sentiment"], "error": str(e)}
        
        # ==========================================
        # 3. INDICADORES TÉCNICOS
        # ==========================================
        try:
            technical_result = self.technical_collector.get_technical_sentiment()
            components["technical"] = {
                "score": technical_result["score"],
                "weight": self.pesos["technical"],
                "details": technical_result
            }
        except Exception as e:
            print(f"⚠️ Error en técnicos: {e}")
            components["technical"] = {"score": 0, "weight": self.pesos["technical"], "error": str(e)}
        
        # ==========================================
        # 4. VIX
        # ==========================================
        try:
            vix_result = self.technical_collector.get_vix_sentiment()
            components["vix"] = {
                "score": vix_result["score"],
                "weight": self.pesos["vix"],
                "details": vix_result
            }
        except Exception as e:
            print(f"⚠️ Error en VIX: {e}")
            components["vix"] = {"score": 0, "weight": self.pesos["vix"], "error": str(e)}
        
        # ==========================================
        # 5. PUT/CALL RATIO
        # ==========================================
        try:
            putcall_result = self.technical_collector.get_put_call_sentiment()
            components["put_call_ratio"] = {
                "score": putcall_result["score"],
                "weight": self.pesos["put_call_ratio"],
                "details": putcall_result
            }
        except Exception as e:
            print(f"⚠️ Error en Put/Call: {e}")
            components["put_call_ratio"] = {"score": 0, "weight": self.pesos["put_call_ratio"], "error": str(e)}
        
        # ==========================================
        # 6. RECOMENDACIONES DE ANALISTAS
        # ==========================================
        try:
            analyst_result = self.analyst_collector.get_analyst_sentiment()
            components["analyst_recommendations"] = {
                "score": analyst_result["score"],
                "weight": self.pesos["analyst_recommendations"],
                "details": analyst_result
            }
        except Exception as e:
            print(f"⚠️ Error en analistas: {e}")
            components["analyst_recommendations"] = {"score": 0, "weight": self.pesos["analyst_recommendations"], "error": str(e)}
        
        # ==========================================
        # CALCULAR SCORE FINAL
        # ==========================================
        final_score = self._calculate_weighted_score(components)
        interpretation = self._interpret_score(final_score)
        
        result = {
            "final_score": round(final_score, 2),
            "interpretation": interpretation,
            "components": components,
            "timestamp": datetime.now().isoformat(),
            "weights_used": self.pesos
        }
        
        # Imprimir resumen
        self._print_summary(result)
        
        return result
    
    def _calculate_weighted_score(self, components):
        """
        Calcula el score final ponderado
        
        Fórmula:
        Final = Σ (score_i × peso_i) / Σ pesos
        """
        total_weighted_score = 0
        total_weight = 0
        
        for name, data in components.items():
            score = data.get("score", 0)
            weight = data.get("weight", 0)
            
            # Solo incluir si no hay error
            if "error" not in data:
                total_weighted_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0
        
        return total_weighted_score / total_weight
    
    def _interpret_score(self, score):
        """
        Interpreta el score en texto
        """
        if score >= 50:
            return "Strong Bullish 🟢🟢"
        elif score >= 30:
            return "Bullish 🟢"
        elif score >= 10:
            return "Slightly Bullish 🟢"
        elif score >= -10:
            return "Neutral ⚪"
        elif score >= -30:
            return "Slightly Bearish 🔴"
        elif score >= -50:
            return "Bearish 🔴"
        else:
            return "Strong Bearish 🔴🔴"
    
    def _print_summary(self, result):
        """
        Imprime un resumen bonito del resultado
        """
        print("\n" + "="*60)
        print("📊 RESUMEN DEL SENTIMENT SCORE")
        print("="*60)
        
        print(f"\n🎯 SCORE FINAL: {result['final_score']}")
        print(f"📈 INTERPRETACIÓN: {result['interpretation']}")
        
        print("\n" + "-"*40)
        print("DESGLOSE POR COMPONENTE:")
        print("-"*40)
        
        for name, data in result["components"].items():
            score = data.get("score", 0)
            weight = data.get("weight", 0)
            
            # Emoji según el score
            if score > 20:
                emoji = "🟢"
            elif score > -20:
                emoji = "⚪"
            else:
                emoji = "🔴"
            
            # Barra visual
            bar_length = int(abs(score) / 5)
            if score >= 0:
                bar = "+" + "█" * bar_length
            else:
                bar = "-" + "█" * bar_length
            
            print(f"{emoji} {name:25} | Score: {score:6.1f} | Peso: {weight}% | {bar}")
        
        print("\n" + "="*60)
        print(f"⏰ Calculado: {result['timestamp']}")
        print("="*60 + "\n")


# ============================================
# API ENDPOINT HELPER
# ============================================
def get_sentiment_json():
    """
    Función helper para obtener el resultado en formato JSON
    Útil para conectar con el frontend
    """
    calculator = SentimentCalculator()
    return calculator.calculate_sentiment()


# ============================================
# EJECUTAR SI SE CORRE DIRECTAMENTE
# ============================================
if __name__ == "__main__":
    calculator = SentimentCalculator()
    result = calculator.calculate_sentiment()
    
    # También guardar en un archivo JSON
    import json
    with open("sentiment_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\n✅ Resultado guardado en 'sentiment_result.json'")
