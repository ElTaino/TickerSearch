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
          stock_data = yf.download(ticker_symbol, period=time_period, interval="1d")

        if stock_data.empty:
            st.error("Invalid ticker symbol or no data found for this period.")
        else:
            # 🌟 FIX: Drop the multi-index ticker level so columns become flat strings again
            if isinstance(stock_data.columns, pd.MultiIndex):
                stock_data.columns = stock_data.columns.droplevel('Ticker')
            
    # Mathematical RSI Calculations continue normally below...

            # Mathematical RSI Calculations
            delta = stock_data['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            
            # Using simple rolling window for Streamlit
            avg_gain = gain.rolling(window=rsi_window).mean()
            avg_loss = loss.rolling(window=rsi_window).mean()
            
            rs = avg_gain / avg_loss
            stock_data['RSI'] = 100 - (100 / (1 + rs))

            # Calculate the moving averages using PANDAS rolling math
            stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
            stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()

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
            # Create a 2 panel visual layout with a shared timeline X-axis (replaces plt.subplots)
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.05, 
                                row_heights=[0.7, 0.3])
            
            # Cleanly extract pandas index and series data
            dates = stock_data.index
            close_prices = stock_data['Close'].squeeze()
            ma20_prices = stock_data['MA20'].squeeze()
            ma50_prices = stock_data['MA50'].squeeze()
            rsi_values = stock_data['RSI'].squeeze()

            # --- TOP PANEL: Main Price Chart with Moving Averages ---
            fig.add_trace(go.Scatter(x=dates, y=close_prices, name='Actual Close Price', line=dict(color='#1f77b4', width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=ma20_prices, name='20-Day Moving Average', line=dict(color='#ff7f0e', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=dates, y=ma50_prices, name='50-Day Moving Average', line=dict(color='#2ca02c', width=2)), row=1, col=1)
            
            # --- BOTTOM PANEL: RSI Momentum Indicator ---
            fig.add_trace(go.Scatter(x=dates, y=rsi_values, name=f'{rsi_window}-Day RSI', line=dict(color='#9467bd', width=1.5)), row=2, col=1)
            
            # Add horizontal baseline markers at 30 (Oversold) and 70 (Overbought)
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.6, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.6, row=2, col=1)
            
            # Add the shaded area between 30 and 70 for RSI
            fig.add_hrect(y0=30, y1=70, fillcolor="#9467bd", opacity=0.08, layer="below", line_width=0, row=2, col=1)
            
            # Configure Layout Settings, Styling, and Consolidated Mouse Hover Tracking Mechanics
            fig.update_layout(
                title=f"<b>{ticker_symbol} Advanced Technical Dashboard</b>",
                xaxis2_title="Date",
                yaxis_title="Stock Price (USD)",
                yaxis2_title="RSI Value",
                yaxis2_range=[10, 90],
                height=600,
                hovermode="x unified",  # <-- THIS CRITICAL LINE CONSOLIDATES HOVER TRACKING VALUES ON YOUR MOUSE
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=50, r=30, t=80, b=50)
            )
            
            # Hand the reactive plotly layout engine frame directly to Streamlit instead of st.pyplot
            st.plotly_chart(fig, use_container_width=True)
            
            # Optional raw spreadsheet inspector inside the webpage UI
            if st.checkbox("Show Data Log Table"):
                st.subheader("Raw Data Stream Inspect")
                st.dataframe(stock_data.tail(10))

    except Exception as e:
        st.error(f"Application encountered an issue processing request details: {e}")