#----- FIRST COMMIT ----
#1. In CMD run the command "pip install yfinance pandas"

#2. If this code does not find yfinance and you are in Visual Studios Code then click Ctrl + Shift + P and search for "Python: Select Interpretor". Then, select the location where it everything was downloaded to in the pip command. I.E.; c:\users\danie\appdata\local\programs\python\python310\

#3. Run the python program in the terminal. You might need to run the command "python TickerSearch.py". This will then prompt a ticker symbol (GOOG for example) and then will fetch the information via API with Yahoo Finance. 

#------ SECOND COMMIT ------
#1. In CMD run the command pip install matplotlib
import yfinance as yf
import matplotlib.pyplot as plt

def plot_stock_chart():
    # 1. Ask the user for a stock symbol
    ticker_symbol = input("Enter a stock ticker symbol (e.g., AAPL, TSLA, GOOG): ").upper()
    
    try:
        print(f"\nDownloading 1 month of historical data for {ticker_symbol}...")
        # 2. Download the historical data (1 Month period, Daily intervals)
        # INFO - Make a fast API bulk-request to Yahoo Finance for a structured table of numbers matching the timeline you specified
        stock_data = yf.download(ticker_symbol, period="1mo", interval="1d")
        
        if stock_data.empty:
            print("No data found. Check your ticker symbol.")
            return
            
        # 3. Initialize the visual layout
        plt.figure(figsize=(10, 5))
        
        # 4. Plot the 'Close' prices against the Dates
        # INFO - This maps the rows of data onto an X and Y grid. AUtomatically links the timeline dates to the X axis and the stock prices to the Y axis.
        plt.plot(stock_data.index, stock_data['Close'], marker='o', color='#1f77b4', linewidth=2)
        
        # 5. Add titles, labels, and visual grid
        plt.title(f"{ticker_symbol} Stock Price Trend - Past 1 Month", fontsize=14, fontweight='bold')
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Closing Price (USD)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)
        
        # Rotate dates on the horizontal axis so they don't overlap
        plt.xticks(rotation=45)
        
        # Adjust layout to fit labels perfectly
        plt.tight_layout()
        
        # 6. Render the window popup showing the chart
        print("Displaying the chart window. Close the window to exit.")
        # INFO - THis command launches a desktop window displaying the interactive vizualization tool. Can zoom in, pan, and save the image directly from the window.
        plt.show()
        
    except Exception as e:
        print(f"An error occurred while plotting: {e}")

if __name__ == "__main__":
    plot_stock_chart()
