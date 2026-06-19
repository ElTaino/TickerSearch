# Using the library Streamlist to turn this into a web dashboard interface. Helps turn it into an interactive web app with not much extra code. Doesn't need HTML, CSS, or Javascript and another benefit is that it works natively with yfinance and Plotly. USA vs Australia tomorrow we're gonna win 4-1 you heard it here first.

#1. Follow steps in TickerSearch.py to get the appropriate libraries for yfinance. I'm not sure if the below command will get all of the libraries. But regardless, you still need to make sure we're in the correct location to reference the libraries (wherever the stuff is downloaded to)
#2. In CMD run the command "pip install streamlit yfinance plotly pandas"

#TO RUN THIS PROGRAM IT IS NOT THE NORMAL TERMINAL COMMAND FOR THIS CLASS.
#... IT MUST BE "streamlit run app_web_StockData.py".
#... ... The terminal will start a local server instance and automatically open a new tab in the default browser (usually at http://localhost:8501). It will display an active responsive webpage where you can change the tickers in the sidebar, move the RSI sliders, check live metrics, and watch the charts instantly re-render in response. 

import streamlit as st
import yfinance as yf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Configure the Web Page Layout
st.set_page_config(page_title="Stock Analytics Dashboards", layout="wide")
st.title("📈 Advanced Technical Analysis Dashboards")
st.markdown("This web app fetches live stock data from Yahoo Finance and calculates multiple real-time technical indicators.")

# --- ADDED SECTION: TOP MOVING TICKER BANNER BAR ---
try:
    # 1. Provide a basket of the market's most heavily traded high-volume stocks
    active_tickers = ["SPY", "QQQ", "NVDA", "SMCI", "BABA", "GOOGL", "VEEV", "AXP"]
    
    # 2. Grab today's raw 1-day pricing structures via a single fast query matrix
    ticker_data = yf.download(active_tickers, period="2d", interval="1d", auto_adjust=True)
    
    # Process and build a flat layout mapping out tracking string items
    ticker_items = []
    for ticker in active_tickers:
        try:
            # Safely slice out close vectors corresponding to our targeted asset keys
            close_series = ticker_data['Close'][ticker].dropna()
            
            if len(close_series) >= 2:
                today_p = float(close_series.iloc[-1])
                yesterday_p = float(close_series.iloc[-2])
                
                # Math calculations evaluating percent swings
                pct_change = ((today_p - yesterday_p) / yesterday_p) * 100
                color_symbol = "🟢" if pct_change >= 0 else "🔴"
                sign = "+" if pct_change >= 0 else ""
                
                ticker_items.append(f"{color_symbol} <b>{ticker}</b>: ${today_p:,.2f} ({sign}{pct_change:.2f}%)")
        except:
            continue  # Silently skip any individual assets that fail to process

    # 3. Construct a running HTML marquee string sequence
    marquee_content = " &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ".join(ticker_items)
    
    # 4. Inject structural CSS layouts directly to force cross-browser horizontal scroll loops
    st.markdown(f"""
        <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; margin-bottom: 25px; overflow: hidden; white-space: nowrap;">
            <marquee behavior="scroll" direction="left" scrollamount="5" style="color: #ffffff; font-family: monospace; font-size: 15px;">
                {marquee_content}
            </marquee>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    # Fail silently or provide a minor notice if api blocks request
    st.warning("Top ticker tape temporarily unavailable.")
# --- END OF TICKER TAPE BANNER SECTION ---

# Build Sidebar User Inputs
st.sidebar.header("Dashboard Configuration")
ticker_symbol = st.sidebar.text_input("Stock Ticker Symbol", value="AAPL").upper()
time_period = st.sidebar.selectbox("Data Time Horizon", options=["1mo", "3mo", "6mo", "1y", "2y"], index=2)
rsi_window = st.sidebar.slider("RSI Lookback Window (Days)", min_value=5, max_value=30, value=14)
bb_window = st.sidebar.slider("Bollinger Bands Window (Days)", min_value=10, max_value=50, value=20)
bb_std = st.sidebar.slider("Bollinger Bands Std Dev", min_value=1.0, max_value=3.0, value=2.0, step=0.1)

# Main Application Logic
if ticker_symbol:
    try:
        # Fetch Data via API
        with st.spinner(f"Loading market metrics for {ticker_symbol}..."):
            # 🌟 ULTIMATE FIX: auto_adjust=True strips MultiIndex layers at the source to preserve Plotly interaction
            stock_data = yf.download(ticker_symbol, period=time_period, interval="1d", auto_adjust=True)
        
        if stock_data.empty:
            st.error("Invalid ticker symbol or no data found for this period.")
        else:
            # Flatten pricing vectors to ensure raw 1D arrays are fed to Plotly
            dates = stock_data.index
            close_prices = stock_data['Close'].values.flatten()
            open_prices = stock_data['Open'].values.flatten()
            volume_values = stock_data['Volume'].values.flatten()

            # --- Technical Indicator Calculations ---
            
            # 1. Moving Averages
            stock_data['MA20'] = pd.Series(close_prices).rolling(window=20).mean().values
            stock_data['MA50'] = pd.Series(close_prices).rolling(window=50).mean().values

            # 2. RSI Calculations
            delta = pd.Series(close_prices).diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=rsi_window).mean()
            avg_loss = loss.rolling(window=rsi_window).mean()
            rs = avg_gain / avg_loss
            stock_data['RSI'] = (100 - (100 / (1 + rs))).values

            # 3. Bollinger Bands Calculations
            stock_data['BB_Middle'] = pd.Series(close_prices).rolling(window=bb_window).mean().values
            bb_std_dev = pd.Series(close_prices).rolling(window=bb_window).std().values
            stock_data['BB_Upper'] = stock_data['BB_Middle'] + (bb_std * bb_std_dev)
            stock_data['BB_Lower'] = stock_data['BB_Middle'] - (bb_std * bb_std_dev)

            # 4. MACD Calculations (12-Day EMA, 26-Day EMA, 9-Day Signal)
            ema12 = pd.Series(close_prices).ewm(span=12, adjust=False).mean()
            ema26 = pd.Series(close_prices).ewm(span=26, adjust=False).mean()
            print(f"Data length going into EMAs: {len(close_prices)}")
            stock_data['MACD'] = (ema12 - ema26).values
            
            stock_data['MACD_Signal'] = pd.Series(stock_data['MACD']).ewm(span=9, adjust=False).mean().values
            stock_data['MACD_Hist'] = (stock_data['MACD'] - stock_data['MACD_Signal']).values

            # 5. Color Coding for Volume Bars (Green for up days, Red for down days)
            volume_colors = ['#2ca02c' if c >= o else '#d62728' for c, o in zip(close_prices, open_prices)]

            # 6. Advanced Color Coding for MACD Histogram (Matches TradingView professional aesthetics)
            macd_hist = stock_data['MACD_Hist'].values.flatten()

            if len(stock_data) > 5:
              print("--- EMA MATHEMATICS VERIFICATION ---")
              print("Last 5 rows of EMA 12:\n", ema12.tail(5).values)
              print("Last 5 rows of EMA 26:\n", ema26.tail(5).values)
            macd_colors = []
            for i in range(len(macd_hist)):
                if macd_hist[i] >= 0:
                    # Green day: check if momentum is expanding (brighter) or contracting (darker)
                    macd_colors.append('#26a69a' if i == 0 or macd_hist[i] >= macd_hist[i-1] else '#b2dfdb')
                else:
                    # Red day: check if selling momentum is expanding (brighter) or contracting (darker)
                    macd_colors.append('#ef5350' if i == 0 or macd_hist[i] <= macd_hist[i-1] else '#ffcdd2')

            # Display high-level metric cards on the website layout
            latest_price = float(close_prices[-1])
            price_change = float(close_prices[-1] - close_prices[-2])
            
            col1, col2 = st.columns(2)
            col1.metric(label=f"Current {ticker_symbol} Closing Price", value=f"${latest_price:,.2f}", delta=f"${price_change:,.2f}")
            
            if not stock_data['RSI'].empty:
                latest_rsi = float(stock_data['RSI'].iloc[-1])
                col2.metric(label="Current RSI Score", value=f"{latest_rsi:.1f}", 
                            delta="Overbought Zone" if latest_rsi >= 70 else "Oversold Zone" if latest_rsi <= 30 else "Normal Momentum")

            # --- PLOTLY INTERACTIVE ENGINE GENERATION ---
            # Expanded layout to a 4-panel visual system sharing the horizontal date pipeline
            fig = make_subplots(rows=4, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.03, 
                                row_heights=[0.45, 0.15, 0.20, 0.20])
            
            # --- PANEL 1: Main Price Chart + MA Overlays + Bollinger Bands ---
            fig.add_trace(go.Scatter(x=dates, y=close_prices, name='Actual Close Price', line=dict(color='#1f77b4', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=stock_data['MA20'].values.flatten(), name='20-Day MA', line=dict(color='#ff7f0e', width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=stock_data['MA50'].values.flatten(), name='50-Day MA', line=dict(color='#2ca02c', width=1.5)), row=1, col=1)
            
            # Bollinger Bands Lines
            fig.add_trace(go.Scatter(x=dates, y=stock_data['BB_Upper'].values.flatten(), name='BB Upper', line=dict(color='#bcbd22', width=1, dash='dash'), legendgroup="bb"), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=stock_data['BB_Middle'].values.flatten(), name='BB Middle', line=dict(color='#7f7f7f', width=1, dash='dot'), legendgroup="bb"), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=stock_data['BB_Lower'].values.flatten(), name='BB Lower', line=dict(color='#bcbd22', width=1, dash='dash'), legendgroup="bb"), row=1, col=1)

            # --- PANEL 2: Volume Bar Graph ---
            fig.add_trace(go.Bar(x=dates, y=volume_values, name='Volume', marker_color=volume_colors, opacity=0.7), row=2, col=1)

            # --- PANEL 3: RSI Momentum Indicator ---
            fig.add_trace(go.Scatter(x=dates, y=stock_data['RSI'].values.flatten(), name=f'{rsi_window}-Day RSI', line=dict(color='#9467bd', width=1.5)), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.6, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.6, row=3, col=1)
            fig.add_hrect(y0=30, y1=70, fillcolor="#9467bd", opacity=0.08, layer="below", line_width=0, row=3, col=1)
            
            # --- PANEL 4: MACD Indicator Panel ---
            fig.add_trace(go.Scatter(x=dates, y=stock_data['MACD'].values.flatten(), name='MACD', line=dict(color='#1f77b4', width=1.5)), row=4, col=1)
            fig.add_trace(go.Scatter(x=dates, y=stock_data['MACD_Signal'].values.flatten(), name='Signal Line', line=dict(color='#ff7f0e', width=1.5)), row=4, col=1)
            fig.add_trace(go.Bar(x=dates, y=macd_hist, name='MACD Hist', marker_color=macd_colors, opacity=0.8), row=4, col=1)
            fig.add_hline(y=0, line_color="gray", opacity=0.5, row=4, col=1)

            # Configure Global Axis, Titles, Window Scales, and Integrated Tracking Pipeline
            fig.update_layout(
                title=f"<b>{ticker_symbol} Advanced Technical Dashboard</b>",
                xaxis4_title="Date",
                yaxis_title="Price (USD)",
                yaxis2_title="Volume",
                yaxis3_title="RSI",
                yaxis3_range=[10, 90],
                yaxis4_title="MACD",
                height=950, # Scaled height upwards so 4 panels aren't squished
                hovermode="x unified", 
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
                margin=dict(l=50, r=30, t=80, b=50)
            )
            
            # Render the high-density framework canvas straight to the browser view
            st.plotly_chart(fig, use_container_width=True)
            
            # Optional raw spreadsheet inspector inside the webpage UI
            # Optional raw spreadsheet inspector inside the webpage UI
            if st.checkbox("Show Data Log Table"):
                st.subheader("Raw Data Stream Inspect")
                st.dataframe(stock_data.tail(10))

    except Exception as e:
        st.error(f"Application encountered an issue processing request details: {e}")