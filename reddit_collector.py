# ============================================
# RECOLECTOR DE REDDIT (REDES SOCIALES)
# ============================================
# Este módulo busca posts en Reddit sobre el NASDAQ
# y analiza si el sentimiento es positivo o negativo

import requests
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, NASDAQ_STOCKS

class RedditCollector:
    """
    Esta clase se encarga de:
    1. Conectarse a Reddit
    2. Buscar posts sobre acciones del NASDAQ
    3. Analizar el sentimiento de los posts
    4. Devolver un puntaje de -100 a +100
    """
    
    def __init__(self):
        self.client_id = REDDIT_CLIENT_ID
        self.client_secret = REDDIT_CLIENT_SECRET
        self.user_agent = REDDIT_USER_AGENT
        self.access_token = None
        
        # Subreddits relacionados con trading/acciones
        self.subreddits = [
            "wallstreetbets",
            "stocks", 
            "investing",
            "options",
            "stockmarket"
        ]
    
    def authenticate(self):
        """
        Se conecta a Reddit y obtiene un token de acceso
        """
        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        
        data = {
            "grant_type": "client_credentials"
        }
        
        headers = {"User-Agent": self.user_agent}
        
        try:
            response = requests.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers
            )
            response.raise_for_status()
            self.access_token = response.json().get("access_token")
            return True
        except Exception as e:
            print(f"Error autenticando con Reddit: {e}")
            return False
    
    def search_posts(self, query, subreddit="all", limit=25):
        """
        Busca posts en Reddit
        
        Parámetros:
        - query: Qué buscar (ej: "AAPL" o "Apple stock")
        - subreddit: En qué subreddit buscar
        - limit: Cuántos posts traer
        """
        if not self.access_token:
            if not self.authenticate():
                return []
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent
        }
        
        url = f"https://oauth.reddit.com/r/{subreddit}/search"
        params = {
            "q": query,
            "sort": "new",
            "limit": limit,
            "t": "week"  # Última semana
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            return [post["data"] for post in posts]
        except Exception as e:
            print(f"Error buscando en Reddit: {e}")
            return []
    
    def analyze_post(self, post):
        """
        Analiza el sentimiento de un post de Reddit
        
        Considera:
        - Título del post
        - Upvotes vs Downvotes
        - Número de comentarios (engagement)
        """
        title = post.get("title", "").lower()
        score = post.get("score", 0)  # Upvotes - Downvotes
        upvote_ratio = post.get("upvote_ratio", 0.5)
        num_comments = post.get("num_comments", 0)
        
        # Analizar el título (similar al análisis de noticias)
        sentiment = self.analyze_text(title)
        
        # Ajustar por popularidad del post
        # Posts muy upvoteados tienen más influencia
        if score > 1000:
            popularity_multiplier = 1.5
        elif score > 100:
            popularity_multiplier = 1.2
        elif score > 10:
            popularity_multiplier = 1.0
        else:
            popularity_multiplier = 0.8
        
        # Ajustar por ratio de upvotes
        # Si tiene muchos downvotes, el sentimiento es más mixto
        ratio_adjustment = (upvote_ratio - 0.5) * 0.5
        
        final_sentiment = sentiment * popularity_multiplier + ratio_adjustment
        
        # Normalizar a -1 a +1
        return max(-1, min(1, final_sentiment))
    
    def analyze_text(self, text):
        """
        Análisis de sentimiento básico para texto de Reddit
        
        Reddit tiene su propio vocabulario, así que incluimos
        términos específicos de la comunidad
        """
        text_lower = text.lower()
        
        # Términos positivos (incluye jerga de Reddit/WSB)
        positive_terms = {
            # Jerga de Reddit
            "moon": 0.8, "mooning": 0.9, "to the moon": 0.9,
            "tendies": 0.7, "diamond hands": 0.8, "💎": 0.8,
            "rocket": 0.7, "🚀": 0.8, "calls": 0.4,
            "bull": 0.6, "bullish": 0.7, "long": 0.5,
            "buy": 0.5, "buying": 0.5, "bought": 0.4,
            "gain": 0.6, "gains": 0.6, "profit": 0.6,
            "green": 0.5, "up": 0.3, "rally": 0.6,
            "breakout": 0.6, "squeeze": 0.7, "yolo": 0.5,
            # Términos financieros positivos
            "upgrade": 0.7, "beat": 0.6, "growth": 0.5,
            "strong": 0.4, "earnings beat": 0.7,
        }
        
        # Términos negativos
        negative_terms = {
            # Jerga de Reddit
            "bag holder": -0.7, "bagholding": -0.7,
            "paper hands": -0.6, "puts": -0.4,
            "bear": -0.6, "bearish": -0.7, "short": -0.5,
            "sell": -0.4, "selling": -0.4, "sold": -0.3,
            "loss": -0.6, "losses": -0.6, "down": -0.3,
            "red": -0.5, "crash": -0.8, "dump": -0.7,
            "rip": -0.5, "rug pull": -0.9,
            # Términos financieros negativos
            "downgrade": -0.7, "miss": -0.6, "missed": -0.6,
            "weak": -0.4, "decline": -0.5, "fall": -0.5,
            "fear": -0.5, "worried": -0.4, "concern": -0.4,
        }
        
        score = 0
        matches = 0
        
        for term, weight in positive_terms.items():
            if term in text_lower:
                score += weight
                matches += 1
        
        for term, weight in negative_terms.items():
            if term in text_lower:
                score += weight
                matches += 1
        
        if matches == 0:
            return 0
        
        return score / matches
    
    def get_social_sentiment(self):
        """
        Obtiene el sentimiento general de Reddit sobre el NASDAQ
        
        Retorna:
        - score: Número de -100 a +100
        - details: Información adicional
        """
        all_scores = []
        details = {}
        
        print("💬 Recolectando sentimiento de Reddit...")
        
        # Buscar posts sobre cada acción
        for symbol in NASDAQ_STOCKS[:5]:  # Limitamos a 5 para no exceder rate limits
            symbol_scores = []
            
            for subreddit in self.subreddits[:2]:  # Limitamos subreddits
                posts = self.search_posts(symbol, subreddit, limit=10)
                
                for post in posts:
                    sentiment = self.analyze_post(post)
                    symbol_scores.append(sentiment)
                    all_scores.append(sentiment)
            
            if symbol_scores:
                avg_score = sum(symbol_scores) / len(symbol_scores)
                details[symbol] = {
                    "score": round(avg_score * 100, 2),
                    "posts_analyzed": len(symbol_scores)
                }
                print(f"  {symbol}: {len(symbol_scores)} posts, score: {avg_score*100:.1f}")
        
        # También buscar "NASDAQ" en general
        nasdaq_posts = self.search_posts("NASDAQ", "wallstreetbets", limit=20)
        for post in nasdaq_posts:
            sentiment = self.analyze_post(post)
            all_scores.append(sentiment)
        
        # Calcular score final
        if all_scores:
            final_score = (sum(all_scores) / len(all_scores)) * 100
        else:
            final_score = 0
        
        return {
            "score": round(final_score, 2),
            "total_posts": len(all_scores),
            "details": details
        }


# ============================================
# PRUEBA DEL MÓDULO
# ============================================
if __name__ == "__main__":
    collector = RedditCollector()
    result = collector.get_social_sentiment()
    
    print("\n" + "="*50)
    print(f"📊 SENTIMENT DE REDDIT: {result['score']}")
    print(f"📝 Total de posts analizados: {result['total_posts']}")
    print("="*50)
