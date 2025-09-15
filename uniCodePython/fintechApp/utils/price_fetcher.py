"""
Price fetching utilities for stocks and cryptocurrencies
Simple and reliable price fetching using CoinGecko and Yahoo Finance APIs
"""

import streamlit as st
import requests
import pandas as pd
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_crypto_price_simple(crypto_id):
    """Get crypto price using CoinGecko simple price API"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if crypto_id in data and 'usd' in data[crypto_id]:
                return float(data[crypto_id]['usd'])
    except Exception as e:
        print(f"CoinGecko simple price failed for {crypto_id}: {e}")
    
    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_price_simple(symbol):
    """Get stock price using Yahoo Finance API - simplified approach"""
    try:
        # Clean the symbol
        clean_symbol = symbol.replace('$', '').strip().upper()
        
        # Use Yahoo Finance query API
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'chart' in data and data['chart']['result']:
                chart_data = data['chart']['result'][0]
                if 'meta' in chart_data and 'regularMarketPrice' in chart_data['meta']:
                    price = chart_data['meta']['regularMarketPrice']
                    if price and price > 0:
                        return float(price)
                
                # Fallback to timestamp data
                if 'timestamp' in chart_data and 'indicators' in chart_data:
                    closes = chart_data['indicators']['quote'][0]['close']
                    if closes and len(closes) > 0:
                        # Get the most recent non-null close price
                        for close_price in reversed(closes):
                            if close_price is not None and close_price > 0:
                                return float(close_price)
        
    except Exception as e:
        print(f"Yahoo Finance API failed for {clean_symbol}: {e}")
    
    return None


def get_crypto_chart_data(crypto_id, days=7):
    """Get crypto price chart data using CoinGecko"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'prices' in data:
                prices_df = pd.DataFrame(data["prices"], columns=["Time", "Price"])
                prices_df["Time"] = pd.to_datetime(prices_df["Time"], unit="ms")
                return prices_df
                
    except Exception as e:
        print(f"CoinGecko chart data failed for {crypto_id}: {e}")
    
    return None


def get_stock_chart_data(symbol, days=7):
    """Get stock price chart data using Yahoo Finance"""
    try:
        clean_symbol = symbol.replace('$', '').strip().upper()
        
        # Calculate period for Yahoo Finance
        if days <= 7:
            period = "7d"
            interval = "1d"
        elif days <= 30:
            period = "1mo"
            interval = "1d"
        elif days <= 90:
            period = "3mo"
            interval = "1d"
        else:
            period = "1y"
            interval = "1wk"
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}?period1=0&period2=9999999999&interval={interval}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'chart' in data and data['chart']['result']:
                chart_data = data['chart']['result'][0]
                
                if 'timestamp' in chart_data and 'indicators' in chart_data:
                    timestamps = chart_data['timestamp']
                    closes = chart_data['indicators']['quote'][0]['close']
                    
                    # Create DataFrame
                    price_data = []
                    for i, timestamp in enumerate(timestamps):
                        if i < len(closes) and closes[i] is not None:
                            price_data.append([timestamp * 1000, closes[i]])  # Convert to milliseconds
                    
                    if price_data:
                        prices_df = pd.DataFrame(price_data, columns=["Time", "Price"])
                        prices_df["Time"] = pd.to_datetime(prices_df["Time"], unit="ms")
                        
                        # Filter to requested days
                        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
                        prices_df = prices_df[prices_df["Time"] >= cutoff_date]
                        
                        return prices_df
                        
    except Exception as e:
        print(f"Yahoo Finance chart data failed for {clean_symbol}: {e}")
    
    return None


def get_symbol_from_selection(investment_name, investment_type):
    """Extract the API symbol from the selected investment"""
    if investment_type == "Stocks":
        return POPULAR_STOCKS.get(investment_name)
    elif investment_type == "Cryptocurrency":
        return POPULAR_CRYPTO.get(investment_name)
    return None


def get_current_price(investment_name, investment_type):
    """Get current price based on investment type and name - simplified version"""
    print(f"DEBUG: Fetching price for '{investment_name}' of type '{investment_type}'")
    
    # First try to get symbol from our predefined lists
    symbol = get_symbol_from_selection(investment_name, investment_type)
    print(f"DEBUG: Mapped symbol: {symbol}")
    
    if symbol:
        if investment_type == "Cryptocurrency":
            price = get_crypto_price_simple(symbol)
            print(f"DEBUG: Crypto price result: {price}")
            return price
        elif investment_type == "Stocks":
            price = get_stock_price_simple(symbol)
            print(f"DEBUG: Stock price result: {price}")
            return price
    
    # Fallback to direct lookup for custom entries
    if investment_type == "Cryptocurrency":
        # Try common crypto name mappings
        crypto_mapping = {
            'bitcoin': 'bitcoin', 'btc': 'bitcoin',
            'ethereum': 'ethereum', 'eth': 'ethereum', 
            'dogecoin': 'dogecoin', 'doge': 'dogecoin',
            'cardano': 'cardano', 'ada': 'cardano',
            'solana': 'solana', 'sol': 'solana',
            'litecoin': 'litecoin', 'ltc': 'litecoin'
        }
        
        name_lower = investment_name.lower().replace(' ', '').replace('-', '')
        for key, value in crypto_mapping.items():
            if key in name_lower:
                price = get_crypto_price_simple(value)
                print(f"DEBUG: Fallback crypto price for {value}: {price}")
                return price
                
    elif investment_type == "Stocks":
        # Try the name as symbol directly if it looks like a stock symbol
        clean_name = investment_name.upper().replace('STOCK', '').replace('SHARES', '').replace('INC.', '').replace('CORP.', '').strip()
        if len(clean_name) <= 5:
            price = get_stock_price_simple(clean_name)
            print(f"DEBUG: Direct symbol lookup for {clean_name}: {price}")
            return price
    
    print(f"DEBUG: No price found for {investment_name}")
    return None

import streamlit as st
import requests
import yfinance as yf
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_price(symbol):
    """Get current stock price with multiple fallback methods"""
    
    # Clean the symbol - remove any $ prefix if present
    clean_symbol = symbol.replace('$', '').strip()
    
    # Method 1: Try yfinance with recent data
    try:
        ticker = yf.Ticker(clean_symbol)
        # Get recent data instead of info which can be unreliable
        hist = ticker.history(period="2d")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            if current_price and current_price > 0:
                return float(current_price)
    except Exception as e:
        print(f"yfinance hist failed for {clean_symbol}: {e}")
    
    # Method 2: Try yfinance info
    try:
        ticker = yf.Ticker(clean_symbol)
        info = ticker.info
        if 'currentPrice' in info and info['currentPrice']:
            return float(info['currentPrice'])
        elif 'regularMarketPrice' in info and info['regularMarketPrice']:
            return float(info['regularMarketPrice'])
        elif 'previousClose' in info and info['previousClose']:
            return float(info['previousClose'])
    except Exception as e:
        print(f"yfinance info failed for {clean_symbol}: {e}")
    
    # Method 3: Yahoo Finance v7 API
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={clean_symbol}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'quoteResponse' in data and data['quoteResponse']['result']:
            result = data['quoteResponse']['result'][0]
            if 'regularMarketPrice' in result:
                return float(result['regularMarketPrice'])
    except Exception as e:
        print(f"Yahoo v7 API failed for {clean_symbol}: {e}")
    
    # Method 4: Yahoo Finance v8 API
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}"
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
    print(f"DEBUG: Fetching price for '{investment_name}' of type '{investment_type}'")
    
    # First try to get symbol from our predefined lists
    symbol = get_symbol_from_selection(investment_name, investment_type)
    print(f"DEBUG: Mapped symbol: {symbol}")
    
    if symbol:
        if investment_type == "Cryptocurrency":
            price = get_crypto_price(symbol)
            print(f"DEBUG: Crypto price result: {price}")
            return price
        elif investment_type == "Stocks":
            price = get_stock_price(symbol)
            print(f"DEBUG: Stock price result: {price}")
            return price
    
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
    
    print(f"DEBUG: No price found for {investment_name}")
    return None
