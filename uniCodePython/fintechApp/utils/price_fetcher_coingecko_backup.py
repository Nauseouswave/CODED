"""
Price fetching utilities for stocks and cryptocurrencies
Simple and reliable price fetching using CoinGecko and Yahoo Finance APIs
"""

import streamlit as st
import requests
import pandas as pd
import time
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO

# Global rate limiting to prevent hitting API limits
_last_coingecko_call = 0
_coingecko_call_interval = 2.0  # Minimum 2 seconds between calls


@st.cache_data(ttl=1800)  # Cache for 30 minutes to reduce API calls
def get_crypto_price_simple(crypto_id):
    """Get crypto price using CoinGecko simple price API with rate limit handling"""
    global _last_coingecko_call
    
    print(f"🔍 DEBUG: Attempting to fetch crypto price for '{crypto_id}'")
    
    # Rate limiting: ensure minimum time between API calls
    current_time = time.time()
    time_since_last_call = current_time - _last_coingecko_call
    
    if time_since_last_call < _coingecko_call_interval:
        sleep_time = _coingecko_call_interval - time_since_last_call
        print(f"⏱️ DEBUG: Rate limiting - waiting {sleep_time:.1f} seconds")
        time.sleep(sleep_time)
    
    max_retries = 3
    base_delay = 5.0  # Start with 5 second delay for retries
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                delay = base_delay * (2 ** attempt)  # Exponential backoff: 5s, 10s, 20s
                print(f"⏱️ DEBUG: Waiting {delay} seconds before retry {attempt + 1}")
                time.sleep(delay)
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
            print(f"🌐 DEBUG: Making request to: {url}")
            
            # Add headers to look more like a regular browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            _last_coingecko_call = time.time()  # Update last call time
            response = requests.get(url, headers=headers, timeout=15)
            print(f"📊 DEBUG: Response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📋 DEBUG: Response data: {data}")
                
                if crypto_id in data and 'usd' in data[crypto_id]:
                    price = float(data[crypto_id]['usd'])
                    print(f"✅ DEBUG: Successfully extracted price: ${price}")
                    return price
                else:
                    print(f"❌ DEBUG: Crypto ID '{crypto_id}' not found in response data")
                    print(f"📋 DEBUG: Available keys in response: {list(data.keys()) if data else 'No data'}")
                    
            elif response.status_code == 429:
                print(f"🚫 DEBUG: Rate limited (429) on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    continue  # Try again with exponential backoff
                else:
                    print(f"💔 DEBUG: Max retries reached, rate limit persists")
                    
            else:
                print(f"❌ DEBUG: Bad status code {response.status_code}")
                print(f"📋 DEBUG: Response text: {response.text[:500]}...")
                
        except Exception as e:
            print(f"💥 DEBUG: Exception occurred while fetching {crypto_id}: {type(e).__name__}: {e}")
            import traceback
            print(f"📍 DEBUG: Full traceback:\n{traceback.format_exc()}")
    
    print(f"🚫 DEBUG: Failed to get price for '{crypto_id}' after {max_retries} attempts")
    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_price_simple(symbol):
    """Get stock price using Yahoo Finance API - simplified approach"""
    print(f"🔍 DEBUG: Attempting to fetch stock price for '{symbol}'")
    
    try:
        # Clean the symbol
        clean_symbol = symbol.replace('$', '').strip().upper()
        print(f"🧹 DEBUG: Cleaned symbol: '{clean_symbol}'")
        
        # Use Yahoo Finance query API
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}"
        print(f"🌐 DEBUG: Making request to: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📊 DEBUG: Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 DEBUG: Response data structure: {list(data.keys()) if data else 'No data'}")
            
            if 'chart' in data and data['chart']['result']:
                chart_data = data['chart']['result'][0]
                print(f"📈 DEBUG: Chart data keys: {list(chart_data.keys())}")
                
                if 'meta' in chart_data and 'regularMarketPrice' in chart_data['meta']:
                    price = chart_data['meta']['regularMarketPrice']
                    print(f"💰 DEBUG: Found regularMarketPrice: {price}")
                    if price and price > 0:
                        print(f"✅ DEBUG: Successfully extracted stock price: ${price}")
                        return float(price)
                
                # Fallback to timestamp data
                if 'timestamp' in chart_data and 'indicators' in chart_data:
                    print(f"📊 DEBUG: Using fallback timestamp data method")
                    closes = chart_data['indicators']['quote'][0]['close']
                    if closes and len(closes) > 0:
                        print(f"📈 DEBUG: Found {len(closes)} closing prices")
                        # Get the most recent non-null close price
                        for i, close_price in enumerate(reversed(closes)):
                            if close_price is not None and close_price > 0:
                                print(f"✅ DEBUG: Using fallback close price: ${close_price}")
                                return float(close_price)
                        print(f"❌ DEBUG: No valid closing prices found")
                    else:
                        print(f"❌ DEBUG: No closing price data available")
            else:
                print(f"❌ DEBUG: Invalid chart data structure")
                if 'chart' in data:
                    print(f"📋 DEBUG: Chart result: {data['chart']}")
        else:
            print(f"❌ DEBUG: Bad status code {response.status_code}")
            print(f"📋 DEBUG: Response text: {response.text[:500]}...")
        
    except Exception as e:
        print(f"💥 DEBUG: Exception occurred while fetching {symbol}: {type(e).__name__}: {e}")
        import traceback
        print(f"📍 DEBUG: Full traceback:\n{traceback.format_exc()}")
    
    print(f"🚫 DEBUG: Failed to get price for '{symbol}', returning None")
    return None


def get_crypto_chart_data(crypto_id, days=7):
    """Get crypto price chart data using CoinGecko with rate limiting"""
    global _last_coingecko_call
    
    print(f"📈 DEBUG: Fetching chart data for '{crypto_id}' ({days} days)")
    
    # Rate limiting: ensure minimum time between API calls
    current_time = time.time()
    time_since_last_call = current_time - _last_coingecko_call
    
    if time_since_last_call < _coingecko_call_interval:
        sleep_time = _coingecko_call_interval - time_since_last_call
        print(f"⏱️ DEBUG: Chart rate limiting - waiting {sleep_time:.1f} seconds")
        time.sleep(sleep_time)
    
    max_retries = 3
    base_delay = 5.0
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                delay = base_delay * (2 ** attempt)
                print(f"⏱️ DEBUG: Chart retry waiting {delay} seconds (attempt {attempt + 1})")
                time.sleep(delay)
            
            url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}"
            print(f"🌐 DEBUG: Chart request to: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            _last_coingecko_call = time.time()  # Update last call time
            response = requests.get(url, headers=headers, timeout=15)
            print(f"📊 DEBUG: Chart response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📋 DEBUG: Chart data keys: {list(data.keys()) if data else 'No data'}")
                
                if 'prices' in data:
                    prices_df = pd.DataFrame(data["prices"], columns=["Time", "Price"])
                    prices_df["Time"] = pd.to_datetime(prices_df["Time"], unit="ms")
                    print(f"✅ DEBUG: Chart data retrieved: {len(prices_df)} price points")
                    return prices_df
                else:
                    print(f"❌ DEBUG: No 'prices' key in chart response")
                    
            elif response.status_code == 429:
                print(f"🚫 DEBUG: Chart rate limited (429) on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    continue
                else:
                    print(f"💔 DEBUG: Chart max retries reached, rate limit persists")
            else:
                print(f"❌ DEBUG: Chart bad status code {response.status_code}")
                print(f"📋 DEBUG: Chart response text: {response.text[:200]}...")
                
        except Exception as e:
            print(f"💥 DEBUG: Chart exception for {crypto_id}: {type(e).__name__}: {e}")
    
    print(f"🚫 DEBUG: Failed to get chart data for '{crypto_id}' after {max_retries} attempts")
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
    print(f"🔍 DEBUG: Looking up symbol for '{investment_name}' in '{investment_type}' category")
    
    if investment_type == "Stocks":
        symbol = POPULAR_STOCKS.get(investment_name)
        print(f"📈 DEBUG: Stock lookup result: {symbol}")
        if symbol is None:
            print(f"📋 DEBUG: Available stocks: {list(POPULAR_STOCKS.keys())[:5]}... (showing first 5)")
        return symbol
    elif investment_type == "Cryptocurrency":
        symbol = POPULAR_CRYPTO.get(investment_name)
        print(f"🪙 DEBUG: Crypto lookup result: {symbol}")
        if symbol is None:
            print(f"📋 DEBUG: Available cryptos: {list(POPULAR_CRYPTO.keys())[:5]}... (showing first 5)")
        return symbol
    else:
        print(f"❌ DEBUG: Unknown investment type: {investment_type}")
    
    return None


def get_current_price(investment_name, investment_type):
    """Get current price based on investment type and name - simplified version"""
    print(f"🚀 DEBUG: === START PRICE FETCH ===")
    print(f"🔍 DEBUG: Fetching price for '{investment_name}' of type '{investment_type}'")
    
    # First try to get symbol from our predefined lists
    symbol = get_symbol_from_selection(investment_name, investment_type)
    print(f"🔗 DEBUG: Mapped symbol: {symbol}")
    
    if symbol:
        print(f"✅ DEBUG: Found symbol in predefined lists")
        if investment_type == "Cryptocurrency":
            print(f"🪙 DEBUG: Processing as cryptocurrency")
            price = get_crypto_price_simple(symbol)
            print(f"💰 DEBUG: Crypto price result: {price}")
            print(f"🏁 DEBUG: === END PRICE FETCH (crypto) ===")
            return price
        elif investment_type == "Stocks":
            print(f"📈 DEBUG: Processing as stock")
            price = get_stock_price_simple(symbol)
            print(f"💰 DEBUG: Stock price result: {price}")
            print(f"🏁 DEBUG: === END PRICE FETCH (stock) ===")
            return price
    else:
        print(f"❌ DEBUG: Symbol not found in predefined lists, trying fallback")
    
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
