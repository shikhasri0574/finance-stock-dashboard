import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

st.title("📈 Stock Price Dashboard")

tickers = ['TCS.NS', 'INFY.NS', 'RELIANCE.NS', 'TSLA', 'AAPL', 'GOOG']
selected = st.multiselect("Select stocks to plot", tickers, default=['TCS.NS', 'AAPL'])

start = st.date_input("Start date", pd.to_datetime("2020-01-01"))
end = st.date_input("End date", pd.to_datetime("2024-12-31"))

if selected:
    data = yf.download(selected, start=start, end=end)['Close']
    st.line_chart(data)
