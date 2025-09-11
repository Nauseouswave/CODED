"""
Portfolio analytics and calculations
"""

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from utils.price_fetcher import get_current_price


def calculate_portfolio_metrics(investments):
    """Calculate portfolio performance metrics"""
    total_portfolio_value = 0
    total_invested = 0
    portfolio_data = []
    
    for inv in investments:
        # Get current price
        current_price = get_current_price(inv['name'], inv['type'])
        
        # Calculate values
        entry_price = inv.get('entry_price', inv['amount'] / inv.get('shares', 1))
        shares = inv.get('shares', 1)
        invested_amount = entry_price * shares
        
        if current_price:
            current_value = current_price * shares
            pnl = current_value - invested_amount
            pnl_percentage = (pnl / invested_amount) * 100 if invested_amount > 0 else 0
        else:
            current_value = invested_amount
            pnl = 0
            pnl_percentage = 0
        
        total_portfolio_value += current_value
        total_invested += invested_amount
        
        portfolio_data.append({
            'investment': inv,
            'entry_price': entry_price,
            'shares': shares,
            'current_price': current_price,
            'invested_amount': invested_amount,
            'current_value': current_value,
            'pnl': pnl,
            'pnl_percentage': pnl_percentage
        })
    
    total_pnl = total_portfolio_value - total_invested
    total_pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    return {
        'portfolio_data': portfolio_data,
        'total_invested': total_invested,
        'total_portfolio_value': total_portfolio_value,
        'total_pnl': total_pnl,
        'total_pnl_percentage': total_pnl_percentage
    }


def create_portfolio_dataframe(investments):
    """Create a pandas DataFrame for portfolio display"""
    portfolio_data = []
    total_value = sum(inv['amount'] for inv in investments)
    
    for inv in investments:
        percentage = (inv['amount'] / total_value) * 100 if total_value > 0 else 0
        portfolio_data.append({
            'Investment Name': inv['name'],
            'Investment Type': inv['type'],
            'Amount ($)': f"${inv['amount']:,.2f}",
            'Percentage (%)': f"{percentage:.1f}%",
            'Risk Level': inv['risk_level']
        })
    
    return pd.DataFrame(portfolio_data)


def create_portfolio_pie_chart(investments):
    """Create a pie chart for portfolio distribution"""
    # Group by investment name and sum amounts (in case of duplicate names)
    name_totals = {}
    for inv in investments:
        if inv['name'] in name_totals:
            name_totals[inv['name']] += inv['amount']
        else:
            name_totals[inv['name']] = inv['amount']
    
    # Create pie chart data
    chart_data = pd.DataFrame(
        list(name_totals.items()),
        columns=['Investment Name', 'Amount']
    )
    
    # Create pie chart using Matplotlib
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(chart_data['Amount'], labels=chart_data['Investment Name'], autopct='%1.1f%%')
    ax.set_title('Portfolio Distribution by Individual Investments')
    
    return fig
