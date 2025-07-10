import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import ta  # pip install ta
import streamlit_authenticator as stauth
from pathlib import Path
import yaml
from yaml.loader import SafeLoader

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Stock Dashboard", layout="wide")

# ---- USER AUTH ----
names = ["Shikha Srivastava", "Guest User"]
usernames = ["shikha", "guest"]
passwords = ["123", "guest123"]
hashed_pw = stauth.Hasher(passwords).generate()

credentials = {
    "usernames": {
        usernames[i]: {
            "name": names[i],
            "password": hashed_pw[i]
        } for i in range(len(usernames))
    }
}

authenticator = stauth.Authenticate(credentials, "finance_dashboard", "abcdef", cookie_expiry_days=1)
name, auth_status, username = authenticator.login("Login", "main")

if auth_status is False:
    st.error("❌ Invalid username or password.")
elif auth_status is None:
    st.warning("⚠️ Please enter your credentials.")
elif auth_status:

    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"👋 Welcome {name}!")

    st.title("📈 Multi-Stock Price Dashboard")

# --- Sidebar Selection ---
tickers = ['TCS.NS', 'INFY.NS', 'RELIANCE.NS', 'TSLA', 'AAPL', 'GOOG']
selected = st.multiselect("Select stocks to compare", tickers, default=['TCS.NS', 'AAPL'])

    start = st.date_input("Start date", pd.to_datetime("2020-01-01"))
    end = st.date_input("End date", pd.to_datetime("2024-12-31"))

    # ---- COMPANY INFO ----
    company_info = {
        'TCS.NS': {'name': 'Tata Consultancy Services', 'sector': 'IT', 'logo': 'https://companiesmarketcap.com/img/company-logos/128/TCS.NS.png'},
        'INFY.NS': {'name': 'Infosys', 'sector': 'IT', 'logo': 'https://companiesmarketcap.com/img/company-logos/128/INFY.NS.png'},
        'RELIANCE.NS': {'name': 'Reliance Industries', 'sector': 'Energy & Telecom', 'logo': 'https://companiesmarketcap.com/img/company-logos/128/RELIANCE.NS.png'},
        'TSLA': {'name': 'Tesla, Inc.', 'sector': 'Auto & Energy', 'logo': 'https://companiesmarketcap.com/img/company-logos/128/TSLA.png'},
        'AAPL': {'name': 'Apple Inc.', 'sector': 'Consumer Tech', 'logo': 'https://companiesmarketcap.com/img/company-logos/128/AAPL.png'},
        'GOOG': {'name': 'Alphabet Inc.', 'sector': 'Search & Ads', 'logo': 'https://companiesmarketcap.com/img/company-logos/128/GOOG.png'},
        'MSFT': {'name': 'Microsoft Corp.', 'sector': 'Technology', 'logo': 'https://companiesmarketcap.com/img/company-logos/128/MSFT.png'},
        'AMZN': {'name': 'Amazon.com, Inc.', 'sector': 'E-commerce & Cloud', 'logo': 'https://companiesmarketcap.com/img/company-logos/128/AMZN.png'},
        'META': {'name': 'Meta Platforms, Inc.', 'sector': 'Social Media', 'logo': 'https://companiesmarketcap.com/img/company-logos/128/META.png'}
    }

    # ---- SIDEBAR COMPANY INFO ----
    for stock in selected:
        info = company_info.get(stock)
        if info:
            st.sidebar.image(info['logo'], width=50)
            st.sidebar.write(f"**{info['name']}**")
            st.sidebar.caption(f"Sector: {info['sector']}")
            st.sidebar.markdown("---")

    # ---- DATA FETCH ----
    if selected:
        try:
            raw_data = yf.download(selected, start=start, end=end, auto_adjust=True)
            if 'Close' in raw_data.columns:
                data = raw_data['Close'].dropna()
            else:
                st.error("No 'Close' prices found.")
                st.stop()
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
            st.stop()

        # ---- TABS ----
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Price Chart", "📈 Normalized Returns", "📥 Download CSV", "📉 Technical Indicators"
        ])

        # --- PRICE CHART ---
        with tab1:
            st.subheader("Stock Prices Over Time")
            st.line_chart(data)

        # --- NORMALIZED RETURN ---
        with tab2:
            st.subheader("Normalized Returns (Start = 100)")
            norm_data = (data / data.iloc[0]) * 100
            fig, ax = plt.subplots()
            norm_data.plot(ax=ax, figsize=(10, 5))
            ax.set_ylabel("Normalized Price")
            ax.set_title("Stock Performance Comparison")
            st.pyplot(fig)

        # --- DOWNLOAD CSV + COMPANY TABLE ---
        with tab3:
            st.subheader("Download Data")
            csv = data.to_csv().encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="selected_stocks_data.csv", mime="text/csv")

            company_table = []
            for stock in selected:
                info = company_info.get(stock)
                if info:
                    company_table.append({'Ticker': stock, 'Name': info['name'], 'Sector': info['sector']})
            if company_table:
                st.subheader("Company Sector Info")
                st.table(pd.DataFrame(company_table))

        # --- TECHNICAL INDICATORS ---
        with tab4:
            st.subheader("📉 Technical Indicators (SMA + RSI)")
            if len(selected) == 1:
                stock = selected[0]
                df = yf.download(stock, start=start, end=end, auto_adjust=True).dropna()
                df['SMA_30'] = df['Close'].rolling(window=30).mean()
                df['SMA_100'] = df['Close'].rolling(window=100).mean()
                df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()

                fig1, ax1 = plt.subplots()
                df[['Close', 'SMA_30', 'SMA_100']].plot(ax=ax1)
                ax1.set_title(f"SMA 30 & 100 for {stock}")
                st.pyplot(fig1)

                fig2, ax2 = plt.subplots()
                df['RSI'].plot(ax=ax2, color='purple')
                ax2.axhline(70, color='red', linestyle='--')
                ax2.axhline(30, color='green', linestyle='--')
                ax2.set_title("RSI Indicator")
                st.pyplot(fig2)
            else:
                st.info("Select only one stock to view SMA & RSI.")

        # --- RAW DATA PREVIEW ---
        st.write("📊 Raw Data Preview")
        st.dataframe(data.tail())

    else:
        st.warning("Please select at least one stock.")
