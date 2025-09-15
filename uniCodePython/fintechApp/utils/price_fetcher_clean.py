"""
Modern Price Fetching with Binance API (No Rate Limits!)
Ultra-fast crypto pricing with 1200 requests/minute capacity
"""

import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import yfinance as yf
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO

# Global rate limiting (Binance allows 1200 requests/minute!)
_last_api_call = 0
_api_call_interval = 0.05  # 0.05 seconds = 1200 requests/minute max

# Symbol mapping for Binance API
CRYPTO_SYMBOLS = {
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

def get_binance_symbol(crypto_id):
    """Convert crypto ID to Binance symbol"""
    return CRYPTO_SYMBOLS.get(crypto_id, f"{crypto_id.upper()}USDT")


@st.cache_data(ttl=60)  # Cache for 1 minute only
def get_crypto_price_simple(crypto_id):
    """Get crypto price using Binance API (NO RATE LIMITS!)"""
    global _last_api_call
    
    print(f"🚀 BINANCE: Fetching {crypto_id}")
    
    # Minimal rate limiting for Binance
    current_time = time.time()
    time_since_last = current_time - _last_api_call
    
    if time_since_last < _api_call_interval:
        sleep_time = _api_call_interval - time_since_last
        time.sleep(sleep_time)
    
    symbol = get_binance_symbol(crypto_id)
    
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=10)
        _last_api_call = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if 'lastPrice' in data:
                price = float(data['lastPrice'])
                print(f"✅ BINANCE: {crypto_id} = ${price:,.2f}")
                return price
                
        print(f"❌ BINANCE: Failed to get {crypto_id}")
        return None
            
    except Exception as e:
        print(f"❌ BINANCE ERROR: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_crypto_chart_data(crypto_id, days=7):
    """Get crypto chart data using Binance API"""
    global _last_api_call
    
    print(f"📊 BINANCE CHART: Fetching {days} days for {crypto_id}")
    
    current_time = time.time()
    time_since_last = current_time - _last_api_call
    
    if time_since_last < _api_call_interval:
        sleep_time = _api_call_interval - time_since_last
        time.sleep(sleep_time)
    
    symbol = get_binance_symbol(crypto_id)
    
    try:
        # Choose interval based on days
        if days <= 1:
            interval = "1h"
            limit = min(days * 24, 1000)
        elif days <= 7:
            interval = "4h"
            limit = min(days * 6, 1000)
        else:
            interval = "1d"
            limit = min(days, 1000)
            
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        response = requests.get(url, timeout=15)
        _last_api_call = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data:
                chart_data = []
                for kline in data:
                    chart_data.append({
                        'Time': pd.to_datetime(int(kline[0]), unit='ms'),
                        'Price': float(kline[4])  # Close price
                    })
                
                df = pd.DataFrame(chart_data)
                print(f"✅ BINANCE CHART: Got {len(df)} points for {crypto_id}")
                return df
                
        print(f"❌ BINANCE CHART: Failed for {crypto_id}")
        return None
            
    except Exception as e:
        print(f"❌ BINANCE CHART ERROR: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_stock_price(symbol):
    """Get stock price using Yahoo Finance"""
    try:
        print(f"📈 YAHOO: Fetching {symbol}")
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            print(f"✅ YAHOO: {symbol} = ${price:.2f}")
            return float(price)
        else:
            print(f"❌ YAHOO: No data for {symbol}")
            return None
    except Exception as e:
        print(f"❌ YAHOO ERROR: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_stock_chart_data(symbol, days=30):
    """Get stock chart data using Yahoo Finance"""
    try:
        print(f"📊 YAHOO CHART: Fetching {days} days for {symbol}")
        ticker = yf.Ticker(symbol)
        
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
            hist = hist.reset_index()
            chart_data = pd.DataFrame({
                'Time': hist['Date'],
                'Price': hist['Close']
            })
            print(f"✅ YAHOO CHART: Got {len(chart_data)} points for {symbol}")
            return chart_data
        else:
            print(f"❌ YAHOO CHART: No data for {symbol}")
            return None
            
    except Exception as e:
        print(f"❌ YAHOO CHART ERROR: {str(e)}")
        return None


def get_price(symbol, asset_type):
    """Universal price getter"""
    if asset_type == 'crypto':
        return get_crypto_price_simple(symbol)
    elif asset_type == 'stock':
        return get_stock_price(symbol)
    else:
        return None


def get_chart_data(symbol, asset_type, days=30):
    """Universal chart data getter"""
    if asset_type == 'crypto':
        return get_crypto_chart_data(symbol, days)
    elif asset_type == 'stock':
        return get_stock_chart_data(symbol, days)
    else:
        return None


# Legacy compatibility
def get_current_price(symbol, asset_type):
    """Legacy compatibility function"""
    return get_price(symbol, asset_type)
