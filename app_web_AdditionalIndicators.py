import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Configure the Web Page Layout
# Test Git Commit after Clone
st.set_page_config(page_title="Stock Analytics Dashboard", layout="wide")
st.title("📈 Advanced Technical Analysis Dashboard")
st.markdown("This web app fetches live stock data from Yahoo Finance and calculates multiple real-time technical indicators.")

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
            stock_data = yf.download(ticker_symbol, period=time_period, interval="1d")
        
        if stock_data.empty:
            st.error("Invalid ticker symbol or no data found for this period.")
        else:
            # --- Technical Indicator Calculations ---
            
            # 1. Moving Averages
            stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
            stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()

            # 2. RSI Calculations
            delta = stock_data['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=rsi_window).mean()
            avg_loss = loss.rolling(window=rsi_window).mean()
            rs = avg_gain / avg_loss
            stock_data['RSI'] = 100 - (100 / (1 + rs))

            # 3. NEW: Bollinger Bands Calculations
            # Middle Band is a standard simple moving average (typically 20 days)
            stock_data['BB_Middle'] = stock_data['Close'].rolling(window=bb_window).mean()
            # Standard deviation calculated over the same rolling window
            bb_std_dev = stock_data['Close'].rolling(window=bb_window).std()
            # Upper and Lower Bands expand and contract based on market volatility
            stock_data['BB_Upper'] = stock_data['BB_Middle'] + (bb_std * bb_std_dev)
            stock_data['BB_Lower'] = stock_data['BB_Middle'] - (bb_std * bb_std_dev)

            # 4. NEW: Color Coding for Volume Bars (Green for up days, Red for down days)
            volume_colors = ['#2ca02c' if close >= open_val else '#d62728' 
                             for close, open_val in zip(stock_data['Close'].squeeze(), stock_data['Open'].squeeze())]

            # Display high-level metric cards on the website layout
            latest_price = float(stock_data['Close'].iloc[-1])
            price_change = float(stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2])
            
            col1, col2 = st.columns(2)
            col1.metric(label=f"Current {ticker_symbol} Closing Price", value=f"${latest_price:,.2f}", delta=f"${price_change:,.2f}")
            
            if not stock_data['RSI'].empty:
                latest_rsi = float(stock_data['RSI'].iloc[-1])
                col2.metric(label="Current RSI Score", value=f"{latest_rsi:.1f}", 
                            delta="Overbought Zone" if latest_rsi >= 70 else "Oversold Zone" if latest_rsi <= 30 else "Normal Momentum")

            # --- PLOTLY INTERACTIVE ENGINE GENERATION ---
            # Expanded layout to a 3-panel visual system sharing the horizontal date pipeline
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.04, 
                                row_heights=[0.55, 0.20, 0.25])
            
            dates = stock_data.index
            close_prices = stock_data['Close'].squeeze()

            # --- PANEL 1: Main Price Chart + MA Overlays + Bollinger Bands ---
            # Core Price & Moving Averages
            fig.add_trace(go.Scatter(x=dates, y=close_prices, name='Actual Close Price', line=dict(color='#1f77b4', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=stock_data['MA20'].squeeze(), name='20-Day MA', line=dict(color='#ff7f0e', width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=stock_data['MA50'].squeeze(), name='50-Day MA', line=dict(color='#2ca02c', width=1.5)), row=1, col=1)
            
            # Bollinger Bands Lines
            fig.add_trace(go.Scatter(x=dates, y=stock_data['BB_Upper'].squeeze(), name='BB Upper', line=dict(color='#bcbd22', width=1, dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=stock_data['BB_Middle'].squeeze(), name='BB Middle', line=dict(color='#7f7f7f', width=1, dash='dot')), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=stock_data['BB_Lower'].squeeze(), name='BB Lower', line=dict(color='#bcbd22', width=1, dash='dash')), row=1, col=1)

            # --- PANEL 2: Volume Bar Graph ---
            fig.add_trace(go.Bar(x=dates, y=stock_data['Volume'].squeeze(), name='Volume', marker_color=volume_colors, opacity=0.7), row=2, col=1)

            # --- PANEL 3: RSI Momentum Indicator ---
            fig.add_trace(go.Scatter(x=dates, y=stock_data['RSI'].squeeze(), name=f'{rsi_window}-Day RSI', line=dict(color='#9467bd', width=1.5)), row=3, col=1)
            
            # RSI Threshold Guides & Shaded Normal Zone Channel
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.6, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.6, row=3, col=1)
            fig.add_hrect(y0=30, y1=70, fillcolor="#9467bd", opacity=0.08, layer="below", line_width=0, row=3, col=1)
            
            # Configure Global Axis, Titles, Window Scales, and Integrated Tracking Pipeline
            fig.update_layout(
                title=f"<b>{ticker_symbol} Advanced Technical Dashboard</b>",
                xaxis3_title="Date",
                yaxis_title="Price (USD)",
                yaxis2_title="Volume",
                yaxis3_title="RSI Value",
                yaxis3_range=[10, 90],
                height=800, # Expanded canvas height to cleanly hold all 3 graphs
                hovermode="x unified", # Locks single tracker vertical bar across all 3 charts
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=50, r=30, t=80, b=50)
            )
            
            # Render the high-density framework canvas straight to the browser view
            st.plotly_chart(fig, use_container_width=True)
            
            # Optional raw spreadsheet inspector inside the webpage UI
            if st.checkbox("Show Data Log Table"):
                st.subheader("Raw Data Stream Inspect")
                st.dataframe(stock_data.tail(10))

    except Exception as e:
        st.error(f"Application encountered an issue processing request details: {e}")
