"""
Price fetching utilities using Binance API (excellent rate limits and reliability)
Binance allows 1200 requests/minute and has comprehensive crypto coverage
"""

import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO

# Global rate limiting (Binance is very generous - 1200 requests/minute)
_last_binance_call = 0
_binance_call_interval = 0.05  # 0.05 seconds = 1200 requests/minute max

# Binance uses different symbols than CoinGecko
BINANCE_SYMBOL_MAP = {
    'bitcoin': 'BTCUSDT',
    'ethereum': 'ETHUSDT', 
    'solana': 'SOLUSDT',
    'cardano': 'ADAUSDT',
    'polkadot': 'DOTUSDT',
    'chainlink': 'LINKUSDT',
    'litecoin': 'LTCUSDT',
    'bitcoin-cash': 'BCHUSDT',
    'stellar': 'XLMUSDT',
    'dogecoin': 'DOGEUSDT',
    'usd-coin': 'USDCUSDT',
    'tether': 'USDTUSDT',
    'ripple': 'XRPUSDT',
    'matic-network': 'MATICUSDT',
    'avalanche-2': 'AVAXUSDT',
    'cosmos': 'ATOMUSDT',
    'algorand': 'ALGOUSDT',
    'tezos': 'XTZUSDT',
    'monero': 'XMRUSDT'
}

def map_coingecko_to_binance(coingecko_id):
    """Map CoinGecko IDs to Binance trading symbols"""
    return BINANCE_SYMBOL_MAP.get(coingecko_id, f"{coingecko_id.upper()}USDT")


@st.cache_data(ttl=60)  # Cache for 1 minute (Binance updates very frequently)
def get_crypto_price_simple(crypto_id):
    """Get crypto price using Binance API with excellent rate limits"""
    global _last_binance_call
    
    print(f"🔍 DEBUG: Fetching crypto price for '{crypto_id}' using Binance API")
    
    # Rate limiting: Binance allows 1200 requests/minute
    current_time = time.time()
    time_since_last_call = current_time - _last_binance_call
    
    if time_since_last_call < _binance_call_interval:
        sleep_time = _binance_call_interval - time_since_last_call
        print(f"⏱️ DEBUG: Rate limiting - waiting {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    # Map to Binance symbol
    binance_symbol = map_coingecko_to_binance(crypto_id)
    
    try:
        # Binance API endpoint for 24hr ticker
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={binance_symbol}"
        print(f"📡 DEBUG: Making request to {url}")
        
        response = requests.get(url, timeout=10)
        _last_binance_call = time.time()
        
        print(f"📊 DEBUG: Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📈 DEBUG: Response data keys: {list(data.keys())}")
            
            if 'lastPrice' in data:
                price = float(data['lastPrice'])
                print(f"✅ DEBUG: Successfully fetched price: ${price:,.2f}")
                return price
            else:
                print(f"❌ DEBUG: No price data in response")
                return None
                
        elif response.status_code == 400:
            print(f"❌ DEBUG: Invalid symbol '{binance_symbol}' on Binance")
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
    """Get crypto historical data using Binance API"""
    global _last_binance_call
    
    print(f"📊 DEBUG: Fetching {days} days of chart data for '{crypto_id}' using Binance")
    
    # Rate limiting
    current_time = time.time()
    time_since_last_call = current_time - _last_binance_call
    
    if time_since_last_call < _binance_call_interval:
        sleep_time = _binance_call_interval - time_since_last_call
        print(f"⏱️ DEBUG: Rate limiting - waiting {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    # Map to Binance symbol
    binance_symbol = map_coingecko_to_binance(crypto_id)
    
    try:
        # Binance kline intervals
        if days <= 1:
            interval = "1h"  # 1 hour intervals
            limit = min(days * 24, 1000)  # Binance max is 1000
        elif days <= 7:
            interval = "4h"  # 4 hour intervals
            limit = min(days * 6, 1000)
        elif days <= 30:
            interval = "1d"  # 1 day intervals
            limit = min(days, 1000)
        else:
            interval = "1d"  # 1 day intervals
            limit = min(days, 1000)
            
        url = f"https://api.binance.com/api/v3/klines?symbol={binance_symbol}&interval={interval}&limit={limit}"
        print(f"📡 DEBUG: Making chart request to {url}")
        
        response = requests.get(url, timeout=15)
        _last_binance_call = time.time()
        
        print(f"📊 DEBUG: Chart response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data:
                # Convert Binance kline data to DataFrame
                chart_data = []
                for kline in data:
                    # Binance kline format: [timestamp, open, high, low, close, volume, ...]
                    chart_data.append({
                        'Time': pd.to_datetime(int(kline[0]), unit='ms'),
                        'Price': float(kline[4])  # Close price
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
