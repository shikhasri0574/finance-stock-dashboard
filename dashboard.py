import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📈 Multi-Stock Price Dashboard")

# --- Sidebar Selection ---
tickers = ['TCS.NS', 'INFY.NS', 'RELIANCE.NS', 'TSLA', 'AAPL', 'GOOG']
selected = st.multiselect("Select stocks to compare", tickers, default=['TCS.NS', 'AAPL'])

start = st.date_input("Start date", pd.to_datetime("2020-01-01"))
end = st.date_input("End date", pd.to_datetime("2024-12-31"))

# --- Fetch Data ---
if selected:
    # Download and check Close prices
    try:
      raw_data = yf.download(selected, start=start, end=end)
      if 'Close' in raw_data.columns:
        data = raw_data['Close'].dropna()
      else:
        st.error("No 'Close' prices found for selected stocks.")
        st.stop()
    except Exception as e:
     st.error(f"Failed to fetch data: {e}")
     st.stop()


    tab1, tab2, tab3 = st.tabs(["📊 Price Chart", "📈 Normalized Returns", "📥 Download CSV"])

    with tab1:
        st.subheader("Stock Prices Over Time")
        st.line_chart(data)

    with tab2:
        st.subheader("Normalized Returns (Start = 100)")
        norm_data = (data / data.iloc[0]) * 100
        fig, ax = plt.subplots()
        norm_data.plot(ax=ax, figsize=(10, 5))
        ax.set_ylabel("Normalized Price")
        ax.set_title("Stock Performance Comparison")
        st.pyplot(fig)

    with tab3:
        st.subheader("Download Data")
        csv = data.to_csv().encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="selected_stocks_data.csv",
            mime="text/csv"
        )
else:
    st.warning("Please select at least one stock.")
import ta  # <-- install this if not already: pip install ta

# inside your 'if selected:' block and after fetching `data`:
tab1, tab2, tab3, tab4 = st.tabs(["📊 Price Chart", "📈 Normalized Returns", "📥 Download CSV", "📉 Technical Indicators"])

# Technical Indicators Tab
with tab4:
    st.subheader("📉 Technical Indicators (SMA + RSI)")

    if len(selected) == 1:
        stock = selected[0]
        df = yf.download(stock, start=start, end=end).dropna()
        df['SMA_30'] = df['Close'].rolling(window=30).mean()
        df['SMA_100'] = df['Close'].rolling(window=100).mean()

        # RSI
        # Ensure Close is 1D
        close_series = df['Close'].squeeze()

        # Calculate RSI safely
        rsi = ta.momentum.RSIIndicator(close_series).rsi()
        df['RSI'] = rsi


        # Plot SMA
        st.write(f"**SMA 30 & 100 for {stock}**")
        fig1, ax1 = plt.subplots()
        df[['Close', 'SMA_30', 'SMA_100']].plot(ax=ax1)
        ax1.set_title("SMA vs Close Price")
        st.pyplot(fig1)

        # Plot RSI
        st.write(f"**RSI (Relative Strength Index) for {stock}**")
        fig2, ax2 = plt.subplots()
        df['RSI'].plot(ax=ax2, color='purple')
        ax2.axhline(70, color='red', linestyle='--')
        ax2.axhline(30, color='green', linestyle='--')
        ax2.set_title("RSI Indicator")
        st.pyplot(fig2)
    else:
        st.info("Select only one stock to view SMA & RSI.")

        # Company sector and logo info
company_info = {
    'TCS.NS': {
        'name': 'Tata Consultancy Services',
        'sector': 'Information Technology',
        'logo': 'https://companiesmarketcap.com/img/company-logos/128/TCS.NS.png'
    },
    'INFY.NS': {
        'name': 'Infosys',
        'sector': 'Information Technology',
        'logo': 'https://companiesmarketcap.com/img/company-logos/128/INFY.NS.png'
    },
    'RELIANCE.NS': {
        'name': 'Reliance Industries',
        'sector': 'Energy & Telecom',
        'logo': 'https://companiesmarketcap.com/img/company-logos/128/RELIANCE.NS.png'
    },
    'TSLA': {
        'name': 'Tesla, Inc.',
        'sector': 'Automotive & Energy',
        'logo': 'https://companiesmarketcap.com/img/company-logos/128/TSLA.png'
    },
    'AAPL': {
        'name': 'Apple Inc.',
        'sector': 'Technology (Consumer)',
        'logo': 'https://companiesmarketcap.com/img/company-logos/128/AAPL.png'
    },
    'GOOG': {
        'name': 'Alphabet Inc. (Google)',
        'sector': 'Technology (Search & Ads)',
        'logo': 'https://companiesmarketcap.com/img/company-logos/128/GOOG.png'
    }
}
# --- Display Company Info ---
for stock in selected:
    info = company_info.get(stock)
    if info:
        st.sidebar.image(info['logo'], width=50)
        st.sidebar.write(f"**{info['name']}**")
        st.sidebar.caption(f"Sector: {info['sector']}")
        st.sidebar.markdown("---")
# indicators like SMA and RSI for a selected stock.
# It includes a sidebar for stock selection, date range input, and tabs for different visualizations
# --- Inside tab3 (Download CSV tab) ---
company_table = []
for stock in selected:
    info = company_info.get(stock)
    if info:
        company_table.append({
            'Ticker': stock,
            'Name': info['name'],
            'Sector': info['sector']
        })

if company_table:
    st.subheader("Company Sector Info")
    st.table(pd.DataFrame(company_table))   

st.write("📊 Raw Data Preview:")
st.dataframe(data.tail())  # show last 5 rows of downloaded data

# --- End of dashboard.py
# This code creates a Streamlit dashboard for visualizing stock prices, normalized returns, and technical