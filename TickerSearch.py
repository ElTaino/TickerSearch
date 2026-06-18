import yfinance as yf

def get_stock_data():
    # 1. Ask the user for a stock symbol
    ticker_symbol = input("Enter a stock ticker symbol (e.g., AAPL, TSLA, GOOG): ").upper()
    
    try:
        # 2. Connect to the yfinance API wrapper for that specific stock
        print(f"\nFetching data for {ticker_symbol} from Yahoo Finance...")
        stock = yf.Ticker(ticker_symbol)
        
        # 3. Pull the most recent 1-day interval history to get the latest price
        historical_data = stock.history(period="1d", interval="1m")
        
        if historical_data.empty:
            print("Error: Could not retrieve data. Please check the ticker symbol.")
            return

        # Extract the last available 'Close' price from the dataset
        current_price = historical_data['Close'].iloc[-1]
        
        # 4. Fetch general company metadata using the .info attribute
        company_info = stock.info
        company_name = company_info.get('longName', 'N/A')
        currency = company_info.get('currency', 'USD')
        
        # 5. Output the results cleanly to the user
        print("\n" + "="*40)
        print(f"Company: {company_name} ({ticker_symbol})")
        print(f"Current Price: {current_price:.2f} {currency}")
        print("="*40)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_stock_data()