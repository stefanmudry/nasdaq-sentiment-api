# 🎯 NinjaTrader Indicators for NASDAQ Sentiment Tracker

This folder contains custom NinjaTrader 8 indicators that display real-time sentiment data from the NASDAQ Sentiment API directly on your charts.

## 📊 What's Included

### 1. NasdaqSentimentIndicator.cs
Displays the overall sentiment score as a line indicator with color-coded zones:
- **Strong Bullish** (≥50): Dark Green
- **Bullish** (30-50): Green  
- **Slightly Bullish** (10-30): Light Green
- **Neutral** (-10 to 10): Gray
- **Slightly Bearish** (-30 to -10): Light Coral
- **Bearish** (-50 to -30): Red
- **Strong Bearish** (≤-50): Dark Red

### 2. NasdaqSentimentComponents.cs
Displays all 6 components that make up the sentiment score:
- 📰 News Sentiment (25% weight) - Orange
- 💬 Social Media (15% weight) - Purple
- 📊 Technical Indicators (20% weight) - Blue
- 😱 VIX (15% weight) - Cyan
- 📈 Put/Call Ratio (10% weight) - Magenta
- 🎯 Analyst Recommendations (15% weight) - Yellow
- **Final Score** - White (bold)

---

## 🛠️ Installation Instructions

### Step 1: Start Your Sentiment API Server

Before using the indicators, make sure your sentiment API server is running:

```bash
# Navigate to your project folder
cd /path/to/nasdaq-sentiment-api

# Start the server
python server.py
```

The server should start on `http://localhost:5000` (or your deployed URL).

### Step 2: Import Indicators into NinjaTrader

1. **Open NinjaTrader 8**

2. **Access the NinjaScript Editor:**
   - From the Control Center, click **Tools** → **Edit NinjaScript** → **Indicator**

3. **Import the Indicator Files:**
   
   **Option A: Copy Files Directly**
   - Copy `NasdaqSentimentIndicator.cs` to:
     ```
     C:\Users\[YourUsername]\Documents\NinjaTrader 8\bin\Custom\Indicators\
     ```
   - Copy `NasdaqSentimentComponents.cs` to the same location
   
   **Option B: Use the NinjaScript Editor**
   - In NinjaScript Editor, click **File** → **New** → **Indicator**
   - Delete all the default code
   - Copy and paste the entire content from `NasdaqSentimentIndicator.cs`
   - Save as "NasdaqSentimentIndicator"
   - Repeat for `NasdaqSentimentComponents.cs`

4. **Compile the Indicators:**
   - In NinjaScript Editor, press **F5** or click **Compile**
   - Check the Output window for any errors
   - If you see "Compiled successfully" - you're good to go!

### Step 3: Add Newtonsoft.Json Reference (Required)

The indicators use JSON parsing which requires the Newtonsoft.Json library:

1. In NinjaScript Editor, click **References** (right side panel)
2. Click **Add** → **Browse**
3. Navigate to:
   ```
   C:\Program Files\NinjaTrader 8\bin\
   ```
4. Find and select `Newtonsoft.Json.dll`
5. Click **OK**
6. Press **F5** to recompile

---

## 📈 Using the Indicators

### Adding to a Chart

1. **Open a Chart** (any instrument, any timeframe)

2. **Add the Main Sentiment Indicator:**
   - Right-click on chart → **Indicators** → **NasdaqSentimentIndicator**
   - Configure the settings:
     - **API URL**: Enter your API URL (default: `http://localhost:5000/api/sentiment`)
     - **Update Interval**: How often to fetch data in minutes (default: 15)
   - Click **Apply** → **OK**

3. **Add the Components Indicator (Optional):**
   - Right-click on chart → **Indicators** → **NasdaqSentimentComponents**
   - Configure the API URL: `http://localhost:5000/api/sentiment/components`
   - Click **Apply** → **OK**

### Understanding the Display

#### Main Sentiment Indicator
- The line shows the current sentiment score (-100 to +100)
- Horizontal reference lines show key levels
- Color changes automatically based on sentiment
- Title updates to show current interpretation

#### Components Indicator
- Shows 7 lines: 6 components + final score
- Each component uses a different color
- All components range from -100 to +100
- The white line (Final Score) is the weighted average

---

## ⚙️ Configuration

### Using a Remote API Server

If you deployed your API to the cloud (Railway, Render, etc.):

1. Right-click indicator → **Properties**
2. Change **API URL** to your deployed URL:
   ```
   https://your-app.railway.app/api/sentiment
   ```
3. Click **Apply**

### Adjusting Update Frequency

**Default:** 15 minutes (matches API cache duration)

To change:
1. Right-click indicator → **Properties**
2. Adjust **Update Interval** (1-60 minutes)
3. **Note:** Setting below 15 min won't get fresher data due to API caching

---

## 🔧 Troubleshooting

### "Could not load file or assembly 'Newtonsoft.Json'"
- **Solution:** Add Newtonsoft.Json reference (see Step 3 above)

### Indicator shows "Loading..." or all zeros
- **Check:** Is your API server running?
- **Check:** Can you access the API in a browser? (http://localhost:5000/api/sentiment)
- **Check:** Is the API URL correct in indicator settings?
- **Check:** Check NinjaTrader's Output Window for error messages

### "Error fetching sentiment: HTTP 503"
- **Cause:** API is still calculating initial data
- **Solution:** Wait 30-60 seconds and the indicator will retry automatically

### Sentiment not updating
- **Check:** Verify the Update Interval setting
- **Check:** Look at NinjaTrader Output Window for error messages
- **Solution:** Try refreshing the API manually: `POST http://localhost:5000/api/sentiment/refresh`

### Compilation errors
- **Check:** Make sure you copied the ENTIRE file content
- **Check:** Verify Newtonsoft.Json reference is added
- **Check:** You're using NinjaTrader 8 (not 7)

---

## 💡 Tips & Best Practices

### For Trading
- Use the main indicator on lower timeframe charts (1-5 min)
- Use components indicator to understand what's driving sentiment
- Combine with price action and other technical indicators
- Remember: This is sentiment data, not a trading signal

### For Performance
- Keep Update Interval at 15 min or higher (matches API cache)
- Only load indicators on charts you're actively monitoring
- If running multiple charts, they'll all use the same cached data

### For Development
- Use the local API (`http://localhost:5000`) for testing
- Deploy to cloud for production trading
- Monitor the NinjaTrader Output Window for debug messages

---

## 📊 Using in Strategies

You can also use these indicators in automated strategies:

```csharp
// In your strategy's OnBarUpdate() method

// Get the current sentiment
double sentiment = NasdaqSentimentIndicator("http://localhost:5000/api/sentiment", 15)[0];

// Example: Only go long when sentiment is bullish
if (sentiment > 30 && Close[0] > SMA(20)[0])
{
    EnterLong();
}

// Example: Exit if sentiment turns bearish
if (sentiment < -30 && Position.MarketPosition == MarketPosition.Long)
{
    ExitLong();
}

// Access individual components
double newsScore = NasdaqSentimentComponents("http://localhost:5000/api/sentiment/components", 15).News[0];
double technicalScore = NasdaqSentimentComponents("http://localhost:5000/api/sentiment/components", 15).Technical[0];
```

---

## 🔗 API Endpoints Used

The indicators connect to these endpoints:

| Indicator | Endpoint | Description |
|-----------|----------|-------------|
| NasdaqSentimentIndicator | `/api/sentiment` | Main sentiment score |
| NasdaqSentimentComponents | `/api/sentiment/components` | Component breakdown |

Make sure your API server is running and these endpoints are accessible.

---

## 📈 Example Chart Setups

### Setup 1: Simple Sentiment Overlay
- Chart: NQ (E-mini NASDAQ) or QQQ, 5-minute bars
- Indicator: NasdaqSentimentIndicator only
- Use: Quick sentiment reference while trading

### Setup 2: Full Analysis
- Chart: Any NASDAQ stock, 15-minute bars  
- Indicators:
  1. NasdaqSentimentIndicator (Panel 1)
  2. NasdaqSentimentComponents (Panel 2)
- Use: Deep dive into what's driving sentiment

### Setup 3: Multi-Timeframe
- Workspace with 3 charts:
  - Chart 1: 1-minute (Price + Sentiment)
  - Chart 2: 5-minute (Price + Components)
  - Chart 3: 15-minute (Price + Sentiment)
- Use: See sentiment trends across timeframes

---

## 🚀 What's Next?

### Potential Enhancements
- Add alerts when sentiment crosses key thresholds
- Create a Market Analyzer column version
- Add volume-weighted sentiment
- Include sentiment divergence detection
- Create SuperDOM integration

### Contributing
If you improve these indicators, please share your enhancements!

---

## ⚠️ Disclaimer

**These indicators are for informational purposes only.**

- Not financial advice
- Sentiment data has inherent limitations  
- Always use proper risk management
- Past performance does not guarantee future results
- Test thoroughly before live trading

---

## 📞 Support

For issues related to:
- **Indicators:** Check troubleshooting section above
- **API Server:** See main README.md in project root
- **NinjaTrader:** Visit https://ninjatrader.com/support/

---

## 📄 License

These indicators are provided as-is. Use at your own risk.

Compatible with **NinjaTrader 8**.

---

**Happy Trading! 🚀📈**
