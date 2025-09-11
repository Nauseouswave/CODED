"""
UI components for the portfolio app
"""

import streamlit as st
from datetime import datetime
from data.constants import POPULAR_STOCKS, POPULAR_CRYPTO
from utils.price_fetcher import get_current_price
from utils.storage import save_to_storage


def render_investment_input():
    """Render the investment input form"""
    st.subheader("Add New Investment")
    col1, col2 = st.columns(2)

    with col1:
        investment_type = st.selectbox("Select Investment Type:", ["Stocks", "Bonds", "Real Estate", "Cryptocurrency"])
        
        # Show different options based on investment type
        if investment_type == "Stocks":
            st.write("**Select from Popular Stocks:**")
            investment_name = st.selectbox(
                "Choose a stock:",
                [""] + list(POPULAR_STOCKS.keys()) + ["Custom Entry"],
                key="stock_select"
            )
            
            # If custom entry is selected, show text input
            if investment_name == "Custom Entry":
                investment_name = st.text_input("Enter custom stock symbol (e.g., AAPL):")
            elif investment_name == "":
                investment_name = ""
                
        elif investment_type == "Cryptocurrency":
            st.write("**Select from Popular Cryptocurrencies:**")
            investment_name = st.selectbox(
                "Choose a cryptocurrency:",
                [""] + list(POPULAR_CRYPTO.keys()) + ["Custom Entry"],
                key="crypto_select"
            )
            
            # If custom entry is selected, show text input
            if investment_name == "Custom Entry":
                investment_name = st.text_input("Enter custom crypto name:")
            elif investment_name == "":
                investment_name = ""
                
        else:
            # For Bonds, Real Estate, etc. - just use text input
            investment_name = st.text_input("Enter Investment Name:")
        
        entry_price = st.number_input("Enter Entry Price per Share/Unit ($):", min_value=0.0, step=0.01)
        
        # Show live price preview for supported assets
        if investment_name and investment_name not in ["", "Custom Entry"] and investment_type in ["Stocks", "Cryptocurrency"]:
            with st.spinner("Fetching live price..."):
                live_price = get_current_price(investment_name, investment_type)
                if live_price:
                    st.success(f"💰 **Live Price**: ${live_price:.2f}")
                    if st.button("📋 Use Live Price as Entry Price"):
                        st.session_state[f"entry_price_{investment_type}"] = live_price
                        st.rerun()
                else:
                    st.warning("⚠️ Unable to fetch live price")
        
    with col2:
        total_amount = st.number_input("Enter Total Amount Invested ($):", min_value=0.0, step=0.01)
        risk_level = st.selectbox("Select Risk Level:", ["Low", "Medium", "High"])
        
    # Auto-fill entry price if requested
    if f"entry_price_{investment_type}" in st.session_state:
        entry_price = st.session_state[f"entry_price_{investment_type}"]
        del st.session_state[f"entry_price_{investment_type}"]

    # Calculate number of shares/units
    if entry_price > 0 and total_amount > 0:
        shares = total_amount / entry_price
        st.info(f"📊 **Shares/Units**: {shares:.4f}")
        st.info(f"💵 **Total Investment Amount**: ${total_amount:,.2f}")
    else:
        shares = 0

    return investment_name, investment_type, entry_price, shares, risk_level, total_amount


def render_action_buttons(investment_name, investment_type, entry_price, shares, risk_level, total_amount):
    """Render the action buttons for adding and clearing investments"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Add Investment", type="primary"):
            if investment_name and investment_type and entry_price > 0 and total_amount > 0:
                investment = {
                    'name': investment_name,
                    'type': investment_type,
                    'entry_price': entry_price,
                    'shares': shares,
                    'amount': total_amount,
                    'risk_level': risk_level,
                    'date_added': datetime.now().isoformat()
                }
                st.session_state.investments.append(investment)
                # Save to storage whenever we add an investment
                save_to_storage(st.session_state.investments)
                st.success(f"Investment '{investment_name}' of ${total_amount:,.2f} ({shares:.4f} shares at ${entry_price}) added successfully!")
                st.balloons()
                return True
            else:
                st.error("Please fill in all fields with valid values.")
                return False

    with col2:
        if st.button("Clear All Investments"):
            st.session_state.investments = []
            # Clear storage when clearing all investments
            save_to_storage([])
            st.success("All investments cleared!")
            return True
    
    return False


def render_performance_table(portfolio_metrics):
    """Render the live performance tracking table"""
    st.subheader("📈 Live Performance Tracking")
    
    # Create columns for performance display
    col_names = ["Investment", "Shares", "Entry Price", "Current Price", "Total Value", "P&L", "P&L %", "Actions"]
    
    # Display header
    header_cols = st.columns([1.5, 0.8, 1, 1, 1.2, 1, 0.8, 1])
    for i, header in enumerate(col_names):
        header_cols[i].write(f"**{header}**")
    
    # Display each investment with performance data
    investments_to_remove = []
    
    for idx, data in enumerate(portfolio_metrics['portfolio_data']):
        inv = data['investment']
        cols = st.columns([1.5, 0.8, 1, 1, 1.2, 1, 0.8, 1])
        
        with cols[0]:
            st.write(inv['name'])
        
        with cols[1]:
            st.write(f"{data['shares']:.2f}")
        
        with cols[2]:
            st.write(f"${data['entry_price']:.2f}")
        
        with cols[3]:
            if data['current_price']:
                st.write(f"${data['current_price']:.2f}")
            else:
                st.write("N/A")
        
        with cols[4]:
            st.write(f"${data['current_value']:,.2f}")
        
        with cols[5]:
            if data['pnl'] >= 0:
                st.write(f"🟢 ${data['pnl']:,.2f}")
            else:
                st.write(f"🔴 ${data['pnl']:,.2f}")
        
        with cols[6]:
            if data['pnl_percentage'] >= 0:
                st.write(f"🟢 {data['pnl_percentage']:.1f}%")
            else:
                st.write(f"🔴 {data['pnl_percentage']:.1f}%")
        
        with cols[7]:
            col_update, col_delete = st.columns(2)
            
            with col_update:
                if st.button("📝", key=f"edit_{idx}", help="Edit investment"):
                    # Set editing flag instead of showing form inline
                    st.session_state[f"editing_{idx}"] = True
                    st.rerun()
            
            with col_delete:
                if st.button("🗑️", key=f"delete_{idx}", help="Delete investment"):
                    investments_to_remove.append(idx)
    
    return investments_to_remove


def render_edit_forms():
    """Render edit forms for investments"""
    for idx, inv in enumerate(st.session_state.investments):
        if st.session_state.get(f"editing_{idx}", False):
            st.divider()
            st.subheader(f"✏️ Edit {inv['name']}")
            
            # Get current values
            current_amount = inv.get('amount', 0)
            current_entry = inv.get('entry_price', 0)
            
            # Create clean edit form with proper width
            edit_col1, edit_col2, edit_col3 = st.columns(3)
            
            with edit_col1:
                new_total = st.number_input(
                    "Total Amount Invested ($):", 
                    value=float(current_amount), 
                    min_value=0.0,
                    step=0.01,
                    key=f"edit_amount_{idx}"
                )
            
            with edit_col2:
                new_entry = st.number_input(
                    "Entry Price per Share/Unit ($):", 
                    value=float(current_entry), 
                    min_value=0.0,
                    step=0.01,
                    key=f"edit_entry_{idx}"
                )
            
            with edit_col3:
                st.write("**Calculated Shares/Units:**")
                if new_entry > 0:
                    new_shares = new_total / new_entry
                    st.info(f"{new_shares:.4f}")
                else:
                    new_shares = 0
                    st.info("0")
            
            # Action buttons
            button_col1, button_col2, button_col3 = st.columns([1, 1, 4])
            
            with button_col1:
                if st.button("💾 Save Changes", key=f"save_{idx}", type="primary"):
                    st.session_state.investments[idx]['shares'] = new_shares
                    st.session_state.investments[idx]['entry_price'] = new_entry
                    st.session_state.investments[idx]['amount'] = new_total
                    save_to_storage(st.session_state.investments)
                    st.session_state[f"editing_{idx}"] = False
                    st.success(f"✅ Updated {inv['name']}")
                    st.rerun()
            
            with button_col2:
                if st.button("❌ Cancel", key=f"cancel_{idx}"):
                    st.session_state[f"editing_{idx}"] = False
                    st.rerun()


def render_portfolio_summary(portfolio_metrics):
    """Render portfolio summary metrics"""
    st.subheader("📊 Portfolio Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Investment", f"${portfolio_metrics['total_invested']:,.2f}")
    
    with col2:
        st.metric("Current Value", f"${portfolio_metrics['total_portfolio_value']:,.2f}")
    
    with col3:
        st.metric("Total P&L", f"${portfolio_metrics['total_pnl']:,.2f}", f"{portfolio_metrics['total_pnl_percentage']:.1f}%")
    
    with col4:
        st.metric("Number of Holdings", len(st.session_state.investments))
