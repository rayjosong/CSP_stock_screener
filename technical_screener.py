import yfinance as yf
import pandas as pd

def check_bounce(ticker):
    """
    Checks if a stock is bouncing off a key moving average.
    """
    # Set auto_adjust=False for a consistent data structure from yfinance
    data = yf.download(ticker, period="1y", progress=False, auto_adjust=False)
    if data.empty:
        return None

    # Calculate moving averages
    data['5-EMA'] = data['Close'].ewm(span=5, adjust=False).mean()
    data['10-EMA'] = data['Close'].ewm(span=10, adjust=False).mean()
    data['50-SMA'] = data['Close'].rolling(window=50).mean()
    data['100-SMA'] = data['Close'].rolling(window=100).mean()
    data['150-SMA'] = data['Close'].rolling(window=150).mean()
    data['200-SMA'] = data['Close'].rolling(window=200).mean()

    data.dropna(inplace=True)
    if data.empty:
        return None

    last_row = data.iloc[-1]
    bounce_ma = None

    # Use a try-except block to handle potential Series vs. scalar issues
    try:
        last_close = last_row['Close']
        last_low = last_row['Low']

        # Check for bounce
        for ma in ['5-EMA', '10-EMA', '50-SMA', '100-SMA', '150-SMA', '200-SMA']:
            ma_value = last_row[ma]
            # Use .item() to extract scalar values and ensure correct comparison
            if last_low.item() <= ma_value.item() * 1.02 and last_close.item() > ma_value.item():
                bounce_ma = ma
                break
    except AttributeError:
        # Fallback for cases where the values are already scalars
        last_close = last_row['Close']
        last_low = last_row['Low']
        for ma in ['5-EMA', '10-EMA', '50-SMA', '100-SMA', '150-SMA', '200-SMA']:
            ma_value = last_row[ma]
            if last_low <= ma_value * 1.02 and last_close > ma_value:
                bounce_ma = ma
                break

    if bounce_ma:
        return (ticker, bounce_ma, last_close)
    return None

if __name__ == "__main__":
    try:
        with open("stocks.txt", "r") as f:
            stocks_to_watch = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("Error: stocks.txt not found. Please create it in the same directory.")
        exit()

    bouncing_stocks = []
    for stock in stocks_to_watch:
        if stock:
            result = check_bounce(stock)
            if result:
                bouncing_stocks.append(result)

    if bouncing_stocks:
        print("--- Stocks Bouncing Off Key Moving Averages ---")
        for stock, ma, price in bouncing_stocks:
            # Use .item() to extract the scalar value for printing
            print(f"{stock}: Bounced off {ma} at ${price.item():.2f}")
        print("-------------------------------------------------")
    else:
        print("No stocks found bouncing off key moving averages today.")
