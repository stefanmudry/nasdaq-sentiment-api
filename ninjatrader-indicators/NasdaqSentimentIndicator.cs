#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.DrawingTools;
using Newtonsoft.Json.Linq;
#endregion

/// <summary>
/// NASDAQ Sentiment Tracker Indicator for NinjaTrader
/// Displays real-time sentiment score from the NASDAQ Sentiment API
/// Score ranges from -100 (Strong Bearish) to +100 (Strong Bullish)
/// </summary>
namespace NinjaTrader.NinjaScript.Indicators
{
    public class NasdaqSentimentIndicator : Indicator
    {
        #region Variables
        private HttpClient httpClient;
        private DateTime lastUpdate = DateTime.MinValue;
        private double currentSentiment = 0;
        private string interpretation = "Loading...";
        private int updateIntervalMinutes = 15; // Cache duration from API
        private bool isUpdating = false;
        #endregion

        #region Properties
        
        [NinjaScriptProperty]
        [Range(1, int.MaxValue)]
        [Display(Name = "API URL", Description = "URL of your NASDAQ Sentiment API server", Order = 1, GroupName = "Parameters")]
        public string ApiUrl { get; set; }

        [NinjaScriptProperty]
        [Range(1, 60)]
        [Display(Name = "Update Interval (minutes)", Description = "How often to fetch new data (min 1, recommended 15)", Order = 2, GroupName = "Parameters")]
        public int UpdateInterval 
        { 
            get { return updateIntervalMinutes; }
            set { updateIntervalMinutes = value; }
        }

        [Browsable(false)]
        [XmlIgnore]
        public Series<double> Sentiment
        {
            get { return Values[0]; }
        }
        
        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = @"NASDAQ Sentiment Tracker - Displays sentiment score from API";
                Name = "NASDAQ Sentiment";
                Calculate = Calculate.OnBarClose;
                IsOverlay = false;
                DisplayInDataBox = true;
                DrawOnPricePanel = false;
                DrawHorizontalGridLines = true;
                DrawVerticalGridLines = true;
                PaintPriceMarkers = true;
                ScaleJustification = NinjaTrader.Gui.Chart.ScaleJustification.Right;
                IsSuspendedWhileInactive = true;
                
                // Default API URL
                ApiUrl = "http://localhost:5000/api/sentiment";
                UpdateInterval = 15;
                
                // Add sentiment value series
                AddPlot(new Stroke(Brushes.DodgerBlue, 2), PlotStyle.Line, "Sentiment");
                
                // Add zones for visual reference
                AddLine(Brushes.Green, 50, "Strong Bullish");
                AddLine(Brushes.LightGreen, 30, "Bullish");
                AddLine(Brushes.Gray, 0, "Neutral");
                AddLine(Brushes.LightCoral, -30, "Bearish");
                AddLine(Brushes.Red, -50, "Strong Bearish");
            }
            else if (State == State.Configure)
            {
                // Initialize HTTP client
                httpClient = new HttpClient();
                httpClient.Timeout = TimeSpan.FromSeconds(10);
            }
            else if (State == State.Terminated)
            {
                // Cleanup
                if (httpClient != null)
                {
                    httpClient.Dispose();
                    httpClient = null;
                }
            }
        }

        protected override void OnBarUpdate()
        {
            // Update sentiment data if needed
            if (CurrentBar < 1)
                return;
            
            // Check if we need to update
            TimeSpan timeSinceUpdate = DateTime.Now - lastUpdate;
            if (timeSinceUpdate.TotalMinutes >= updateIntervalMinutes && !isUpdating)
            {
                Task.Run(() => UpdateSentimentData());
            }
            
            // Set the current sentiment value
            Sentiment[0] = currentSentiment;
            
            // Color the plot based on sentiment
            if (currentSentiment >= 50)
                PlotBrushes[0][0] = Brushes.DarkGreen;
            else if (currentSentiment >= 30)
                PlotBrushes[0][0] = Brushes.Green;
            else if (currentSentiment >= 10)
                PlotBrushes[0][0] = Brushes.LightGreen;
            else if (currentSentiment >= -10)
                PlotBrushes[0][0] = Brushes.Gray;
            else if (currentSentiment >= -30)
                PlotBrushes[0][0] = Brushes.LightCoral;
            else if (currentSentiment >= -50)
                PlotBrushes[0][0] = Brushes.Red;
            else
                PlotBrushes[0][0] = Brushes.DarkRed;
        }

        private async void UpdateSentimentData()
        {
            if (isUpdating)
                return;
                
            isUpdating = true;
            
            try
            {
                // Fetch data from API
                string url = ApiUrl;
                HttpResponseMessage response = await httpClient.GetAsync(url);
                
                if (response.IsSuccessStatusCode)
                {
                    string jsonContent = await response.Content.ReadAsStringAsync();
                    JObject json = JObject.Parse(jsonContent);
                    
                    // Parse the response
                    bool success = (bool)json["success"];
                    if (success && json["data"] != null)
                    {
                        currentSentiment = (double)json["data"]["final_score"];
                        interpretation = (string)json["data"]["interpretation"];
                        lastUpdate = DateTime.Now;
                        
                        Print(string.Format("Sentiment updated: {0} ({1})", currentSentiment, interpretation));
                    }
                    else
                    {
                        Print("API returned unsuccessful response");
                    }
                }
                else
                {
                    Print(string.Format("Error fetching sentiment: HTTP {0}", response.StatusCode));
                }
            }
            catch (Exception ex)
            {
                Print(string.Format("Error updating sentiment: {0}", ex.Message));
            }
            finally
            {
                isUpdating = false;
            }
        }
        
        public override string DisplayName
        {
            get { return string.Format("NASDAQ Sentiment ({0})", interpretation); }
        }
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private NasdaqSentimentIndicator[] cacheNasdaqSentimentIndicator;
		public NasdaqSentimentIndicator NasdaqSentimentIndicator(string apiUrl, int updateInterval)
		{
			return NasdaqSentimentIndicator(Input, apiUrl, updateInterval);
		}

		public NasdaqSentimentIndicator NasdaqSentimentIndicator(ISeries<double> input, string apiUrl, int updateInterval)
		{
			if (cacheNasdaqSentimentIndicator != null)
				for (int idx = 0; idx < cacheNasdaqSentimentIndicator.Length; idx++)
					if (cacheNasdaqSentimentIndicator[idx] != null && cacheNasdaqSentimentIndicator[idx].ApiUrl == apiUrl && cacheNasdaqSentimentIndicator[idx].UpdateInterval == updateInterval && cacheNasdaqSentimentIndicator[idx].EqualsInput(input))
						return cacheNasdaqSentimentIndicator[idx];
			return CacheIndicator<NasdaqSentimentIndicator>(new NasdaqSentimentIndicator(){ ApiUrl = apiUrl, UpdateInterval = updateInterval }, input, ref cacheNasdaqSentimentIndicator);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.NasdaqSentimentIndicator NasdaqSentimentIndicator(string apiUrl, int updateInterval)
		{
			return indicator.NasdaqSentimentIndicator(Input, apiUrl, updateInterval);
		}

		public Indicators.NasdaqSentimentIndicator NasdaqSentimentIndicator(ISeries<double> input , string apiUrl, int updateInterval)
		{
			return indicator.NasdaqSentimentIndicator(input, apiUrl, updateInterval);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.NasdaqSentimentIndicator NasdaqSentimentIndicator(string apiUrl, int updateInterval)
		{
			return indicator.NasdaqSentimentIndicator(Input, apiUrl, updateInterval);
		}

		public Indicators.NasdaqSentimentIndicator NasdaqSentimentIndicator(ISeries<double> input , string apiUrl, int updateInterval)
		{
			return indicator.NasdaqSentimentIndicator(input, apiUrl, updateInterval);
		}
	}
}

#endregion
