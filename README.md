# Stock Screener for Cash-Secured Puts

This project was built with the Gemini CLI.

This Python script performs technical analysis on a predefined list of stocks to identify potential opportunities for selling Cash-Secured Puts (CSPs). It screens for stocks that are bouncing off key moving average support levels.

## The Strategy: Combining Fundamentals with Technical Entry Points

The core idea behind this tool is to enhance the probability of success with CSPs by layering technical analysis on top of fundamental analysis.

1.  **Start with Strength:** The process begins with a curated list of fundamentally strong companies you wouldn't mind owning long-term. This is the most critical step.
2.  **Identify Key Support:** The script identifies when a stock's price is showing signs of a bounce off a significant technical support level (key Exponential or Simple Moving Averages). These levels are widely watched by institutional investors and often act as a price floor.
3.  **High-Probability CSPs:** When a stock respects a support level, it signals that buyers are stepping in. By selling a CSP with a strike price at or just below this support level, you are strategically positioning your trade where the stock has already demonstrated strength. This can increase the likelihood that the put will expire worthless, allowing you to keep the full premium.

_Disclaimer: This tool is for educational purposes only and does not constitute financial advice. Always conduct your own due diligence before making any investment decisions._

## How to Use

### Prerequisites

- Python 3.8+
- `uv` (for Python virtual environment and package management)

### Setup & Installation

1.  **Clone the repository (or download the files):**

    ```bash
    git clone <repository-url>
    cd stock_screener
    ```

2.  **Create the virtual environment and install packages:**
    The `uv` tool will create a local virtual environment in a `.venv` directory and install the required packages from `requirements.txt`.
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```

### Running the Streamlit App

1.  **Execute the app:**
    Make sure your virtual environment is activated.
    ```bash
    streamlit run app.py
    ```

    This will open the Streamlit application in your web browser.

### Features

-   **Stock Screening:** Identify stocks bouncing off key moving averages.
-   **Interactive Charts:** Visualize stock price action with moving averages.
-   **Implied Volatility:** Display implied volatility for screened stocks (fetched from yfinance options data).

### Sample Output

The Streamlit app will display a table of screened stocks and interactive charts.

## Future Improvements

This tool provides a solid foundation, but it can be enhanced with several new features:

- **Adjustable Parameters:** Allow the "bounce sensitivity" (currently hardcoded at 2%) to be configured as a command-line argument or in the config file.
- **Additional Indicators:** Incorporate other technical indicators, such as the Relative Strength Index (RSI), to avoid "catching a falling knife" and ensure the stock isn't oversold for a good reason.
- **Automated Alerts:** Integrate with an email service (e.g., SendGrid) or a messaging app (e.g., Telegram) to send daily alerts with the results.
- **Web Interface:** Build a simple web dashboard using a framework like **Streamlit** or **Flask** to provide a more interactive user experience.
- **Automated Scheduling:** Use a `cron` job (on Linux/macOS) or Task Scheduler (on Windows) to run the script automatically after market close each day.
