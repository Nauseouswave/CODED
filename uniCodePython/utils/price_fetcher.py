"""
Price fetching utilities for stocks and cryptocurrencies
"""

import streamlit as st
import requests
import yfinance as yf
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_price(symbol):
    """Get current stock price with multiple fallback methods"""
    
    # Method 1: yfinance library (most reliable)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if 'currentPrice' in info:
            return float(info['currentPrice'])
        elif 'regularMarketPrice' in info:
            return float(info['regularMarketPrice'])
        elif 'previousClose' in info:
            return float(info['previousClose'])
    except Exception as e:
        print(f"yfinance failed: {e}")
    
    # Method 2: Yahoo Finance v7 API
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'quoteResponse' in data and data['quoteResponse']['result']:
            result = data['quoteResponse']['result'][0]
            if 'regularMarketPrice' in result:
                return float(result['regularMarketPrice'])
    except Exception as e:
        print(f"Yahoo v7 API failed: {e}")
    
    # Method 3: Yahoo Finance v8 API
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            price = data['chart']['result'][0]['meta']['regularMarketPrice']
            return float(price)
    except Exception as e:
        print(f"Yahoo v8 API failed: {e}")
    
    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes  
def get_crypto_price(symbol):
    """Get current crypto price from CoinGecko API"""
    try:
        # CoinGecko API (free, no API key needed)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        
        if symbol in data and 'usd' in data[symbol]:
            return float(data[symbol]['usd'])
    except:
        pass
    return None


def get_symbol_from_selection(investment_name, investment_type):
    """Extract the API symbol from the selected investment"""
    if investment_type == "Stocks":
        return POPULAR_STOCKS.get(investment_name)
    elif investment_type == "Cryptocurrency":
        return POPULAR_CRYPTO.get(investment_name)
    return None


def get_current_price(investment_name, investment_type):
    """Get current price based on investment type and name"""
    # First try to get symbol from our predefined lists
    symbol = get_symbol_from_selection(investment_name, investment_type)
    
    if symbol:
        if investment_type == "Cryptocurrency":
            return get_crypto_price(symbol)
        elif investment_type == "Stocks":
            return get_stock_price(symbol)
    
    # Fallback to old logic for custom entries
    if investment_type == "Cryptocurrency":
        name_lower = investment_name.lower().replace(' ', '')
        crypto_fallback = {
            'bitcoin': 'bitcoin', 'btc': 'bitcoin',
            'ethereum': 'ethereum', 'eth': 'ethereum',
            'dogecoin': 'dogecoin', 'doge': 'dogecoin',
            'cardano': 'cardano', 'ada': 'cardano'
        }
        
        for key, value in crypto_fallback.items():
            if key in name_lower:
                return get_crypto_price(value)
                
    elif investment_type == "Stocks":
        # Try the name as symbol directly if it's short
        clean_name = investment_name.upper().replace('STOCK', '').replace('SHARES', '').strip()
        if len(clean_name) <= 5:
            return get_stock_price(clean_name)
    
    return None
