import streamlit as st
import pandas as pd
import requests

st.title("Crypto Price Tracking")

crypto = st.selectbox("Choose Crypto", ["bitcoin", "ethereum", "dogecoin", "pax-gold"])

currency = st.selectbox("Choose Currency", ["usd", "aed", "eur", "kwd"])

days = st.number_input("Number of Days", min_value=1, max_value=365, value=7)

url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency={currency}&days={days}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    current_price = data["prices"][-1][1]
    st.metric(
        label=f"Current {crypto.upper()} Price",
        value=f"{current_price:,.2f} {currency.upper()}"
    )
    
    prices_df = pd.DataFrame(data["prices"], columns=["Time", "Price"])
    prices_df["Time"] = pd.to_datetime(prices_df["Time"], unit="ms")
    
    st.subheader(f"Price Last {days} days")
    st.line_chart(data=prices_df.set_index("Time")["Price"])
    
    volumes_df = pd.DataFrame(data["total_volumes"], columns=["Time", "Volume"])
    volumes_df["Time"] = pd.to_datetime(volumes_df["Time"], unit="ms")
    
    st.subheader(f"Trading Volume - Last {days} Days")
    st.bar_chart(data=volumes_df.set_index("Time")["Volume"])