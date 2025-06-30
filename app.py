import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def check_bounce(ticker, selected_mas):
    """
    Checks if a stock is bouncing off a key moving average and returns data for plotting.
    """
    # Fetch stock data using yfinance (still good for historical prices)
    data = yf.download(ticker, period="1y", progress=False, auto_adjust=False)
    if data.empty:
        return None, None

    bounce_ma = None # Initialize here to ensure it's always defined

    # Calculate moving averages
    for ma in selected_mas:
        if 'EMA' in ma:
            span = int(ma.split('-')[0])
            data[(ma, '')] = data[('Close', ticker)].ewm(span=span, adjust=False).mean()
        elif 'SMA' in ma:
            window = int(ma.split('-')[0])
            data[(ma, '')] = data[('Close', ticker)].rolling(window=window).mean()

    processed_data = data.copy()
    processed_data.dropna(inplace=True)
    if processed_data.empty:
        return None, None

    last_row_processed = processed_data.iloc[-1]
    last_close = last_row_processed[('Close', ticker)]
    last_low = last_row_processed[('Low', ticker)]

    last_two_days = processed_data.iloc[-2:]

    # Check for bounce in the last two trading days
    for ma in selected_mas:
        for index, row in last_two_days.iterrows():
            current_low = row[('Low', ticker)]
            current_close = row[('Close', ticker)]
            ma_value = row[(ma, '')]

            # Check if the low dipped below the MA and the close came up from it
            if current_low.item() < ma_value.item() and current_close.item() > ma_value.item():
                bounce_ma = ma
                break # Found a bounce, no need to check other MAs for this stock
        if bounce_ma: # If bounce found for any MA, break outer loop
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

def plot_chart(ticker, data, bounce_ma, selected_mas):
    """
    Plots the stock chart with moving averages.
    """
    # Drop NaN values from OHLC for candlestick plotting
    plot_data = data.dropna(subset=[('Open', ticker), ('High', ticker), ('Low', ticker), ('Close', ticker)])
    if plot_data.empty:
        st.warning(f"Not enough data to plot candlestick for {ticker}")
        return go.Figure()

    fig = go.Figure(data=[go.Candlestick(x=plot_data.index, open=plot_data[('Open', ticker)], high=plot_data[('High', ticker)], low=plot_data[('Low', ticker)], close=plot_data[('Close', ticker)], name='Candlestick')])

    for ma in selected_mas:
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

# Multiselect for configurable moving averages
default_mas = ['5-EMA', '10-EMA', '50-SMA', '100-SMA', '150-SMA', '200-SMA']
selected_mas = st.multiselect(
    "Select Moving Averages to Analyze",
    options=default_mas,
    default=default_mas
)

# Text area for user to input stocks
stocks_input = st.text_area("Stock Tickers", """AAPL
GOOGL
MSFT
AMZN
IBIT
NKE
NVDA
CELH""", height=150)
stocks_to_watch = [ticker.strip().upper() for ticker in stocks_input.split('\n') if ticker.strip()]

if st.button("Run Screener"):
    if not stocks_to_watch:
        st.warning("Please enter at least one stock ticker.")
    elif not selected_mas:
        st.warning("Please select at least one moving average.")
    else:
        bouncing_stocks = []
        charts_to_display = []

        progress_bar = st.progress(0)
        for i, stock in enumerate(stocks_to_watch):
            result, chart_data = check_bounce(stock, selected_mas)
            if result:
                bouncing_stocks.append(result)
                charts_to_display.append((stock, chart_data, result[1], selected_mas))
            progress_bar.progress((i + 1) / len(stocks_to_watch))

        if bouncing_stocks:
            st.subheader("Stocks Bouncing Off Key Moving Averages")
            df = pd.DataFrame(bouncing_stocks, columns=["Ticker", "Bounced Off", "Last Close", "Implied Volatility"])
            st.dataframe(df)

            st.header("Price Charts")
            for ticker, chart_data, bounce_ma, mas_for_plot in charts_to_display:
                st.plotly_chart(plot_chart(ticker, chart_data, bounce_ma, mas_for_plot))
        else:
            st.info("No stocks found bouncing off key moving averages today.")