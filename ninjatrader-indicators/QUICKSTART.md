# 🚀 Quick Start Guide - NinjaTrader Indicators

## Prerequisites
- ✅ NinjaTrader 8 installed
- ✅ NASDAQ Sentiment API server running
- ✅ Basic familiarity with NinjaTrader

## 3-Minute Setup

### 1️⃣ Start Your API Server (30 seconds)

```bash
cd /path/to/nasdaq-sentiment-api
python server.py
```

Wait for: `* Running on http://0.0.0.0:5000`

### 2️⃣ Install Indicators (1 minute)

**Easy Method:**
1. Copy both `.cs` files from `ninjatrader-indicators/` folder
2. Paste into: `Documents\NinjaTrader 8\bin\Custom\Indicators\`
3. Open NinjaTrader → Tools → Edit NinjaScript → Indicator
4. Click References → Add → Browse
5. Select `Newtonsoft.Json.dll` from `C:\Program Files\NinjaTrader 8\bin\`
6. Press F5 to compile
7. Look for "Compiled successfully" ✅

### 3️⃣ Add to Chart (30 seconds)

1. Open any chart
2. Right-click → Indicators → "NasdaqSentimentIndicator"
3. Set API URL: `http://localhost:5000/api/sentiment`
4. Click Apply → OK
5. See your sentiment score! 🎉

### 4️⃣ Optional: Add Components (30 seconds)

1. Right-click chart → Indicators → "NasdaqSentimentComponents"  
2. Set API URL: `http://localhost:5000/api/sentiment/components`
3. Click Apply → OK
4. See all 6 components! 📊

## ✅ Verify It's Working

You should see:
- A colored line showing sentiment score
- Title showing interpretation (e.g., "Bullish 🟢")
- Score updating every 15 minutes
- Console messages in Output Window

## ❌ Common Issues

| Problem | Solution |
|---------|----------|
| "Newtonsoft.Json not found" | Add the DLL reference (Step 2.4-2.6) |
| Shows "Loading..." | Wait 60 seconds for first update |
| All zeros | Check API server is running |
| Won't compile | Make sure you copied the ENTIRE .cs file |

## 🎯 What You Can Do Now

- **View Sentiment:** See real-time NASDAQ sentiment on any chart
- **Track Components:** Understand what's driving sentiment  
- **Set Alerts:** Create alerts on sentiment thresholds
- **Build Strategies:** Use sentiment in your automated trading

## 📚 Next Steps

- Read full `README.md` for detailed configuration
- Try different chart setups and timeframes
- Experiment with combining sentiment + price action
- Consider deploying API to cloud for 24/7 access

## 🆘 Still Having Issues?

1. Check NinjaTrader Output Window for errors
2. Verify API works in browser: http://localhost:5000/api/sentiment
3. Read troubleshooting section in main README.md
4. Make sure you're using NinjaTrader 8 (not 7)

---

**That's it! You now have NASDAQ sentiment data on your charts!** 🚀
