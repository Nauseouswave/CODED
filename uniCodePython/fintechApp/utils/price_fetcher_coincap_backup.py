"""
Price fetching utilities using CoinCap API (better rate limits than CoinGecko)
CoinCap allows 200 requests/minute vs CoinGecko's strict limits
"""

import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO

# Global rate limiting (CoinCap is much more generous)
_last_coincap_call = 0
_coincap_call_interval = 0.3  # 0.3 seconds = 200 requests/minute max

# CoinCap uses different IDs than CoinGecko
COINCAP_ID_MAP = {
    'bitcoin': 'bitcoin',
    'ethereum': 'ethereum', 
    'solana': 'solana',
    'cardano': 'cardano',
    'polkadot': 'polkadot',
    'chainlink': 'chainlink',
    'litecoin': 'litecoin',
    'bitcoin-cash': 'bitcoin-cash',
    'stellar': 'stellar',
    'dogecoin': 'dogecoin',
    'usd-coin': 'usd-coin',
    'tether': 'tether',
    'ripple': 'xrp',
    'matic-network': 'polygon',
    'avalanche-2': 'avalanche',
    'cosmos': 'cosmos',
    'algorand': 'algorand',
    'tezos': 'tezos',
    'monero': 'monero'
}

def map_coingecko_to_coincap(coingecko_id):
    """Map CoinGecko IDs to CoinCap IDs"""
    return COINCAP_ID_MAP.get(coingecko_id, coingecko_id)


@st.cache_data(ttl=300)  # Cache for 5 minutes (CoinCap updates frequently)
def get_crypto_price_simple(crypto_id):
    """Get crypto price using CoinCap API with better rate limits"""
    global _last_coincap_call
    
    print(f"🔍 DEBUG: Fetching crypto price for '{crypto_id}' using CoinCap API")
    
    # Rate limiting: CoinCap allows 200 requests/minute
    current_time = time.time()
    time_since_last_call = current_time - _last_coincap_call
    
    if time_since_last_call < _coincap_call_interval:
        sleep_time = _coincap_call_interval - time_since_last_call
        print(f"⏱️ DEBUG: Rate limiting - waiting {sleep_time:.1f} seconds")
        time.sleep(sleep_time)
    
    # Map to CoinCap ID
    coincap_id = map_coingecko_to_coincap(crypto_id)
    
    try:
        # CoinCap API endpoint
        url = f"https://api.coincap.io/v2/assets/{coincap_id}"
        print(f"📡 DEBUG: Making request to {url}")
        
        response = requests.get(url, timeout=10)
        _last_coincap_call = time.time()
        
        print(f"📊 DEBUG: Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📈 DEBUG: Response data keys: {list(data.keys())}")
            
            if 'data' in data and data['data']:
                price = float(data['data']['priceUsd'])
                print(f"✅ DEBUG: Successfully fetched price: ${price:,.2f}")
                return price
            else:
                print(f"❌ DEBUG: No price data in response")
                return None
                
        elif response.status_code == 404:
            print(f"❌ DEBUG: Cryptocurrency '{crypto_id}' not found on CoinCap")
            return None
        else:
            print(f"❌ DEBUG: API error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ DEBUG: Request timeout")
        return None
    except Exception as e:
        print(f"❌ DEBUG: Exception occurred: {str(e)}")
        return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_crypto_chart_data(crypto_id, days=7):
    """Get crypto historical data using CoinCap API"""
    global _last_coincap_call
    
    print(f"📊 DEBUG: Fetching {days} days of chart data for '{crypto_id}' using CoinCap")
    
    # Rate limiting
    current_time = time.time()
    time_since_last_call = current_time - _last_coincap_call
    
    if time_since_last_call < _coincap_call_interval:
        sleep_time = _coincap_call_interval - time_since_last_call
        print(f"⏱️ DEBUG: Rate limiting - waiting {sleep_time:.1f} seconds")
        time.sleep(sleep_time)
    
    # Map to CoinCap ID
    coincap_id = map_coingecko_to_coincap(crypto_id)
    
    try:
        # CoinCap uses different interval system
        if days <= 1:
            interval = "m5"  # 5 minute intervals
        elif days <= 7:
            interval = "h1"  # 1 hour intervals
        elif days <= 30:
            interval = "h6"  # 6 hour intervals
        else:
            interval = "d1"  # 1 day intervals
            
        # Calculate start and end timestamps
        end_time = int(time.time() * 1000)  # Current time in milliseconds
        start_time = end_time - (days * 24 * 60 * 60 * 1000)  # Days ago in milliseconds
        
        url = f"https://api.coincap.io/v2/assets/{coincap_id}/history?interval={interval}&start={start_time}&end={end_time}"
        print(f"📡 DEBUG: Making chart request to {url}")
        
        response = requests.get(url, timeout=15)
        _last_coincap_call = time.time()
        
        print(f"📊 DEBUG: Chart response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and data['data']:
                # Convert to DataFrame
                chart_data = []
                for item in data['data']:
                    chart_data.append({
                        'Time': pd.to_datetime(item['time']),
                        'Price': float(item['priceUsd'])
                    })
                
                df = pd.DataFrame(chart_data)
                print(f"✅ DEBUG: Successfully fetched {len(df)} data points")
                return df
            else:
                print(f"❌ DEBUG: No chart data in response")
                return None
                
        else:
            print(f"❌ DEBUG: Chart API error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ DEBUG: Chart exception: {str(e)}")
        return None


# Stock price functions remain the same (using Yahoo Finance)
import yfinance as yf

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_price(symbol):
    """Get current stock price using Yahoo Finance"""
    try:
        print(f"📈 DEBUG: Fetching stock price for '{symbol}'")
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            print(f"✅ DEBUG: Stock price for {symbol}: ${price:.2f}")
            return float(price)
        else:
            print(f"❌ DEBUG: No stock data for '{symbol}'")
            return None
    except Exception as e:
        print(f"❌ DEBUG: Stock price error for {symbol}: {str(e)}")
        return None


@st.cache_data(ttl=300)  # Cache for 5 minutes  
def get_stock_chart_data(symbol, days=30):
    """Get stock historical data using Yahoo Finance"""
    try:
        print(f"📊 DEBUG: Fetching {days} days of stock data for '{symbol}'")
        ticker = yf.Ticker(symbol)
        
        # Calculate period string for yfinance
        if days <= 5:
            period = "5d"
        elif days <= 30:
            period = "1mo"
        elif days <= 90:
            period = "3mo"
        elif days <= 365:
            period = "1y"
        else:
            period = "2y"
            
        hist = ticker.history(period=period)
        
        if not hist.empty:
            # Reset index to get dates as column
            hist = hist.reset_index()
            chart_data = pd.DataFrame({
                'Time': hist['Date'],
                'Price': hist['Close']
            })
            print(f"✅ DEBUG: Successfully fetched {len(chart_data)} stock data points")
            return chart_data
        else:
            print(f"❌ DEBUG: No stock chart data for '{symbol}'")
            return None
            
    except Exception as e:
        print(f"❌ DEBUG: Stock chart error for {symbol}: {str(e)}")
        return None


def get_price(symbol, asset_type):
    """Universal price getter that determines if asset is stock or crypto"""
    print(f"🔍 DEBUG: Getting price for '{symbol}' (type: {asset_type})")
    
    if asset_type == 'crypto':
        return get_crypto_price_simple(symbol)
    elif asset_type == 'stock':
        return get_stock_price(symbol)
    else:
        print(f"❌ DEBUG: Unknown asset type '{asset_type}'")
        return None


def get_chart_data(symbol, asset_type, days=30):
    """Universal chart data getter"""
    print(f"📊 DEBUG: Getting chart data for '{symbol}' (type: {asset_type}, days: {days})")
    
    if asset_type == 'crypto':
        return get_crypto_chart_data(symbol, days)
    elif asset_type == 'stock':
        return get_stock_chart_data(symbol, days)
    else:
        print(f"❌ DEBUG: Unknown asset type '{asset_type}'")
        return None
