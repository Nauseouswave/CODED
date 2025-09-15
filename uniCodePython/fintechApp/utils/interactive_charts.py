"""
Interactive Portfolio Charts using Plotly
Modern, interactive visualization components for the portfolio dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
import yfinance as yf
import requests
from datetime import datetime, timedelta
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO
from utils.price_fetcher import get_crypto_chart_data, get_stock_chart_data

def create_interactive_portfolio_pie_chart(investments: List[Dict]) -> go.Figure:
    """Create an interactive plotly pie chart for portfolio distribution"""
    
    # Group by investment name and sum amounts
    name_totals = {}
    for inv in investments:
        if inv['name'] in name_totals:
            name_totals[inv['name']] += inv['amount']
        else:
            name_totals[inv['name']] = inv['amount']
    
    # Create chart data
    names = list(name_totals.keys())
    amounts = list(name_totals.values())
    
    # Modern color palette
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
              '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5']
    
    # Create interactive pie chart
    fig = go.Figure(data=[go.Pie(
        labels=names,
        values=amounts,
        hole=0.3,  # Make it a donut chart
        hovertemplate='<b>%{label}</b><br>' +
                      'Amount: $%{value:,.0f}<br>' +
                      'Percentage: %{percent}<br>' +
                      '<extra></extra>',
        textinfo='label+percent',
        textposition='inside',
        marker=dict(
            colors=colors[:len(names)],
            line=dict(color='#FFFFFF', width=2)
        ),
        pull=[0.05] * len(names)  # Slightly separate all slices
    )])
    
    fig.update_layout(
        title={
            'text': '💼 Portfolio Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        height=500,
        margin=dict(l=20, r=150, t=70, b=20)
    )
    
    return fig

def create_interactive_portfolio_donut_chart(investments: List[Dict]) -> go.Figure:
    """Create an interactive plotly donut chart for investment types"""
    
    # Group by investment type
    type_totals = {}
    for inv in investments:
        inv_type = inv['type']
        if inv_type in type_totals:
            type_totals[inv_type] += inv['amount']
        else:
            type_totals[inv_type] = inv['amount']
    
    if not type_totals:
        return None
    
    # Create chart data
    types = list(type_totals.keys())
    amounts = list(type_totals.values())
    
    # Color scheme for investment types
    type_colors = {
        'Stocks': '#3498db',
        'Cryptocurrency': '#f39c12',
        'Bonds': '#27ae60',
        'Real Estate': '#e74c3c',
        'Other': '#9b59b6'
    }
    
    colors = [type_colors.get(inv_type, '#95a5a6') for inv_type in types]
    
    # Create interactive donut chart
    fig = go.Figure(data=[go.Pie(
        labels=types,
        values=amounts,
        hole=0.5,  # Larger hole for donut effect
        hovertemplate='<b>%{label}</b><br>' +
                      'Amount: $%{value:,.0f}<br>' +
                      'Percentage: %{percent}<br>' +
                      '<extra></extra>',
        textinfo='label+percent',
        textposition='inside',
        marker=dict(
            colors=colors,
            line=dict(color='#FFFFFF', width=2)
        )
    )])
    
    # Add center text
    fig.add_annotation(
        text="Portfolio<br>by Type",
        x=0.5, y=0.5,
        font_size=16,
        font_color='#2c3e50',
        showarrow=False
    )
    
    fig.update_layout(
        title={
            'text': '📊 Investment Types Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        height=500,
        margin=dict(l=20, r=150, t=70, b=20)
    )
    
    return fig

def create_portfolio_time_series_chart(investments: List[Dict], time_period: str = "1M", chart_type: str = "percentage") -> go.Figure:
    """Create an interactive time series chart showing portfolio performance over time
    
    Args:
        investments: List of investment dictionaries
        time_period: Time period for data (1D, 7D, 1M, etc.)
        chart_type: 'percentage' for percentage change, 'absolute' for absolute values, 'normalized' for normalized values
    """
    
    # Convert time period to days
    period_days = {
        "1D": 1,
        "7D": 7,
        "1M": 30,
        "3M": 90,
        "6M": 180,
        "1Y": 365,
        "ALL": 730
    }
    
    days = period_days.get(time_period, 30)
    
    # Create figure
    fig = go.Figure()
    
    # Add traces for each investment
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, investment in enumerate(investments):
        try:
            if investment['type'].lower() == 'cryptocurrency':
                # Get crypto data using centralized Binance API
                crypto_id = POPULAR_CRYPTO.get(investment['name'], 'bitcoin')
                prices_df = get_crypto_chart_data(crypto_id, days)
                
                if prices_df is not None and not prices_df.empty:
                    # Rename columns to match expected format
                    prices_df = prices_df.rename(columns={'Price': 'Price', 'Time': 'Time'})
                    
                    # Calculate different chart types
                    if chart_type == "percentage":
                        # Calculate percentage change from first value
                        first_price = prices_df["Price"].iloc[0]
                        prices_df["Performance"] = ((prices_df["Price"] - first_price) / first_price) * 100
                        y_values = prices_df["Performance"]
                        y_format = '.2f'
                        y_suffix = '%'
                    elif chart_type == "normalized":
                        # Normalize to start at 100
                        first_price = prices_df["Price"].iloc[0]
                        prices_df["Performance"] = (prices_df["Price"] / first_price) * 100
                        y_values = prices_df["Performance"]
                        y_format = '.2f'
                        y_suffix = ''
                    else:  # absolute
                        # Calculate portfolio value for this investment
                        prices_df["Performance"] = prices_df["Price"] * investment['shares']
                        y_values = prices_df["Performance"]
                        y_format = ',.2f'
                        y_suffix = ''
                        
                        fig.add_trace(go.Scatter(
                            x=prices_df["Time"],
                            y=y_values,
                            mode='lines',
                            name=investment['name'],
                            line=dict(color=colors[i % len(colors)], width=2),
                            hovertemplate='<b>%{fullData.name}</b><br>' +
                                        'Date: %{x}<br>' +
                                        f'Value: %{{y:{y_format}}}{y_suffix}<br>' +
                                        '<extra></extra>'
                        ))
            
            else:
                # Get stock data using centralized function
                ticker_symbol = POPULAR_STOCKS.get(investment['name'], 'AAPL')
                stock_df = get_stock_chart_data(ticker_symbol, days)
                
                if stock_df is not None and not stock_df.empty:
                    # Calculate different chart types
                    if chart_type == "percentage":
                        # Calculate percentage change from first value
                        first_price = stock_df["Price"].iloc[0]
                        stock_df["Performance"] = ((stock_df["Price"] - first_price) / first_price) * 100
                        y_values = stock_df["Performance"]
                        y_format = '.2f'
                        y_suffix = '%'
                    elif chart_type == "normalized":
                        # Normalize to start at 100
                        first_price = stock_df["Price"].iloc[0]
                        stock_df["Performance"] = (stock_df["Price"] / first_price) * 100
                        y_values = stock_df["Performance"]
                        y_format = '.2f'
                        y_suffix = ''
                    else:  # absolute
                        # Calculate portfolio value
                        stock_df["Performance"] = stock_df["Price"] * investment['shares']
                        y_values = stock_df["Performance"]
                        y_format = ',.2f'
                        y_suffix = ''
                    
                    fig.add_trace(go.Scatter(
                        x=stock_df["Time"],
                        y=y_values,
                        mode='lines',
                        name=investment['name'],
                        line=dict(color=colors[i % len(colors)], width=2),
                        hovertemplate='<b>%{fullData.name}</b><br>' +
                                    'Date: %{x}<br>' +
                                    f'Value: %{{y:{y_format}}}{y_suffix}<br>' +
                                    '<extra></extra>'
                    ))
        
        except Exception as e:
            st.warning(f"Could not load data for {investment['name']}: {str(e)}")
            continue
    
    # Determine y-axis title and format based on chart type
    if chart_type == "percentage":
        y_title = "Performance (%)"
        y_tickformat = '.1f'
    elif chart_type == "normalized":
        y_title = "Normalized Value (Base = 100)"
        y_tickformat = '.1f'
    else:  # absolute
        y_title = "Portfolio Value (USD)"
        y_tickformat = '$,.0f'
    
    fig.update_layout(
        title={
            'text': f'📈 Portfolio Performance - {time_period}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        xaxis_title="Time",
        yaxis_title=y_title,
        yaxis=dict(tickformat=y_tickformat),
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)'),
        yaxis_showgrid=True,
        height=500,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    return fig

def render_interactive_portfolio_charts(investments: List[Dict]):
    """Render the complete interactive portfolio visualization section"""
    
    st.subheader("📈 Interactive Portfolio Visualizations")
    
    # Control panel for performance chart
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write("**Portfolio Performance Over Time**")
    with col2:
        time_period = st.selectbox(
            "Time Period:",
            ["1D", "7D", "1M", "3M", "6M", "1Y", "ALL"],
            index=2,  # Default to 1M
            key="portfolio_time_period"
        )
    with col3:
        chart_type = st.selectbox(
            "Chart Type:",
            ["Percentage Change", "Normalized Values", "Absolute Values"],
            index=0,  # Default to percentage
            key="portfolio_chart_type"
        )
    
    # Map display names to internal values
    chart_type_map = {
        "Percentage Change": "percentage",
        "Normalized Values": "normalized", 
        "Absolute Values": "absolute"
    }
    chart_type_key = chart_type_map[chart_type]
    
    # Add explanation for chart types
    if chart_type == "Percentage Change":
        st.info("📊 Shows percentage change from the start of the period - best for comparing relative performance")
    elif chart_type == "Normalized Values":
        st.info("📊 Shows values normalized to 100 at start - good for comparing growth patterns")
    else:
        st.info("📊 Shows actual portfolio values in dollars - useful for seeing absolute investment worth")
    
    # Performance chart
    with st.spinner(f"📊 Loading {time_period} portfolio performance chart..."):
        try:
            perf_fig = create_portfolio_time_series_chart(investments, time_period, chart_type_key)
            st.plotly_chart(perf_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading performance chart: {str(e)}")
    
    st.divider()
    
    # Distribution charts in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Individual Investments Distribution**")
        try:
            pie_fig = create_interactive_portfolio_pie_chart(investments)
            st.plotly_chart(pie_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating pie chart: {str(e)}")
    
    with col2:
        st.write("**Investment Types Distribution**")
        try:
            donut_fig = create_interactive_portfolio_donut_chart(investments)
            if donut_fig:
                st.plotly_chart(donut_fig, use_container_width=True)
            else:
                st.info("Add investments to see type distribution")
        except Exception as e:
            st.error(f"Error creating donut chart: {str(e)}")
