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
/// NASDAQ Sentiment Components Indicator for NinjaTrader
/// Displays individual components that make up the sentiment score:
/// - News Sentiment (25%)
/// - Social Media (15%)
/// - Technical Indicators (20%)
/// - VIX (15%)
/// - Put/Call Ratio (10%)
/// - Analyst Recommendations (15%)
/// </summary>
namespace NinjaTrader.NinjaScript.Indicators
{
    public class NasdaqSentimentComponents : Indicator
    {
        #region Variables
        private HttpClient httpClient;
        private DateTime lastUpdate = DateTime.MinValue;
        private int updateIntervalMinutes = 15;
        private bool isUpdating = false;
        
        // Component scores
        private double newsScore = 0;
        private double socialScore = 0;
        private double technicalScore = 0;
        private double vixScore = 0;
        private double putCallScore = 0;
        private double analystScore = 0;
        private double finalScore = 0;
        #endregion

        #region Properties
        
        [NinjaScriptProperty]
        [Range(1, int.MaxValue)]
        [Display(Name = "API URL", Description = "URL of your NASDAQ Sentiment API server", Order = 1, GroupName = "Parameters")]
        public string ApiUrl { get; set; }

        [NinjaScriptProperty]
        [Range(1, 60)]
        [Display(Name = "Update Interval (minutes)", Description = "How often to fetch new data", Order = 2, GroupName = "Parameters")]
        public int UpdateInterval 
        { 
            get { return updateIntervalMinutes; }
            set { updateIntervalMinutes = value; }
        }

        [Browsable(false)]
        [XmlIgnore]
        public Series<double> News
        {
            get { return Values[0]; }
        }

        [Browsable(false)]
        [XmlIgnore]
        public Series<double> Social
        {
            get { return Values[1]; }
        }

        [Browsable(false)]
        [XmlIgnore]
        public Series<double> Technical
        {
            get { return Values[2]; }
        }

        [Browsable(false)]
        [XmlIgnore]
        public Series<double> Vix
        {
            get { return Values[3]; }
        }

        [Browsable(false)]
        [XmlIgnore]
        public Series<double> PutCall
        {
            get { return Values[4]; }
        }

        [Browsable(false)]
        [XmlIgnore]
        public Series<double> Analyst
        {
            get { return Values[5]; }
        }

        [Browsable(false)]
        [XmlIgnore]
        public Series<double> Final
        {
            get { return Values[6]; }
        }
        
        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = @"NASDAQ Sentiment Components - Shows breakdown of sentiment factors";
                Name = "NASDAQ Sentiment Components";
                Calculate = Calculate.OnBarClose;
                IsOverlay = false;
                DisplayInDataBox = true;
                DrawOnPricePanel = false;
                DrawHorizontalGridLines = true;
                DrawVerticalGridLines = true;
                PaintPriceMarkers = false;
                ScaleJustification = NinjaTrader.Gui.Chart.ScaleJustification.Right;
                IsSuspendedWhileInactive = true;
                
                // Default API URL
                ApiUrl = "http://localhost:5000/api/sentiment/components";
                UpdateInterval = 15;
                
                // Add plots for each component
                AddPlot(new Stroke(Brushes.Orange, 2), PlotStyle.Line, "News (25%)");
                AddPlot(new Stroke(Brushes.Purple, 2), PlotStyle.Line, "Social (15%)");
                AddPlot(new Stroke(Brushes.Blue, 2), PlotStyle.Line, "Technical (20%)");
                AddPlot(new Stroke(Brushes.Cyan, 2), PlotStyle.Line, "VIX (15%)");
                AddPlot(new Stroke(Brushes.Magenta, 2), PlotStyle.Line, "Put/Call (10%)");
                AddPlot(new Stroke(Brushes.Yellow, 2), PlotStyle.Line, "Analyst (15%)");
                AddPlot(new Stroke(Brushes.White, 3), PlotStyle.Line, "Final Score");
                
                // Add reference lines
                AddLine(Brushes.Gray, 0, "Neutral");
                AddLine(Brushes.Green, 50, "Strong Bullish");
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
            if (CurrentBar < 1)
                return;
            
            // Check if we need to update
            TimeSpan timeSinceUpdate = DateTime.Now - lastUpdate;
            if (timeSinceUpdate.TotalMinutes >= updateIntervalMinutes && !isUpdating)
            {
                Task.Run(() => UpdateComponentData());
            }
            
            // Set the current values
            News[0] = newsScore;
            Social[0] = socialScore;
            Technical[0] = technicalScore;
            Vix[0] = vixScore;
            PutCall[0] = putCallScore;
            Analyst[0] = analystScore;
            Final[0] = finalScore;
        }

        private async void UpdateComponentData()
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
                    if (success && json["components"] != null)
                    {
                        JArray components = (JArray)json["components"];
                        
                        foreach (JObject component in components)
                        {
                            string name = ((string)component["name"]).ToLower();
                            double score = (double)component["score"];
                            
                            // Map to the appropriate variable
                            if (name.Contains("news"))
                                newsScore = score;
                            else if (name.Contains("social"))
                                socialScore = score;
                            else if (name.Contains("technical"))
                                technicalScore = score;
                            else if (name.Contains("vix"))
                                vixScore = score;
                            else if (name.Contains("put") || name.Contains("call"))
                                putCallScore = score;
                            else if (name.Contains("analyst"))
                                analystScore = score;
                        }
                        
                        finalScore = (double)json["final_score"];
                        lastUpdate = DateTime.Now;
                        
                        Print(string.Format("Components updated - Final: {0}", finalScore));
                    }
                    else
                    {
                        Print("API returned unsuccessful response");
                    }
                }
                else
                {
                    Print(string.Format("Error fetching components: HTTP {0}", response.StatusCode));
                }
            }
            catch (Exception ex)
            {
                Print(string.Format("Error updating components: {0}", ex.Message));
            }
            finally
            {
                isUpdating = false;
            }
        }
        
        public override string DisplayName
        {
            get { return "NASDAQ Sentiment Components"; }
        }
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private NasdaqSentimentComponents[] cacheNasdaqSentimentComponents;
		public NasdaqSentimentComponents NasdaqSentimentComponents(string apiUrl, int updateInterval)
		{
			return NasdaqSentimentComponents(Input, apiUrl, updateInterval);
		}

		public NasdaqSentimentComponents NasdaqSentimentComponents(ISeries<double> input, string apiUrl, int updateInterval)
		{
			if (cacheNasdaqSentimentComponents != null)
				for (int idx = 0; idx < cacheNasdaqSentimentComponents.Length; idx++)
					if (cacheNasdaqSentimentComponents[idx] != null && cacheNasdaqSentimentComponents[idx].ApiUrl == apiUrl && cacheNasdaqSentimentComponents[idx].UpdateInterval == updateInterval && cacheNasdaqSentimentComponents[idx].EqualsInput(input))
						return cacheNasdaqSentimentComponents[idx];
			return CacheIndicator<NasdaqSentimentComponents>(new NasdaqSentimentComponents(){ ApiUrl = apiUrl, UpdateInterval = updateInterval }, input, ref cacheNasdaqSentimentComponents);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.NasdaqSentimentComponents NasdaqSentimentComponents(string apiUrl, int updateInterval)
		{
			return indicator.NasdaqSentimentComponents(Input, apiUrl, updateInterval);
		}

		public Indicators.NasdaqSentimentComponents NasdaqSentimentComponents(ISeries<double> input , string apiUrl, int updateInterval)
		{
			return indicator.NasdaqSentimentComponents(input, apiUrl, updateInterval);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.NasdaqSentimentComponents NasdaqSentimentComponents(string apiUrl, int updateInterval)
		{
			return indicator.NasdaqSentimentComponents(Input, apiUrl, updateInterval);
		}

		public Indicators.NasdaqSentimentComponents NasdaqSentimentComponents(ISeries<double> input , string apiUrl, int updateInterval)
		{
			return indicator.NasdaqSentimentComponents(input, apiUrl, updateInterval);
		}
	}
}

#endregion
