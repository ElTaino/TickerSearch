# Using the library Streamlist to turn this into a web dashboard interface. Helps turn it into an interactive web app with not much extra code. Doesn't need HTML, CSS, or Javascript and another benefit is that it works natively with matplotlib and yfinance. USA vs Australia tomorrow we're gonna win 4-1 you heard it here first.

#1. Follow steps in TickerSearch.py to get the appropriate libraries for yfinance and matplotlib. I'm not sure if the below command will get all of the libraries. But regardless, you still need to make sure we're in the correct location to reference the libraries (wherever the stuff is downloaded to)
#2. In CMD run the command "pip install streamlit yfinance matplotlib pandas"

#TO RUN THIS PROGRAM IT IS NOT THE NORMAL TERMINAL COMMAND FOR THIS CLASS.
#... IT MUST BE "streamlit run app_web_StockData.py".
#... ... The terminal will start a local server instance and automatically open a new tab in the default browser (usually at http://localhost:8501). It will display an active responsive webpage where you can change the tickers in the sidebar, move the RSI sliders, check live metrics, and watch the charts instantly re-render in response. 

import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

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
            # Mathematical RSI Calculations
            # Separate gains and losses
            # INFO - This lower=0/upper=0 separates down days from up days. If a stock went down, its gain value for that day drops to 0 and vice versa.
            delta = stock_data['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            
            # Using simple rolling window for Streamlit
            avg_gain = gain.rolling(window=rsi_window).mean()
            avg_loss = loss.rolling(window=rsi_window).mean()
            
            rs = avg_gain / avg_loss
            stock_data['RSI'] = 100 - (100 / (1 + rs))

            # Calculate the moving averages using PANDAS rolling math (.rolling(window=X) looks at the last X days of data)
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

            # Create a 2 panel visual layout (Grid Setup)
            # sharex=True locks the timelines of both graphs together
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
            
            # --- TOP PANEL: Main Price Chart with Moving Averages ---
            # Plot the stock price and the moving averages
            # INFO - This maps the 3 types of data onto an X and Y grid. AUtomatically links the timeline dates to the X axis and the stock prices to the Y axis.
            ax1.plot(stock_data.index, stock_data['Close'], label = 'Actual Close Price', color='#1f77b4', alpha=0.6, linewidth=1.5)
            ax1.plot(stock_data.index, stock_data['MA20'], label = '20-Day Moving Average', color='#ff7f0e', linewidth=2)
            ax1.plot(stock_data.index, stock_data['MA50'], label = '50-Day Moving Average', color='#2ca02c', linewidth=2)

            ax1.set_title(f"{ticker_symbol} Advanced Technical Dashboard", fontsize=14, fontweight='bold')
            ax1.set_ylabel("Stock Price (USD)", fontsize=11)
            ax1.grid(True, linestyle='--', alpha=0.4)
            ax1.legend(loc='upper left')
            
            # --- BOTTOM PANEL: RSI Momentum Indicator ---
            ax2.plot(stock_data.index, stock_data['RSI'], color='#9467bd', linewidth=1.5, label=f"{rsi_window}-Day RSI")

            # Add horizontal baseline markers at 30 (Oversold) and 70 (Overbought)
            ax2.axhline(70, color='red', linestyle='--', alpha=0.5)
            ax2.axhline(30, color='green', linestyle='--', alpha=0.5)

            # Shaded area between 30 and 70 represents the normal trading momentum zone
            # INFO - Creates a subtle light purple backdrop. If the RSI line breaks out of the shaded purple area is can indicate a strong buying or selling frenzy.
            ax2.fill_between(stock_data.index, 30, 70, color='#9467bd', alpha=0.08)
            ax2.set_ylabel("RSI Value", fontsize=10)

            # Keeps the RSI bounded cleanly on screen
            ax2.set_ylim(10, 90)
            ax2.grid(True, linestyle='--', alpha=0.3)
            ax2.legend(loc="upper left")
            
            # Rotate dates on the horizontal axis so they don't overlap
            plt.xticks(rotation=30)
            
            # Clean up the layout
            plt.tight_layout()
            
            # Hand the matplotlib figure off to Streamlit to display inside the browser
            st.pyplot(fig)

            plt.show()
            
            # Optional raw spreadsheet inspector inside the webpage UI
            if st.checkbox("Show Data Log Table"):
                st.subheader("Raw Data Stream Inspect")
                st.dataframe(stock_data.tail(10))

    except Exception as e:
        st.error(f"Application encountered an issue processing request details: {e}")