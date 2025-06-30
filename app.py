import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def check_bounce(ticker):
    """
    Checks if a stock is bouncing off a key moving average and returns data for plotting.
    """
    # Fetch stock data using yfinance (still good for historical prices)
    data = yf.download(ticker, period="1y", progress=False, auto_adjust=False)
    if data.empty:
        return None, None

    # Calculate moving averages
    data[('5-EMA', '')] = data[('Close', ticker)].ewm(span=5, adjust=False).mean()
    data[('10-EMA', '')] = data[('Close', ticker)].ewm(span=10, adjust=False).mean()
    data[('50-SMA', '')] = data[('Close', ticker)].rolling(window=50).mean()
    data[('100-SMA', '')] = data[('Close', ticker)].rolling(window=100).mean()
    data[('150-SMA', '')] = data[('Close', ticker)].rolling(window=150).mean()
    data[('200-SMA', '')] = data[('Close', ticker)].rolling(window=200).mean()

    processed_data = data.copy()
    processed_data.dropna(inplace=True)
    if processed_data.empty:
        return None, None

    last_row = processed_data.iloc[-1]
    # Use a try-except block to handle potential Series vs. scalar issues
    try:
        last_close = last_row[('Close', ticker)]
        last_low = last_row[('Low', ticker)]

        # Check for bounce
        for ma in ['5-EMA', '10-EMA', '50-SMA', '100-SMA', '150-SMA', '200-SMA']:
            ma_value = last_row[(ma, '')]
            # Use .item() to extract scalar values and ensure correct comparison
            if last_low.item() <= ma_value.item() * 1.02 and last_close.item() > ma_value.item():
                bounce_ma = ma
                break
    except AttributeError:
        # Fallback for cases where the values are already scalars
        last_close = last_row[('Close', ticker)]
        last_low = last_row[('Low', ticker)]
        for ma in ['5-EMA', '10-EMA', '50-SMA', '100-SMA', '150-SMA', '200-SMA']:
            ma_value = last_row[(ma, '')]
            if last_low <= ma_value * 1.02 and last_close > ma_value:
                bounce_ma = ma
                break

    if bounce_ma:
        implied_volatility = "N/A"
        try:
            ticker_obj = yf.Ticker(ticker)
            options = ticker_obj.option_chain()
            if options.calls is not None and not options.calls.empty:
                # Find ATM call option (closest strike to current price)
                atm_call = options.calls.iloc[(options.calls['strike'] - last_close.item()).abs().argsort()[:1]]
                if not atm_call.empty and 'impliedVolatility' in atm_call.columns:
                    raw_iv = atm_call['impliedVolatility'].iloc[0]
                    if pd.notna(raw_iv) and raw_iv > 0:
                        implied_volatility = f"{raw_iv * 100:.2f}%"
        except Exception as e:
            st.warning(f"Could not fetch implied volatility for {ticker}: {e}")

        return (ticker, bounce_ma, last_close, implied_volatility), data
    return None, None

def plot_chart(ticker, data, bounce_ma):
    """
    Plots the stock chart with moving averages.
    """
    # Drop NaN values from OHLC for candlestick plotting
    plot_data = data.dropna(subset=[('Open', ticker), ('High', ticker), ('Low', ticker), ('Close', ticker)])
    if plot_data.empty:
        st.warning(f"Not enough data to plot candlestick for {ticker}")
        return go.Figure()

    fig = go.Figure(data=[go.Candlestick(x=plot_data.index, open=plot_data[('Open', ticker)], high=plot_data[('High', ticker)], low=plot_data[('Low', ticker)], close=plot_data[('Close', ticker)], name='Candlestick')])

    for ma in ['5-EMA', '10-EMA', '50-SMA', '100-SMA', '150-SMA', '200-SMA']:
        fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data[(ma, '')], mode='lines', name=ma))

    fig.update_layout(
        title=f'{ticker} - Bounced off {bounce_ma}',
        xaxis_title='Date',
        yaxis_title='Price',
        legend_title='Moving Averages'
    )
    return fig

st.title("Stock Screener for Cash-Secured Puts")

st.write("Enter stock tickers below (one per line) to find stocks bouncing off key moving averages.")

# Text area for user to input stocks
stocks_input = st.text_area("Stock Tickers", "AAPL\nGOOGL\nMSFT\nAMZN", height=150)
stocks_to_watch = [ticker.strip().upper() for ticker in stocks_input.split('\n') if ticker.strip()]

if st.button("Run Screener"):
    if not stocks_to_watch:
        st.warning("Please enter at least one stock ticker.")
    else:
        bouncing_stocks = []
        charts_to_display = []

        progress_bar = st.progress(0)
        for i, stock in enumerate(stocks_to_watch):
            result, chart_data = check_bounce(stock)
            if result:
                bouncing_stocks.append(result)
                charts_to_display.append((stock, chart_data, result[1]))
            progress_bar.progress((i + 1) / len(stocks_to_watch))

        if bouncing_stocks:
            st.subheader("Stocks Bouncing Off Key Moving Averages")
            df = pd.DataFrame(bouncing_stocks, columns=["Ticker", "Bounced Off", "Last Close", "Implied Volatility"])
            st.dataframe(df)

            st.header("Price Charts")
            for ticker, chart_data, bounce_ma in charts_to_display:
                st.plotly_chart(plot_chart(ticker, chart_data, bounce_ma))
        else:
            st.info("No stocks found bouncing off key moving averages today.")