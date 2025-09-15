"""
Performance Tracking Utility
Uses CoinGecko API and Yahoo Finance for real-time performance tracking
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import streamlit as st
import time

class PerformanceTracker:
    def __init__(self):
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        # Rate limiting to respect API limits
        self.last_request_time = 0
        self.min_request_interval = 1.1  # 1.1 seconds between requests
    
    def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _extract_symbol_from_name(self, name: str, investment_type: str) -> str:
        """Extract trading symbol from investment name"""
        if investment_type.lower() == 'cryptocurrency':
            # Handle crypto names
            crypto_mapping = {
                'bitcoin': 'bitcoin',
                'ethereum': 'ethereum', 
                'litecoin': 'litecoin',
                'dogecoin': 'dogecoin',
                'cardano': 'cardano',
                'solana': 'solana',
                'chainlink': 'chainlink',
                'polkadot': 'polkadot'
            }
            
            # Try exact match first
            name_lower = name.lower()
            if name_lower in crypto_mapping:
                return crypto_mapping[name_lower]
            
            # Try partial matches
            for key, value in crypto_mapping.items():
                if key in name_lower:
                    return value
            
            # Return lowercase name as fallback
            return name.lower().replace(' ', '-')
            
        else:  # Stocks
            # Extract symbol from parentheses if present
            import re
            symbol_match = re.search(r'\(([A-Z]{1,5}(?:-[A-Z])?)\)', name)
            if symbol_match:
                return symbol_match.group(1)
            
            # Common stock name to symbol mapping
            stock_mapping = {
                'apple': 'AAPL',
                'microsoft': 'MSFT',
                'google': 'GOOGL',
                'alphabet': 'GOOGL',
                'amazon': 'AMZN',
                'tesla': 'TSLA',
                'nvidia': 'NVDA',
                'meta': 'META',
                'facebook': 'META',
                'netflix': 'NFLX'
            }
            
            name_lower = name.lower()
            for key, value in stock_mapping.items():
                if key in name_lower:
                    return value
            
            # If no mapping found, return the name as-is (cleaned)
            return name.upper().replace(' INC.', '').replace(' CORP.', '').replace(' CO.', '').strip()

    def get_crypto_historical_data(self, crypto_name: str, start_date: str, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Get historical price data for cryptocurrency - using exact pattern from myFintechApp.py
        """
        try:
            self._rate_limit()
            
            # Extract proper crypto symbol
            crypto_id = self._extract_symbol_from_name(crypto_name, 'cryptocurrency')
            print(f"DEBUG: Crypto name '{crypto_name}' mapped to '{crypto_id}'")
            
            # Calculate days using simple approach like myFintechApp.py
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date) if end_date else pd.to_datetime(datetime.now())
            
            # Use pandas-compatible timedelta calculation
            time_diff = end_dt - start_dt
            days_diff = time_diff.total_seconds() / (24 * 3600)  # Convert to days
            days_diff = int(days_diff)
            if days_diff < 1:
                days_diff = 1
            
            # Use exact same pattern as myFintechApp.py
            url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days_diff}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Use exact same DataFrame creation as myFintechApp.py
                if 'prices' in data:
                    prices_df = pd.DataFrame(data["prices"], columns=["Time", "price"])
                    prices_df["Time"] = pd.to_datetime(prices_df["Time"], unit="ms")
                    prices_df = prices_df.set_index("Time")
                    
                    return prices_df
            else:
                st.warning(f"Unable to fetch data for {crypto_name}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error fetching crypto data for {crypto_name}: {str(e)}")
            return None
    
    def get_stock_historical_data(self, symbol: str, start_date: str, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Get historical price data for stocks - using simple approach like myFintechApp.py
        """
        try:
            # Extract proper stock symbol
            ticker_symbol = self._extract_symbol_from_name(symbol, 'stocks')
            print(f"DEBUG: Stock name '{symbol}' mapped to '{ticker_symbol}'")
            
            # Calculate days for period using simple approach
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date) if end_date else pd.to_datetime(datetime.now())
            
            # Use pandas-compatible timedelta calculation
            time_diff = end_dt - start_dt
            days_diff = time_diff.total_seconds() / (24 * 3600)  # Convert to days
            days_diff = int(days_diff)
            if days_diff < 1:
                days_diff = 1
            
            # Use simple yfinance approach instead of complex API calls
            import yfinance as yf
            
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period=f"{days_diff}d")
            
            if not hist.empty:
                # Convert to simple format like myFintechApp.py
                df = pd.DataFrame()
                df['price'] = hist['Close']
                df.index = hist.index
                
                return df
            else:
                st.warning(f"No data found for symbol {ticker_symbol}")
                return None
                
        except Exception as e:
            st.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return None
    
    def calculate_investment_performance(self, investment: Dict, historical_data: pd.DataFrame) -> Dict:
        """
        Calculate performance metrics for an investment - simplified approach
        """
        try:
            entry_date = pd.to_datetime(investment['date_added'])
            entry_price = investment['entry_price']
            shares = investment['shares']
            total_invested = investment['amount']
            
            # Simple approach: use entry_price as provided, current price from latest data
            current_price = historical_data['price'].iloc[-1]
            current_value = shares * current_price
            
            # Calculate returns
            absolute_return = current_value - total_invested
            percentage_return = (absolute_return / total_invested) * 100
            
            # Calculate time-based metrics using pandas-compatible arithmetic
            current_datetime = pd.to_datetime(datetime.now())
            
            # Use pandas-compatible timedelta calculation
            time_diff = current_datetime - entry_date
            days_held = time_diff.total_seconds() / (24 * 3600)  # Convert to days
            days_held = int(days_held)
            
            if days_held > 0:
                annualized_return = ((current_value / total_invested) ** (365 / days_held) - 1) * 100
            else:
                annualized_return = 0
            
            return {
                'name': investment['name'],
                'type': investment['type'],
                'entry_date': entry_date.strftime('%Y-%m-%d'),
                'entry_price': entry_price,
                'current_price': current_price,
                'shares': shares,
                'total_invested': total_invested,
                'current_value': current_value,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'annualized_return': annualized_return,
                'days_held': days_held,
                'market_entry_price': entry_price  # Use entry price as market price
            }
            
        except Exception as e:
            st.error(f"Error calculating performance for {investment['name']}: {str(e)}")
            return None
    
    def get_portfolio_performance(self, investments: List[Dict]) -> pd.DataFrame:
        """
        Get performance data for entire portfolio
        """
        performance_data = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, investment in enumerate(investments):
            status_text.text(f"Fetching data for {investment['name']}...")
            progress_bar.progress((i + 1) / len(investments))
            
            try:
                # Get historical data based on investment type
                start_date = investment['date_added']
                
                if investment['type'].lower() == 'cryptocurrency':
                    historical_data = self.get_crypto_historical_data(investment['name'], start_date)
                else:  # Stocks and others
                    historical_data = self.get_stock_historical_data(investment['name'], start_date)
                
                if historical_data is not None and not historical_data.empty:
                    performance = self.calculate_investment_performance(investment, historical_data)
                    if performance:
                        performance_data.append(performance)
                else:
                    # If no historical data, create basic performance with current price
                    try:
                        if investment['type'].lower() == 'cryptocurrency':
                            # Try to get current price at least
                            current_data = self.get_crypto_historical_data(
                                investment['name'], 
                                (datetime.now() - timedelta(days=1)).isoformat()
                            )
                        else:
                            current_data = self.get_stock_historical_data(
                                investment['name'],
                                (datetime.now() - timedelta(days=1)).isoformat()
                            )
                        
                        if current_data is not None and not current_data.empty:
                            current_price = current_data['price'].iloc[-1]
                            performance_data.append({
                                'name': investment['name'],
                                'type': investment['type'],
                                'entry_date': pd.to_datetime(investment['date_added']).strftime('%Y-%m-%d'),
                                'entry_price': investment['entry_price'],
                                'current_price': current_price,
                                'shares': investment['shares'],
                                'total_invested': investment['amount'],
                                'current_value': investment['shares'] * current_price,
                                'absolute_return': (investment['shares'] * current_price) - investment['amount'],
                                'percentage_return': ((investment['shares'] * current_price - investment['amount']) / investment['amount']) * 100,
                                'annualized_return': 0,  # Can't calculate without historical data
                                'days_held': (datetime.now() - pd.to_datetime(investment['date_added'])).days,
                                'market_entry_price': investment['entry_price']
                            })
                    except:
                        # Fallback to entry data only
                        performance_data.append({
                            'name': investment['name'],
                            'type': investment['type'],
                            'entry_date': pd.to_datetime(investment['date_added']).strftime('%Y-%m-%d'),
                            'entry_price': investment['entry_price'],
                            'current_price': investment['entry_price'],  # Assume no change
                            'shares': investment['shares'],
                            'total_invested': investment['amount'],
                            'current_value': investment['amount'],
                            'absolute_return': 0,
                            'percentage_return': 0,
                            'annualized_return': 0,
                            'days_held': (datetime.now() - pd.to_datetime(investment['date_added'])).days,
                            'market_entry_price': investment['entry_price']
                        })
                        
            except Exception as e:
                st.warning(f"Skipping {investment['name']} due to error: {str(e)}")
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        if performance_data:
            return pd.DataFrame(performance_data)
        else:
            return pd.DataFrame()
    
    def create_performance_charts(self, portfolio_df: pd.DataFrame) -> Dict:
        """
        Create various performance visualization charts
        """
        charts = {}
        
        if portfolio_df.empty:
            return charts
        
        # Portfolio overview metrics
        total_invested = portfolio_df['total_invested'].sum()
        total_current = portfolio_df['current_value'].sum()
        total_return = total_current - total_invested
        total_return_pct = (total_return / total_invested) * 100 if total_invested > 0 else 0
        
        charts['overview'] = {
            'total_invested': total_invested,
            'total_current': total_current,
            'total_return': total_return,
            'total_return_pct': total_return_pct
        }
        
        # Individual performance data for charts
        charts['individual_performance'] = portfolio_df.copy()
        
        return charts
