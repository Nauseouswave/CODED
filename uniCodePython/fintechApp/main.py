"""
FinSight - AI-Powered Portfolio Tracker
A streamlined Streamlit application for intelligent investment portfolio tracking
"""

import os
from pathlib import Path

import streamlit as st

# Load environment variables from .env file FIRST
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)  # Override existing environment variables
    print(f"DEBUG MAIN: Loaded API key starts with: {os.getenv('OPENAI_API_KEY', 'Not found')[:15]}...")
except ImportError:
    print("DEBUG MAIN: python-dotenv not available")

from utils.storage import load_from_storage, save_to_storage
from utils.analytics import calculate_portfolio_metrics, create_portfolio_dataframe, create_portfolio_pie_chart, create_portfolio_donut_chart
from utils.interactive_charts import render_interactive_portfolio_charts
from components.ui_components import (
    render_investment_input, 
    render_action_buttons, 
    render_performance_table,
    render_edit_forms,
    render_portfolio_summary
)
from components.import_export_ui import render_import_export_page
from components.goals_ui import render_goals_dashboard, render_goals_sidebar_widget
from components.financial_advisor_ui import render_financial_advisor, render_advisor_sidebar_widget
from components.performance_ui import render_performance_dashboard

APP_DIR = Path(__file__).parent
LOGO_PATH = APP_DIR / "logo.png"

# Page configuration
st.set_page_config(
    page_title="FinSight - AI Portfolio Tracker",
    page_icon="💰",
    layout="wide"
)


# Mobile-friendly styling
st.markdown("""
<style>
    /* Improve spacing and typography on small screens */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        h1, h2, h3 {
            line-height: 1.2;
            word-break: break-word;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.25rem;
        }

        .stButton > button,
        .stDownloadButton > button {
            width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing investments
if 'investments' not in st.session_state:
    # Try to load from storage first
    stored_investments = load_from_storage()
    st.session_state.investments = stored_investments

# Sidebar navigation
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=200)
    st.title("Navigation")
    
    # Check if we need to override the page selection
    default_index = 0
    if 'current_page' in st.session_state:
        if st.session_state.current_page == "🤖 AI Financial Advisor":
            default_index = 2
        elif st.session_state.current_page == "🎯 Investment Goals":
            default_index = 1
        elif st.session_state.current_page == "� Performance Tracker":
            default_index = 3
        elif st.session_state.current_page == "�📊 Import/Export Data":
            default_index = 4
        # Clear the session state after setting the index
        del st.session_state.current_page
    
    page = st.radio(
        "Select Page:",
        ["📈 Portfolio Dashboard", "🎯 Investment Goals", "🤖 AI Financial Advisor", "📈 Performance Tracker", "📊 Import/Export Data"],
        index=default_index
    )
    
    st.divider()
    
    # Quick stats in sidebar
    if st.session_state.investments:
        st.subheader("📊 Quick Stats")
        total_investments = len(st.session_state.investments)
        portfolio_metrics = calculate_portfolio_metrics(st.session_state.investments)
        total_value = portfolio_metrics["total_portfolio_value"]
        st.metric("Investments", total_investments)
        st.metric("Total Value", f"${total_value:,.0f}")
        
        st.divider()
        
        # Goals widget in sidebar
        render_goals_sidebar_widget()
        
        # AI Advisor widget in sidebar
        render_advisor_sidebar_widget()
    else:
        st.info("Add investments to see stats")

# Main content area
if page == "📊 Import/Export Data":
    render_import_export_page()
elif page == "🎯 Investment Goals":
    render_goals_dashboard()
elif page == "🤖 AI Financial Advisor":
    render_financial_advisor()
elif page == "📈 Performance Tracker":
    render_performance_dashboard()
else:
    # Original portfolio dashboard
    # Display logo at the top
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=300)

    st.title("FinSight")
    st.header("AI-Powered Investment Portfolio Tracker")
    st.subheader("Monitor your investments and portfolio spread with intelligent insights.")
    st.write("Welcome to FinSight! Here you can track and visualize your investments effortlessly with AI-powered analytics.")

    st.divider()

    # Input section
    investment_name, investment_type, entry_price, shares, risk_level, total_amount, entry_date = render_investment_input()

    st.divider()

    # Buttons section
    action_taken = render_action_buttons(investment_name, investment_type, entry_price, shares, risk_level, total_amount, entry_date)

    st.divider()

    # Display investments and calculations
    if st.session_state.investments:
        # Portfolio header with quick export
        st.subheader("Your Investment Portfolio")
        from utils.import_export import export_portfolio_to_csv
        from datetime import datetime

        # Quick export button
        if st.button("💾 Quick Export", help="Export portfolio to CSV"):
            csv_data = export_portfolio_to_csv(st.session_state.investments)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"portfolio_export_{timestamp}.csv"

            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                key="quick_download"
            )
        
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
        st.dataframe(df, width='stretch')
        
        # Enhanced Portfolio Summary with P&L
        render_portfolio_summary(portfolio_metrics)
        
        # Interactive Portfolio visualizations
        render_interactive_portfolio_charts(st.session_state.investments)
        
    else:
        st.info("No investments added yet. Add your first investment above to get started!")

if LOGO_PATH.exists():
    st.logo(str(LOGO_PATH))
