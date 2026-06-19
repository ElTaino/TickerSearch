#----- FIRST COMMIT ----
#1. In CMD run the command "pip install yfinance pandas"

#2. If this code does not find yfinance and you are in Visual Studios Code then click Ctrl + Shift + P and search for "Python: Select Interpretor". Then, select the location where it everything was downloaded to in the pip command. I.E.; c:\users\danie\appdata\local\programs\python\python310\

#3. Run the python program in the terminal. You might need to run the command "python TickerSearch.py". This will then prompt a ticker symbol (GOOG for example) and then will fetch the information via API with Yahoo Finance. 

#------ SECOND COMMIT ------
#1. In CMD run the command pip install matplotlib

#----- THIRD COMMIT -----
# Grabbing 6 months of historical data and calculating a 20 and 50 day moving average. Overlaying them directly onto the visualization

#----- FOURTH COMMIT -----
# Calculating the relative strength index (RSI). Its a momentum oscillator that measures the speed and change of price movements on a scale of 0-100. Can be used by traders to spot market extremes. For example, above 70 can signal the stock is overbought and potentially due for a price drop. Below 30 can signal the stock is oversold and potentially due for a price rebound.
import yfinance as yf
import matplotlib.pyplot as plt

def plot_stock_with_moving_average_and_RSI():
    # Ask the user for a stock symbol
    ticker_symbol = input("Enter a stock ticker symbol (e.g., AAPL, TSLA, GOOG, SPCX (Ewww)): ").upper()
    
    try:
        print(f"\nDownloading 6 months of historical data for {ticker_symbol}...")
        # Download 6 months of data to give the moving averages and RSI enough background data to calculate
        # INFO - Make a fast API bulk-request to Yahoo Finance for a structured table of numbers matching the timeline you specified
        stock_data = yf.download(ticker_symbol, period="6mo", interval="1d")
        
        if stock_data.empty:
            print("No data found. Check your ticker symbol ya idiot.")
            return
            
        # Computer RSI (Standard 14-day window)
        # Calculate daily price changes
        delta = stock_data['Close'].diff()

        # Separate gains and losses
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        # Calculate exponential moving averages for gains and losses
        avg_gain = gain.ewm(com=13, adjust=False).mean()
        avg_loss = loss.ewm(com=13, adjust=False).mean()

        # Calculate Relative Strength (RS) and RSI
        rs = avg_gain / avg_loss
        stock_data['RSI'] = 100 - (100 / (1 + rs))

        # Calculate the moving averages using PANDAS rolling math (.rolling(window=X) looks at the last X days of data)
        stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
        #stock_data['MA100'] = stock_data['Close'].rolling(window=100).mean()
        
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
        ax2.plot(stock_data.index, stock_data['RSI'], label='14-Day RSI', color='#9467bd', linewidth=1.5)
        
        # Add horizontal baseline markers at 30 (Oversold) and 70 (Overbought)
        ax2.axhline(70, color='red', linestyle='--', alpha=0.6, label='Overbought (70)')
        ax2.axhline(30, color='green', linestyle='--', alpha=0.6, label='Oversold (30)')
        
        # Shaded area between 30 and 70 represents the normal trading momentum zone
        ax2.fill_between(stock_data.index, 30, 70, color='#9467bd', alpha=0.1)
        
        ax2.set_ylabel("RSI Value", fontsize=11)
        ax2.set_xlabel("Date", fontsize=11)
        ax2.set_ylim(10, 90) # Keeps the RSI bounded cleanly on screen
        ax2.grid(True, linestyle='--', alpha=0.4)
        ax2.legend(loc='upper left')

        # Rotate dates on the horizontal axis so they don't overlap
        plt.xticks(rotation=45)
        # Clean up the layout
        plt.tight_layout()
        
        # Render the window popup showing the chart
        print("Displaying the chart window. Close the window to exit.")
        # INFO - THis command launches a desktop window displaying the interactive vizualization tool. Can zoom in, pan, and save the image directly from the window.
        plt.show()
        
    except Exception as e:
        print(f"An error occurred while plotting: {e}")

if __name__ == "__main__":
    plot_stock_with_moving_average_and_RSI()
