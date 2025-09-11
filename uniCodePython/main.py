"""
Main Portfolio App
A streamlined Streamlit application for investment portfolio tracking
"""

import streamlit as st
from utils.storage import load_from_storage, save_to_storage
from utils.analytics import calculate_portfolio_metrics, create_portfolio_dataframe, create_portfolio_pie_chart
from components.ui_components import (
    render_investment_input, 
    render_action_buttons, 
    render_performance_table,
    render_edit_forms,
    render_portfolio_summary
)

# Page configuration
st.set_page_config(
    page_title="Fintech Portfolio App",
    page_icon="💰",
    layout="wide"
)

# Display logo at the top
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", width=300)

st.title("Fintech Portfolio App")
st.header("Investment Portfolio Tracker")
st.subheader("Monitor your investments and portfolio spread.")
st.write("Welcome to the Fintech Portfolio App! Here you can track and visualize your investments effortlessly.")

# Initialize session state for storing investments
if 'investments' not in st.session_state:
    # Try to load from storage first
    stored_investments = load_from_storage()
    st.session_state.investments = stored_investments

st.divider()

# Input section
investment_name, investment_type, entry_price, shares, risk_level, total_amount = render_investment_input()

st.divider()

# Buttons section
action_taken = render_action_buttons(investment_name, investment_type, entry_price, shares, risk_level, total_amount)

st.divider()

# Display investments and calculations
if st.session_state.investments:
    st.subheader("Your Investment Portfolio")
    
    # Calculate portfolio metrics
    portfolio_metrics = calculate_portfolio_metrics(st.session_state.investments)
    
    # Performance tracking section
    investments_to_remove = render_performance_table(portfolio_metrics)
    
    # Remove investments marked for deletion
    if investments_to_remove:
        for idx in sorted(investments_to_remove, reverse=True):
            removed_inv = st.session_state.investments.pop(idx)
            st.success(f"Deleted {removed_inv['name']}")
        save_to_storage(st.session_state.investments)
        st.rerun()
    
    # Edit form section
    render_edit_forms()
    
    st.divider()
    
    # Portfolio summary table (read-only view)
    st.subheader("Portfolio Summary Table")
    df = create_portfolio_dataframe(st.session_state.investments)
    st.dataframe(df, use_container_width=True)
    
    # Enhanced Portfolio Summary with P&L
    render_portfolio_summary(portfolio_metrics)
    
    # Pie chart for visualization
    st.subheader("Portfolio Distribution")
    fig = create_portfolio_pie_chart(st.session_state.investments)
    st.pyplot(fig)
    
else:
    st.info("No investments added yet. Add your first investment above to get started!")

st.logo("logo.png")
