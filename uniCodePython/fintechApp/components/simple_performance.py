"""
Simple Performance Tracking UI Component
Streamlit interface for investment performance analysis with time period selectors
"""

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
from typing import List, Dict
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO

def render_simple_individual_performance(investments: List[Dict]):
    """Render individual investment performance with simple chart and time selectors"""
    
    st.subheader("📈 Individual Investment Analysis")
    
    # Select investment to analyze
    investment_names = [inv['name'] for inv in investments]
    selected_investment = st.selectbox("Select an investment to analyze:", investment_names)
    
    if not selected_investment:
        return
    
    # Find the selected investment
    investment = next(inv for inv in investments if inv['name'] == selected_investment)
    
    # Time period selector
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{selected_investment}** - {investment['type']}")
    
    with col2:
        time_period = st.selectbox(
            "Time Period:",
            ["1D", "7D", "1M", "3M", "6M", "1Y", "ALL"],
            index=3,  # Default to 3M
            key="time_period_selector"
        )
    
    # Convert time period to days with better granularity
    period_days = {
        "1D": 1,
        "7D": 7, 
        "1M": 30,
        "3M": 90,
        "6M": 180,
        "1Y": 365,
        "ALL": 730  # 2 years max for better performance
    }
    
    days = period_days[time_period]
    
    with st.spinner(f"📊 Loading {time_period} chart for {selected_investment}..."):
        try:
            # Get chart data based on investment type
            if investment['type'].lower() == 'cryptocurrency':
                # Use centralized crypto mapping
                crypto_id = POPULAR_CRYPTO.get(investment['name'], 'bitcoin')
                
                # Use CoinGecko API directly like myFintechApp.py
                url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}"
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'prices' in data and data['prices']:
                        # Create chart exactly like myFintechApp.py
                        prices_df = pd.DataFrame(data["prices"], columns=["Time", "Price"])
                        prices_df["Time"] = pd.to_datetime(prices_df["Time"], unit="ms")
                        
                        # Display current price
                        current_price = data["prices"][-1][1]
                        st.metric(
                            label=f"Current {investment['name']} Price",
                            value=f"${current_price:,.2f} USD"
                        )
                        
                        # Display chart with proper scaling
                        st.subheader(f"📈 Price Chart - Last {time_period}")
                        
                        # Create a proper scaled chart
                        chart_df = prices_df.set_index("Time")["Price"]
                        
                        # Calculate price range for better scaling
                        min_price = chart_df.min()
                        max_price = chart_df.max()
                        price_range = max_price - min_price
                        
                        # Add some padding (5% on each side)
                        padding = price_range * 0.05
                        y_min = max(0, min_price - padding)  # Don't go below 0
                        y_max = max_price + padding
                        
                        # Use plotly for better control over scaling
                        import plotly.graph_objects as go
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=chart_df.index,
                            y=chart_df.values,
                            mode='lines',
                            name='Price',
                            line=dict(color='#1f77b4', width=2),
                            hovertemplate='<b>%{x}</b><br>Price: $%{y:.2f}<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title=f"{investment['name']} - {time_period}",
                            xaxis_title="Time",
                            yaxis_title="Price (USD)",
                            yaxis=dict(range=[y_min, y_max], tickformat='.2f'),
                            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)'),
                            yaxis_showgrid=True,
                            showlegend=False,
                            height=400,
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show basic investment info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("💰 Your Investment", f"${investment['amount']:,.2f}")
                        with col2:
                            st.metric("📊 Shares/Units", f"{investment['shares']:,.4f}")
                        with col3:
                            st.metric("💵 Entry Price", f"${investment['entry_price']:,.2f}")
                    else:
                        st.error("No price data available")
                else:
                    st.error(f"Failed to fetch data: HTTP {response.status_code}")
                    
            else:
                # Stock data using centralized mapping
                import yfinance as yf
                
                ticker_symbol = POPULAR_STOCKS.get(investment['name'], 'AAPL')
                
                ticker = yf.Ticker(ticker_symbol)
                
                # Get different periods with more data points for smoother appearance
                if time_period == "1D":
                    hist = ticker.history(period="1d", interval="2m")  # 2-minute intervals
                elif time_period == "7D":
                    hist = ticker.history(period="7d", interval="30m")  # 30-minute intervals
                elif time_period == "1M":
                    hist = ticker.history(period="1mo", interval="90m")  # 90-minute intervals
                elif time_period == "3M":
                    hist = ticker.history(period="3mo", interval="1d")   # Daily
                elif time_period == "6M":
                    hist = ticker.history(period="6mo", interval="1d")   # Daily
                elif time_period == "1Y":
                    hist = ticker.history(period="1y", interval="1d")    # Daily
                else:  # ALL
                    hist = ticker.history(period="2y", interval="1d")    # Daily for 2 years
                
                if not hist.empty:
                    # Display current price
                    current_price = hist['Close'].iloc[-1]
                    st.metric(
                        label=f"Current {investment['name']} Price",
                        value=f"${current_price:.2f} USD"
                    )
                    
                    # Display chart with proper scaling  
                    st.subheader(f"📈 Price Chart - Last {time_period}")
                    
                    # Create a proper scaled chart
                    chart_data = hist['Close']
                    
                    # Calculate price range for better scaling
                    min_price = chart_data.min()
                    max_price = chart_data.max()
                    price_range = max_price - min_price
                    
                    # Add some padding (5% on each side)
                    padding = price_range * 0.05
                    y_min = max(0, min_price - padding)  # Don't go below 0
                    y_max = max_price + padding
                    
                    # Use plotly for better control over scaling
                    import plotly.graph_objects as go
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=chart_data.index,
                        y=chart_data.values,
                        mode='lines',
                        name='Price',
                        line=dict(color='#1f77b4', width=2),
                        hovertemplate='<b>%{x}</b><br>Price: $%{y:.2f}<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title=f"{investment['name']} - {time_period}",
                        xaxis_title="Time",
                        yaxis_title="Price (USD)",
                        yaxis=dict(range=[y_min, y_max], tickformat='.2f'),
                        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)'),
                        yaxis_showgrid=True,
                        showlegend=False,
                        height=400,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show basic investment info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("💰 Your Investment", f"${investment['amount']:,.2f}")
                    with col2:
                        st.metric("📊 Shares", f"{investment['shares']:,.4f}")
                    with col3:
                        st.metric("💵 Entry Price", f"${investment['entry_price']:,.2f}")
                else:
                    st.error("No stock data available")
            
        except Exception as e:
            st.error(f"❌ Error loading chart for {selected_investment}: {str(e)}")
            
    # Simple current value calculation (no complex date arithmetic)
    try:
        if 'current_price' in locals():
            current_value = investment['shares'] * current_price
            profit_loss = current_value - investment['amount']
            
            st.divider()
            st.subheader("💼 Your Position")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💎 Current Value", f"${current_value:,.2f}")
            with col2:
                delta_color = "normal" if profit_loss >= 0 else "inverse"
                st.metric(
                    "📊 Profit/Loss",
                    f"${profit_loss:+,.2f}",
                    delta=f"{(profit_loss/investment['amount'])*100:+.2f}%",
                    delta_color=delta_color
                )
            with col3:
                # Simple days calculation using basic datetime - no pandas issues
                entry_date = datetime.strptime(investment['date_added'], '%Y-%m-%d')
                days_held = (datetime.now() - entry_date).days
                st.metric("📅 Days Held", f"{days_held} days")
                
    except Exception as e:
        st.info("Current position calculation unavailable")
