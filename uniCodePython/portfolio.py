import streamlit as st
import pandas as pd
import plotly.express as px

# Fintech Portfolio App: Track and visualize your investments

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
    st.session_state.investments = []

st.divider()

# Input section
st.subheader("Add New Investment")
col1, col2 = st.columns(2)

with col1:
    investment_name = st.text_input("Enter Investment Name (e.g., Bitcoin, Apple Stock, etc.):")
    investment_type = st.selectbox("Select Investment Type:", ["Stocks", "Bonds", "Real Estate", "Cryptocurrency"])
    
with col2:
    amount = st.number_input("Enter Investment Amount ($):", min_value=0.0, step=0.01)
    risk_level = st.selectbox("Select Risk Level:", ["Low", "Medium", "High"])

st.divider()

# Buttons section
col1, col2 = st.columns(2)
with col1:
    if st.button("Add Investment", type="primary"):
        if investment_name and investment_type and amount > 0:
            investment = {
                'name': investment_name,
                'type': investment_type,
                'amount': amount,
                'risk_level': risk_level
            }
            st.session_state.investments.append(investment)
            st.success(f"Investment '{investment_name}' of ${amount:,.2f} in {investment_type} added successfully!")
            st.balloons()
        else:
            st.error("Please fill in all fields and enter a valid amount.")

with col2:
    if st.button("Clear All Investments"):
        st.session_state.investments = []
        st.success("All investments cleared!")

st.divider()

# Display investments and calculations
if st.session_state.investments:
    st.subheader("Your Investment Portfolio")
    
    # Calculate total portfolio value
    total_value = sum(inv['amount'] for inv in st.session_state.investments)
    
    # Create dataframe for display
    portfolio_data = []
    for inv in st.session_state.investments:
        percentage = (inv['amount'] / total_value) * 100
        portfolio_data.append({
            'Investment Name': inv['name'],
            'Investment Type': inv['type'],
            'Amount ($)': f"${inv['amount']:,.2f}",
            'Percentage (%)': f"{percentage:.1f}%",
            'Risk Level': inv['risk_level']
        })
    
    df = pd.DataFrame(portfolio_data)
    st.dataframe(df, use_container_width=True)
    
    # Summary statistics
    st.subheader("Portfolio Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Portfolio Value", f"${total_value:,.2f}")
    
    with col2:
        st.metric("Number of Investments", len(st.session_state.investments))
    
    with col3:
        # Calculate average risk (simplified)
        risk_scores = {'Low': 1, 'Medium': 2, 'High': 3}
        avg_risk_score = sum(risk_scores[inv['risk_level']] for inv in st.session_state.investments) / len(st.session_state.investments)
        if avg_risk_score <= 1.5:
            avg_risk = "Low"
        elif avg_risk_score <= 2.5:
            avg_risk = "Medium"
        else:
            avg_risk = "High"
        st.metric("Average Risk Level", avg_risk)
    
    # Pie chart for visualization
    st.subheader("Portfolio Distribution")
    
    # Group by investment type and sum amounts
    type_totals = {}
    for inv in st.session_state.investments:
        if inv['type'] in type_totals:
            type_totals[inv['type']] += inv['amount']
        else:
            type_totals[inv['type']] = inv['amount']
    
    # Create pie chart data
    chart_data = pd.DataFrame(
        list(type_totals.items()),
        columns=['Investment Type', 'Amount']
    )
    
    # Create pie chart using Plotly
    fig = px.pie(chart_data, values='Amount', names='Investment Type', 
                 title='Portfolio Distribution by Investment Type')
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info("No investments added yet. Add your first investment above to get started!")

st.logo("logo.png")