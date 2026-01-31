# NASDAQ SENTIMENT TRACKER - CONFIGURACION

# Finnhub API Key (pon tu key aqui)
FINNHUB_API_KEY = "d5um3vpr01qr4f89n1ggd5um3vpr01qr4f89n1h0"
# Alpha Vantage (dejalo asi por ahora)
ALPHA_VANTAGE_API_KEY = "demo"

# Reddit (no lo usaremos por ahora)
REDDIT_CLIENT_ID = "no_usar"
REDDIT_CLIENT_SECRET = "no_usar"
REDDIT_USER_AGENT = "NasdaqSentimentTracker/1.0"

# Pesos del algoritmo
PESOS = {
    "news_sentiment": 25,
    "social_sentiment": 15,
    "technical": 20,
    "vix": 15,
    "put_call_ratio": 10,
    "analyst_recommendations": 15
}

# Acciones del NASDAQ a monitorear
NASDAQ_STOCKS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "AMD",
    "NFLX",
    "INTC",
]

NASDAQ_INDEX = "QQQ"