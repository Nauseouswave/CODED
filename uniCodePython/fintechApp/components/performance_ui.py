"""
Performance Tracking UI Component
Streamlit interface for investment performance analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import List, Dict

try:
    from ..utils.performance_tracker import PerformanceTracker
    from ..utils.storage import load_investments
except ImportError:
    # Fallback imports for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from utils.performance_tracker import PerformanceTracker
    from utils.storage import load_investments

def render_performance_dashboard():
    """Render the performance tracking dashboard"""
    
    st.header("📈 Investment Performance Tracker")
    st.write("Track your investment performance over time with real-time data from CoinGecko and Yahoo Finance.")
    
    # Load investments
    investments = load_investments()
    
    if not investments:
        st.info("🏦 No investments found. Add some investments first to track performance!")
        return
    
    # Initialize performance tracker
    tracker = PerformanceTracker()
    
    # Performance options
    st.subheader("⚙️ Performance Analysis Options")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analysis_type = st.selectbox(
            "Select Analysis Type:",
            ["📊 Portfolio Overview", "📈 Individual Performance", "📉 Detailed Analytics"],
            help="Choose the type of performance analysis you want to see"
        )
    
    with col2:
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    # Main analysis section
    if analysis_type == "📊 Portfolio Overview":
        render_portfolio_overview(tracker, investments)
    elif analysis_type == "📈 Individual Performance":
        # Use simple approach without complex pandas calculations
        from .simple_performance import render_simple_individual_performance
        render_simple_individual_performance(investments)
    else:  # Detailed Analytics
        render_detailed_analytics(tracker, investments)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_portfolio_performance(investments_data):
    """Get portfolio performance with caching"""
    tracker = PerformanceTracker()
    return tracker.get_portfolio_performance(investments_data)

def render_portfolio_overview(tracker: PerformanceTracker, investments: List[Dict]):
    """Render portfolio-level overview"""
    
    st.subheader("💼 Portfolio Performance Overview")
    
    with st.spinner("📡 Fetching real-time performance data..."):
        # Convert investments to a hashable format for caching
        investments_tuple = tuple(
            (inv['name'], inv['type'], inv['entry_price'], inv['shares'], 
             inv['amount'], inv['date_added']) for inv in investments
        )
        
        portfolio_df = get_cached_portfolio_performance(investments)
        
        if portfolio_df.empty:
            st.error("❌ Unable to fetch performance data. Please try again later.")
            return
        
        # Calculate portfolio metrics
        total_invested = portfolio_df['total_invested'].sum()
        total_current = portfolio_df['current_value'].sum()
        total_return = total_current - total_invested
        total_return_pct = (total_return / total_invested) * 100 if total_invested > 0 else 0
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Total Invested", 
                f"${total_invested:,.2f}",
                help="Total amount invested across all holdings"
            )
        
        with col2:
            st.metric(
                "💎 Current Value", 
                f"${total_current:,.2f}",
                help="Current market value of all holdings"
            )
        
        with col3:
            delta_color = "normal" if total_return >= 0 else "inverse"
            st.metric(
                "📊 Total Return", 
                f"${total_return:,.2f}",
                delta=f"{total_return_pct:+.2f}%",
                delta_color=delta_color,
                help="Absolute and percentage return on investment"
            )
        
        with col4:
            best_performer = portfolio_df.loc[portfolio_df['percentage_return'].idxmax()]
            st.metric(
                "🏆 Best Performer", 
                best_performer['name'],
                delta=f"+{best_performer['percentage_return']:.1f}%",
                help="Investment with highest percentage return"
            )
        
        st.divider()
        
        # Portfolio composition chart
        st.subheader("🥧 Portfolio Composition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart by current value
            fig_pie = px.pie(
                portfolio_df, 
                values='current_value', 
                names='name',
                title="Portfolio Distribution by Current Value",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart of returns
            portfolio_df_sorted = portfolio_df.sort_values('percentage_return', ascending=True)
            
            colors = ['red' if x < 0 else 'green' for x in portfolio_df_sorted['percentage_return']]
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=portfolio_df_sorted['percentage_return'],
                    y=portfolio_df_sorted['name'],
                    orientation='h',
                    marker_color=colors,
                    text=[f"{x:.1f}%" for x in portfolio_df_sorted['percentage_return']],
                    textposition='auto'
                )
            ])
            
            fig_bar.update_layout(
                title="Performance by Investment",
                xaxis_title="Return (%)",
                yaxis_title="Investment",
                showlegend=False
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Performance table
        st.subheader("📋 Detailed Performance Table")
        
        display_df = portfolio_df[['name', 'type', 'entry_date', 'entry_price', 
                                  'current_price', 'total_invested', 'current_value', 
                                  'absolute_return', 'percentage_return', 'days_held']].copy()
        
        # Format columns for better display
        display_df['entry_price'] = display_df['entry_price'].apply(lambda x: f"${x:.2f}")
        display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:.2f}")
        display_df['total_invested'] = display_df['total_invested'].apply(lambda x: f"${x:,.2f}")
        display_df['current_value'] = display_df['current_value'].apply(lambda x: f"${x:,.2f}")
        display_df['absolute_return'] = display_df['absolute_return'].apply(lambda x: f"${x:+,.2f}")
        display_df['percentage_return'] = display_df['percentage_return'].apply(lambda x: f"{x:+.2f}%")
        
        # Rename columns for display
        display_df.columns = ['Investment', 'Type', 'Entry Date', 'Entry Price', 
                             'Current Price', 'Invested', 'Current Value', 
                             'Return ($)', 'Return (%)', 'Days Held']
        
        st.dataframe(display_df, width='stretch')

def render_individual_performance(tracker: PerformanceTracker, investments: List[Dict]):
    """Render individual investment performance"""
    
    st.subheader("🔍 Individual Investment Analysis")
    
    # Select investment to analyze
    investment_names = [inv['name'] for inv in investments]
    selected_investment = st.selectbox("Select an investment to analyze:", investment_names)
    
    if not selected_investment:
        return
    
    # Find the selected investment
    investment = next(inv for inv in investments if inv['name'] == selected_investment)
    
    with st.spinner(f"📊 Analyzing {selected_investment}..."):
        try:
            # Get historical data
            start_date = investment['date_added']
            
            if investment['type'].lower() == 'cryptocurrency':
                historical_data = tracker.get_crypto_historical_data(investment['name'], start_date)
            else:
                historical_data = tracker.get_stock_historical_data(investment['name'], start_date)
            
            if historical_data is None or historical_data.empty:
                st.error(f"❌ Unable to fetch historical data for {selected_investment}")
                return
            
            # Calculate performance
            performance = tracker.calculate_investment_performance(investment, historical_data)
            
            if not performance:
                st.error("❌ Unable to calculate performance metrics")
                return
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Invested", f"${performance['total_invested']:,.2f}")
            
            with col2:
                st.metric("💎 Current Value", f"${performance['current_value']:,.2f}")
            
            with col3:
                delta_color = "normal" if performance['absolute_return'] >= 0 else "inverse"
                st.metric(
                    "📊 Return", 
                    f"${performance['absolute_return']:+,.2f}",
                    delta=f"{performance['percentage_return']:+.2f}%",
                    delta_color=delta_color
                )
            
            with col4:
                st.metric("📅 Days Held", f"{performance['days_held']} days")
            
            # Price chart
            st.subheader(f"📈 Price History for {selected_investment}")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=historical_data.index,
                y=historical_data['price'],
                mode='lines',
                name='Price',
                line=dict(color='blue', width=2)
            ))
            
            # Add entry point
            entry_date = pd.to_datetime(performance['entry_date'])
            fig.add_vline(
                x=entry_date,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Entry: ${performance['entry_price']:.2f}",
                annotation_position="top left"
            )
            
            fig.update_layout(
                title=f"{selected_investment} Price History",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                showlegend=True,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Investment Details")
                st.write(f"**Type:** {performance['type']}")
                st.write(f"**Entry Date:** {performance['entry_date']}")
                st.write(f"**Entry Price:** ${performance['entry_price']:.2f}")
                st.write(f"**Shares/Units:** {performance['shares']:.4f}")
                st.write(f"**Current Price:** ${performance['current_price']:.2f}")
            
            with col2:
                st.subheader("📈 Performance Metrics")
                st.write(f"**Total Return:** ${performance['absolute_return']:+,.2f}")
                st.write(f"**Return Percentage:** {performance['percentage_return']:+.2f}%")
                st.write(f"**Annualized Return:** {performance['annualized_return']:+.2f}%")
                st.write(f"**Days Held:** {performance['days_held']} days")
                
                # Price change indicator
                price_change = ((performance['current_price'] - performance['entry_price']) / performance['entry_price']) * 100
                if price_change >= 0:
                    st.success(f"📈 Price increased by {price_change:.2f}%")
                else:
                    st.error(f"📉 Price decreased by {abs(price_change):.2f}%")
                    
        except Exception as e:
            st.error(f"❌ Error analyzing {selected_investment}: {str(e)}")

def render_detailed_analytics(tracker: PerformanceTracker, investments: List[Dict]):
    """Render detailed analytics and insights"""
    
    st.subheader("🔬 Detailed Portfolio Analytics")
    
    with st.spinner("🧮 Computing advanced analytics..."):
        portfolio_df = get_cached_portfolio_performance(investments)
        
        if portfolio_df.empty:
            st.error("❌ Unable to fetch performance data for analytics")
            return
        
        # Risk analysis
        st.subheader("⚠️ Risk Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Volatility analysis (based on returns)
            returns_std = portfolio_df['percentage_return'].std()
            st.metric("📊 Portfolio Volatility", f"{returns_std:.2f}%")
            
            # Concentration risk
            portfolio_df['weight'] = portfolio_df['current_value'] / portfolio_df['current_value'].sum()
            max_weight = portfolio_df['weight'].max() * 100
            st.metric("🎯 Max Position Size", f"{max_weight:.1f}%")
        
        with col2:
            # Performance distribution
            positive_returns = len(portfolio_df[portfolio_df['percentage_return'] > 0])
            total_investments = len(portfolio_df)
            win_rate = (positive_returns / total_investments) * 100
            st.metric("🏆 Win Rate", f"{win_rate:.1f}%")
            
            # Average return
            avg_return = portfolio_df['percentage_return'].mean()
            st.metric("📊 Average Return", f"{avg_return:.2f}%")
        
        # Time analysis
        st.subheader("⏰ Time-Based Analysis")
        
        # Group by holding period
        portfolio_df['holding_period'] = pd.cut(
            portfolio_df['days_held'], 
            bins=[0, 30, 90, 180, 365, float('inf')],
            labels=['< 1 Month', '1-3 Months', '3-6 Months', '6-12 Months', '> 1 Year']
        )
        
        holding_analysis = portfolio_df.groupby('holding_period', observed=True).agg({
            'percentage_return': 'mean',
            'name': 'count'
        }).round(2)
        holding_analysis.columns = ['Average Return (%)', 'Number of Investments']
        
        st.subheader("📅 Performance by Holding Period")
        st.dataframe(holding_analysis, width='stretch')
        
        # Investment type analysis
        st.subheader("🏷️ Performance by Investment Type")
        
        type_analysis = portfolio_df.groupby('type', observed=True).agg({
            'total_invested': 'sum',
            'current_value': 'sum',
            'percentage_return': 'mean',
            'name': 'count'
        }).round(2)
        type_analysis['total_return'] = type_analysis['current_value'] - type_analysis['total_invested']
        type_analysis.columns = ['Total Invested', 'Current Value', 'Avg Return (%)', 'Count', 'Total Return']
        
        # Format for display
        type_display = type_analysis.copy()
        type_display['Total Invested'] = type_display['Total Invested'].apply(lambda x: f"${x:,.2f}")
        type_display['Current Value'] = type_display['Current Value'].apply(lambda x: f"${x:,.2f}")
        type_display['Total Return'] = type_display['Total Return'].apply(lambda x: f"${x:+,.2f}")
        type_display['Avg Return (%)'] = type_display['Avg Return (%)'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(type_display, width='stretch')

if __name__ == "__main__":
    # For testing the component directly
    st.set_page_config(page_title="Performance Tracker Test", layout="wide")
    render_performance_dashboard()
