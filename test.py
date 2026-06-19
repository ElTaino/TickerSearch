import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

# Configure the Web Page Layout
st.set_page_config(page_title="Stock Analytics Dashboard", layout="wide")
st.title("📈 Interactive Technical Analysis Dashboard")
st.markdown("This web app fetches live stock data from Yahoo Finance and calculates real-time technical markers.")

# Build Sidebar User Inputs
st.sidebar.header("Dashboard Configuration")
ticker_symbol = st.sidebar.text_input("Stock Ticker Symbol", value="AAPL").upper()
time_period = st.sidebar.selectbox("Data Time Horizon", options=["1mo", "3mo", "6mo", "1y", "2y"], index=2)
rsi_window = st.sidebar.slider("RSI Lookback Window (Days)", min_value=5, max_value=30, value=14)

# Main Application Logic
if ticker_symbol:
    try:
        # Fetch Data via API
        with st.spinner(f"Loading market metrics for {ticker_symbol}..."):
            # 🌟 ULTIMATE FIX: auto_adjust=True forces yfinance to drop the nested MultiIndex tuples entirely
            stock_data = yf.download(ticker_symbol, period=time_period, interval="1d", auto_adjust=True)

        if stock_data.empty:
            st.error("Invalid ticker symbol or no data found for this period.")
        else:
            # Clean extraction arrays to guarantee single-dimension vectors for Plotly
            dates = stock_data.index
            close_prices = stock_data['Close'].values.flatten()
            
            # Mathematical RSI Calculations
            delta = pd.Series(close_prices).diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            
            avg_gain = gain.rolling(window=rsi_window).mean()
            avg_loss = loss.rolling(window=rsi_window).mean()
            
            rs = avg_gain / avg_loss
            stock_data['RSI'] = 100 - (100 / (1 + rs))

            # Calculate the moving averages using flat vectors
            stock_data['MA20'] = pd.Series(close_prices).rolling(window=20).mean().values
            stock_data['MA50'] = pd.Series(close_prices).rolling(window=50).mean().values

            # Safely parse metric values out of single-element values
            latest_price = float(close_prices[-1])
            price_change = float(close_prices[-1] - close_prices[-2])
            
            col1, col2 = st.columns(2)
            col1.metric(label=f"Current {ticker_symbol} Closing Price", value=f"${latest_price:,.2f}", delta=f"${price_change:,.2f}")
            
            if not stock_data['RSI'].empty:
                latest_rsi = float(stock_data['RSI'].iloc[-1])
                col2.metric(label="Current RSI Score", value=f"{latest_rsi:.1f}", 
                            delta="Overbought Zone" if latest_rsi >= 70 else "Oversold Zone" if latest_rsi <= 30 else "Normal Momentum")

            # --- PLOTLY INTERACTIVE ENGINE GENERATION ---
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.05, 
                                row_heights=[0.7, 0.3])
            
            ma20_prices = stock_data['MA20'].values.flatten()
            ma50_prices = stock_data['MA50'].values.flatten()
            rsi_values = stock_data['RSI'].values.flatten()

            # --- TOP PANEL: Main Price Chart with Moving Averages ---
            fig.add_trace(go.Scatter(x=dates, y=close_prices, name='Actual Close Price', line=dict(color='#1f77b4', width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=ma20_prices, name='20-Day Moving Average', line=dict(color='#ff7f0e', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=ma50_prices, name='50-Day Moving Average', line=dict(color='#2ca02c', width=2)), row=1, col=1)
            
            # --- BOTTOM PANEL: RSI Momentum Indicator ---
            fig.add_trace(go.Scatter(x=dates, y=rsi_values, name=f'{rsi_window}-Day RSI', line=dict(color='#9467bd', width=1.5)), row=2, col=1)
            
            # Add horizontal baseline markers at 30 (Oversold) and 70 (Overbought)
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.6, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.6, row=2, col=1)
            fig.add_hrect(y0=30, y1=70, fillcolor="#9467bd", opacity=0.08, layer="below", line_width=0, row=2, col=1)
            
            # Configure Layout Settings and Unified Hover Mechanics
            fig.update_layout(
                title=f"<b>{ticker_symbol} Advanced Technical Dashboard</b>",
                xaxis2_title="Date",
                yaxis_title="Stock Price (USD)",
                yaxis2_title="RSI Value",
                yaxis2_range=[10, 90],
                height=600,
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=50, r=30, t=80, b=50)
            )
            
            # Hand the functional plot directly to Streamlit
            st.plotly_chart(fig, use_container_width=True)
            
            # Optional raw spreadsheet inspector inside the webpage UI
            if st.checkbox("Show Data Log Table"):
                st.subheader("Raw Data Stream Inspect")
                st.dataframe(stock_data.tail(10))

    except Exception as e:
        st.error(f"Application encountered an issue processing request details: {e}")
