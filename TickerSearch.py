#----- FIRST COMMIT ----
#1. In CMD run the command "pip install yfinance pandas"

#2. If this code does not find yfinance and you are in Visual Studios Code then click Ctrl + Shift + P and search for "Python: Select Interpretor". Then, select the location where it everything was downloaded to in the pip command. I.E.; c:\users\danie\appdata\local\programs\python\python310\

#3. Run the python program in the terminal. You might need to run the command "python TickerSearch.py". This will then prompt a ticker symbol (GOOG for example) and then will fetch the information via API with Yahoo Finance. 

#------ SECOND COMMIT ------
#1. In CMD run the command pip install matplotlib

#----- THIRD COMMIT -----
# Grabbing 6 months of historical data and calculating a 20 and 50 day moving average. Overlaying them directly onto the visualization
import yfinance as yf
import matplotlib.pyplot as plt

def plot_stock_with_moving_average():
    # 1. Ask the user for a stock symbol
    ticker_symbol = input("Enter a stock ticker symbol (e.g., AAPL, TSLA, GOOG, SPCX (Ewww)): ").upper()
    
    try:
        print(f"\nDownloading 6 months of historical data for {ticker_symbol}...")
        # 2. Download 6 months of data to give the moving averages enough background data to calculate
        # INFO - Make a fast API bulk-request to Yahoo Finance for a structured table of numbers matching the timeline you specified
        stock_data = yf.download(ticker_symbol, period="6mo", interval="1d")
        
        if stock_data.empty:
            print("No data found. Check your ticker symbol ya idiot.")
            return
            

        # 3. Calculate the moving averages using PANDAS rolling math (.rolling(window=X) looks at the last X days of data)
        stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
        stock_data['MA100'] = stock_data['Close'].rolling(window=100).mean()
        
        # 4. Initialize the visual layout
        plt.figure(figsize=(12, 6))
        
        # 5. Plot the stock price and the moving averages
        # INFO - This maps the 3 types of data onto an X and Y grid. AUtomatically links the timeline dates to the X axis and the stock prices to the Y axis.
        plt.plot(stock_data.index, stock_data['Close'], label = 'Actual Close Price', color='#1f77b4', alpha=0.6, linewidth=1.5)
        plt.plot(stock_data.index, stock_data['MA20'], label = '20-Day Moving Average', color='#ff7f0e', linewidth=2)
        plt.plot(stock_data.index, stock_data['MA50'], label = '50-Day Moving Average', color='#2ca02c', linewidth=2)
        plt.plot(stock_data.index, stock_data['MA100'], label = '100-Day Moving Average', color="#a02c81", linewidth=2)
        
        # 6 . Add titles, labels, a legend, and visual grid
        plt.title(f"{ticker_symbol} Stock Price Trend w/ Moving Averages- Past 6 Month", fontsize=14, fontweight='bold')
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Price (USD)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)
        
        # The legend explains what each colored line represents
        plt.legend(loc='upper left', fontsize=10)

        # Rotate dates on the horizontal axis so they don't overlap
        plt.xticks(rotation=45)
        # Clean up the layout
        plt.tight_layout()
        
        # 7. Render the window popup showing the chart
        print("Displaying the chart window. Close the window to exit.")
        # INFO - THis command launches a desktop window displaying the interactive vizualization tool. Can zoom in, pan, and save the image directly from the window.
        plt.show()
        
    except Exception as e:
        print(f"An error occurred while plotting: {e}")

if __name__ == "__main__":
    plot_stock_with_moving_average()
