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
    """Create a modern, styled pie chart for portfolio distribution"""
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
    
    # Modern color palette - gradient from dark to light
    colors = [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange  
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
        '#bcbd22',  # Olive
        '#17becf',  # Cyan
        '#aec7e8',  # Light Blue
        '#ffbb78',  # Light Orange
        '#98df8a',  # Light Green
        '#ff9896',  # Light Red
        '#c5b0d5',  # Light Purple
    ]
    
    # Create figure with modern styling
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('#f8f9fa')  # Light background
    
    # Create the pie chart with enhanced styling
    wedges, texts, autotexts = ax.pie(
        chart_data['Amount'], 
        labels=None,  # We'll create custom labels
        autopct='%1.1f%%',
        colors=colors[:len(chart_data)],
        startangle=90,
        explode=[0.05] * len(chart_data),  # Slightly separate all slices
        shadow=True,
        textprops={'fontsize': 11, 'fontweight': 'bold', 'color': 'white'}
    )
    
    # Customize the percentage text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    # Create custom legend with investment names and amounts
    legend_labels = []
    for i, (name, amount) in enumerate(zip(chart_data['Investment Name'], chart_data['Amount'])):
        # Truncate long names for better display
        display_name = name if len(name) <= 15 else name[:12] + "..."
        legend_labels.append(f'{display_name}: ${amount:,.0f}')
    
    # Position legend to the right of the chart
    legend = ax.legend(
        wedges, 
        legend_labels,
        title="Investments",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=10,
        title_fontsize=12,
        frameon=True,
        fancybox=True,
        shadow=True,
        framealpha=0.9
    )
    
    # Set title weight separately for compatibility
    legend.get_title().set_fontweight('bold')
    
    # Modern title styling
    ax.set_title(
        '💼 Portfolio Distribution', 
        fontsize=18, 
        fontweight='bold', 
        pad=20,
        color='#2c3e50'
    )
    
    # Add a subtle subtitle
    fig.suptitle(
        'Investment Allocation by Value',
        fontsize=12,
        y=0.02,
        color='#7f8c8d',
        alpha=0.8
    )
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')
    
    # Adjust layout to prevent legend cutoff
    plt.tight_layout()
    
    return fig


def create_portfolio_donut_chart(investments):
    """Create a modern donut chart for portfolio distribution"""
    # Group by investment type for a different view
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
    chart_data = pd.DataFrame(
        list(type_totals.items()),
        columns=['Investment Type', 'Amount']
    )
    
    # Color scheme for investment types
    type_colors = {
        'Stocks': '#3498db',        # Blue
        'Cryptocurrency': '#f39c12', # Orange
        'Bonds': '#27ae60',         # Green
        'Real Estate': '#e74c3c',   # Red
        'Other': '#9b59b6'          # Purple
    }
    
    colors = [type_colors.get(inv_type, '#95a5a6') for inv_type in chart_data['Investment Type']]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('#f8f9fa')
    
    # Create donut chart
    wedges, texts, autotexts = ax.pie(
        chart_data['Amount'],
        labels=chart_data['Investment Type'],
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        pctdistance=0.85,
        wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2),
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )
    
    # Customize percentage text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
    
    # Add center circle for donut effect
    centre_circle = plt.Circle((0, 0), 0.70, fc='white', linewidth=2, edgecolor='#bdc3c7')
    fig.gca().add_artist(centre_circle)
    
    # Add center text
    ax.text(0, 0.1, 'Portfolio', horizontalalignment='center', fontsize=16, fontweight='bold', color='#2c3e50')
    ax.text(0, -0.1, 'by Type', horizontalalignment='center', fontsize=12, color='#7f8c8d')
    
    # Title
    ax.set_title('📊 Investment Types Distribution', fontsize=18, fontweight='bold', pad=20, color='#2c3e50')
    
    ax.axis('equal')
    plt.tight_layout()
    
    return fig
